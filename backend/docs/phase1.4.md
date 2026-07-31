# Technical Documentation — Phase 1.4: Backend REST API

## Executive Summary
Phase 1.4 implements the **Backend REST API** for the **AI Virtual Wear Simulation** project using FastAPI, Pydantic v2, Uvicorn, pytest, and a decoupled service layer. It exposes all Phase 1 subsystems—Product Catalog (Phase 1.1), User Preference Modeling (Phase 1.2), Recommendation Engine & Caching (Phase 1.3), Health Monitoring, and Performance Analytics—through production-ready REST endpoints ready for React frontend and IDM-VTON AI Virtual Try-On pipeline integration.

---

## 1. REST API Architecture

```
                                  ┌───────────────────────────────┐
                                  │   React Frontend / Clients    │
                                  └───────────────┬───────────────┘
                                                  │
                                                  ▼
┌──────────────────────────────────────────────────────────────────────────────────────────┐
│                                     FastAPI Router                                       │
│                                  (backend/api/app.py)                                    │
└─────────────────────────────────────────┬────────────────────────────────────────────────┘
                                          │
        ┌─────────────────────────────────┼─────────────────────────────────┐
        ▼                                 ▼                                 ▼
┌──────────────┐                  ┌──────────────┐                  ┌──────────────┐
│ Logging Middleware              │ CORS Middleware              │ Global Error Handler
└───────┬──────┘                  └───────┬──────┘                  └───────┬──────┘
        │                                 │                                 │
        └─────────────────────────────────┼─────────────────────────────────┘
                                          │
                                          ▼
┌──────────────────────────────────────────────────────────────────────────────────────────┐
│                                   API Route Handlers                                     │
│  GET /products | GET /users | POST /recommendations | GET /health | GET /metrics         │
└─────────────────────────────────────────┬────────────────────────────────────────────────┘
                                          │
                                          ▼
┌──────────────────────────────────────────────────────────────────────────────────────────┐
│                                    Service Layer                                         │
│  ProductService | UserService | RecommendationService | HealthService | MetricsService   │
└─────────────────────────────────────────┬────────────────────────────────────────────────┘
                                          │
                                          ▼
┌──────────────────────────────────────────────────────────────────────────────────────────┐
│                               Subsystems & Datasets                                      │
│  products.json | user_preferences.json | RecommendationEngine | RecommendationCache       │
└──────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Endpoint Catalog

| HTTP Method | Endpoint Path | Description | Response Schema |
| :--- | :--- | :--- | :--- |
| **`GET`** | `/api/v1/products` | Returns all products with optional category & gender filters | `ProductListResponse` |
| **`GET`** | `/api/v1/products/{productId}` | Returns single product details by ID or 404 | `ProductResponse` |
| **`GET`** | `/api/v1/users/{userId}` | Returns user preference profile by ID or 404 | `UserResponse` |
| **`POST`** | `/api/v1/recommendations` | Generates personalized product recommendations | `RecommendationResponse` |
| **`GET`** | `/api/v1/health` | Returns system health status across all subsystems | `HealthResponse` |
| **`GET`** | `/api/v1/metrics` | Returns performance benchmarks, analytics & cache stats | `MetricsResponse` |

---

## 3. Middleware Architecture

1. **`LoggingMiddleware`** (`backend/api/middleware/logging.py`): Logs request method, path, HTTP status, and latency in milliseconds (`X-Process-Time-Ms`).
2. **`ExceptionMiddleware`** (`backend/api/middleware/exception_handler.py`): Catches HTTP 404/400 exceptions, Pydantic validation errors (422), and unexpected server errors (500), returning clean JSON envelopes.
3. **`CORSMiddleware`** (`backend/api/middleware/cors.py`): Configures cross-origin requests using `ALLOWED_ORIGINS` environment variables.

---

## 4. Service Layer Decoupling

Routes strictly execute request parsing and delegate business logic to decoupled services:
- **`ProductService`**: Catalog loading, filtering, and single-item retrieval.
- **`UserService`**: User profile lookups.
- **`RecommendationService`**: Invokes Phase 1.3 `RecommendationEngine` and `RecommendationCache`.
- **`HealthService`**: Executes `check_system_health()`.
- **`MetricsService`**: Loads exported `recommendation_metrics.json` analytics.

---

## 5. OpenAPI, Swagger UI & ReDoc Documentation

Interactive API documentation is automatically exposed by FastAPI:
- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`
- **OpenAPI JSON Schema**: `http://localhost:8000/openapi.json`

---

## 6. Testing & Quality Assurance

API integration tests in [`backend/tests/test_api.py`](file:///c:/Users/Gagan/OneDrive/Desktop/Virtual_Wear_Simulation/backend/tests/test_api.py) verify:
- Endpoints return expected status codes (200, 404, 422).
- Pydantic models validate response structures.
- FastAPI docs endpoints (`/docs`, `/redoc`) are reachable.

Run tests using:
```bash
python backend/tests/test_api.py
```

---

## 7. Production Enhancements

- **API Versioning**: Modular route organization under `backend/api/v1/` with backward compatibility wrappers.
- **Centralized Configuration Management**: Dynamic setting management in `backend/config/settings.py`.
- **Request Tracing**: `RequestIdMiddleware` generating UUID v4 tracking IDs (`X-Request-ID`) attached to every request state and logger output.
- **Standardized Response Envelope**: `BaseResponse[T]` schema enforcing `{ success, message, data, timestamp, requestId }` across all endpoints and exception handlers.
- **Structured JSON Logging**: Custom JSON logger outputting structured events with latency and request tracing context.
- **Startup Dependency Validation**: Lifespan startup validation confirming datasets, configurations, schemas, recommendation engine, cache, and health readiness before accepting requests.
- **Docker Containerization**: Production `Dockerfile`, `docker-compose.yml`, and `.dockerignore`.
- **Continuous Integration (CI/CD)**: GitHub Actions workflow (`.github/workflows/backend.yml`).
- **Postman API Collection**: Collection export (`VirtualWearAPI.postman_collection.json`).

---

## 8. Future Enhancements (Phase 2.0 Roadmap)

1. **Authentication & Authorization**: JWT token / OAuth2 authentication mapping user sessions to `userId`.
2. **Database Migration**: PostgreSQL / MongoDB integration replacing seed JSON files.
3. **AI Virtual Try-On Pipeline Integration (IDM-VTON)**: Endpoint `POST /api/v1/try-on` connecting user photos and recommended garments.

