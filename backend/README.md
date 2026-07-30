# Virtual Wear Simulation – Backend Foundation API

Production-grade, modular **FastAPI** backend architecture for the **AI-Powered Virtual Wear Simulation** application.

---

## 🌟 Features & Architecture

- **Python 3.11+ & FastAPI**: High-performance asynchronous web framework with automatic OpenAPI documentation.
- **Aggregated Router Architecture**: Modular routing structure via `app/api/v1/router.py` for effortless scaling (e.g., adding `images.py`, `try_on.py`, `jobs.py`).
- **Pydantic v2 Settings Management**: Strict environment loading and type validation for ports, origins, upload limits, and logging.
- **Request Tracing Middleware**: Automatic UUID generation and header propagation via `X-Request-ID`.
- **FastAPI Lifespan Hooks**: Context manager managing application startup and graceful shutdown resources.
- **Standardized Response Contracts**: Explicit Pydantic response models (`HealthResponse`, `StandardErrorResponse`) with machine-readable error codes (`NOT_FOUND`, `VALIDATION_ERROR`, `INTERNAL_SERVER_ERROR`).
- **Comprehensive Test Suite**: Pytest test cases covering health status, CORS headers, Request IDs, and error handlers.

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
│   ├── __init__.py
│   ├── main.py                    # FastAPI app initialization, CORS, middleware, lifespan
│   ├── api/
│   │   ├── __init__.py
│   │   └── v1/
│   │       ├── __init__.py
│   │       ├── router.py          # Aggregated v1 API router
│   │       └── routes/
│   │           ├── __init__.py
│   │           └── health.py      # GET /api/v1/health route
│   ├── config/
│   │   ├── __init__.py
│   │   └── settings.py        # Typed settings with Pydantic validators
│   ├── middleware/
│   │   ├── __init__.py
│   │   ├── error_handler.py   # Global 404, 422, 500 exception handlers
│   │   └── request_id.py      # X-Request-ID tracing middleware
│   ├── schemas/
│   │   ├── __init__.py
│   │   └── response.py        # HealthResponse & StandardErrorResponse schemas
│   ├── services/              # Reserved for Phase 1.2+ AI inference services
│   ├── models/                # Reserved for Phase 1.2+ database models
│   └── utils/
│       ├── __init__.py
│       └── logger.py          # Centralized logger (timestamp | LOG_LEVEL | module | message)
├── tests/
│   ├── __init__.py
│   ├── test_health.py         # Health endpoint tests
│   ├── test_errors.py         # 404 & 422 error handler tests
│   └── test_middleware.py     # CORS & Request ID header tests
├── .env.example
├── .env
├── .gitignore
├── pyproject.toml
├── README.md
└── requirements.txt
```

---

## ⚡ Setup & Development Guide

### 1. Prerequisites
- **Python**: `v3.11` or higher installed.

### 2. Create Virtual Environment & Install Dependencies

```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python -m venv .venv

# Activate virtual environment
# Windows (PowerShell):
.venv\Scripts\Activate.ps1
# macOS/Linux:
source .venv/bin/activate

# Install requirements
pip install -r requirements.txt
```

### 3. Environment Configuration

Copy `.env.example` to `.env`:

```bash
# Windows (Command Prompt / PowerShell):
copy .env.example .env
# Linux / macOS:
cp .env.example .env
```

Verify key variables in `.env`:
```env
APP_NAME="Virtual Wear Simulation API"
APP_VERSION="1.0.0"
APP_ENV=development
DEBUG=true
API_V1_PREFIX=/api/v1
HOST=0.0.0.0
PORT=8000
FRONTEND_URL=http://localhost:5173
CORS_ORIGINS=["http://localhost:5173", "http://127.0.0.1:5173"]
MAX_UPLOAD_SIZE_MB=10
LOG_LEVEL=INFO
```

---

## 🏃 Running the Application

Start the Uvicorn ASGI development server:

```bash
uvicorn app.main:app --reload
```

- **Health Endpoint**: `GET http://localhost:8000/api/v1/health`
- **Swagger Interactive API Docs**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **ReDoc Documentation**: [http://localhost:8000/redoc](http://localhost:8000/redoc)

---

## 🧪 Testing & Code Quality

### Run Pytest Suite

```bash
pytest
```

### Run Ruff Linter Check

```bash
ruff check .
```

### Run Black Formatting Verification

```bash
black --check .
```

---

## 📋 API Endpoints Overview

| Method | Endpoint | Description | Response Model |
| :--- | :--- | :--- | :--- |
| `GET` | `/api/v1/health` | Lightweight service health & version metadata | `HealthResponse` |
| `GET` | `/docs` | Interactive Swagger UI documentation | HTML |
| `GET` | `/redoc` | ReDoc API specification documentation | HTML |
