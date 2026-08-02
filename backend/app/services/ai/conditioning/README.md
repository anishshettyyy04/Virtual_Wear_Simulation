# Conditioning Layer — AI Pipeline Architecture

**Package:** `app.services.ai.conditioning`  
**Phase:** Architecture Improvement — Dedicated Conditioning Layer  
**Status:** Abstract Interfaces & Structural Boundary Defined  

---

## 🎯 Purpose & Architectural Isolation

The **Conditioning Layer** forms a clean architectural boundary between canonical, model-agnostic pipeline artifacts (`PreprocessingResult`, `HumanParsingResult`, `PoseEstimationResult`, `AgnosticMaskResult`) and model-specific neural engine requirements (such as IDM-VTON, CatVTON, or future diffusion backbones).

By isolating model-specific data preparation within this layer, the upstream stages of the `VirtualWearPipeline` remain **100% model-agnostic**. The core pipeline never imports or interacts with model-specific tensor shapes, normalization rules, or model-specific auxiliary services directly.

---

## 🛠️ Layer Responsibilities

The Conditioning Layer is explicitly responsible for:

1. **Person Image Adaptation (`PersonImageAdapter`):** Transforming canonical preprocessed person images to target engine resolutions (e.g. $768 \times 1024$) via $3:4$ aspect cropping or padding.
2. **Garment Image Adaptation (`GarmentImageAdapter`):** Transforming canonical garment images to target engine resolutions and background specifications.
3. **Mask Adaptation (`IDMVTONMaskAdapter`):** Converting canonical single-channel 8-bit PNG agnostic masks into model-specific float32 tensor formats ($[1, 1, 1024, 768]$).
4. **DensePose Generation (`BaseDensePoseService`):** Generating 3-channel RGB body surface map visualizations from person images when required by spatial UNet conditioning models.
5. **Future Model-Specific Conditioning (`BaseConditioningAdapter`):** Orchestrating multi-modal conditioning packages required by future virtual try-on engines.

---

## 📐 Abstract Interfaces & Data Contracts

* `BaseConditioningAdapter`: Abstract orchestrator combining images, masks, and pose conditioning for specific VTON engines.
* `BaseImageAdapter`: Abstract base class for image resolution and aspect ratio adaptation.
* `BaseMaskAdapter`: Abstract base class for mask format and tensor conversion.
* `BaseDensePoseService`: Abstract service interface for DensePose body surface estimation.
* `DensePoseResult`: Pydantic data model encapsulating DensePose artifact metadata and paths.

---

## 📁 Repository Structure Roadmap

```text
services/
    ai/
        preprocessing/          # Real image normalization (Pillow)
        parsing/                # Real human parsing (SegFormer)
        pose/                   # Real pose estimation (DWPose)
        masking/                # Real agnostic mask generation

        conditioning/           # Dedicated Conditioning Layer
            base.py             # Abstract interfaces & data models
            adapters/           # Model-specific image & mask adapters
                person_adapter.py
                garment_adapter.py
                mask_adapter.py
            densepose/          # DensePose body surface estimation
                service.py

        engines/                # Neural try-on inference engines
            idm_vton/           # IDM-VTON engine implementation
            future_engines/     # Alternative/commercial engines
```
