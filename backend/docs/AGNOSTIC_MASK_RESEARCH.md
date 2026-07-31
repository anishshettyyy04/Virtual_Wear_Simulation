# Phase 1.2.5A: Agnostic Mask Research & Architecture

**Project:** Virtual Wear Simulation — Backend  
**Phase:** 1.2.5A — Agnostic Mask Research & Architecture  
**Status:** Completed (Research & Architecture Planning Only)  
**Author:** AI Engineering & Architecture Team  

---

## Executive Summary

This document presents the research, comparative VTON analysis, mask semantics specification, identity preservation rules, pose-parsing fusion strategy, and technical architecture for the **BaseAgnosticMaskGenerator** stage in the Virtual Wear Simulation backend pipeline.

An **agnostic mask** is a single-channel binary image that isolates the garment replacement region (target clothing area to be inpainted by the VTON engine) while strictly preserving identity-sensitive regions (face, hair, skin, non-target clothing, hands, and background).

Following thorough analysis of open-source VTON models (**IDM-VTON**, **CatVTON**, **OOTDiffusion**, **StableVITON**), existing human parsing masks (`ProjectSemanticLabel` v1), and skeletal pose landmarks (`ProjectPose` COCO-18 v1):

*   **Recommended Target VTON Engine:** **IDM-VTON** (Rank #1 Target) with **CatVTON** as Rank #2 Fallback.
*   **Canonical Mask Semantics:** 8-bit single-channel Grayscale PNG (`mode="L"`). `255` = **REPLACE** (Inpainting region), `0` = **PRESERVE** (Identity & non-target area).
*   **Dependencies:** Uses existing **Pillow** + **NumPy** dependencies (zero OpenCV or heavy C++ additions required).
*   **DensePose Decision:** **NOT REQUIRED BEFORE MASK GENERATION**. Agnostic mask generation relies 100% on 2D human parsing + 2D skeletal pose keypoints.

---

## 1. Current Backend Pipeline State

The backend operates on a modular, model-agnostic AI pipeline:

```text
Phase 1.1: FastAPI Backend Foundation         [✅ Completed]
Phase 1.2.1: Model-Agnostic AI Pipeline      [✅ Completed]
Phase 1.2.2: Real ImagePreprocessor (Pillow)  [✅ Completed]
Phase 1.2.3A/B: Real Human Parser (SegFormer) [✅ Completed]
Phase 1.2.4A/B: Real Pose Estimator (DWPose)   [✅ Completed]
Phase 1.2.5A: Agnostic Mask Research          [✅ Current Phase]
```

### Next Execution Flow (Phase 1.2.5B)

```text
Person + Garment
       ↓
Real ImagePreprocessor (Phase 1.2.2)
       │
       ├────────────────────────────────┐
       ▼                                ▼
Real SegFormer Parser              Real DWPose Estimator
(Phase 1.2.3B)                     (Phase 1.2.4B)
       │                                │
       └────────────────┬───────────────┘
                        ▼
            Real AgnosticMaskGenerator
            (Phase 1.2.5B Implementation)
                        ↓
               Mock Try-On Engine
                        ↓
              Mock Postprocessor
                        ↓
                   TryOnResult
```

---

## 2. VTON Mask Requirements Analysis

We investigated the official preprocessing expectations of major open-source VTON models:

| Requirement | IDM-VTON | CatVTON | OOTDiffusion | StableVITON |
| :--- | :--- | :--- | :--- | :--- |
| **Mask Required?** | **Mandatory** | **Mandatory** | **Mandatory** | **Mandatory** |
| **Mask Semantics** | `255` = Replace, `0` = Keep | `255` = Replace, `0` = Keep | `255` = Replace, `0` = Keep | `255` = Replace, `0` = Keep |
| **Format & Mode** | Single-channel 8-bit PNG (`L`) | Single-channel 8-bit PNG (`L`) | Single-channel 8-bit PNG (`L`) | Single-channel 8-bit PNG (`L`) |
| **Parsing Dependency** | `UPPER`/`LOWER` garment | `UPPER`/`LOWER` garment | `UPPER`/`LOWER`/`DRESS` | `UPPER`/`LOWER` garment |
| **Pose Synergy** | OpenPose/DWPose arm protection | OpenPose/DWPose arm protection | OpenPose 18-point COCO | OpenPose + DensePose |
| **Morphology** | Dilation (15–20 px) | Dilation (12–16 px) | Dilation (16–20 px) | Dilation (15–25 px) |
| **DensePose in Mask?**| **No (Mask is 2D)** | **No** | **No** | **No (DensePose is separate)** |

### Key Findings
1.  **Universal Mask Semantics:** All major open-source VTON models expect an 8-bit single-channel binary mask image where **White (`255`)** indicates the region to be inpainted/replaced by target clothing, and **Black (`0`)** indicates the preserved person identity/background.
2.  **Parsing + Pose Synergy:** All models construct agnostic masks by combining human parsing segmentations with skeletal pose arm/shoulder line vectors to protect arms, wrists, and hands from accidental erasure.
3.  **DensePose Separation:** DensePose (3D surface mapping) is used by models like IDM-VTON and StableVITON during latent UNet conditioning, but is **never embedded inside the binary agnostic mask image itself**.

---

## 3. Recommended Target VTON Architecture

Based on pipeline compatibility, open-source adoption, output visual quality, and identity preservation:

### Ranked Recommendation

1.  **IDM-VTON (Rank #1 — Primary Target)**
    *   **Why:** State-of-the-art try-on fidelity (CVPR 2024), superior garment texture/pattern warping, and direct native compatibility with our SegFormer 18-class parser and DWPose COCO-18 pose estimator.
2.  **CatVTON (Rank #2 — Secondary / Lightweight Target)**
    *   **Why:** Ultra-fast concatenation-based diffusion inpainting with low VRAM footprint (~8GB), using identical binary agnostic mask conventions.
3.  **OOTDiffusion (Rank #3)**
    *   **Why:** Robust multi-category support (`upper_body`, `lower_body`, `dress`), clean ONNX/PyTorch support.
4.  **StableVITON (Rank #4)**
    *   **Why:** High quality, but introduces mandatory DensePose preprocessing dependencies alongside skeletal pose and parsing.

Phase 1.2.5B will design and optimize `AgnosticMaskGenerator` specifically for **IDM-VTON / CatVTON** mask conventions.

---

## 4. Canonical Agnostic Mask Semantics

We freeze the canonical mask format for the Virtual Wear backend:

```text
Format:          PNG
Color Mode:      Single-channel 8-bit Grayscale (PIL mode "L")
Dimensions:      Identical to preprocessed person image (e.g., 1024x1024)
Interpolation:   NEAREST (when resizing or saving)

Pixel Values:
  255 (0xFF / White) -> REPLACE (Target garment try-on inpainting region)
    0 (0x00 / Black) -> PRESERVE (Identity, skin, hair, face, non-target garments, background)
```

---

## 5. Canonical Garment Categories

We define a stable enum/string classification for target try-on garments:

```python
class GarmentCategory(str, Enum):
    UPPER_BODY = "upper_body"  # T-shirts, shirts, tops, jackets, hoodies, sweaters
    LOWER_BODY = "lower_body"  # Pants, jeans, shorts, skirts, trousers
    FULL_BODY = "full_body"    # Dresses, jumpsuits, overalls, full suits
```

User inputs (`GarmentInput.category`) will be validated against `GarmentCategory`. Category mappings (e.g. `"tops" -> UPPER_BODY`, `"pants" -> LOWER_BODY`) will be handled centrally.

---

## 6. Mask Generation Strategy by Category

### A. Upper-Body Try-On (`UPPER_BODY`)

```text
Step 1: Extract Initial Replace Region
        Replace = SegFormer(UPPER_GARMENT) ∪ SegFormer(FULL_BODY_GARMENT)

Step 2: Morphological Dilation
        Replace = Dilation(Replace, radius = 16px)  # Absorbs collar/sleeve seam errors

Step 3: Pose-Guided Arm Protection
        Protect_Arms = RasterizeLineVectors(
            [L_Shoulder -> L_Elbow -> L_Wrist],
            [R_Shoulder -> R_Elbow -> R_Wrist],
            width = 30px
        )

Step 4: Subtract Protected Regions
        Final_Mask = Replace \ (FACE ∪ HAIR ∪ HEAD_ACC ∪ LOWER_GARMENT ∪ LEGS ∪ FOOTWEAR ∪ Protect_Arms ∪ BACKGROUND)
```

### B. Lower-Body Try-On (`LOWER_BODY`)

```text
Step 1: Extract Initial Replace Region
        Replace = SegFormer(LOWER_GARMENT) ∪ SegFormer(FULL_BODY_GARMENT)

Step 2: Morphological Dilation
        Replace = Dilation(Replace, radius = 16px)

Step 3: Pose-Guided Leg & Waist Refinement
        Protect_Upper = UPPER_GARMENT ∪ Protect_Arms ∪ FACE ∪ HAIR

Step 4: Subtract Protected Regions
        Final_Mask = Replace \ (Protect_Upper ∪ FOOTWEAR ∪ BACKGROUND)
```

### C. Full-Body Try-On (`FULL_BODY`)

```text
Step 1: Extract Initial Replace Region
        Replace = SegFormer(UPPER_GARMENT) ∪ SegFormer(LOWER_GARMENT) ∪ SegFormer(FULL_BODY_GARMENT)

Step 2: Morphological Dilation
        Replace = Dilation(Replace, radius = 20px)

Step 3: Subtract Protected Regions
        Final_Mask = Replace \ (FACE ∪ HAIR ∪ HEAD_ACC ∪ FOOTWEAR ∪ Protect_Arms ∪ BACKGROUND)
```

---

## 7. Identity Preservation Rules

The mask generator enforces non-negotiable identity preservation:

1.  **Face & Head Protection:** `FACE`, `HAIR`, `HEAD_ACCESSORY` pixel regions are **always** forced to `0` (Preserve).
2.  **Limb & Skin Protection:** `LEFT_ARM`, `RIGHT_ARM`, `LEFT_LEG`, `RIGHT_LEG` pixel regions outside the target garment category are strictly preserved.
3.  **Pose Line Vector Protection:** When arms overlap the upper body, skeletal limb line vectors (shoulder $\rightarrow$ elbow $\rightarrow$ wrist) are rendered with a protective radius to prevent erasing forearm skin or hands.
4.  **Non-Target Garment Protection:** For `UPPER_BODY` try-on, `LOWER_GARMENT` pixels are strictly preserved; for `LOWER_BODY` try-on, `UPPER_GARMENT` pixels are strictly preserved.
5.  **Background Protection:** `BACKGROUND` (label 0) is forced to `0` (Preserve).

---

## 8. Morphological Processing Strategy

*   **Dilation:** Clothing boundaries in semantic parsing masks often have slight gaps or tight fits around collars, armpits, and hems. Dilating the initial clothing mask outward by $15 \text{ to } 20$ pixels ensures that old garment collars and sleeve edges are fully covered by the inpainting mask.
*   **Implementation:** Pure **Pillow** (`PIL.ImageFilter.MaxFilter(size=33)`) or **NumPy** 2D array maximum filter. No OpenCV (`cv2`) dependency required.

---

## 9. DensePose Decision

*   **Decision:** **NOT REQUIRED BEFORE MASK GENERATION**.
*   **Justification:** Agnostic mask generation is a 2D spatial segmentation process relying exclusively on 2D human parsing + 2D skeletal pose landmarks. DensePose 3D surface maps (if required for StableVITON or IDM-VTON in Phase 1.2.6) belong in a separate VTON conditioning service, keeping `BaseAgnosticMaskGenerator` clean and fast.

---

## 10. Proposed Schema & Interface Definitions

### A. New Schema Contract (`app/schemas/ai.py`)

```python
class AgnosticMaskResult(BaseModel):
    """Contract emitted by clothing-agnostic mask generation stage."""

    mask_id: str = Field(
        ..., json_schema_extra={"example": "agnostic_mask_proc_person_001_a82f19c4"}
    )
    mask_ref: str = Field(
        ...,
        json_schema_extra={
            "example": "data/processed/agnostic_masks/mask_proc_person_001_a82f19c4.png"
        },
    )
    garment_category: str = Field(
        ..., json_schema_extra={"example": "upper_body"}
    )
    dimensions: Optional[ImageDimensions] = Field(default=None)
    metadata: dict[str, Any] = Field(default_factory=dict)
```

### B. New Abstract Interface (`app/services/ai/interfaces/agnostic_mask_generator.py`)

```python
from abc import ABC, abstractmethod
from app.schemas.ai import (
    AgnosticMaskResult,
    GarmentInput,
    HumanParsingResult,
    PoseEstimationResult,
    PreprocessingResult,
)

class BaseAgnosticMaskGenerator(ABC):
    """Abstract interface defining clothing-agnostic mask generation stage."""

    @abstractmethod
    async def generate(
        self,
        preprocessed: PreprocessingResult,
        parsing: HumanParsingResult,
        pose: PoseEstimationResult,
        garment: GarmentInput,
    ) -> AgnosticMaskResult:
        """Asynchronously generates binary clothing-agnostic mask for VTON inpainting."""
        pass
```

---

## 11. Pipeline Integration Strategy

In Phase 1.2.5B, `VirtualWearPipeline` will be extended to include Stage 3 (Agnostic Mask Generation):

```python
# Stage 1: Preprocessing
preprocessed = await self.preprocessor.process(person, garment)

# Stage 2: Concurrent Human Parsing & Pose Estimation
parsing_result, pose_result = await asyncio.gather(
    self.human_parser.parse(preprocessed),
    self.pose_estimator.estimate(preprocessed),
)

# Stage 3: Agnostic Mask Generation (New Stage)
agnostic_mask = await self.agnostic_mask_generator.generate(
    preprocessed, parsing_result, pose_result, garment
)

# Stage 4: Virtual Try-On Engine
raw_render = await self.tryon_engine.generate(
    preprocessed, parsing_result, pose_result, agnostic_mask, garment
)

# Stage 5: Postprocessing
final_result = await self.postprocessor.process(raw_render)
```

*   `MockAgnosticMaskGenerator` will be created to maintain fast, deterministic testing without requiring real disk images.

---

## 12. Quality Validation & Error Handling

### Automated Validation Rules in Phase 1.2.5B Tests
1.  **Non-Empty Mask:** Replace pixel count (`pixel_value == 255`) $> 0$.
2.  **Bounded Coverage:** Replace region area $< 70\%$ of total image area.
3.  **Zero Face Overlap:** Intersection of `FACE` pixels and `Replace` mask pixels must be $0$.
4.  **Binary Integrity:** Image pixel values must contain strictly `{0, 255}`.
5.  **Dimensions Match:** Mask dimensions must equal `preprocessed.person_dimensions`.

### Controlled Error Policy
If parsing or pose artifacts are missing/corrupted, raise `AgnosticMaskError` with clear contextual details.

---

## 13. Phase 1.2.5B Implementation Plan Preview

When Phase 1.2.5B begins:

1.  **Schemas & Interfaces:** Add `AgnosticMaskResult` to `app/schemas/ai.py` and create `BaseAgnosticMaskGenerator` interface.
2.  **Package Setup:** Create `app/services/ai/agnostic_mask/` package (`__init__.py`, `generator.py`, `mock_generator.py`).
3.  **Real Implementation:** Implement `RealAgnosticMaskGenerator` with Pillow/NumPy morphological dilation, pose line vector protection, and category-specific category masks.
4.  **Mock Implementation:** Create `MockAgnosticMaskGenerator` for fast offline unit/pipeline tests.
5.  **Pipeline Update:** Update `VirtualWearPipeline` to inject and execute `BaseAgnosticMaskGenerator`.
6.  **Tests:** Add unit tests for mask logic, category handling, identity protection, path traversal, and pipeline integration.

---
