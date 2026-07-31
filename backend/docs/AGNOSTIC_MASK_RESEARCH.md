# Phase 1.2.5A: Agnostic Mask Research & Architecture (Verified)

**Project:** Virtual Wear Simulation — Backend  
**Phase:** 1.2.5A — Agnostic Mask Research & Architecture  
**Status:** Completed & Verified  
**Author:** AI Engineering & Architecture Team  

---

## Executive Summary

This document presents the verified technical research, resolution-scaling morphology, arm/sleeve replacement strategy, identity protection rules, and model-agnostic architecture for the **BaseAgnosticMaskGenerator** stage in the Virtual Wear Simulation backend.

Following deep inspection of official **IDM-VTON** (CVPR 2024), **CatVTON**, **OOTDiffusion**, and **StableVITON** preprocessing implementations:

*   **DensePose Requirement:**
    *   Mask Generation: **NOT REQUIRED** (Agnostic mask generation relies 100% on 2D human parsing + 2D skeletal pose keypoints).
    *   IDM-VTON Inference: **REQUIRED FOR FULL PIPELINE** (IDM-VTON uses DensePose surface IUV maps in its conditioning branch alongside `openpose_img` and `agnostic_mask`, which will be integrated in Phase 1.2.6).
*   **Canonical Mask Semantics:** 8-bit single-channel Grayscale PNG (`mode="L"`). `255` = **REPLACE** (Inpainting region), `0` = **PRESERVE** (Identity & non-target area).
*   **Resolution-Scaled Morphology:** Dilation and arm-vector protection widths scale dynamically relative to image resolution ($\text{scale} = \min(W,H)/1024$) with odd integer kernel bounds.
*   **Arm / Sleeve Replacement Strategy:** Upper arms and elbows are included in the garment replacement zone for upper-body try-on to allow VTON models to render short, long, or sleeveless garments without sleeve boundary artifacts, while wrists and hands are strictly preserved.
*   **Verification Status:** **GO for Phase 1.2.5B**

---

## 1. IDM-VTON Official Preprocessing vs. Project Architecture

The official IDM-VTON repository (`yakyoma/IDM-VTON`) generates clothing-agnostic masks by combining:
1.  **Human Parsing:** Segmenting upper clothing, lower clothing, dresses, and background.
2.  **OpenPose Keypoints:** Using neck, shoulder, elbow, and wrist keypoints to define upper-body boundaries and preserve hands.
3.  **DensePose IUV Maps:** Generated as a separate conditioning image (`densepose_img`) for UNet surface alignment.

### Project Adapter Flow

```text
ProjectSemanticLabel v1 (SegFormer)
           +
ProjectPose COCO-18 v1 (DWPose)
           ↓
AgnosticMaskGenerator (Phase 1.2.5B)
           ↓
Canonical Agnostic Mask (0 = Preserve, 255 = Replace)
           ↓
IDM-VTON Adapter (Model-Specific Format Conversion in Phase 1.2.6)
```

---

## 2. DensePose Requirement Analysis

| Stage / Component | DensePose Requirement | Justification |
| :--- | :--- | :--- |
| **Agnostic Mask Generation** | **NOT REQUIRED** | Agnostic mask generation is a 2D spatial segmentation process relying exclusively on 2D human parsing + 2D skeletal pose landmarks. |
| **IDM-VTON Inference** | **REQUIRED FOR FULL PIPELINE** | IDM-VTON uses DensePose IUV maps (`densepose_img`) in its conditioning branch alongside `openpose_img` and `agnostic_mask`. |

---

## 3. Resolution-Dependent Morphology Scaling

Static pixel counts (e.g. hardcoded 16px dilation) create inconsistent mask boundaries across varying image resolutions (e.g., 512x512 vs 2048x2048).

### Dynamic Scaling Formula
Using reference dimension $S_{\text{ref}} = 1024$:

$$\text{scale} = \frac{\min(\text{width}, \text{height})}{1024.0}$$

$$\text{dilation\_px} = \text{clamp}\left(\text{round}(16 \times \text{scale}), \text{min}=4, \text{max}=48\right)$$

$$\text{arm\_width\_px} = \text{clamp}\left(\text{round}(30 \times \text{scale}), \text{min}=10, \text{max}=90\right)$$

$$\text{kernel\_size} = 2 \times \text{dilation\_px} + 1 \quad (\text{Guaranteed odd integer for PIL MaxFilter})$$

---

## 4. Nuanced Arm & Sleeve Replacement Strategy

Unconditionally preserving the entire arm for upper-body try-on causes severe visual defects (e.g., trying on a short-sleeved t-shirt leaves original long sleeves intact).

### Sleeve & Arm Region Policy

1.  **Hands & Wrists (ALWAYS PRESERVED):** Keypoint regions for `RIGHT_WRIST` (ID 4) and `LEFT_WRIST` (ID 7) plus distal hand areas are **always forced to `0` (Preserve)**.
2.  **Upper Arm & Elbow (REPLACE ZONE FOR UPPER_BODY):** Upper arms (`LEFT_ARM`, `RIGHT_ARM`) that overlap upper garment replacement regions are included in the replacement mask (`255`), allowing IDM-VTON's attention mechanism to render short, long, or sleeveless garments cleanly.
3.  **Forearm Buffer:** A pose-guided line vector from elbow to wrist is rendered with a protected skin buffer ($\text{arm\_width\_px}$) to preserve skin below the sleeve hem.

---

## 5. Face, Hair & Neck Boundary Strategy

SegFormer does not expose a separate `NECK` semantic class. To prevent mask dilation around collars from encroaching into the chin or neck:

1.  **Face & Hair Shield:** `FACE` (label 2) and `HAIR` (label 1) masks are extracted and dilated by a 4px protective safety boundary.
2.  **Neck Boundary Anchor:** Derived `NECK` keypoint (ID 1) provides the lower boundary anchor.
3.  **Subtraction:** The expanded Face/Hair shield is subtracted from the try-on replacement mask **after** morphological dilation.

---

## 6. Coverage Validation by Garment Category

Mask replace area coverage ($\% \text{ of total image area}$) is validated against category-specific bounds:

| Garment Category | Min Coverage | Max Coverage | Failure / Warning Policy |
| :--- | :---: | :---: | :--- |
| `UPPER_BODY` | $10\%$ | $45\%$ | Warning in metadata if out-of-bounds |
| `LOWER_BODY` | $15\%$ | $50\%$ | Warning in metadata if out-of-bounds |
| `FULL_BODY` | $25\%$ | $75\%$ | Warning in metadata if out-of-bounds |

---

## 7. Canonical vs. Model-Specific Mask Semantics

*   **Canonical Internal Mask:** `0` = PRESERVE, `255` = REPLACE (8-bit single-channel PNG, mode `"L"`).
*   **Model Adapters:** Downstream VTON model adapters (e.g. `IDM-VTON Adapter`) convert the canonical mask to target tensor shapes, polarities, or normalization as required during inference.

---

## 8. Canonical GarmentCategory Enum

```python
class GarmentCategory(str, Enum):
    UPPER_BODY = "upper_body"
    LOWER_BODY = "lower_body"
    FULL_BODY = "full_body"
```

Incoming user string categories (e.g., `"tops"`, `"shirts"`, `"pants"`, `"dresses"`) are normalized to `GarmentCategory` via a central mapper.

---

## 9. Degradation & Error Handling Policies

| Condition | Action | Metadata / Log Output |
| :--- | :--- | :--- |
| **Missing Target Garment Mask** | **Degrade Gracefully** (Construct bounding torso polygon from pose shoulders/hips) | `"parsing_degraded": true` |
| **Missing Arm / Wrist Keypoints** | **Degrade Gracefully** (Use parsing mask alone with default dilation) | `"pose_degraded": true` |
| **Missing / Corrupted File** | **FAIL HARD** (Raise `AgnosticMaskError`) | `AgnosticMaskError` |
| **Zero Replace Pixels** | **FAIL HARD** (Raise `AgnosticMaskError`) | `AgnosticMaskError` |

---

## 10. Phase 1.2.5B Implementation Plan Preview

When Phase 1.2.5B begins:

1.  **Schemas & Interfaces:** Add `GarmentCategory` enum and `AgnosticMaskResult` to `app/schemas/ai.py`; create `BaseAgnosticMaskGenerator` interface in `app/services/ai/interfaces/agnostic_mask_generator.py`.
2.  **Package Setup:** Create `app/services/ai/agnostic_mask/` package (`__init__.py`, `generator.py`, `mock_generator.py`).
3.  **Real Implementation:** Implement `RealAgnosticMaskGenerator` with resolution-scaled dilation, sleeve replacement rules, face/neck protection, and atomic artifact writes.
4.  **Pipeline Integration:** Update `VirtualWearPipeline` to execute Stage 3 `AgnosticMaskGenerator`.
5.  **Tests:** Add unit tests for resolution scaling, arm replacement, face protection, path traversal, and pipeline integration.

---
