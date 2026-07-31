import asyncio
import hashlib
import os
import re
from pathlib import Path
from typing import Any, List, Optional, Tuple

import numpy as np
from PIL import Image

from app.config.settings import settings
from app.schemas.ai import HumanParsingResult, PreprocessingResult
from app.services.ai.exceptions import AIPipelineError, HumanParsingError
from app.services.ai.interfaces.human_parser import BaseHumanParser
from app.services.ai.parsing.labels import (
    PROJECT_SEMANTIC_LABEL_VERSION,
    SEGFORMER_B2_CLOTHES_MAPPING,
    ProjectSemanticLabel,
)
from app.utils.logger import logger

# Build 256-element lookup array for fast NumPy vector mapping
LOOKUP_TABLE = np.full(256, int(ProjectSemanticLabel.OTHER), dtype=np.uint8)
for raw_id, project_label in SEGFORMER_B2_CLOTHES_MAPPING.items():
    LOOKUP_TABLE[raw_id] = int(project_label)


class SegFormerHumanParser(BaseHumanParser):
    """Real human parser using SegFormer (mattmdjaga/segformer_b2_clothes)."""

    def __init__(
        self,
        model_name_or_path: Optional[str] = None,
        device: Optional[str] = None,
        output_dir: Optional[str] = None,
        image_processor: Any = None,
        model: Any = None,
    ) -> None:
        self.model_name_or_path = model_name_or_path or settings.AI_HUMAN_PARSER_MODEL
        self.device_config = (device or settings.AI_HUMAN_PARSER_DEVICE).lower()
        self.output_dir = Path(output_dir or settings.AI_HUMAN_PARSER_OUTPUT_DIR)

        self.target_device = self._resolve_device(self.device_config)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        self.image_processor = image_processor
        self.model = model

        # Lazy/Instance loading of PyTorch and Transformers model
        if self.image_processor is None or self.model is None:
            self._load_model()
        else:
            if hasattr(self.model, "to"):
                self.model.to(self.target_device)
            if hasattr(self.model, "eval"):
                self.model.eval()

        logger.info(
            f"SegFormerHumanParser initialized (model='{self.model_name_or_path}', "
            f"device='{self.target_device}', output_dir='{self.output_dir}')"
        )

    def _resolve_device(self, device_config: str) -> str:
        """Resolves target execution device based on configuration and hardware."""
        import torch

        if device_config == "cuda":
            if not torch.cuda.is_available():
                raise HumanParsingError(
                    "CUDA device requested via configuration but CUDA is not available "
                    "on this system.",
                    details="AI_HUMAN_PARSER_DEVICE=cuda requirement failed.",
                )
            return "cuda"
        elif device_config == "cpu":
            return "cpu"
        elif device_config == "auto":
            return "cuda" if torch.cuda.is_available() else "cpu"
        else:
            raise HumanParsingError(
                f"Unsupported device configuration '{device_config}'. "
                "Must be one of: auto, cpu, cuda."
            )

    def _load_model(self) -> None:
        """Loads Hugging Face SegFormer model and image processor."""
        try:
            from transformers import (
                AutoImageProcessor,
                SegformerForSemanticSegmentation,
            )

            logger.info(f"Loading SegFormer model from '{self.model_name_or_path}'...")
            self.image_processor = AutoImageProcessor.from_pretrained(
                self.model_name_or_path
            )
            self.model = SegformerForSemanticSegmentation.from_pretrained(
                self.model_name_or_path
            )
            self.model.to(self.target_device)
            self.model.eval()
            logger.info("SegFormer model loaded successfully.")
        except Exception as exc:
            if isinstance(exc, HumanParsingError):
                raise
            raise HumanParsingError(
                f"Failed to load SegFormer human parser model: {exc}",
                details=str(exc),
            ) from exc

    def _sanitize_id(self, logical_id: str) -> str:
        """Sanitizes logical ID to prevent directory traversal or unsafe filenames."""
        cleaned = re.sub(r"[^a-zA-Z0-9_\-]", "_", logical_id).strip("_")
        if not cleaned:
            cleaned = "person"
        hash_suffix = hashlib.sha256(logical_id.encode("utf-8")).hexdigest()[:8]
        return f"{cleaned}_{hash_suffix}"

    def _run_inference_sync(
        self,
        person_image_path: Path,
        safe_id: str,
        target_dimensions: Tuple[int, int],
    ) -> Tuple[Path, List[str]]:
        """Synchronous CPU/GPU PyTorch inference and semantic mask generation helper."""
        import torch

        # Load and validate input image
        try:
            image = Image.open(person_image_path).convert("RGB")
        except Exception as exc:
            raise HumanParsingError(
                f"Failed to decode person image for parsing: {exc}",
                details=str(exc),
            ) from exc

        target_w, target_h = target_dimensions

        # Execute model inference
        try:
            with torch.no_grad():
                # Test injection fallback or real HF processor/model call
                if hasattr(self.image_processor, "__call__"):
                    inputs = self.image_processor(images=image, return_tensors="pt")
                    if hasattr(inputs, "to"):
                        inputs = inputs.to(self.target_device)
                    elif isinstance(inputs, dict):
                        inputs = {
                            k: v.to(self.target_device) if hasattr(v, "to") else v
                            for k, v in inputs.items()
                        }
                    outputs = self.model(**inputs)
                else:
                    outputs = self.model(image)

                logits = getattr(outputs, "logits", outputs)
                if hasattr(logits, "argmax"):
                    raw_mask = torch.argmax(logits, dim=1).squeeze(0).cpu().numpy()
                else:
                    raw_mask = np.array(logits, dtype=np.uint8)

                if raw_mask.ndim > 2:
                    raw_mask = raw_mask.squeeze()

                raw_mask = raw_mask.astype(np.uint8)
        except Exception as exc:
            if isinstance(exc, HumanParsingError):
                raise
            raise HumanParsingError(
                f"SegFormer inference execution failed: {exc}",
                details=str(exc),
            ) from exc

        # Restore resolution using NEAREST neighbor interpolation
        try:
            resample_mode = getattr(Image, "Resampling", Image).NEAREST
            raw_mask_img = Image.fromarray(raw_mask, mode="L")
            if raw_mask_img.size != (target_w, target_h):
                resized_mask_img = raw_mask_img.resize(
                    (target_w, target_h), resample=resample_mode
                )
            else:
                resized_mask_img = raw_mask_img

            raw_arr = np.array(resized_mask_img, dtype=np.uint8)
        except Exception as exc:
            raise HumanParsingError(
                f"Resolution restoration of semantic mask failed: {exc}",
                details=str(exc),
            ) from exc

        # Map raw model class IDs to stable ProjectSemanticLabel values
        project_arr = LOOKUP_TABLE[raw_arr]

        # Extract active segment categories present in generated mask
        unique_labels = np.unique(project_arr)
        present_categories = sorted(
            [ProjectSemanticLabel(val).name for val in unique_labels]
        )

        # Atomic commit of single-channel 8-bit PNG mask artifact
        final_filename = f"mask_{safe_id}.png"
        final_path = self.output_dir / final_filename
        temp_path = self.output_dir / f"tmp_{final_filename}"

        try:
            project_mask_img = Image.fromarray(project_arr, mode="L")
            project_mask_img.save(temp_path, format="PNG")
            os.replace(temp_path, final_path)
        except Exception as exc:
            if temp_path.exists():
                try:
                    temp_path.unlink()
                except OSError:
                    pass
            raise HumanParsingError(
                f"Failed to write semantic mask artifact: {exc}",
                details=str(exc),
            ) from exc

        return final_path, present_categories

    async def parse(self, preprocessed: PreprocessingResult) -> HumanParsingResult:
        """Asynchronously extracts human body parsing segmentation mask."""
        logger.info(
            f"SegFormerHumanParser: Parsing person image for logical ID "
            f"'{preprocessed.person_processed_id}'"
        )

        # Resolve person image reference
        image_ref = preprocessed.person_image_ref
        person_path = Path(image_ref)
        if not person_path.exists() or not person_path.is_file():
            raise HumanParsingError(
                f"Preprocessed person image reference '{image_ref}' does not exist "
                "or is not a file."
            )

        # Determine target output dimensions
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
                raise HumanParsingError(
                    f"Failed to read image dimensions from '{image_ref}': {exc}"
                ) from exc

        safe_id = self._sanitize_id(preprocessed.person_processed_id)

        # Offload synchronous PyTorch inference to worker thread
        try:
            final_path, present_categories = await asyncio.to_thread(
                self._run_inference_sync,
                person_path,
                safe_id,
                target_dims,
            )
        except AIPipelineError:
            raise
        except Exception as exc:
            raise HumanParsingError(
                f"Human parsing execution failed: {exc}",
                details=str(exc),
            ) from exc

        # Format portable relative path string
        relative_mask_ref = final_path.as_posix()
        mask_id = f"mask_{safe_id}"

        logger.info(
            f"SegFormerHumanParser: Parsing completed. Mask saved to "
            f"'{relative_mask_ref}' with {len(present_categories)} categories."
        )

        return HumanParsingResult(
            mask_id=mask_id,
            mask_ref=relative_mask_ref,
            segment_categories=present_categories,
            metadata={
                "parser_model": self.model_name_or_path,
                "device_used": self.target_device,
                "mask_dimensions": {
                    "width": target_dims[0],
                    "height": target_dims[1],
                },
                "label_mapping_version": PROJECT_SEMANTIC_LABEL_VERSION,
                "raw_class_count": 18,
            },
        )
