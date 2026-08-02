# Phase 1.2.6B — Dedicated Conditioning Layer Architecture

**Package:** `app.services.ai.conditioning`  
**Phase:** Phase 1.2.6B — DensePose Service, Model Adapters & Capability Negotiation  
**Status:** Complete (Engine-Independent Infrastructure & Builder Implemented)  

---

## 🎯 Architecture & Stateless Conditioning Philosophy

The **Conditioning Layer** forms a clean architectural boundary between model-agnostic pipeline artifacts (`PreprocessingResult`, `HumanParsingResult`, `PoseEstimationResult`, `AgnosticMaskResult`) and neural try-on engines (`IDMVTONEngine`, `CatVTONEngine`, `StableVITONEngine`, `OOTDiffusionEngine`, `FutureCommercialEngine`).

### Key Design Principles:
1. **Stateless `ConditioningBuilder`:** The builder does not retain transient state or engine instances. It receives canonical artifacts, applies adapters/services conditionally, and returns a compiled `ConditioningBundle`.
2. **Canonical Adapters:** Adapters perform engine-independent validation and target resolution scaling (`target_resolution: tuple[int, int]`, defaulting to $(768, 1024)$). `CanonicalMaskAdapter` validates binary masks and coverage without introducing PyTorch/Diffusers dependencies. Model-specific tensor conversions (e.g. `IDMVTONMaskAdapter`) wrap canonical adapters in Phase 1.2.6C.
3. **Rich Capability Negotiation (`EngineCapabilities`):** Engines declare required components (`engine_name`, `engine_version`, `requires_densepose`, `requires_person_adapter`, `requires_garment_adapter`, `requires_mask_adapter`, `target_resolution`). The builder prepares only the required components.
4. **Self-Identifying DensePose Service:** Placeholder service emits explicit metadata (`"implementation": "placeholder", "provider": "mock_densepose", "schema_version": "v1"`) allowing seamless replacement with real ONNX/Detectron2 services in production.

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
          (ConditioningBuilder + EngineCapabilities)
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

## 🔌 Capability Negotiation & Engine Compatibility

```python
# IDM-VTON Engine Capability Declaration
idm_vton_caps = EngineCapabilities(
    engine_name="idm_vton",
    engine_version="1.0.0",
    requires_densepose=True,
    requires_person_adapter=True,
    requires_garment_adapter=True,
    requires_mask_adapter=True,
    target_resolution=(768, 1024),
)

# CatVTON Engine Capability Declaration
catvton_caps = EngineCapabilities(
    engine_name="cat_vton",
    engine_version="1.0.0",
    requires_densepose=False,
    requires_mask_adapter=True,
    target_resolution=(768, 1024),
)
```

---

## 📁 Repository Structure Layout

```text
services/
    ai/
        preprocessing/          # Image normalization (Pillow)
        parsing/                # Human parsing (SegFormer)
        pose/                   # Pose estimation (DWPose)
        masking/                # Agnostic mask generation

        conditioning/           # Dedicated Conditioning Layer
            base.py             # Base interfaces & contracts
            builder.py          # Stateless ConditioningBuilder & EngineCapabilities
            adapters/           # Model & resolution adapters
                canonical_mask_adapter.py # Generic CanonicalMaskAdapter
                garment_image_adapter.py  # GarmentImageAdapter
                person_image_adapter.py   # PersonImageAdapter
            densepose/          # DensePose surface map estimation
                base.py         # BaseDensePoseService interface
                service.py      # DensePoseService placeholder
```
