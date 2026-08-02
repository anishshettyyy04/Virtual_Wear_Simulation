# Virtual Wear Simulation – Backend API

Production-grade, modular **FastAPI** backend architecture for the **AI-Powered Virtual Wear Simulation** application.

---

## 🌟 Features & Architecture

- **Python 3.11+ & FastAPI**: High-performance asynchronous web framework with automatic OpenAPI documentation.
- **Aggregated Router Architecture**: Modular routing structure via `app/api/v1/router.py` for effortless scaling.
- **Pydantic v2 Settings Management**: Strict environment loading and type validation for ports, origins, upload limits, and logging.
- **Request Tracing Middleware**: Automatic UUID generation and header propagation via `X-Request-ID`.
- **FastAPI Lifespan Hooks**: Context manager managing application startup and graceful shutdown resources.
- **Standardized Response Contracts**: Explicit Pydantic response models (`HealthResponse`, `StandardErrorResponse`) with machine-readable error codes (`NOT_FOUND`, `VALIDATION_ERROR`, `INTERNAL_SERVER_ERROR`).
- **Model-Agnostic AI Pipeline Architecture (Phase 1.2.1)**: Internal service-layer abstraction for virtual try-on processing with concurrent stage execution.
- **Real Image Preprocessing Service (Phase 1.2.2)**: Production Pillow-based image normalization (`ImagePreprocessor`) featuring EXIF transpose, RGBA transparency compositing onto white, proportional `FIT_WITHIN` resizing, and transaction-like atomic commits.
- **Comprehensive Test Suite**: Pytest test cases covering health status, CORS headers, Request IDs, error handlers, AI schemas, interfaces, stage ordering, pipeline concurrency, image preprocessing unit tests, and pipeline integration tests.

---

## 🧠 AI Pipeline Architecture

```text
Person ──────┐
             ▼
      ImagePreprocessor (Real - Phase 1.2.2)
             │
Garment ─────┘
             │
      ┌──────┴──────────────┐
      ▼                     ▼
 SegFormerParser       DWPoseEstimator
 (Real - Phase 1.2.3B) (Real - Phase 1.2.4B)
      └──────┬──────────────┘
             ▼
   AgnosticMaskGenerator (Real - Phase 1.2.5B)
             │
             ▼
    Conditioning Layer (Interfaces - Dedicated Architectural Layer)
             │
             ▼
     Mock Try-On Engine
             │
             ▼
     Mock Postprocessor
             │
             ▼
        TryOnResult
```

### Stage Implementation Status
- **Preprocessing (`ImagePreprocessor`)**: **REAL** (Pillow-based validation, EXIF transpose, RGB normalization, `FIT_WITHIN` resizing, atomic output writes).
- **Human Parsing (`SegFormerHumanParser`)**: **REAL** (`mattmdjaga/segformer_b2_clothes` via PyTorch + Hugging Face Transformers, 18-class raw segmentation, `ProjectSemanticLabel` v1 mapping, 8-bit lossless PNG mask artifacts). `MockHumanParser` remains available for mock pipeline testing.
- **Pose Estimation (`DWPoseEstimator`)**: **REAL** (YOLOX-l Person Detector + RTMPose-l DWPose via ONNX Runtime, 18-point OpenPose COCO-18 schema v1 mapping, derived `NECK` calculation, JSON pose artifacts). `MockPoseEstimator` remains available for mock pipeline testing.
- **Agnostic Mask Generation (`AgnosticMaskGenerator`)**: **REAL** (Combines SegFormer human parsing + DWPose COCO-18 skeletal pose, resolution-scaled morphology, garment sleeve replacement rules, face/hair shield protection, canonical 8-bit single-channel PNG mask artifacts). `MockAgnosticMaskGenerator` remains available for mock pipeline testing.
- **Conditioning Layer (`app.services.ai.conditioning`)**: **INTERFACES** (Dedicated architectural layer defining `BaseConditioningAdapter`, `BaseImageAdapter`, `BaseMaskAdapter`, and `BaseDensePoseService` to isolate model-specific resolution, mask tensor, and surface map preparation).
- **Virtual Try-On Engine (`BaseTryOnEngine`)**: **MOCK** (`MockTryOnEngine`).
- **Postprocessing (`BasePostprocessor`)**: **MOCK** (`MockPostprocessor`).


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
│   │   │   ├── __init__.py
│   │   │   └── image_preprocessor.py
│   │   └── mock/                  # Mock stage implementations
│   └── utils/logger.py            # Centralized logger
├── tests/
│   ├── test_health.py             # Health endpoint tests
│   ├── test_errors.py             # Error handler tests
│   ├── test_middleware.py         # CORS & Request ID header tests
│   └── ai/
│       ├── test_schemas.py        # Schema validation tests
│       ├── test_interfaces.py     # Interface inheritance tests
│       ├── test_pipeline.py       # Pipeline E2E & concurrency tests
│       ├── test_image_preprocessor.py # ImagePreprocessor unit tests
│       └── test_pipeline_integration.py # Real preprocessor + pipeline integration tests
├── .env.example
├── pyproject.toml
├── README.md
└── requirements.txt
```

---

## ⚡ Setup & Development Guide

### 1. Prerequisites
- **Python**: `v3.11` or higher installed.

### 2. Create Virtual Environment & Activate

```bash
cd backend
python -m venv .venv
```

#### Activating Virtual Environment:
- **Windows (PowerShell)**: `.\.venv\Scripts\Activate.ps1`
- **Windows (CMD)**: `.venv\Scripts\activate.bat`
- **macOS / Linux**: `source .venv/bin/activate`

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Environment Configuration

```bash
# Windows
copy .env.example .env
# Linux / macOS
cp .env.example .env
```

---

## 🏃 Running Application & Test Suite

### Start Uvicorn Server

```bash
uvicorn app.main:app --reload
```

- **Health Endpoint**: `GET http://localhost:8000/api/v1/health`
- **Swagger Documentation**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **ReDoc Documentation**: [http://localhost:8000/redoc](http://localhost:8000/redoc)

### Run Pytest Suite

```bash
pytest
```

### Run Linter & Formatter

```bash
ruff check .
black --check .
```
