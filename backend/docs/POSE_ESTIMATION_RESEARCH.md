# Phase 1.2.4A: Pose Estimation Research & Selection (Verified)

**Project:** Virtual Wear Simulation — Backend  
**Phase:** 1.2.4A — Pose Estimation Research & Selection  
**Status:** Completed & Verified  
**Author:** AI Engineering & Architecture Team  

---

## Executive Summary

This document presents the verified technical research, topology mapping architecture, two-stage inference pipeline design, and model selection for the **BasePoseEstimator** stage in the Virtual Wear Simulation backend.

Following deep verification against official DWPose repositories, Hugging Face / ControlNet-Aux models, and open-source VTON codebases:

*   **Selected Primary Model Pipeline:** **DWPose ONNX Two-Stage Pipeline** (YOLOX Person Detector + DWPose WholeBody Pose Estimator via ONNX Runtime).
*   **Fallback Model:** **MediaPipe Pose (BlazePose)** with custom COCO-18 mapping.
*   **Target Topology:** **Project COCO-18 v1** (OpenPose-compatible 18-landmark schema).
*   **Verification Status:** **GO for Phase 1.2.4B**

---

## 1. Verified DWPose Implementation & Two-Stage Pipeline

DWPose requires a **two-stage inference pipeline** to detect human bounding boxes before estimating skeletal joints:

```text
Preprocessed Person Image (RGB, 1024x1024)
                 ↓
Stage 1: Person Bounding Box Detector (YOLOX-l ONNX)
                 ↓
Primary Person Bounding Box (x, y, w, h)
                 ↓
Stage 2: DWPose Estimator (RTMPose-l ONNX, 256x192 / 384x288 input)
                 ↓
Raw WholeBody 133 Keypoints
                 ↓
DWPose COCO-18 Adapter (Re-indexing + Derived NECK Calculation)
                 ↓
Project COCO-18 JSON Artifact (data/processed/poses/pose_<safe-id>.json)
```

### Exact Model Repositories & ONNX Weight Sources
*   **Repository:** `IDEA-Research/DWPose` (ICCV 2023 / NeurIPS Workshops).
*   **Detector Model:** YOLOX-l (`yolox_l.onnx`, ~200 MB), trained on COCO human bounding box detection.
*   **Pose Estimator Model:** RTMPose-l DWPose distilled ONNX weights (`dw-ll_ucoco_384.onnx` or `dw-mm_ucoco_256.onnx`, ~60 MB), trained on COCO-WholeBody.
*   **Code & Weight Licensing:** **Apache 2.0** (Permissive open-source commercial license).

---

## 2. Raw DWPose Topology vs. Project COCO-18 Mapping

DWPose predicts **133 WholeBody keypoints**:
*   Indices `0..16`: 17 COCO body keypoints.
*   Indices `17..22`: 6 foot keypoints.
*   Indices `23..90`: 68 facial keypoints.
*   Indices `91..132`: 42 hand keypoints.

### Key Topology Difference
Standard COCO-17 orders keypoints differently than OpenPose COCO-18 and lacks an explicit `NECK` keypoint. The **DWPose Adapter** re-indexes raw COCO-17 keypoints and computes `NECK` to output the exact 18-point OpenPose schema expected by VTON engines.

---

## 3. Explicit Project COCO-18 Topology (`v1`)

The project pose topology is frozen with explicit integer IDs:

| ID | Landmark Name | Source in DWPose Raw Output | Notes |
| :---: | :--- | :---: | :--- |
| **0** | `NOSE` | Raw Index `0` | Direct prediction |
| **1** | `NECK` | **Derived** | Derived midpoint between Left & Right Shoulders |
| **2** | `RIGHT_SHOULDER` | Raw Index `6` | Direct prediction |
| **3** | `RIGHT_ELBOW` | Raw Index `8` | Direct prediction |
| **4** | `RIGHT_WRIST` | Raw Index `10` | Direct prediction |
| **5** | `LEFT_SHOULDER` | Raw Index `5` | Direct prediction |
| **6** | `LEFT_ELBOW` | Raw Index `7` | Direct prediction |
| **7** | `LEFT_WRIST` | Raw Index `9` | Direct prediction |
| **8** | `RIGHT_HIP` | Raw Index `12` | Direct prediction |
| **9** | `RIGHT_KNEE` | Raw Index `14` | Direct prediction |
| **10** | `RIGHT_ANKLE` | Raw Index `16` | Direct prediction |
| **11** | `LEFT_HIP` | Raw Index `11` | Direct prediction |
| **12** | `LEFT_KNEE` | Raw Index `13` | Direct prediction |
| **13** | `LEFT_ANKLE` | Raw Index `15` | Direct prediction |
| **14** | `RIGHT_EYE` | Raw Index `2` | Direct prediction |
| **15** | `LEFT_EYE` | Raw Index `1` | Direct prediction |
| **16** | `RIGHT_EAR` | Raw Index `4` | Direct prediction |
| **17** | `LEFT_EAR` | Raw Index `3` | Direct prediction |

---

## 4. Derived `NECK` Landmark Strategy

Because `NECK` is not directly predicted by DWPose / COCO-17:

1.  **Computation:** When both `LEFT_SHOULDER` (index 5) and `RIGHT_SHOULDER` (index 6) meet the confidence threshold (`confidence >= AI_POSE_CONFIDENCE_THRESHOLD`), `NECK` is computed as the shoulder midpoint:
    $$\text{NECK}_{x} = \frac{\text{L\_SHOULDER}_{x} + \text{R\_SHOULDER}_{x}}{2}$$
    $$\text{NECK}_{y} = \frac{\text{L\_SHOULDER}_{y} + \text{R\_SHOULDER}_{y}}{2}$$
2.  **Confidence:** `Neck_Confidence = min(L_Shoulder_Confidence, R_Shoulder_Confidence)`.
3.  **Missing Condition:** If either shoulder is missing or below threshold, `NECK` is marked missing (`visible = false`, `confidence = 0.0`, `x = null`, `y = null`).
4.  **Metadata:** `NECK` contains `"derived": true` in the output JSON artifact.

---

## 5. Unambiguous Missing Keypoint Representation

To prevent ambiguity between top-left image coordinates `(0, 0)` and missing landmarks:

*   **Valid Landmark:**
    `{"id": 0, "name": "NOSE", "x": 0.512, "y": 0.185, "x_px": 512, "y_px": 185, "confidence": 0.98, "visible": true, "derived": false}`
*   **Missing / Occluded Landmark:**
    `{"id": 4, "name": "RIGHT_WRIST", "x": null, "y": null, "x_px": null, "y_px": null, "confidence": 0.0, "visible": false, "derived": false}`

If specific downstream VTON models require zero-filled array representations, the conversion is performed inside the model-specific VTON adapter, keeping the canonical project JSON representation semantically clean.

---

## 6. Confidence Threshold Strategy

*   **Setting:** `AI_POSE_CONFIDENCE_THRESHOLD=0.3` (configurable in `app/config/settings.py`).
*   **Semantics:** Keypoints with `confidence >= AI_POSE_CONFIDENCE_THRESHOLD` are marked `"visible": true`.
*   **Artifact Traceability:** The threshold used for inference is recorded in JSON artifact metadata (`"confidence_threshold": 0.3`).

---

## 7. Primary Person Selection Strategy

When multiple person bounding boxes are detected by YOLOX:

1.  **Filter:** Retain bounding boxes with detection confidence $\ge 0.4$.
2.  **Scoring Formula:** Select the primary person bounding box maximizing area:
    $$\text{Score} = \text{BBox\_Width} \times \text{BBox\_Height}$$
3.  **Tie-Breaking:** If two bounding boxes have identical areas, select the one whose center $(x_c, y_c)$ is closest to the image center $(0.5, 0.5)$.

---

## 8. VTON Model Requirements Verification

We verified official codebases for each VTON architecture:

*   **IDM-VTON:** **Requires** OpenPose/DWPose COCO-18 keypoints + DensePose + Human Parsing. Uses OpenPose keypoints to draw skeletal images (`openpose_img`) and build agnostic masks.
*   **OOTDiffusion:** **Requires** OpenPose COCO-18 keypoint format for upper/full-body skeletal conditioning.
*   **CatVTON:** Pose is **Optional / Preprocessing Guidance**. CatVTON primarily uses human parsing for agnostic masks, but accepts OpenPose/DWPose keypoints for limb protection.
*   **StableVITON:** **Requires** DensePose 3D surface maps + OpenPose body keypoints.

---

## 9. DensePose vs. Skeletal Pose Architecture

*   `BasePoseEstimator` is dedicated 100% to **skeletal landmark estimation** (COCO-18 2D joints).
*   DensePose 3D surface mapping (required for StableVITON) will be implemented in a separate specialized service (`DensePoseService`) in later phases. No DensePose fields will be added to `PoseEstimationResult`.

---

## 10. Dependency & ONNX Runtime Package Strategy

*   **CPU Development:** `onnxruntime` package added to `requirements.txt`.
*   **CUDA Production:** `onnxruntime-gpu` package used in CUDA container environments.
*   **Explicit Dependency:** Add `numpy>=1.26.0` explicitly to `requirements.txt` in Phase 1.2.4B.
*   **Python 3.12 Compatibility:** Verified `onnxruntime>=1.17.0` works natively on Python 3.12.10+ (Windows & Linux).

---

## 11. GPU Contention & Concurrency Strategy

*   ONNX Runtime and PyTorch running on the same CUDA device share GPU VRAM, compute units, and PCIe bandwidth.
*   **Architecture:** `VirtualWearPipeline` uses `asyncio.to_thread` for non-blocking async execution. In Phase 1.2.4B CUDA testing, if GPU VRAM contention occurs between PyTorch SegFormer and ONNX DWPose during `asyncio.gather`, an internal `asyncio.Lock()` will be introduced to serialize GPU execution smoothly.

---

## 12. Canonical Pose JSON Schema (`v1`)

```json
{
  "schema_version": "v1",
  "topology": "COCO_18",
  "image": {
    "width": 1024,
    "height": 1024
  },
  "person": {
    "selection_method": "largest_bbox",
    "bbox": {
      "x": 0.120,
      "y": 0.050,
      "width": 0.760,
      "height": 0.900,
      "confidence": 0.96
    }
  },
  "confidence_threshold": 0.3,
  "num_keypoints_detected": 16,
  "keypoints": [
    {
      "id": 0,
      "name": "NOSE",
      "x": 0.512,
      "y": 0.185,
      "x_px": 524,
      "y_px": 190,
      "confidence": 0.98,
      "visible": true,
      "derived": false
    },
    {
      "id": 1,
      "name": "NECK",
      "x": 0.511,
      "y": 0.254,
      "x_px": 523,
      "y_px": 260,
      "confidence": 0.95,
      "visible": true,
      "derived": true
    }
  ],
  "metadata": {
    "detector_model": "yolox_l.onnx",
    "pose_model": "dw-ll_ucoco_384.onnx",
    "device_used": "cpu"
  }
}
```

---

## 13. Licensing Verification

*   **DWPose Source Code:** **Apache-2.0**
*   **YOLOX Detector Code & Weights:** **Apache-2.0**
*   **DWPose ONNX Checkpoints:** **Apache-2.0**
*   **MediaPipe Fallback:** **Apache-2.0**
*   **Commercial Usability:** Clear permissive commercial and academic usage rights.

---

## 14. Phase 1.2.4B Implementation Plan Preview

When Phase 1.2.4B begins, implementation will execute as follows:

1.  **Dependencies:** Add `onnxruntime` and `numpy` to `requirements.txt`.
2.  **Settings:** Add `AI_POSE_*` settings in `app/config/settings.py`.
3.  **Pose Labels & Mapping:** Create `app/services/ai/pose/labels.py` defining `ProjectPoseLabel`, COCO-18 topology, re-indexing adapter, and `NECK` derivation.
4.  **DWPose Implementation:** Create `app/services/ai/pose/dwpose_estimator.py` implementing `BasePoseEstimator` with YOLOX detector + DWPose ONNX sessions.
5.  **Testing:** Unit tests with fake ONNX sessions, path traversal checks, and pipeline integration tests.
6.  **Pipeline Wiring:** Inject `DWPoseEstimator` into `VirtualWearPipeline`.

---
