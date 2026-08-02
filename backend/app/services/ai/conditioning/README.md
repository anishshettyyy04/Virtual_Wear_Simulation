# Phase 1.2.6AA — ConditioningBundle Architecture

**Package:** `app.services.ai.conditioning`  
**Phase:** Phase 1.2.6AA — Engine-Independent ConditioningBundle Architecture  
**Status:** Canonical Interface & Data Contract Defined  

---

## 🎯 Canonical Conditioning Philosophy

The **Conditioning Layer** acts as the explicit architectural boundary between canonical, engine-independent project artifacts (`PreprocessingResult`, `HumanParsingResult`, `PoseEstimationResult`, `AgnosticMaskResult`) and neural try-on engines (`IDMVTONEngine`, `CatVTONEngine`, `StableVITONEngine`, `OOTDiffusionEngine`, `FutureCommercialEngine`).

Instead of allowing each neural try-on engine to request arbitrary internal project artifacts directly, the Conditioning Layer aggregates canonical resources into a single engine-independent object:

```text
ConditioningBundle
```

Every neural try-on engine consumes this bundle as its primary input.

---

## 🧠 AI Pipeline Architecture

```text
Person + Garment
        ↓
ImagePreprocessor (Stage 1)
        │
        ├──────────────────────┐
        ▼                      ▼
 SegFormerParser        DWPoseEstimator (Stage 2)
        └──────────┬───────────┘
                   ▼
       AgnosticMaskGenerator (Stage 3)
                   │
                   ▼
           Conditioning Layer
                   │
                   ▼
           ConditioningBundle
                   │
                   ▼
              TryOnEngine (Stage 4)
                   │
                   ▼
             Postprocessor (Stage 5)
```

---

## 📐 Data Contracts & Engine Boundary

* **Canonical Project Artifacts:** Internal pipeline artifacts produced by Stages 1–3 (`PreprocessingResult`, `HumanParsingResult`, `PoseEstimationResult`, `AgnosticMaskResult`).
* **ConditioningBundle:** Aggregates person/garment image references, canonical agnostic mask, optional `DensePoseResult`, and standardized lightweight metadata (`schema_version`, `conditioning_version`, `garment_category`, `dimensions`, `generator_versions`).
* **Engine Boundary:** Try-on engines begin at the `ConditioningBundle` boundary. Engines never import or directly depend on internal parsing/pose models or Diffusers/PyTorch objects.

---

## 🔌 Future Engine Compatibility

Each virtual try-on engine consumes the `ConditioningBundle` and extracts only the components it requires:

| Engine | Consumed Bundle Components | Notes |
| :--- | :--- | :--- |
| **IDM-VTON** | `person_image_ref`, `garment_image_ref`, `agnostic_mask`, `densepose` | SDXL dual-UNet with DensePose spatial surface map conditioning |
| **CatVTON** | `person_image_ref`, `garment_image_ref`, `agnostic_mask` | Lightweight concatenation-based VTON without DensePose |
| **StableVITON** | `person_image_ref`, `garment_image_ref`, `agnostic_mask`, `pose` | Pose keypoint-conditioned diffusion |
| **OOTDiffusion** | `person_image_ref`, `garment_image_ref`, `agnostic_mask` | Outfitting fusion try-on |
| **Future Commercial Engine** | `person_image_ref`, `garment_image_ref`, `metadata` | Permissively licensed SaaS engine |

The overall pipeline flow remain 100% unchanged when swapping or adding try-on engines.

---

## 📁 Repository Structure Roadmap

```text
services/
    ai/
        preprocessing/          # Image normalization (Pillow)
        parsing/                # Human parsing (SegFormer)
        pose/                   # Pose estimation (DWPose)
        masking/                # Agnostic mask generation

        conditioning/           # Dedicated Conditioning Layer
            base.py             # Base interfaces & ConditioningBundle contract
            adapters/           # Model-specific adapters
                person_adapter.py
                garment_adapter.py
                mask_adapter.py
            densepose/          # DensePose service & result schema
                service.py

        engines/                # Virtual try-on neural engines
            idm_vton/           # IDM-VTON engine implementation
            catvton/            # CatVTON engine implementation (roadmap)
            stableviton/        # StableVITON engine implementation (roadmap)
            ootdiffusion/       # OOTDiffusion engine implementation (roadmap)
```
