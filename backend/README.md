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
- **Comprehensive Test Suite**: Pytest test cases covering health status, CORS headers, Request IDs, error handlers, AI schemas, interfaces, stage ordering, and pipeline concurrency.

---

## 🧠 AI Pipeline Architecture (Phase 1.2.1)

The backend AI pipeline is designed around a model-agnostic, modular flow that decouples stage orchestration from specific neural network engines (e.g. CatVTON, IDM-VTON, StableVITON, OOTDiffusion).

### Conceptual Pipeline Flow

```text
Person Input + Garment Input
             │
             ▼
       Preprocessing
             │
             ├──────────────────────────┐
             ▼                          ▼
       Human Parsing             Pose Estimation
             │                          │
             └─────────────┬────────────┘
                           │
                           ▼
                 Virtual Try-On Engine
                           │
                           ▼
                    Postprocessing
                           │
                           ▼
                  Final Try-On Result
```

### Stage Responsibilities & Data Contracts

1. **Preprocessing (`BasePreprocessor`)**: Validates input resources and normalizes person avatar and garment properties into `PreprocessingResult` containing `person_image_ref` and `garment_image_ref`.
2. **Human Parsing (`BaseHumanParser`)**: Extracts body segmentation mask reference (`mask_ref`) and category labels into `HumanParsingResult`.
3. **Pose Estimation (`BasePoseEstimator`)**: Identifies 33 body pose landmarks and exports `pose_ref` into `PoseEstimationResult`. Executed **concurrently** with Human Parsing via `asyncio.gather`.
4. **Virtual Try-On Engine (`BaseTryOnEngine`)**: Performs neural apparel warp and fusion using preprocessed resources, parsing masks, and pose landmarks, producing `RawTryOnOutput`.
5. **Postprocessing (`BasePostprocessor`)**: Applies format encoding, image sharpening, and quality resolution scaling into `PostprocessingResult`.

---

## 🎯 Future AI Non-Functional Requirements

### 1. Identity Preservation
Future real VTON engine implementations must preserve subject identity characteristics without distortion:
- Facial structure, expression, and features
- Hair style and texture
- Skin tone and natural appearance
- Body proportions and non-garment regions (background, arms, posture)

### 2. Garment Fidelity
Future real VTON engine implementations must preserve garment characteristics:
- Color palette and fabric texture
- Patterns, prints, logos, and graphics
- Garment silhouette, neckline, and sleeve structure

---

## 🚀 Tech Stack

- **Framework**: FastAPI (v0.115+) & Starlette
- **Server**: Uvicorn (ASGI)
- **Validation**: Pydantic v2 & `pydantic-settings`
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
│   │   └── ai.py                  # Internal AI pipeline contracts (PersonInput, TryOnResult)
│   ├── services/ai/
│   │   ├── pipeline.py            # VirtualWearPipeline orchestrator
│   │   ├── exceptions.py          # AIPipelineError exception hierarchy
│   │   ├── interfaces/            # Abstract base classes (BasePreprocessor, BaseTryOnEngine)
│   │   └── mock/                  # Lightweight deterministic mock stage implementations
│   ├── models/                    # Reserved for Phase 1.2+ database models
│   └── utils/logger.py            # Centralized logger (timestamp | LOG_LEVEL | module | message)
├── tests/
│   ├── test_health.py             # Health endpoint tests
│   ├── test_errors.py             # Error handler tests
│   ├── test_middleware.py         # CORS & Request ID header tests
│   └── ai/
│       ├── test_schemas.py        # Schema validation tests
│       ├── test_interfaces.py     # Interface inheritance tests
│       └── test_pipeline.py       # Pipeline E2E, stage ordering & concurrency tests
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
