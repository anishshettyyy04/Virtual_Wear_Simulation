# Phase 1.2.3A: Human Parsing Model Research & Selection (Verified)

**Project:** Virtual Wear Simulation — Backend  
**Phase:** 1.2.3A — Human Parsing Model Research & Selection  
**Status:** Completed & Verified  
**Author:** AI Engineering & Architecture Team  

---

## Executive Summary

This document presents the verified research, label-mapping architecture, individual VTON model dependency analysis, and technical selection for the **BaseHumanParser** stage in the Virtual Wear Simulation pipeline.

Following deep verification against authoritative model cards, Hugging Face repositories, and open-source VTON codebases:

*   **Selected Primary Model:** **SegFormer Human Parser (`mattmdjaga/segformer_b2_clothes`)**
*   **Fallback Model:** **Self-Correction for Human Parsing (SCHP)**
*   **Verification Status:** **GO for Phase 1.2.3B**

---

## 1. Verified Model Specification

### Exact Model ID
`mattmdjaga/segformer_b2_clothes`

### Technical Specification
*   **Base Architecture:** SegFormer (`SegformerForSemanticSegmentation` based on `nvidia/mit-b2`).
*   **Output Classes:** 18 classes (indices `0` through `17`).
*   **Dataset:** Fine-tuned on `mattmdjaga/human_parsing_dataset` (compiled from human parsing benchmarks including ATR, DeepFashion, and LIP subsets).
*   **Weight Format:** `.safetensors` & `pytorch_model.bin` available on Hugging Face Hub.
*   **Model Footprint:** ~109 MB.
*   **License:** **MIT License** (Repository & Model Weights).
*   **Transformers Compatibility:** Native support via `transformers.AutoImageProcessor` and `transformers.SegformerForSemanticSegmentation`.
*   **Expected Preprocessing:** Standard ImageNet normalization (mean `[0.485, 0.456, 0.406]`, std `[0.229, 0.224, 0.225]`), input shape `(3, H, W)` RGB image tensor.

### Verified Model `id2label` Mapping
The model config (`config.json`) publishes the exact 18-class mapping:

| Index | Raw Label | Index | Raw Label |
| :---: | :--- | :---: | :--- |
| **0** | `Background` | **9** | `Left-shoe` |
| **1** | `Hat` | **10** | `Right-shoe` |
| **2** | `Hair` | **11** | `Face` |
| **3** | `Sunglasses` | **12** | `Left-leg` |
| **4** | `Upper-clothes` | **13** | `Right-leg` |
| **5** | `Skirt` | **14** | `Left-arm` |
| **6** | `Pants` | **15** | `Right-arm` |
| **7** | `Dress` | **16** | `Bag` |
| **8** | `Belt` | **17** | `Scarf` |

---

## 2. Individual VTON Requirements Analysis

Each candidate VTON architecture has distinct preprocessing, pose, and parsing expectations:

### CatVTON
*   **Human parser required?** Yes.
*   **Parser used by official code:** SCHP / SegFormer clothes mask.
*   **Parsing label set:** 18-class / 20-class.
*   **Pose required?** Optional / Integrated.
*   **DensePose required?** Yes (uses DensePose structural masks).
*   **Agnostic mask required?** Yes.
*   **Mask generation method:** Combines clothing segmentation mask with body region boundary.
*   **Can SegFormer output feed it directly?** Yes, via Agnostic Mask Adapter.
*   **Adapter required?** Yes (maps SegFormer `Upper-clothes` / `Dress` / `Pants` to binary target mask).

### IDM-VTON
*   **Human parser required?** Yes (Mandatory).
*   **Parser used by official code:** SCHP (LIP 20-class format).
*   **Parsing label set:** LIP 20-class.
*   **Pose required?** Yes (OpenPose 18/25 keypoints).
*   **DensePose required?** Yes (DensePose IUV map).
*   **Agnostic mask required?** Yes (`mask` and `mask_gray`).
*   **Mask generation method:** Masks upper-body/dress pixels while preserving neck, face, and arms based on parsing + OpenPose.
*   **Can SegFormer output feed it directly?** Yes.
*   **Adapter required?** Yes (Label Adapter mapping SegFormer class `4` Upper-clothes, `5` Skirt, `6` Pants, `7` Dress into IDM-VTON mask generator logic).

### StableVITON
*   **Human parser required?** Yes.
*   **Parser used by official code:** SCHP (LIP dataset).
*   **Parsing label set:** LIP 20-class.
*   **Pose required?** Yes.
*   **DensePose required?** Yes (Mandatory).
*   **Agnostic mask required?** Yes.
*   **Mask generation method:** Dilates upper garment mask obtained from human parsing.
*   **Can SegFormer output feed it directly?** Yes.
*   **Adapter required?** Yes (Label Adapter).

### OOTDiffusion
*   **Human parser required?** Yes.
*   **Parser used by official code:** OpenPose + Human Parser (SCHP / SegFormer).
*   **Parsing label set:** 18/20-class.
*   **Pose required?** Yes (OpenPose keypoints).
*   **DensePose required?** No.
*   **Agnostic mask required?** Yes.
*   **Mask generation method:** Masks upper-body (`half_body`) or full garment (`full_body`) based on category input.
*   **Can SegFormer output feed it directly?** Yes.
*   **Adapter required?** Yes (Label Adapter).

---

## 3. Distinction: Semantic Parsing vs. Clothing-Agnostic Mask

```text
Semantic Parsing Mask  ≠  Clothing-Agnostic Mask
```

1.  **Semantic Parsing Mask (Output of `BaseHumanParser`):** A multi-class pixel map containing discrete integer class IDs (`0` to `17`) delineating all body parts and clothing items.
2.  **Clothing-Agnostic Mask (Output of Future `AgnosticMaskGenerator`):** A single-channel binary mask (`0` for background/preserve, `255` for repaint area) representing the target region to be erased and regenerated by VTON diffusion models.

### Future Architecture Recommendation
The clothing-agnostic mask generator should be implemented in a dedicated pipeline stage/utility (`AgnosticMaskGenerator` or inside VTON preprocessing in Phase 1.2.5). It will consume:
$$\text{Agnostic Mask} = \text{Dilation}\left(\text{SemanticParsingMask}[\text{TargetGarmentClasses}] \cup \text{TorsoMask}\right) \setminus \text{Face/Hair/Skin}$$

`BaseHumanParser` remains clean, decoupled, and focused purely on semantic segmentation.

---

## 4. Project-Level Label Mapping

Because `mattmdjaga/segformer_b2_clothes` explicitly differentiates left/right limbs (`Left-arm`, `Right-arm`, `Left-leg`, `Right-leg`, `Left-shoe`, `Right-shoe`), the project semantic mapping preserves full spatial resolution:

```python
# Raw SegFormer Class ID -> ProjectSemanticLabel Mapping

SEGFORMER_B2_CLOTHES_MAPPING = {
    0: ProjectSemanticLabel.BACKGROUND,        # Background
    1: ProjectSemanticLabel.HEAD_ACCESSORY,    # Hat
    2: ProjectSemanticLabel.HAIR,              # Hair
    3: ProjectSemanticLabel.HEAD_ACCESSORY,    # Sunglasses
    4: ProjectSemanticLabel.UPPER_GARMENT,     # Upper-clothes
    5: ProjectSemanticLabel.LOWER_GARMENT,     # Skirt
    6: ProjectSemanticLabel.LOWER_GARMENT,     # Pants
    7: ProjectSemanticLabel.FULL_BODY_GARMENT, # Dress
    8: ProjectSemanticLabel.OTHER,             # Belt
    9: ProjectSemanticLabel.FOOTWEAR,          # Left-shoe
    10: ProjectSemanticLabel.FOOTWEAR,         # Right-shoe
    11: ProjectSemanticLabel.FACE,             # Face
    12: ProjectSemanticLabel.LEFT_LEG,         # Left-leg
    13: ProjectSemanticLabel.RIGHT_LEG,        # Right-leg
    14: ProjectSemanticLabel.LEFT_ARM,         # Left-arm
    15: ProjectSemanticLabel.RIGHT_ARM,        # Right-arm
    16: ProjectSemanticLabel.OTHER,            # Bag
    17: ProjectSemanticLabel.HEAD_ACCESSORY,   # Scarf
}
```

---

## 5. Licensing Verification

*   **Model Repository License:** **MIT License** (Authoritative, published on HF repository page).
*   **Model Weights License:** **MIT License** (Authoritative).
*   **Training Dataset Considerations:** `mattmdjaga/human_parsing_dataset` (Open research dataset compiled from public benchmarks).
*   **Commercial Evaluation:** Permissive (MIT). Clear open-source commercial and academic usability.

---

## 6. Performance & Benchmark Guidelines

Hardware latency benchmarks vary significantly based on execution environment, batch size, and GPU generation.

*   **Phase 1.2.3A Stance:** Formal numerical benchmarks are omitted until Phase 1.2.3B empirical testing.
*   **Verified Expectation:** CUDA execution will provide substantially lower inference latency than CPU execution. Both devices will be supported transparently.

---

## 7. Minimal Dependency Set

To keep the backend lightweight and prevent dependency bloat, Phase 1.2.3B requires **only** the following additions:

### Required Dependencies
*   `torch`
*   `transformers`
*   `safetensors`

### Excluded Dependencies
*   `accelerate`: **Excluded** (Not required for single-image CPU/GPU SegFormer inference).
*   `torchvision`: **Excluded** (Image preprocessing is handled natively by `transformers.AutoImageProcessor` via Pillow / NumPy).

---

## 8. Compatible Pinned Dependencies for Phase 1.2.3B

To ensure compatibility with Python 3.11+, PyTorch 2.x, and existing FastAPI backend dependencies:

```text
torch>=2.0.0,<2.3.0
transformers>=4.38.0,<4.45.0
safetensors>=0.4.0
```

No existing backend core dependencies (`fastapi`, `pydantic`, `uvicorn`, `pillow`) will be upgraded.

---

## 9. Device Strategy

Device selection will be driven by application settings (`AI_HUMAN_PARSER_DEVICE`):

```text
AI_HUMAN_PARSER_DEVICE=auto
```

*   `auto`: Resolves to `"cuda"` if `torch.cuda.is_available()` is True; otherwise `"cpu"`.
*   `cpu`: Forces execution on CPU regardless of GPU availability.
*   `cuda`: Requires CUDA execution; raises an explicit `ConfigurationError` if CUDA is unavailable.

No hardcoded `cuda:0 if available else cpu` logic will be written inside parser class methods.

---

## 10. Precision Strategy

*   **Default Precision:** `fp32` (single precision).
*   **Optimization Stance:** `fp16` (half precision) is treated as an optional future optimization setting (`AI_HUMAN_PARSER_PRECISION=fp32`). Phase 1.2.3B prioritizes numerical output correctness first.

---

## 11. Async Strategy & Concurrency Isolation

*   `BaseHumanParser.parse()` presents an `async` interface contract.
*   Synchronous PyTorch model inference is CPU-bound / CUDA-blocking. Phase 1.2.3B will wrap synchronous inference calls in `asyncio.to_thread(...)` to prevent blocking the FastAPI asyncio event loop.
*   Inference execution occurs on a single model instance resident in memory. No Celery, Redis, or distributed worker infrastructure is required.

---

## 12. Model Lifecycle

```text
SegFormerHumanParser(config)
           ↓
Instantiate & Load Weights Once (In __init__)
           ↓
Reuse Model Instance Across parse() Calls
```

*   Weights remain resident in memory.
*   Model loading will **not** be triggered on every `parse()` invocation.
*   Coupling model lifespan to FastAPI app lifespan hooks will happen during HTTP API wiring in later phases.

---

## 13. Model Download & Local Storage Strategy

```env
AI_HUMAN_PARSER_MODEL=mattmdjaga/segformer_b2_clothes
```

*   **Development:** Downloads model from Hugging Face Hub on first run using standard `transformers` cache behavior.
*   **Production / Offline:** Setting `AI_HUMAN_PARSER_MODEL=data/models/human_parser/segformer_b2_clothes` loads pre-downloaded local weights offline.
*   Model weights directory is ignored by Git (`.gitignore`).

---

## 14. Mask Resource References & Storage

*   **Artifact Format:** Single-channel 8-bit Grayscale PNG (`PNG`, mode `"L"`).
*   **Pixel Values:** Raw integer class IDs (`0` through `17`).
*   **Resizing Interpolation:** **Nearest-Neighbor (`NEAREST`)** strictly required. JPEG, Bilinear, Bicubic, and Lanczos are strictly prohibited for class-ID maps.
*   **Resource Reference:** `data/processed/parsing/mask_<person_id>_<hash>.png` (consistent with Phase 1.2.2 relative output paths). Custom `storage://` URI schemes are deferred until a dedicated storage resolver is built.

---
