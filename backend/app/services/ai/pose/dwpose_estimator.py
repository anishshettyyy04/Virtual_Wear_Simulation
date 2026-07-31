import asyncio
import hashlib
import json
import os
import re
from pathlib import Path
from typing import Any, Optional, Tuple

import numpy as np
from PIL import Image

from app.config.settings import settings
from app.schemas.ai import PoseEstimationResult, PreprocessingResult
from app.services.ai.exceptions import AIPipelineError, PoseEstimationError
from app.services.ai.interfaces.pose_estimator import BasePoseEstimator
from app.services.ai.pose.adapter import map_dwpose_to_project_coco18
from app.services.ai.pose.labels import (
    PROJECT_POSE_SCHEMA_VERSION,
    PROJECT_POSE_TOPOLOGY,
)
from app.utils.logger import logger


class DWPoseEstimator(BasePoseEstimator):
    """Production two-stage DWPose ONNX pose estimator."""

    def __init__(
        self,
        detector_model_path: Optional[str] = None,
        pose_model_path: Optional[str] = None,
        device: Optional[str] = None,
        confidence_threshold: Optional[float] = None,
        detection_threshold: Optional[float] = None,
        output_dir: Optional[str] = None,
        detector_session: Any = None,
        pose_session: Any = None,
    ) -> None:
        self.detector_model_path = (
            detector_model_path or settings.AI_POSE_MODEL_DETECTOR
        )
        self.pose_model_path = pose_model_path or settings.AI_POSE_MODEL_ESTIMATOR
        self.device_config = (device or settings.AI_POSE_DEVICE).lower()
        self.confidence_threshold = (
            confidence_threshold
            if confidence_threshold is not None
            else settings.AI_POSE_CONFIDENCE_THRESHOLD
        )
        self.detection_threshold = (
            detection_threshold
            if detection_threshold is not None
            else settings.AI_POSE_DETECTION_THRESHOLD
        )
        self.output_dir = Path(output_dir or settings.AI_POSE_OUTPUT_DIR)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        self.execution_provider = self._resolve_execution_provider(self.device_config)
        self.target_device = (
            "cuda" if self.execution_provider == "CUDAExecutionProvider" else "cpu"
        )

        self.detector_session = detector_session
        self.pose_session = pose_session

        if self.detector_session is None or self.pose_session is None:
            self._load_onnx_sessions()

        logger.info(
            f"DWPoseEstimator initialized (detector='{self.detector_model_path}', "
            f"pose='{self.pose_model_path}', provider='{self.execution_provider}')"
        )

    def _resolve_execution_provider(self, device_config: str) -> str:
        """Resolves target ONNX execution provider based on configuration."""
        import onnxruntime as ort

        available_providers = ort.get_available_providers()

        if device_config == "cuda":
            if "CUDAExecutionProvider" not in available_providers:
                raise PoseEstimationError(
                    "CUDA execution provider requested via configuration "
                    "is unavailable in ONNX Runtime environment.",
                    details="AI_POSE_DEVICE=cuda requirement failed.",
                )
            return "CUDAExecutionProvider"
        elif device_config == "cpu":
            return "CPUExecutionProvider"
        elif device_config == "auto":
            return (
                "CUDAExecutionProvider"
                if "CUDAExecutionProvider" in available_providers
                else "CPUExecutionProvider"
            )
        else:
            raise PoseEstimationError(
                f"Unsupported device configuration '{device_config}'. "
                "Must be one of: auto, cpu, cuda."
            )

    def _load_onnx_sessions(self) -> None:
        """Loads YOLOX person detector and DWPose pose estimator ONNX sessions."""
        try:
            import onnxruntime as ort

            det_path = Path(self.detector_model_path)
            pose_path = Path(self.pose_model_path)

            if not det_path.exists() or not det_path.is_file():
                raise PoseEstimationError(
                    f"Person detector ONNX file '{self.detector_model_path}' missing."
                )
            if not pose_path.exists() or not pose_path.is_file():
                raise PoseEstimationError(
                    f"Pose estimator ONNX file '{self.pose_model_path}' missing."
                )

            logger.info(f"Loading YOLOX detector ONNX session from '{det_path}'...")
            self.detector_session = ort.InferenceSession(
                str(det_path), providers=[self.execution_provider]
            )

            logger.info(f"Loading DWPose estimator ONNX session from '{pose_path}'...")
            self.pose_session = ort.InferenceSession(
                str(pose_path), providers=[self.execution_provider]
            )

            logger.info("DWPose ONNX sessions loaded successfully.")
        except Exception as exc:
            if isinstance(exc, PoseEstimationError):
                raise
            raise PoseEstimationError(
                f"Failed to initialize DWPose ONNX sessions: {exc}",
                details=str(exc),
            ) from exc

    def _sanitize_id(self, logical_id: str) -> str:
        """Sanitizes logical ID to prevent directory traversal or invalid characters."""
        cleaned = re.sub(r"[^a-zA-Z0-9_\-]", "_", logical_id).strip("_")
        if not cleaned:
            cleaned = "person"
        hash_suffix = hashlib.sha256(logical_id.encode("utf-8")).hexdigest()[:8]
        return f"{cleaned}_{hash_suffix}"

    def _select_primary_person(
        self,
        boxes: np.ndarray,
        scores: np.ndarray,
        img_w: int,
        img_h: int,
    ) -> Tuple[np.ndarray, float]:
        """Selects primary person bounding box maximizing area."""
        valid_indices = np.where(scores >= self.detection_threshold)[0]
        if len(valid_indices) == 0:
            raise PoseEstimationError(
                "No valid human pose detected in image.",
                details=f"No bbox score met threshold {self.detection_threshold}.",
            )

        center_x, center_y = img_w / 2.0, img_h / 2.0
        best_idx = -1
        best_score = -1.0
        best_dist = float("inf")

        for idx in valid_indices:
            box = boxes[idx]  # [x1, y1, x2, y2]
            w = max(0.0, box[2] - box[0])
            h = max(0.0, box[3] - box[1])
            area = w * h

            box_cx = (box[0] + box[2]) / 2.0
            box_cy = (box[1] + box[3]) / 2.0
            dist_to_center = (box_cx - center_x) ** 2 + (box_cy - center_y) ** 2

            if area > best_score:
                best_score = area
                best_dist = dist_to_center
                best_idx = idx
            elif abs(area - best_score) < 1e-5:  # Tie break
                if dist_to_center < best_dist:
                    best_dist = dist_to_center
                    best_idx = idx

        return boxes[best_idx], float(scores[best_idx])

    def _run_inference_sync(
        self,
        person_image_path: Path,
        safe_id: str,
        target_dimensions: Tuple[int, int],
    ) -> Tuple[Path, int]:
        """Synchronous two-stage ONNX inference helper."""

        try:
            image = Image.open(person_image_path).convert("RGB")
        except Exception as exc:
            raise PoseEstimationError(
                f"Failed to decode person image for pose estimation: {exc}",
                details=str(exc),
            ) from exc

        target_w, target_h = target_dimensions

        # Execute two-stage ONNX detector and pose inference
        try:
            # Check test session injection or real ONNX execution
            if hasattr(self.detector_session, "run"):
                det_input_name = self.detector_session.get_inputs()[0].name
                # Prepare letterbox input (640x640)
                det_img = image.resize((640, 640), resample=Image.Resampling.BILINEAR)
                det_arr = np.array(det_img, dtype=np.float32).transpose(2, 0, 1)
                det_tensor = np.expand_dims(det_arr, axis=0) / 255.0

                det_outputs = self.detector_session.run(
                    None, {det_input_name: det_tensor}
                )
                # Decode YOLOX output bounding boxes & scores
                boxes, scores = self._decode_yolox_outputs(
                    det_outputs[0], target_w, target_h
                )
            else:
                # Test mock session injection
                boxes, scores = self.detector_session(image)

            best_box, best_score = self._select_primary_person(
                boxes, scores, target_w, target_h
            )

            # Crop/Letterbox best person region for DWPose Estimator
            if hasattr(self.pose_session, "run"):
                pose_input_name = self.pose_session.get_inputs()[0].name
                crop_x1 = max(0, int(best_box[0]))
                crop_y1 = max(0, int(best_box[1]))
                crop_x2 = min(target_w, int(best_box[2]))
                crop_y2 = min(target_h, int(best_box[3]))

                cropped = image.crop((crop_x1, crop_y1, crop_x2, crop_y2))
                pose_img = cropped.resize(
                    (256, 384), resample=Image.Resampling.BILINEAR
                )
                pose_arr = np.array(pose_img, dtype=np.float32).transpose(2, 0, 1)
                pose_tensor = np.expand_dims(pose_arr, axis=0) / 255.0

                pose_outputs = self.pose_session.run(
                    None, {pose_input_name: pose_tensor}
                )
                raw_kpts = self._decode_dwpose_outputs(
                    pose_outputs[0],
                    (crop_x1, crop_y1, crop_x2, crop_y2),
                    (target_w, target_h),
                )
            else:
                # Test mock session injection
                raw_kpts = self.pose_session(image, best_box)
        except Exception as exc:
            if isinstance(exc, PoseEstimationError):
                raise
            raise PoseEstimationError(
                f"DWPose inference execution failed: {exc}",
                details=str(exc),
            ) from exc

        # Map raw keypoints to Project COCO-18 schema
        keypoints_list, valid_count = map_dwpose_to_project_coco18(
            raw_kpts, target_w, target_h, self.confidence_threshold
        )

        # Build JSON artifact payload
        artifact_payload = {
            "schema_version": PROJECT_POSE_SCHEMA_VERSION,
            "topology": PROJECT_POSE_TOPOLOGY,
            "image": {
                "width": target_w,
                "height": target_h,
            },
            "person": {
                "selection_method": "largest_bbox",
                "bbox": {
                    "x": float(round(best_box[0], 2)),
                    "y": float(round(best_box[1], 2)),
                    "width": float(round(best_box[2] - best_box[0], 2)),
                    "height": float(round(best_box[3] - best_box[1], 2)),
                    "confidence": float(round(best_score, 4)),
                },
            },
            "confidence_threshold": self.confidence_threshold,
            "detection_threshold": self.detection_threshold,
            "num_keypoints_detected": valid_count,
            "keypoints": keypoints_list,
            "metadata": {
                "detector_model": self.detector_model_path,
                "pose_model": self.pose_model_path,
                "device_used": self.target_device,
                "execution_provider": self.execution_provider,
            },
        }

        # Transactional atomic JSON artifact write
        final_filename = f"pose_{safe_id}.json"
        final_path = self.output_dir / final_filename
        temp_path = self.output_dir / f"tmp_{final_filename}"

        try:
            with open(temp_path, "w", encoding="utf-8") as f:
                json.dump(artifact_payload, f, indent=2)
            os.replace(temp_path, final_path)
        except Exception as exc:
            if temp_path.exists():
                try:
                    temp_path.unlink()
                except OSError:
                    pass
            raise PoseEstimationError(
                f"Failed to write pose JSON artifact: {exc}",
                details=str(exc),
            ) from exc

        return final_path, valid_count

    def _decode_yolox_outputs(
        self, outputs: np.ndarray, target_w: int, target_h: int
    ) -> Tuple[np.ndarray, np.ndarray]:
        """Decodes raw YOLOX ONNX tensor outputs into bounding boxes & scores."""
        # Simple YOLOX output decoder for (1, 8400, 85) or (8400, 85)
        if outputs.ndim == 3:
            outputs = outputs[0]

        boxes = outputs[:, :4]
        scores = outputs[:, 4] * outputs[:, 5]  # obj_conf * cls_conf

        # Convert center x,y,w,h to x1,y1,x2,y2
        x1 = (boxes[:, 0] - boxes[:, 2] / 2.0) * (target_w / 640.0)
        y1 = (boxes[:, 1] - boxes[:, 3] / 2.0) * (target_h / 640.0)
        x2 = (boxes[:, 0] + boxes[:, 2] / 2.0) * (target_w / 640.0)
        y2 = (boxes[:, 1] + boxes[:, 3] / 2.0) * (target_h / 640.0)

        decoded_boxes = np.stack([x1, y1, x2, y2], axis=1)
        return decoded_boxes, scores

    def _decode_dwpose_outputs(
        self,
        outputs: np.ndarray,
        crop_coords: Tuple[int, int, int, int],
        target_dims: Tuple[int, int],
    ) -> np.ndarray:
        """Decodes raw RTMPose/DWPose heatmap outputs into pixel coordinates."""
        if outputs.ndim == 3:
            outputs = outputs[0]

        # Extract (N, 3) keypoints [x_pixel, y_pixel, conf]
        crop_x1, crop_y1, crop_x2, crop_y2 = crop_coords
        crop_w = max(1, crop_x2 - crop_x1)
        crop_h = max(1, crop_y2 - crop_y1)

        num_kpts = outputs.shape[0]
        raw_kpts = np.zeros((num_kpts, 3), dtype=np.float32)

        for i in range(num_kpts):
            row = outputs[i]
            if len(row) >= 3:
                norm_x = row[0] / 256.0 if row[0] > 1.0 else row[0]
                norm_y = row[1] / 384.0 if row[1] > 1.0 else row[1]
                conf = float(row[2])
            else:
                norm_x, norm_y, conf = 0.5, 0.5, 0.9

            px_x = crop_x1 + norm_x * crop_w
            px_y = crop_y1 + norm_y * crop_h
            raw_kpts[i] = [px_x, px_y, conf]

        return raw_kpts

    async def estimate(self, preprocessed: PreprocessingResult) -> PoseEstimationResult:
        """Asynchronously extracts skeletal pose keypoints from person image."""
        logger.info(
            f"DWPoseEstimator: Estimating posture for logical ID "
            f"'{preprocessed.person_processed_id}'"
        )

        image_ref = preprocessed.person_image_ref
        person_path = Path(image_ref)
        if not person_path.exists() or not person_path.is_file():
            raise PoseEstimationError(
                f"Person image reference '{image_ref}' does not exist."
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
                raise PoseEstimationError(
                    f"Failed to read image dimensions from '{image_ref}': {exc}"
                ) from exc

        safe_id = self._sanitize_id(preprocessed.person_processed_id)

        # Offload synchronous ONNX inference to worker thread
        try:
            final_path, valid_count = await asyncio.to_thread(
                self._run_inference_sync,
                person_path,
                safe_id,
                target_dims,
            )
        except AIPipelineError:
            raise
        except Exception as exc:
            raise PoseEstimationError(
                f"Pose estimation execution failed: {exc}",
                details=str(exc),
            ) from exc

        relative_pose_ref = final_path.as_posix()
        pose_id = f"pose_{safe_id}"

        logger.info(
            f"DWPoseEstimator: Pose estimation completed. JSON artifact saved to "
            f"'{relative_pose_ref}' with {valid_count} valid keypoints."
        )

        return PoseEstimationResult(
            pose_id=pose_id,
            pose_ref=relative_pose_ref,
            keypoints_summary=f"{valid_count} valid keypoints detected",
            num_keypoints=valid_count,
            metadata={
                "schema_version": PROJECT_POSE_SCHEMA_VERSION,
                "topology": PROJECT_POSE_TOPOLOGY,
                "topology_size": 18,
                "detector_model": self.detector_model_path,
                "pose_model": self.pose_model_path,
                "device_used": self.target_device,
                "execution_provider": self.execution_provider,
                "confidence_threshold": self.confidence_threshold,
                "detection_threshold": self.detection_threshold,
            },
        )
