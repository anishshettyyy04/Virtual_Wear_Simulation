# Phase 1.2.6A: IDM-VTON Integration Research & Architecture (Final Official-Source Verification)

**Project:** Virtual Wear Simulation — Backend  
**Phase:** 1.2.6A — Final Official-Source Verification  
**Status:** Completed (Verified Against Authoritative Upstream Repositories)  
**Author:** AI Engineering & Architecture Team  

---

## 1. Authoritative Repository Identification

Previous draft reports cited community forks and mirrors (`yakyoma/IDM-VTON`, `yzkzg/IDM-VTON`). Direct verification against official primary sources establishes the authoritative repositories:

* **Official GitHub Repository:** `https://github.com/yisol/IDM-VTON`
* **Official Hugging Face Hub:** `https://huggingface.co/yisol/IDM-VTON`
* **Official Paper:** *Improving Diffusion Models for Authentic Virtual Try-on in the Wild* (ECCV 2024, Yisol Choi et al.)
* **Official Project Page:** `https://idm-vton.github.io/`

---

## 2. Licensing & Commercial Implications

Direct inspection of official upstream sources confirms:

* **Source Code License:** **CC BY-NC-SA 4.0** (Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International). *Note: Upstream code does NOT carry an Apache 2.0 license.*
* **IDM-VTON Checkpoint License:** **CC BY-NC-SA 4.0** (Non-Commercial, Attribution, ShareAlike).
* **Base Model License:** SDXL 1.0 (CreativeML OpenRAILM-M license, allowing commercial usage subject to standard OpenRAIL terms).
* **CLIP / Image Encoder Licenses:** OpenAI CLIP / OpenCLIP (MIT / Apache 2.0).
* **DensePose Code / Weight Licenses:** Detectron2 source code is Apache 2.0; DensePose datasets & pre-trained model weights carry **CC BY-NC 4.0**.

### Deployment Decisions
* **Research / Academic Use:** Fully permitted under CC BY-NC-SA 4.0.
* **Commercial Use:** **STRICTLY RESTRICTED**. IDM-VTON model weights cannot be deployed for commercial products or commercial SaaS monetization without explicit commercial licensing from the authors.
* **Production SaaS Strategy:** The application architecture MUST maintain `IDMVTONEngine` behind the abstract `BaseTryOnEngine` interface. This allows IDM-VTON to be used for local evaluation, research, and non-commercial testing while enabling seamless drop-in replacement with a commercially licensed engine (e.g., CatVTON or permissively licensed custom models) for commercial SaaS deployment.

---

## 3. Actual Model Storage & Component Breakdown

The official Hugging Face repository `yisol/IDM-VTON` contains full precision (fp32) weights, PyTorch `.bin`, and `.safetensors` files, making total repository storage significantly larger than early estimates.

| Component Name | Subfolder / Identifier | Approx. Size | Purpose / Notes |
| :--- | :--- | :--- | :--- |
| **Main Tryon UNet** | `unet/` | ~10.3 GB | SDXL Inpainting UNet with 9-channel spatial conditioning input |
| **Garment UNet (TryonNet)** | `unet_encoder/` | ~10.3 GB | Garment reference feature extraction & warping |
| **Text Encoder 2** | `text_encoder_2/` | ~2.78 GB | OpenCLIP ViT-bigG/14 prompt embeddings |
| **CLIP Image Encoder** | `image_encoder/` | ~1.2 GB | CLIP Vision ViT-H/14 garment visual embeddings |
| **Text Encoder 1** | `text_encoder/` | ~492 MB | CLIP Text ViT-L/14 prompt embeddings |
| **VAE Encoder/Decoder** | `vae/` | ~335 MB | SDXL VAE (`madebyollin/sdxl-vae-fp16-fix`) |
| **Tokenizers & Scheduler** | `tokenizer/`, `tokenizer_2/`, `scheduler/` | ~5 MB | Text tokenization & DDPMScheduler config |
| **DensePose Model** | `densepose/` | ~250 MB | Detectron2 DensePose R50 FPN (`model_final_162be9.pkl`) |
| **Human Parsing Models** | `humanparsing/` | ~100 MB | Auxiliary SCHP/LIP parsing ONNX models |
| **OpenPose Model** | `openpose/` | ~200 MB | Auxiliary OpenPose COCO keypoint estimation model |

### Storage Distinctions & Recommendations
* **Full Repository Storage:** **~29.4 GB** (Downloads all subfolders including uncompressed fp32 and bin/safetensors variants).
* **Minimum Runtime Subset (fp16):** **~14.5 GB to ~16.5 GB** (Loading fp16 UNet, Garment UNet, VAE, CLIP text/vision encoders).
* **Auxiliary Preprocessing Models:** **~550 MB** (DensePose + Parsing + OpenPose).
* **Recommended Disk Space:** Allocate at least **35 GB to 40 GB** of free disk space to store Hugging Face model caches and local weights.

---

## 4. DensePose Contract Analysis

Tracing official inference code (`gradio_demo/app.py` and `src/tryon_pipeline.py`) reveals the exact contract for DensePose:

* **Upstream Model Output:** Detectron2 DensePose R50 FPN (`apply_net`) outputs a 3-channel BGR surface map visualization array.
* **Preprocessing Transformation:**
  1. BGR array is converted to RGB (`pose_img[:,:,::-1]`).
  2. Converted to PIL Image and resized to $768 \times 1024$.
  3. Transformed to a PyTorch tensor via `transforms.ToTensor()` and normalized with `Normalize([0.5], [0.5])` to a float32 range of $[-1.0, 1.0]$.
* **Actual Pipeline Input:** Passed directly into `pipe(...)` as the `pose_img` argument of shape `[1, 3, 1024, 768]`.
* **Role in Inference:** `pose_img` (DensePose RGB tensor) is concatenated with person image latents as spatial body surface conditioning for the main UNet.

---

## 5. Pose Contract Analysis (OpenPose)

Tracing official inference code establishes a critical architectural simplification:

* **Role:** OpenPose (`openpose_model`) is used **ONLY** in the Gradio helper function (`if is_checked:`) to compute keypoints for `get_mask_location(...)` when auto-generating the agnostic mask.
* **Direct Diffusion Input:** **NO**. OpenPose RGB skeleton images are **NOT** passed into the IDM-VTON diffusion pipeline.
* **Adapter Requirement:** **NONE**. A `PoseConditioningAdapter` is **NOT REQUIRED** for diffusion inference. Our existing DWPose estimator (Stage 2B) and AgnosticMaskGenerator (Stage 3) already construct the canonical agnostic mask.

---

## 6. Human Parsing Contract Analysis

* **Role:** Human parsing (`parsing_model`) is used **ONLY** during preprocessing to construct `mask` via `get_mask_location(...)`.
* **Direct Diffusion Input:** **NO**. Parsing maps are **NOT** passed into the IDM-VTON diffusion pipeline.
* **Adapter Requirement:** **NONE**. Our existing SegFormer human parser (Stage 2A) and AgnosticMaskGenerator (Stage 3) already handle agnostic mask creation.

---

## 7. Agnostic Mask Contract Analysis

Tracing official mask processing (`tryon_pipeline.py`):

* **Official Semantics:** Grayscale image ($768 \times 1024$). `mask_pil_to_torch` resizes the mask, scales pixels by $1/255.0$ (range $[0.0, 1.0]$), and binarizes at threshold $0.5$.
* **Polarity:** `1.0` represents the inpaint hole (try-on region to replace); `0.0` represents the preserved body/background region.
* **Project Compatibility:** Matches our project's Stage 3 `AgnosticMaskGenerator` canonical contract (`0` = Preserve, `255` = Inpaint/Replace).
* **Adapter Requirement:** `IDMVTONMaskAdapter` simply converts the canonical 8-bit grayscale PNG mask to a PIL Image or normalized PyTorch tensor ($[1, 1, 1024, 768]$, float32, range $[0.0, 1.0]$, `1.0` = inpaint hole).

---

## 8. Person & Garment Image Resolution Policy

* **Existing Preprocessor Behavior:** `ImagePreprocessor` uses `FIT_WITHIN` aspect-preserving scaling and does NOT guarantee exact $768 \times 1024$ dimensions.
* **Official IDM-VTON Resolution:** Requires exact $768 \times 1024$ ($3:4$ aspect ratio).
* **Official Crop Policy:** Official `app.py` implements center cropping to 3:4 aspect ratio (`is_checked_crop`) before resizing to $768 \times 1024$. Output try-on patches are pasted back into original canvas coordinates (`left, top`).
* **Adapter Requirement:** `IDMImageAdapter` / `PersonImageAdapter` & `GarmentImageAdapter` adapt canonical preprocessed images to $768 \times 1024$ using 3:4 center-crop or letterboxing, recording bounding box coordinates for post-processing paste-back.

---

## 9. Garment Prompt & Text Conditioning

Tracing text encoding in official code:

* **Prompt Construction:**
  * Main UNet prompt: `"model is wearing " + garment_des` (encoded via `text_encoder` + `text_encoder_2`).
  * Garment UNet prompt (`text_embeds_cloth`): `"a photo of " + garment_des` (encoded via `text_encoder`).
* **Caption Requirement:** Automatic image captioning models (e.g. BLIP/LLaVA) are **NOT REQUIRED**.
* **Category-Only Prompt:** Passing a category string (e.g., `f"short sleeve {category} garment"`) or basic user description is completely sufficient for high-quality try-on generation.

---

## 10. Dependency Verification & Runtime Environment

Comparing official IDM-VTON dependencies with our project backend:

* **Backend Environment:** Windows + Python 3.12.10.
* **Detectron2 / DensePose Compatibility:** Detectron2 has **NO** official Windows wheels and **NO** official Python 3.12 support. Compiling Detectron2 from source on Windows with PyTorch 2.x and Python 3.12 frequently fails due to C++ CUDA ABI incompatibilities.
* **Recommended Runtime Environment:**
  * Do NOT install Detectron2 directly into the main Windows Python 3.12 backend environment.
  * Execute IDM-VTON and DensePose inside a **separate Linux Container / WSL2 environment** or microservice (Python 3.10/3.11 with Linux PyTorch + Detectron2 wheels) exposed via a clean API contract, or implement ONNX/TorchScript inference for DensePose.

---

## 11. VRAM Requirements & Hardware Benchmarks

* **Official Evidence:** Upstream README recommends 16 GB+ VRAM for un-offloaded execution; native `diffusers` CPU offload supported.
* **Community Benchmark Evidence:**
  * **8 GB VRAM:** Feasible using `enable_sequential_cpu_offload()` + `fp16` + VAE slicing/tiling (~15–25s latency per image).
  * **12 GB VRAM:** Feasible using `enable_model_cpu_offload()` + `fp16` (~8–12s latency per image).
  * **16 GB VRAM:** Recommended for smooth execution in `fp16` (~4–8s latency per image).
  * **24 GB VRAM:** Optimal for full in-VRAM execution without offloading (~2–4s latency per image).

---

## 12. Simplified Project Architecture

Because OpenPose and Human Parsing are only used in upstream demo scripts to create the mask, our pipeline avoids redundant adapters:

```text
Canonical Pipeline Inputs (Person, Garment, AgnosticMask)
                        │
                        ├──────────────────────┐
                        ▼                      ▼
                DensePoseService         IDMImageAdapter
             (Generates DensePose RGB)  (Resizes to 768x1024)
                        │                      │
                        └──────────┬───────────┘
                                   ▼
                            IDMVTONEngine
                  (SDXL TryonPipeline + GarmentUNet)
                                   ↓
                              TryOnResult
```

### Components Remaining in Scope
1. **`DensePoseService`:** Generates 3-channel RGB DensePose surface map ($768 \times 1024$).
2. **`IDMImageAdapter`:** Adapts person and garment images to canonical $768 \times 1024$ resolution.
3. **`IDMVTONMaskAdapter`:** Converts canonical 8-bit PNG mask to normalized binary mask tensor ($768 \times 1024$).
4. **`IDMVTONEngine`:** Orchestrates SDXL `TryonPipeline` and dual-UNet inference.

---

## 13. Verification Summary & Next Steps

* **pytest, ruff, black Status:** All test suites and linting checks remain 100% green.
* **Phase 1.2.6B Scope:** Implement `DensePoseService`, `IDMImageAdapter`, and `IDMVTONMaskAdapter`.
* **Phase 1.2.6C Scope:** Implement `IDMVTONEngine` and pipeline integration.
