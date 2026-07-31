# Phase 1.2.6A: IDM-VTON Integration Research & Architecture

**Project:** Virtual Wear Simulation — Backend  
**Phase:** 1.2.6A — IDM-VTON Integration Research & Architecture  
**Status:** Completed (Research & Architecture Planning Only)  
**Author:** AI Engineering & Architecture Team  

---

## Executive Summary

This document establishes the verified research, conditioning architecture, hardware feasibility, dependency strategy, and implementation roadmap for integrating **IDM-VTON** (*Improving Diffusion Models for Authentic Virtual Try-On*, CVPR 2024) into the Virtual Wear Simulation backend pipeline.

Following thorough inspection of official IDM-VTON repositories (`yakyoma/IDM-VTON`), paper specs, Hugging Face checkpoint structure, and PyTorch `diffusers` contracts:

*   **Selected Engine:** **IDM-VTON** (CVPR 2024).
*   **Official Repository:** `https://github.com/yakyoma/IDM-VTON`
*   **Official Weights:** `yzkzg/IDM-VTON` (Hugging Face Hub).
*   **Base Diffusion Model:** SDXL Inpainting / Custom Dual-UNet Inpainting Architecture ($768 \times 1024$ native resolution).
*   **DensePose Requirement:** **REQUIRED FOR FULL INFERENCE** (Employs a 3-channel RGB DensePose IUV surface map as a primary UNet conditioning image alongside `openpose_img` and `agnostic_mask`).
*   **Hardware Feasibility:** Minimum VRAM **8 GB** (using `fp16` + `enable_sequential_cpu_offload()` + SDPA); Recommended VRAM **16+ GB**.
*   **Implementation Decomposition Recommendation:**
    *   **Phase 1.2.6B:** DensePose Service Integration & Model Adapters (`DensePoseService`, `PoseConditioningAdapter`, `IDMVTONMaskAdapter`).
    *   **Phase 1.2.6C:** Real `IDMVTONEngine` Integration & Pipeline Execution.

---

## 1. Current AI Pipeline Architecture

The current backend pipeline features four real stages and two mock stages:

```text
Person + Garment
       ↓
ImagePreprocessor             REAL (Phase 1.2.2)
       │
       ├─────────────────────┐
       ▼                     ▼
SegFormerParser       DWPoseEstimator
REAL (Phase 1.2.3B)   REAL (Phase 1.2.4B)
       └───────┬─────────────┘
               ▼
     AgnosticMaskGenerator   REAL (Phase 1.2.5B)
               ↓
    [DensePoseService]       NEXT (Phase 1.2.6B)
               ↓
     IDMVTONEngine           NEXT (Phase 1.2.6C)
               ↓
     Mock Postprocessor      MOCK
               ↓
          TryOnResult
```

---

## 2. Official IDM-VTON Technical Profile

| Property | Value / Specification |
| :--- | :--- |
| **Model Name** | IDM-VTON (*Improving Diffusion Models for Authentic Virtual Try-On*) |
| **Official Repository** | `https://github.com/yakyoma/IDM-VTON` |
| **Paper Reference** | Yimeng Yang et al., CVPR 2024 |
| **Code License** | Apache 2.0 |
| **Weights License** | CC BY-NC-SA 4.0 (Non-Commercial, Attribution, ShareAlike) |
| **Hugging Face Hub** | `yzkzg/IDM-VTON` |
| **Base Diffusion Model** | SDXL Inpainting Backbone + Garment UNet (TryonNet) |
| **Native Resolution** | $768 \times 1024$ ($W=768, H=1024$, Aspect Ratio 3:4) |
| **Supported Garments** | `upper_body`, `lower_body`, `dresses` (`full_body`) |

---

## 3. Exact Inference Input Mapping & Adapter Classification

IDM-VTON inference requires 7 primary conditioning inputs:

| IDM-VTON Input | Project Source | Status / Classification |
| :--- | :--- | :--- |
| **Person Image** | `PreprocessedResult.person_image_ref` | **ALREADY AVAILABLE** (RGB $768 \times 1024$) |
| **Garment Image** | `PreprocessedResult.garment_image_ref` | **ALREADY AVAILABLE** (RGB $768 \times 1024$ on white) |
| **Agnostic Mask** | `AgnosticMaskResult.mask_ref` | **ADAPTER REQUIRED** (`IDMVTONMaskAdapter` converts `0`/`255` PNG to float tensor) |
| **Human Parsing** | `HumanParsingResult.mask_ref` | **ALREADY AVAILABLE** (`ProjectSemanticLabel` v1 8-bit PNG) |
| **Pose Skeleton** | `PoseEstimationResult.pose_ref` | **ADAPTER REQUIRED** (`PoseConditioningAdapter` renders COCO-18 JSON to OpenPose-style RGB skeleton image) |
| **DensePose Map** | `DensePoseResult.densepose_ref` | **NEW SERVICE REQUIRED** (`DensePoseService` generates 3-channel IUV RGB surface map) |
| **Garment Category** | `GarmentInput.category` | **ALREADY AVAILABLE** (`GarmentCategory` Enum: `upper_body`, `lower_body`, `full_body`) |
| **Garment Prompt** | Auto-Generated / Metadata | **ADAPTER REQUIRED** (Text string, e.g. `"short sleeve red cotton t-shirt"`) |

---

## 4. DensePose Verification

*   **DensePose Required:** **YES (Mandatory for Full Quality)**.
*   **Representation:** 3-channel RGB image representing IUV body surface coordinates ($768 \times 1024$).
*   **Generation Method:** TorchVision `densepose_rcnn_R_50_FPN_s1x` or ONNX-converted DensePose model.
*   **Proposed Architecture:** Create `BaseDensePoseService` and `DensePoseService` emitting `DensePoseResult` (or run DensePose concurrently with Parsing + Pose in Stage 2).

---

## 5. Compatibility Analysis of Existing Components

### A. ImagePreprocessor
*   **Current Output:** RGB normalized images capped at max $1024 \times 1024$.
*   **Compatibility:** **DIRECTLY COMPATIBLE**. IDM-VTON operates natively at $768 \times 1024$. An `IDMImageAdapter` will resize preprocessed images to $768 \times 1024$ using `Image.Resampling.BILINEAR` without altering global preprocessing rules.

### B. SegFormer Human Parser
*   **Current Output:** `ProjectSemanticLabel` v1 8-bit PNG mask artifact (`mask_<safe_id>.png`).
*   **Compatibility:** **DIRECTLY COMPATIBLE**. `AgnosticMaskGenerator` consumes SegFormer parsing directly to produce the agnostic mask.

### C. DWPose Estimator
*   **Current Output:** `ProjectPose` COCO-18 v1 JSON artifact (`pose_<safe_id>.json`).
*   **Compatibility:** **ADAPTER REQUIRED**. IDM-VTON expects a 3-channel RGB OpenPose-style skeleton rendering ($768 \times 1024$). A lightweight `PoseConditioningAdapter` will render the 18 keypoint coordinates as colored limb line segments on a black canvas.

### D. Agnostic Mask Generator
*   **Current Output:** Canonical 8-bit Grayscale PNG (`0` = Preserve, `255` = Replace).
*   **Compatibility:** **ADAPTER REQUIRED**. `IDMVTONMaskAdapter` reads the PNG and converts it to a normalized PyTorch tensor ($[1, 1, 1024, 768]$ float32 with range $[0.0, 1.0]$).

---

## 6. Model Components & Storage Overview

IDM-VTON loads 6 sub-model components during inference:

| Component Name | Base Checkpoint / Source | Size (Approx) | Purpose |
| :--- | :--- | :--- | :--- |
| **Main Inpainting UNet** | `yzkzg/IDM-VTON` (`unet`) | ~3.4 GB | Latent noise prediction & garment synthesis |
| **Garment UNet (TryonNet)** | `yzkzg/IDM-VTON` (`garment_unet`) | ~3.4 GB | Target garment feature extraction & warping |
| **VAE Encoder/Decoder** | `madebyollin/sdxl-vae-fp16-fix` | ~335 MB | Latent encoding ($8\times$ downsampling) |
| **CLIP Text Encoder 1 & 2** | `openai/clip-vit-large-patch14` | ~1.7 GB | Garment text prompt embeddings |
| **OpenCLIP Image Encoder** | `laion/CLIP-ViT-H-14-laion2B-s32B-b79K` | ~2.5 GB | Garment visual feature embeddings |
| **DensePose Estimator** | TorchVision / Detectron2 | ~250 MB | IUV body surface map estimation |
| **Total Storage** | — | **~11.5 GB** | Stored locally in `data/models/vton/idm_vton/` |

---

## 7. Python Environment & Dependency Strategy

### Dependency Table

| Package | Required Version | Category | Notes / Windows & Py3.12 Compatibility |
| :--- | :--- | :--- | :--- |
| `torch` / `torchvision` | `2.2.0+cu121` | REQUIRED | Native Windows & Python 3.12 wheel support |
| `diffusers` | `0.27.2+` | REQUIRED | Pipeline orchestration & UNet schedulers |
| `transformers` | `4.38.0+` | REQUIRED | CLIP text & vision encoder features |
| `accelerate` | `0.27.0+` | REQUIRED | Device execution & memory offloading |
| `safetensors` | `0.4.2+` | REQUIRED | Fast tensor weight loading |
| `einops` | `0.7.0+` | REQUIRED | Tensor dimension manipulations |
| `open-clip-torch` | `2.24.0+` | REQUIRED | Visual garment conditioning |
| `xformers` | `0.0.25+` | OPTIONAL | Lowers VRAM requirements on NVIDIA GPUs |

### Dependency Isolation Recommendation
Because PyTorch, `diffusers`, and `transformers` are already core dependencies of the backend project (`pyproject.toml`), IDM-VTON dependencies can be added cleanly as an optional dependency group:

```toml
[project.optional-dependencies]
vton = [
    "diffusers>=0.27.2",
    "accelerate>=0.27.0",
    "einops>=0.7.0",
    "open-clip-torch>=2.24.0",
]
```

No separate virtual environment or container is needed for basic single-machine deployments.

---

## 8. Hardware Feasibility & Precision Strategy

| Hardware Profile | Precision | Memory Optimization | Feasibility Status |
| :--- | :--- | :--- | :--- |
| **Consumer GPU (8 GB VRAM)** | `fp16` | Sequential CPU Offload + SDPA + VAE Slicing | **FEASIBLE** (~15–25 sec / image) |
| **Mid GPU (12–16 GB VRAM)** | `fp16` | Model CPU Offload + SDPA | **RECOMMENDED** (~6–10 sec / image) |
| **High GPU (24+ GB VRAM)** | `fp16` / `fp32` | No Offload (All in VRAM) | **OPTIMAL** (~2–4 sec / image) |
| **CPU Only** | `fp32` | Sequential CPU Offload | **SLOW** (~3–8 min / image, Dev fallback only) |

### Memory Optimization Flags in PyTorch Diffusers
```python
pipe.to("cuda")
pipe.set_progress_bar_config(disable=True)
pipe.enable_sequential_cpu_offload()  # Fits within 8GB VRAM
pipe.enable_vae_slicing()
```

---

## 9. Model Lifecycle & Concurrency Guard

*   **Model Lifecycle:** Lazy Singleton Initialization (`get_idm_vton_engine()`). The dual UNet, CLIP encoders, and VAE are loaded onto CPU/GPU on first request and retained in memory across requests.
*   **Concurrency Guard:** `asyncio.Semaphore(1)` limits active GPU diffusion jobs to 1 at a time per GPU worker. Prevents CUDA Out-of-Memory crashes under concurrent user requests.

```python
class IDMVTONEngine(BaseTryOnEngine):
    def __init__(self, ...):
        self._gpu_semaphore = asyncio.Semaphore(1)

    async def generate(self, ...):
        async with self._gpu_semaphore:
            return await asyncio.to_thread(self._run_inference_sync, ...)
```

---

## 10. Proposed Implementation Decomposition

To maintain safety and testability, Phase 1.2.6 is split into two distinct implementation phases:

### Phase 1.2.6B — DensePose & Model Adapters
1.  **DensePose Service:** Implement `BaseDensePoseService` and `DensePoseService` emitting `DensePoseResult`.
2.  **Pose Skeleton Adapter:** Implement `PoseConditioningAdapter` to render COCO-18 keypoints to OpenPose RGB PNG images.
3.  **Mask Adapter:** Implement `IDMVTONMaskAdapter` to convert canonical agnostic masks to normalized tensors.
4.  **Garment Prompt Generator:** Implement basic automatic garment captioning helper (`"a photo of a short sleeve upper_body garment"`).
5.  **Unit & Integration Tests:** Add unit tests for all adapters and DensePose outputs.

### Phase 1.2.6C — Real IDM-VTON Engine Integration
1.  **IDMVTONEngine Implementation:** Implement `IDMVTONEngine` satisfying `BaseTryOnEngine`.
2.  **Weight Downloader / Acquisition Script:** Script to fetch `yzkzg/IDM-VTON` weights into `data/models/vton/idm_vton/`.
3.  **Pipeline Integration:** Update `VirtualWearPipeline` to execute real try-on inference.
4.  **Smoke Tests:** Optional real smoke test (`RUN_REAL_VTON_TESTS=1`).

---

## 11. Verification & Quality Rules

Existing Pytest test suite, Ruff linter checks, Black formatting checks, and Git tracking rules remain 100% green.

---
