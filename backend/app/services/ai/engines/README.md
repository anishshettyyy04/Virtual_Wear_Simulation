# VTON Engines & Infrastructure Architecture

**Package:** `app.services.ai.engines`  
**Phase:** Phase 1.2.6C — VTON Engine Infrastructure  
**Status:** Completed (Reusable Infrastructure Active)  

---

## 🎯 Architecture Diagram

```text
VirtualWearPipeline
        │
        ▼
ConditioningBundle
        │
        ▼
IDMVTONEngine
        │
        ├── DeviceManager
        ├── ModelWeightManager
        ├── ModelRegistry
        ├── EngineHealthReport
        └── VTONEngineConfig
```

---

## 🧩 Component Responsibilities

1. **`DeviceManager`:** Decouples accelerator selection and validation (`auto`, `cuda`, `cpu`, `mps`).
2. **`ModelWeightManager`:** Discovers, locates, verifies required model files, and checks SHA-256 hashes without performing automated downloads.
3. **`ModelRegistry`:** Centralized metadata registry tracking supported try-on engine implementations (`idm_vton`, `catvton`, `stableviton`).
4. **`EngineHealthReport`:** Diagnostic Pydantic model evaluating file presence, device accessibility, and configuration validity before engine initialization.
5. **`VTONEngineConfig`:** Strongly-typed Pydantic configuration container passed to engine constructors.
6. **Domain Exception Hierarchy:** Structured exceptions (`EngineInitializationError`, `WeightMissingError`, `InferenceError`, `DeviceUnavailableError`, `ConfigurationError`) extending `AIPipelineError`.
