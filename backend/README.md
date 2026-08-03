# AI Virtual Wear Simulation — Backend System

Welcome to the backend system for **AI Virtual Wear Simulation** (`v1.0.0-phase1`). This system provides a unified FastAPI server powering personalized outfit recommendations, 3D body preference modeling, REST APIs, and AI Virtual Try-On execution using IDM-VTON.

---

## 🌟 Current Status & Release Info (`v1.0.0-phase1`)

**Phase 1 Complete (Version v1.0.0-phase1)** — Fully production-ready backend supporting:
- **Product Data Catalog** (Phase 1.1)
- **User Preference Model** (Phase 1.2)
- **Personalized Recommendation Engine & Caching** (Phase 1.3)
- **Backend REST API & Versioning** (Phase 1.4)
- **Frontend & AI Service Integration & Deployment Readiness** (Phase 1.5)
- **System Validation, QA Audit & Release Preparation** (Phase 1.6)

---

## 📌 Project & Release Engineering Assets

- 📌 **Version File**: [`VERSION`](../VERSION) (`v1.0.0-phase1`)
- 📋 **Release Notes**: [`RELEASE_NOTES.md`](../RELEASE_NOTES.md)
- 📜 **Changelog**: [`CHANGELOG.md`](../CHANGELOG.md)
- 🏷️ **Release Tag Guide**: [`docs/release/release-tag.md`](../docs/release/release-tag.md)
- ✅ **Release Checklist**: [`docs/release/release_checklist.md`](../docs/release/release_checklist.md)
- 🔒 **Software Bill of Materials (SBOM)**: [`docs/security/sbom.md`](../docs/security/sbom.md)
- ⚖️ **License**: [`LICENSE`](../LICENSE) (MIT License)
- 🤝 **Contributing Guide**: [`CONTRIBUTING.md`](../CONTRIBUTING.md)
- 📜 **Code of Conduct**: [`CODE_OF_CONDUCT.md`](../CODE_OF_CONDUCT.md)

---

## 📚 Technical Documentation & Audit Reports

- 🎨 **React Frontend Guide**: [`backend/docs/frontend-guide.md`](file:///c:/Users/Gagan/OneDrive/Desktop/Virtual_Wear_Simulation/backend/docs/frontend-guide.md)
- 🤖 **AI Try-On Guide**: [`backend/docs/ai-guide.md`](file:///c:/Users/Gagan/OneDrive/Desktop/Virtual_Wear_Simulation/backend/docs/ai-guide.md)
- 📊 **Monitoring Guide**: [`backend/docs/monitoring.md`](file:///c:/Users/Gagan/OneDrive/Desktop/Virtual_Wear_Simulation/backend/docs/monitoring.md)
- 📝 **API Contracts**: [`backend/contracts/`](file:///c:/Users/Gagan/OneDrive/Desktop/Virtual_Wear_Simulation/backend/contracts/)
- 💡 **API Response Examples**: [`backend/examples/`](file:///c:/Users/Gagan/OneDrive/Desktop/Virtual_Wear_Simulation/backend/examples/)
- 📁 **System Quality Audit Reports**: [`backend/reports/`](file:///c:/Users/Gagan/OneDrive/Desktop/Virtual_Wear_Simulation/backend/reports/)
  - [`repository_audit.md`](file:///c:/Users/Gagan/OneDrive/Desktop/Virtual_Wear_Simulation/backend/reports/repository_audit.md)
  - [`documentation_audit.md`](file:///c:/Users/Gagan/OneDrive/Desktop/Virtual_Wear_Simulation/backend/reports/documentation_audit.md)
  - [`testing_report.md`](file:///c:/Users/Gagan/OneDrive/Desktop/Virtual_Wear_Simulation/backend/reports/testing_report.md)
  - [`performance_summary.md`](file:///c:/Users/Gagan/OneDrive/Desktop/Virtual_Wear_Simulation/backend/reports/performance_summary.md)
  - [`api_validation.md`](file:///c:/Users/Gagan/OneDrive/Desktop/Virtual_Wear_Simulation/backend/reports/api_validation.md)
  - [`security_checklist.md`](file:///c:/Users/Gagan/OneDrive/Desktop/Virtual_Wear_Simulation/backend/reports/security_checklist.md)
  - [`code_quality.md`](file:///c:/Users/Gagan/OneDrive/Desktop/Virtual_Wear_Simulation/backend/reports/code_quality.md)
  - [`dependency_audit.md`](file:///c:/Users/Gagan/OneDrive/Desktop/Virtual_Wear_Simulation/backend/reports/dependency_audit.md)
  - [`release_summary.md`](file:///c:/Users/Gagan/OneDrive/Desktop/Virtual_Wear_Simulation/backend/reports/release_summary.md)
  - [`final_phase1_report.md`](file:///c:/Users/Gagan/OneDrive/Desktop/Virtual_Wear_Simulation/backend/reports/final_phase1_report.md)

---

## ⚡ Developer Quick Start (`Makefile`)

```bash
make run        # Start FastAPI dev server (http://localhost:8000)
make test       # Run unit and API integration tests
make smoke      # Run automated smoke test suite
make validate   # Validate JSON datasets against schemas
make benchmark  # Run recommendation engine benchmark
make report     # Generate performance & latency report
```

---

## 🤖 AI Subsystem Architecture (Anish)

### Stage Implementation Status
- **Preprocessing (`ImagePreprocessor`)**: **REAL** (Pillow-based validation, EXIF transpose, RGB normalization, `FIT_WITHIN` resizing, atomic output writes).
- **Human Parsing (`SegFormerHumanParser`)**: **REAL** (`mattmdjaga/segformer_b2_clothes` via PyTorch + Hugging Face Transformers, 18-class raw segmentation, `ProjectSemanticLabel` v1 mapping, 8-bit lossless PNG mask artifacts). `MockHumanParser` remains available for mock pipeline testing.
- **Pose Estimation (`DWPoseEstimator`)**: **REAL** (YOLOX-l Person Detector + RTMPose-l DWPose via ONNX Runtime, 18-point OpenPose COCO-18 schema v1 mapping, derived `NECK` calculation, JSON pose artifacts). `MockPoseEstimator` remains available for mock pipeline testing.
- **Agnostic Mask Generation (`AgnosticMaskGenerator`)**: **REAL** (Combines SegFormer human parsing + DWPose COCO-18 skeletal pose, resolution-scaled morphology, garment sleeve replacement rules, face/hair shield protection, canonical 8-bit single-channel PNG mask artifacts). `MockAgnosticMaskGenerator` remains available for mock pipeline testing.
- **Conditioning Layer (`app.services.ai.conditioning`)**: **REAL (Phase 1.2.6AA)** (Canonical `ConditioningBundle` engine-independent data contract aggregating image refs, agnostic mask, optional `DensePoseResult`, and metadata).
- **Virtual Try-On Engine (`BaseTryOnEngine`)**: **REAL / IDM-VTON**.

---

## 🖼️ Image Preprocessing Details (Phase 1.2.2)

### Processing Features
1. **Input Safety Limits**: Validates file size (`AI_INPUT_MAX_FILE_SIZE_MB`) and dimensions (`AI_INPUT_MAX_WIDTH` x `AI_INPUT_MAX_HEIGHT`).
2. **EXIF Orientation**: Applies `ImageOps.exif_transpose` to fix mobile photo orientation before reading dimensions.
3. **RGB & Alpha Normalization**: Converts all image modes (`RGBA`, `P`, `L`, `CMYK`) to `RGB`. Source alpha transparency is composited onto a solid white background `(255, 255, 255)`.
4. **Proportional Resizing (`FIT_WITHIN`)**: Scales down oversized images to `AI_PREPROCESS_MAX_WIDTH` x `AI_PREPROCESS_MAX_HEIGHT` using `LANCZOS` resampling while preserving aspect ratio. Small images below target bounds are **not** upscaled.
5. **Atomic Commit & Collision Resistance**: Generates safe output paths using sanitized IDs + short SHA-256 hashes (e.g. `proc_person_user123_a82f19c4.jpg`). Commits both person and garment artifacts atomically using transaction-like replacement.

---

## 👤 Real Human Parser Details (Phase 1.2.3B)

### Features & Architecture
1. **SegFormer Model (`mattmdjaga/segformer_b2_clothes`)**: Fine-tuned on clothing and human body datasets, generating 18 raw semantic classes.
2. **Model-Independent Semantic Labels (`ProjectSemanticLabel`)**: Centralized `v1` IntEnum mapping raw class IDs to `BACKGROUND`, `HAIR`, `FACE`, `HEAD_ACCESSORY`, `UPPER_GARMENT`, `LOWER_GARMENT`, `FULL_BODY_GARMENT`, `LEFT_ARM`, `RIGHT_ARM`, `LEFT_LEG`, `RIGHT_LEG`, `FOOTWEAR`, and `OTHER`. Unknown classes default gracefully to `OTHER`.
3. **Lossless Semantic Mask Artifacts**: Generated as 8-bit single-channel Grayscale PNG (`PNG`, mode `"L"`). Pixel values equal stable integer `ProjectSemanticLabel` values. Resizing strictly uses `NEAREST` neighbor interpolation.
4. **Configurable Execution Device (`auto` / `cpu` / `cuda`)**: Automatically selects CUDA when hardware is available; forces CPU or validates CUDA availability based on setting `AI_HUMAN_PARSER_DEVICE`.
5. **Non-Blocking Thread Offloading**: Synchronous PyTorch model inference is wrapped using `asyncio.to_thread(...)`, preserving non-blocking event loop execution during concurrent stage processing in `VirtualWearPipeline`.
6. **Collision-Resistant & Atomic Artifact Writes**: Mask filenames use sanitized IDs + SHA-256 hashes (`mask_<safe_id>.png`) written via atomic temporary replacement.

---

## 🦴 Real Pose Estimator Details (Phase 1.2.4B)

### Features & Architecture
1. **Two-Stage ONNX Pipeline**: YOLOX-l Person Bounding Box Detector + RTMPose-l DWPose Estimator via ONNX Runtime (`onnxruntime`).
2. **Project COCO-18 Topology (`v1`)**: Model-independent 18-landmark schema (`NOSE`, `NECK`, `RIGHT_SHOULDER`, `RIGHT_ELBOW`, `RIGHT_WRIST`, `LEFT_SHOULDER`, `LEFT_ELBOW`, `LEFT_WRIST`, `RIGHT_HIP`, `RIGHT_KNEE`, `RIGHT_ANKLE`, `LEFT_HIP`, `LEFT_KNEE`, `LEFT_ANKLE`, `RIGHT_EYE`, `LEFT_EYE`, `RIGHT_EAR`, `LEFT_EAR`).
3. **Derived `NECK` Calculation**: Computed as the midpoint of `LEFT_SHOULDER` and `RIGHT_SHOULDER` when both shoulders meet confidence threshold ($\ge 0.3$). Marked `"derived": true`. If either shoulder is missing or low-confidence, `NECK` is marked missing with explicit `null` coordinates.
4. **Unambiguous Missing Coordinates**: Missing landmarks use `x: null, y: null, x_px: null, y_px: null, confidence: 0.0, visible: false` instead of ambiguous `(0, 0)` coordinates.
5. **Deterministic Primary Person Selection**: Selects largest person bounding box area ($\text{Width} \times \text{Height}$) with confidence $\ge 0.4$, tie-breaking by distance to image center.
6. **Portable Pose Artifacts**: Saved as JSON documents under `data/processed/poses/pose_<safe_id>.json` and referenced via `PoseEstimationResult.pose_ref`.

---

## ⚙️ Configuration Variables

| Setting | Default | Description |
| :--- | :--- | :--- |
| `AI_INPUT_MAX_FILE_SIZE_MB` | `20.0` | Maximum allowed input image file size in megabytes |
| `AI_INPUT_MAX_WIDTH` | `8192` | Maximum allowed input image width safety bound |
| `AI_INPUT_MAX_HEIGHT` | `8192` | Maximum allowed input image height safety bound |
| `AI_PREPROCESS_MAX_WIDTH` | `1024` | Maximum preprocessed output image target width |
| `AI_PREPROCESS_MAX_HEIGHT` | `1024` | Maximum preprocessed output image target height |
| `AI_PREPROCESS_OUTPUT_FORMAT` | `"JPEG"` | Preprocessed output image format (`JPEG`, `PNG`, `WEBP`) |
| `AI_PREPROCESS_JPEG_QUALITY` | `95` | JPEG encoding quality (1–100) |
| `AI_PROCESSED_DIR` | `"data/processed"` | Output directory for preprocessed image artifacts |
| `AI_HUMAN_PARSER_MODEL` | `"mattmdjaga/segformer_b2_clothes"` | Hugging Face model repository ID or local model weights directory |
| `AI_HUMAN_PARSER_DEVICE` | `"auto"` | Target execution device (`auto`, `cpu`, `cuda`) |
| `AI_HUMAN_PARSER_OUTPUT_DIR` | `"data/processed/parsing"` | Output directory for single-channel PNG semantic mask artifacts |
| `AI_HUMAN_PARSER_PRECISION` | `"fp32"` | Model inference numerical precision (`fp32`, `fp16`) |
| `AI_POSE_MODEL_DETECTOR` | `"data/models/pose/yolox_l.onnx"` | Path to YOLOX person detector ONNX model file |
| `AI_POSE_MODEL_ESTIMATOR` | `"data/models/pose/dw-ll_ucoco_384.onnx"` | Path to DWPose pose estimator ONNX model file |
| `AI_POSE_DEVICE` | `"auto"` | Target execution device for pose estimator (`auto`, `cpu`, `cuda`) |
| `AI_POSE_CONFIDENCE_THRESHOLD` | `0.3` | Minimum confidence score to mark keypoint visible |
| `AI_POSE_DETECTION_THRESHOLD` | `0.4` | Minimum bounding box score threshold for person detector |
| `AI_POSE_OUTPUT_DIR` | `"data/processed/poses"` | Output directory for JSON pose artifacts |

---

## 🚀 Tech Stack

- **Framework**: FastAPI (v0.115+) & Starlette
- **Server**: Uvicorn (ASGI)
- **Validation**: Pydantic v2 & `pydantic-settings`
- **Image Processing**: Pillow (v10.4+)
- **Testing**: Pytest & HTTPX (`AsyncClient`)
- **Quality & Format**: Ruff & Black

---

## 📁 Directory Structure

```text
backend/
├── api/                           # REST API routes (v1) and custom middleware
├── app/
│   ├── main.py                    # FastAPI app initialization, lifespan, CORS, middleware
│   ├── api/v1/
│   │   ├── router.py              # Aggregated v1 API router
│   │   └── routes/health.py       # GET /api/v1/health route
│   ├── config/settings.py         # Pydantic BaseSettings with typed validators
│   ├── middleware/
│   │   ├── error_handler.py       # Global 404, 422, 500 exception handlers
│   │   └── request_id.py          # X-Request-ID tracing middleware
│   ├── schemas/
│   │   ├── response.py            # HealthResponse & StandardErrorResponse schemas
│   │   └── ai.py                  # Internal AI pipeline contracts
│   ├── services/ai/
│   │   ├── pipeline.py            # VirtualWearPipeline orchestrator
│   │   ├── exceptions.py          # AIPipelineError exception hierarchy
│   │   ├── interfaces/            # Abstract base classes
│   │   ├── preprocessing/         # Real image preprocessor implementation (Pillow)
│   │   └── mock/                  # Mock stage implementations
│   └── utils/logger.py            # Centralized logger
├── data/                          # Seed datasets (products.json, user_preferences.json)
├── recommendation/                # Recommendation engine modules
├── services/                      # Product, User, Recommendation, Health & Metrics services
├── tests/
│   ├── test_api.py                # API integration test suite
│   ├── test_recommendation.py     # Recommendation engine test suite
│   ├── test_smoke.py               # E2E smoke test suite
│   ├── test_health.py             # Health endpoint tests
│   ├── test_errors.py             # Error handler tests
│   └── ai/                        # AI pipeline unit test suite
├── .env.example
├── pyproject.toml
├── README.md
└── requirements.txt
```

---

## 🏃 Running Server & Testing

### Start FastAPI Uvicorn Server

```bash
uvicorn backend.api.app:app --reload
```

- **Health Endpoint**: `GET http://localhost:8000/api/v1/health`
- **Products Endpoint**: `GET http://localhost:8000/api/v1/products`
- **Users Endpoint**: `GET http://localhost:8000/api/v1/users`
- **Recommendations Endpoint**: `POST http://localhost:8000/api/v1/recommendations`
- **Swagger Documentation**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **ReDoc Documentation**: [http://localhost:8000/redoc](http://localhost:8000/redoc)

### Run Tests & Validation

```bash
# Run backend validation scripts
python backend/scripts/validate_products.py
python backend/scripts/validate_user_preferences.py

# Run recommendation & API unit test suites
python backend/tests/test_recommendation.py
python backend/tests/test_api.py
python backend/tests/test_smoke.py

# Run Pytest suite
pytest

# Run Linter & Formatter
ruff check .
black --check .
```
