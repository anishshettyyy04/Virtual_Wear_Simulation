import asyncio
import hashlib
import json
import os
import re
from pathlib import Path
from typing import Any, Dict, Optional, Tuple, Union

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

from app.config.settings import settings
from app.schemas.ai import (
    AgnosticMaskResult,
    GarmentCategory,
    GarmentInput,
    HumanParsingResult,
    PoseEstimationResult,
    PreprocessingResult,
)
from app.services.ai.exceptions import AgnosticMaskError, AIPipelineError
from app.services.ai.interfaces.agnostic_mask_generator import (
    BaseAgnosticMaskGenerator,
)
from app.services.ai.parsing.labels import ProjectSemanticLabel
from app.utils.logger import logger


class AgnosticMaskGenerator(BaseAgnosticMaskGenerator):
    """Production Pillow/NumPy clothing-agnostic mask generator."""

    def __init__(self, output_dir: Optional[str] = None) -> None:
        self.output_dir = Path(output_dir or settings.AI_AGNOSTIC_MASK_OUTPUT_DIR)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        logger.info(
            f"AgnosticMaskGenerator initialized (output_dir='{self.output_dir}')"
        )

    def _sanitize_id(self, logical_id: str) -> str:
        """Sanitizes logical ID for collision-resistant filenames."""
        cleaned = re.sub(r"[^a-zA-Z0-9_\-]", "_", logical_id).strip("_")
        if not cleaned:
            cleaned = "person"
        hash_suffix = hashlib.sha256(logical_id.encode("utf-8")).hexdigest()[:8]
        return f"{cleaned}_{hash_suffix}"

    def _normalize_category(
        self, category_input: Union[GarmentCategory, str]
    ) -> GarmentCategory:
        """Normalizes user category input to canonical GarmentCategory Enum."""
        if isinstance(category_input, GarmentCategory):
            return category_input

        cat_str = str(category_input).lower().strip()
        if cat_str in (
            "upper_body",
            "upper",
            "top",
            "tops",
            "shirt",
            "tshirt",
            "t-shirt",
            "jacket",
            "hoodie",
            "sweater",
        ):
            return GarmentCategory.UPPER_BODY
        elif cat_str in (
            "lower_body",
            "lower",
            "bottom",
            "bottoms",
            "pants",
            "jeans",
            "shorts",
            "skirt",
            "trousers",
        ):
            return GarmentCategory.LOWER_BODY
        elif cat_str in ("full_body", "full", "dress", "jumpsuit", "suit", "overalls"):
            return GarmentCategory.FULL_BODY
        else:
            raise AgnosticMaskError(
                f"Unsupported garment category '{category_input}'. "
                "Must be upper_body, lower_body, or full_body."
            )

    def _load_parsing_mask(
        self, mask_ref: str, expected_dims: Tuple[int, int]
    ) -> Tuple[np.ndarray, Image.Image]:
        """Loads and validates single-channel 8-bit parsing mask artifact."""
        mask_path = Path(mask_ref)
        if not mask_path.exists() or not mask_path.is_file():
            raise AgnosticMaskError(
                f"Human parsing mask artifact '{mask_ref}' does not exist."
            )

        try:
            pil_img = Image.open(mask_path).convert("L")
            if pil_img.size != expected_dims:
                raise AgnosticMaskError(
                    f"Dimension mismatch between parsing mask {pil_img.size} "
                    f"and person image {expected_dims}."
                )
            return np.array(pil_img, dtype=np.uint8), pil_img
        except Exception as exc:
            if isinstance(exc, AgnosticMaskError):
                raise
            raise AgnosticMaskError(
                f"Failed to read parsing mask artifact '{mask_ref}': {exc}"
            ) from exc

    def _load_pose_artifact(self, pose_ref: str) -> Tuple[Dict[str, Any], bool]:
        """Loads and validates COCO-18 pose JSON artifact."""
        pose_path = Path(pose_ref)
        if not pose_path.exists() or not pose_path.is_file():
            raise AgnosticMaskError(
                f"Pose estimation artifact '{pose_ref}' does not exist."
            )

        try:
            with open(pose_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            schema_version = data.get("schema_version")
            if schema_version != "v1":
                logger.warning(
                    f"Pose schema version '{schema_version}' differs from 'v1'."
                )

            keypoints = data.get("keypoints", [])
            valid_kpts = [k for k in keypoints if k.get("visible", False)]
            has_pose = len(valid_kpts) > 0
            return data, has_pose
        except Exception as exc:
            if isinstance(exc, AgnosticMaskError):
                raise
            raise AgnosticMaskError(
                f"Failed to parse pose JSON artifact '{pose_ref}': {exc}"
            ) from exc

    def _generate_sync(
        self,
        person_image_path: Path,
        parsing: HumanParsingResult,
        pose: PoseEstimationResult,
        garment: GarmentInput,
        safe_id: str,
        target_dims: Tuple[int, int],
    ) -> Tuple[Path, float, dict[str, Any]]:
        """Synchronous mask generation and Pillow/NumPy processing helper."""
        img_w, img_h = target_dims
        category = self._normalize_category(garment.category)

        # Resolution-scaled morphology calculations
        scale = min(img_w, img_h) / 1024.0
        dilation_px = max(4, min(48, int(round(16.0 * scale))))
        arm_width_px = max(10, min(90, int(round(30.0 * scale))))
        kernel_size = 2 * dilation_px + 1  # Guaranteed odd integer for PIL MaxFilter
        face_shield_px = max(2, min(16, int(round(4.0 * scale))))

        # Load input parsing and pose artifacts
        parsing_arr, parsing_img = self._load_parsing_mask(
            parsing.mask_ref, target_dims
        )
        pose_data, has_pose = self._load_pose_artifact(pose.pose_ref)

        fallback_used = False
        fallback_reason: Optional[str] = None

        # Build initial replace mask (uint8 array, 0 or 255)
        replace_mask = np.zeros((img_h, img_w), dtype=np.uint8)

        if category == GarmentCategory.UPPER_BODY:
            target_labels = (
                int(ProjectSemanticLabel.UPPER_GARMENT),
                int(ProjectSemanticLabel.FULL_BODY_GARMENT),
            )
            initial_target = np.isin(parsing_arr, target_labels)

            if not np.any(initial_target):
                # Fallback: construct torso region from pose shoulders/hips
                if has_pose:
                    replace_mask = self._build_pose_torso_fallback(
                        pose_data.get("keypoints", []), img_w, img_h
                    )
                    fallback_used = True
                    fallback_reason = (
                        "Missing UPPER_GARMENT parsing; constructed torso fallback."
                    )
                else:
                    raise AgnosticMaskError(
                        "Cannot generate upper-body mask: target clothing region "
                        "is absent in parsing mask and pose keypoints are unavailable."
                    )

            else:
                replace_mask[initial_target] = 255

        elif category == GarmentCategory.LOWER_BODY:
            target_labels = (
                int(ProjectSemanticLabel.LOWER_GARMENT),
                int(ProjectSemanticLabel.FULL_BODY_GARMENT),
            )
            initial_target = np.isin(parsing_arr, target_labels)
            if not np.any(initial_target):
                fallback_used = True
                fallback_reason = (
                    "Missing LOWER_GARMENT in parsing; using degraded bounds."
                )
                replace_mask[parsing_arr == int(ProjectSemanticLabel.LEFT_LEG)] = 255
                replace_mask[parsing_arr == int(ProjectSemanticLabel.RIGHT_LEG)] = 255
            else:
                replace_mask[initial_target] = 255

        elif category == GarmentCategory.FULL_BODY:
            target_labels = (
                int(ProjectSemanticLabel.UPPER_GARMENT),
                int(ProjectSemanticLabel.LOWER_GARMENT),
                int(ProjectSemanticLabel.FULL_BODY_GARMENT),
            )
            initial_target = np.isin(parsing_arr, target_labels)
            if not np.any(initial_target) and has_pose:
                replace_mask = self._build_pose_torso_fallback(
                    pose_data.get("keypoints", []), img_w, img_h
                )
                fallback_used = True
                fallback_reason = (
                    "Missing full-body garment parsing; using pose torso fallback."
                )
            else:
                replace_mask[initial_target] = 255

        # Apply resolution-scaled morphological dilation using Pillow MaxFilter
        replace_pil = Image.fromarray(replace_mask, mode="L")
        dilated_pil = replace_pil.filter(ImageFilter.MaxFilter(size=kernel_size))
        dilated_arr = np.array(dilated_pil, dtype=np.uint8)

        # Include upper arms/elbows for UPPER_BODY try-on for clean sleeve replacement
        if category == GarmentCategory.UPPER_BODY:
            arms_mask = (parsing_arr == int(ProjectSemanticLabel.LEFT_ARM)) | (
                parsing_arr == int(ProjectSemanticLabel.RIGHT_ARM)
            )
            # Include arm overlap regions in replacement mask
            dilated_arr[arms_mask & (dilated_arr > 0)] = 255

        # Build identity protection mask (FACE, HAIR, HEAD_ACCESSORY, FOOTWEAR, etc.)

        protected_mask = np.zeros((img_h, img_w), dtype=bool)

        # Protect Face & Hair with face_shield dilation
        face_hair = (
            (parsing_arr == int(ProjectSemanticLabel.FACE))
            | (parsing_arr == int(ProjectSemanticLabel.HAIR))
            | (parsing_arr == int(ProjectSemanticLabel.HEAD_ACCESSORY))
        )

        if np.any(face_hair):
            fh_pil = Image.fromarray(face_hair.astype(np.uint8) * 255, mode="L")
            fh_shield = fh_pil.filter(
                ImageFilter.MaxFilter(size=2 * face_shield_px + 1)
            )
            protected_mask |= np.array(fh_shield, dtype=np.uint8) > 0

        # Protect wrists and hands using pose keypoint anchors
        if has_pose:
            wrist_shield = self._protect_wrists_and_hands(
                pose_data.get("keypoints", []), img_w, img_h, arm_width_px
            )
            protected_mask |= wrist_shield

        # Protect non-target garments
        if category == GarmentCategory.UPPER_BODY:
            protected_mask |= parsing_arr == int(ProjectSemanticLabel.LOWER_GARMENT)
            protected_mask |= parsing_arr == int(ProjectSemanticLabel.FOOTWEAR)
        elif category == GarmentCategory.LOWER_BODY:
            protected_mask |= parsing_arr == int(ProjectSemanticLabel.UPPER_GARMENT)
            protected_mask |= parsing_arr == int(ProjectSemanticLabel.FOOTWEAR)

        # Protect background (label 0)
        protected_mask |= parsing_arr == int(ProjectSemanticLabel.BACKGROUND)

        # Subtract protected identity regions from try-on replacement mask
        dilated_arr[protected_mask] = 0

        # Enforce binary integrity (pixels strictly 0 or 255)
        final_binary = np.where(dilated_arr > 127, np.uint8(255), np.uint8(0))

        # Calculate coverage ratio
        replace_pixels = int(np.count_nonzero(final_binary == 255))
        total_pixels = img_w * img_h
        coverage = float(replace_pixels / total_pixels)

        # Coverage bounds check heuristics
        coverage_status = "normal"
        if coverage == 0.0:
            raise AgnosticMaskError(
                "Agnostic mask generation failed: replace coverage is 0.0%."
            )
        elif coverage > 0.95:
            raise AgnosticMaskError(
                f"Replace coverage is pathological ({coverage * 100:.1f}%)."
            )

        if category == GarmentCategory.UPPER_BODY and not (0.05 <= coverage <= 0.55):
            coverage_status = "low" if coverage < 0.05 else "high"
        elif category == GarmentCategory.LOWER_BODY and not (0.10 <= coverage <= 0.60):
            coverage_status = "low" if coverage < 0.10 else "high"
        elif category == GarmentCategory.FULL_BODY and not (0.15 <= coverage <= 0.80):
            coverage_status = "low" if coverage < 0.15 else "high"

        # Save canonical single-channel 8-bit PNG mask artifact atomically
        final_filename = f"mask_{safe_id}.png"
        final_path = self.output_dir / final_filename
        temp_path = self.output_dir / f"tmp_{final_filename}"

        try:
            final_img = Image.fromarray(final_binary, mode="L")
            final_img.save(temp_path, format="PNG", compress_level=6)
            os.replace(temp_path, final_path)
        except Exception as exc:
            if temp_path.exists():
                try:
                    temp_path.unlink()
                except OSError:
                    pass
            raise AgnosticMaskError(
                f"Failed to write agnostic mask artifact: {exc}",
                details=str(exc),
            ) from exc

        meta = {
            "schema_version": "v1",
            "generator_version": "1.0.0",
            "garment_category": category.value,
            "dilation_px": dilation_px,
            "arm_width_px": arm_width_px,
            "replace_coverage": round(coverage, 4),
            "coverage_status": coverage_status,
            "fallback_used": fallback_used,
        }
        if fallback_reason:
            meta["fallback_reason"] = fallback_reason

        return final_path, coverage, meta

    def _build_pose_torso_fallback(
        self, keypoints: list[dict[str, Any]], img_w: int, img_h: int
    ) -> np.ndarray:
        """Constructs torso bounding polygon from pose keypoints as fallback."""
        kpt_map = {k["id"]: k for k in keypoints if k.get("visible", False)}

        r_shoulder = kpt_map.get(2)  # RIGHT_SHOULDER
        l_shoulder = kpt_map.get(5)  # LEFT_SHOULDER
        r_hip = kpt_map.get(8)  # RIGHT_HIP
        l_hip = kpt_map.get(11)  # LEFT_HIP

        if r_shoulder and l_shoulder and r_hip and l_hip:
            poly = [
                (r_shoulder["x_px"], r_shoulder["y_px"]),
                (l_shoulder["x_px"], l_shoulder["y_px"]),
                (l_hip["x_px"], l_hip["y_px"]),
                (r_hip["x_px"], r_hip["y_px"]),
            ]
            canvas = Image.new("L", (img_w, img_h), 0)
            draw = ImageDraw.Draw(canvas)
            draw.polygon(poly, fill=255)
            return np.array(canvas, dtype=np.uint8)

        # Simple center rectangle fallback
        mask = np.zeros((img_h, img_w), dtype=np.uint8)
        y1, y2 = int(img_h * 0.25), int(img_h * 0.65)
        x1, x2 = int(img_w * 0.25), int(img_w * 0.75)
        mask[y1:y2, x1:x2] = 255
        return mask

    def _protect_wrists_and_hands(
        self,
        keypoints: list[dict[str, Any]],
        img_w: int,
        img_h: int,
        arm_width_px: int,
    ) -> np.ndarray:
        """Constructs protective circle shields around wrists and hand keypoints."""
        shield = Image.new("L", (img_w, img_h), 0)
        draw = ImageDraw.Draw(shield)
        radius = max(10, arm_width_px // 2)

        for kpt in keypoints:
            # Right Wrist (4), Left Wrist (7)
            if kpt.get("id") in (4, 7) and kpt.get("visible", False):
                cx, cy = kpt.get("x_px"), kpt.get("y_px")
                if cx is not None and cy is not None:
                    draw.ellipse(
                        [cx - radius, cy - radius, cx + radius, cy + radius], fill=255
                    )

        return np.array(shield, dtype=np.uint8) > 0

    async def generate(
        self,
        preprocessed: PreprocessingResult,
        parsing: HumanParsingResult,
        pose: PoseEstimationResult,
        garment: GarmentInput,
    ) -> AgnosticMaskResult:
        """Asynchronously generates binary clothing-agnostic mask for VTON."""
        logger.info(
            f"AgnosticMaskGenerator: Generating mask for logical ID "
            f"'{preprocessed.person_processed_id}'"
        )

        person_path = Path(preprocessed.person_image_ref)
        if not person_path.exists() or not person_path.is_file():
            raise AgnosticMaskError(
                f"Person image reference '{preprocessed.person_image_ref}' "
                "does not exist."
            )

        if preprocessed.person_dimensions:
            target_dims = (
                preprocessed.person_dimensions.width,
                preprocessed.person_dimensions.height,
            )
        else:
            try:
                with Image.open(person_path) as img:
                    target_dims = img.size
            except Exception as exc:
                raise AgnosticMaskError(
                    f"Failed to read image dimensions from '{person_path}': {exc}"
                ) from exc

        safe_id = self._sanitize_id(preprocessed.person_processed_id)
        cat_enum = self._normalize_category(garment.category)

        # Offload synchronous Pillow/NumPy processing to worker thread
        try:
            final_path, coverage, metadata = await asyncio.to_thread(
                self._generate_sync,
                person_path,
                parsing,
                pose,
                garment,
                safe_id,
                target_dims,
            )
        except AIPipelineError:
            raise
        except Exception as exc:
            raise AgnosticMaskError(
                f"Agnostic mask generation failed: {exc}",
                details=str(exc),
            ) from exc

        relative_mask_ref = final_path.as_posix()
        mask_id = f"agnostic_mask_{safe_id}"

        logger.info(
            f"AgnosticMaskGenerator: Mask generated successfully. Saved to "
            f"'{relative_mask_ref}' with {coverage*100:.1f}% replace coverage."
        )

        return AgnosticMaskResult(
            mask_id=mask_id,
            mask_ref=relative_mask_ref,
            garment_category=cat_enum.value,
            dimensions=preprocessed.person_dimensions,
            replace_coverage=round(coverage, 4),
            metadata=metadata,
        )
