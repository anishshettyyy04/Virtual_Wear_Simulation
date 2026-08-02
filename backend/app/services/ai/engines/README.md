# VTON Engines & Infrastructure Architecture

**Package:** `app.services.ai.engines`  
**Phase:** Phase 1.2.6C — Real IDM-VTON Engine Implementation  
**Status:** Completed (Production IDM-VTON Engine Active)  

---

## 🎯 Architecture Diagram

```text
VirtualWearPipeline
        │
        ▼
ConditioningBundle
        │
        ▼
IDMVTONEngine (BaseTryOnEngine)
        │
        ├── IDMVTONLoader (Weight verification & diffusers component loading)
        ├── IDMVTONConditioningAdapter (ConditioningBundle mapping)
        ├── IDMVTONPipeline (Diffusion sampling loop wrapper)
        ├── DeviceManager (CUDA/CPU device resolution)
        ├── ModelWeightManager (Asset discovery & revision tracking)
        ├── ModelRegistry (Engine metadata registration)
        ├── EngineHealthReport (Readiness validation)
        ├── ArtifactStorage (Atomic render saving)
        └── VTONEngineConfig (Engine parameterization)
```

---

## 🧩 Component Responsibilities

1. **`IDMVTONEngine`:** Production virtual try-on engine implementing `BaseTryOnEngine`. Handles lazy initialization, warm-up, shutdown, `asyncio.Semaphore(1)` GPU concurrency protection, and performance metrics computation.
2. **`IDMVTONLoader`:** Verifies checkpoint existence, resolves hardware execution devices, loads diffusers pipeline components (`unet`, `unet_encoder`, `vae`, `text_encoders`), and applies precision (`fp16`/`fp32`) and CPU offloading (`enable_sequential_cpu_offload()`).
3. **`IDMVTONConditioningAdapter`:** Framework-agnostic adapter converting `ConditioningBundle` artifacts (person image, garment image, agnostic mask, DensePose) into $768 \times 1024$ normalized PIL images and tensors.
4. **`IDMVTONPipeline`:** Low-level wrapper executing diffusion sampling loop and decoding try-on latents to PIL `Image`.
5. **`DeviceManager`:** Decouples accelerator selection and validation (`auto`, `cuda`, `cpu`, `mps`).
6. **`ModelWeightManager`:** Discovers, locates, verifies required model files, and checks SHA-256 hashes without performing automated downloads.
7. **`ModelRegistry`:** Centralized metadata registry tracking supported try-on engine implementations (`idm_vton`, `catvton`, `stableviton`).
8. **`EngineHealthReport`:** Diagnostic Pydantic model evaluating file presence, device accessibility, and configuration validity before engine initialization.
9. **`VTONEngineConfig`:** Strongly-typed Pydantic configuration container passed to engine constructors.

---

## ⚙️ Hardware & VRAM Offload Profiles

* **Consumer GPU (8 GB VRAM):** `fp16` + `enable_sequential_cpu_offload()` + `enable_vae_slicing()` (~15–25s / render)
* **Mid-Tier GPU (12 GB VRAM):** `fp16` + `enable_model_cpu_offload()` + VAE slicing (~8–12s / render)
* **High-End GPU (16–24+ GB VRAM):** `fp16` / `fp32` (All models resident in VRAM, ~2–5s / render)
