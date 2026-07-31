# AI Virtual Wear Simulation — Project Core Repository

[![Backend CI](https://github.com/anishshettyyy04/Virtual_Wear_Simulation/actions/workflows/backend.yml/badge.svg)](https://github.com/anishshettyyy04/Virtual_Wear_Simulation/actions/workflows/backend.yml)
![Version](https://img.shields.io/badge/version-v1.0.0--phase1-blue.svg)
![Python](https://img.shields.io/badge/python-3.11-green.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.116.1-009688.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

Welcome to the **AI Virtual Wear Simulation** repository. This project powers an end-to-end e-commerce apparel simulation experience featuring personalized outfit recommendations, 3D body preference modeling, REST APIs, and AI Virtual Try-On execution using IDM-VTON.

---

## 🌟 Release Information (`v1.0.0-phase1`)

**Current Release**: `v1.0.0-phase1` (Phase 1 Backend System Complete)

- 📌 **Version Tag**: [`VERSION`](VERSION) (`v1.0.0-phase1`)
- 📋 **Release Notes**: [`RELEASE_NOTES.md`](RELEASE_NOTES.md)
- 📜 **Changelog**: [`CHANGELOG.md`](CHANGELOG.md)
- 🏷️ **Release Tag Guide**: [`docs/release/release-tag.md`](docs/release/release-tag.md)
- ✅ **Release Checklist**: [`docs/release/release_checklist.md`](docs/release/release_checklist.md)
- 🔒 **Software Bill of Materials (SBOM)**: [`docs/security/sbom.md`](docs/security/sbom.md)
- ⚖️ **License**: [`LICENSE`](LICENSE) (MIT License)
- 🤝 **Contributing Guide**: [`CONTRIBUTING.md`](CONTRIBUTING.md)
- 📜 **Code of Conduct**: [`CODE_OF_CONDUCT.md`](CODE_OF_CONDUCT.md)

---

## Architecture Overview

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
│ Request ID   │                  │ CORS         │                  │ Structured   │
│ Middleware   │                  │ Middleware   │                  │ Logger       │
└───────┬──────┘                  └───────┬──────┘                  └───────┬──────┘
        │                                 │                                 │
        └─────────────────────────────────┼─────────────────────────────────┘
                                          │
                                          ▼
┌──────────────────────────────────────────────────────────────────────────────────────────┐
│                                   Versioned Routers (v1)                                 │
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

## 📚 Integration Guides & Technical Documentation

- 🎨 **React Frontend Guide (Ashwin)**: [`backend/docs/frontend-guide.md`](file:///c:/Users/Gagan/OneDrive/Desktop/Virtual_Wear_Simulation/backend/docs/frontend-guide.md)
- 🤖 **AI Try-On Guide (Anish / IDM-VTON)**: [`backend/docs/ai-guide.md`](file:///c:/Users/Gagan/OneDrive/Desktop/Virtual_Wear_Simulation/backend/docs/ai-guide.md)
- 📊 **Monitoring & Observability Guide**: [`backend/docs/monitoring.md`](file:///c:/Users/Gagan/OneDrive/Desktop/Virtual_Wear_Simulation/backend/docs/monitoring.md)
- 📝 **API Contracts & JSON Schemas**: [`backend/contracts/`](file:///c:/Users/Gagan/OneDrive/Desktop/Virtual_Wear_Simulation/backend/contracts/)
- 💡 **API Response Payload Examples**: [`backend/examples/`](file:///c:/Users/Gagan/OneDrive/Desktop/Virtual_Wear_Simulation/backend/examples/)
- 📁 **System Quality & Audit Reports**: [`backend/reports/`](file:///c:/Users/Gagan/OneDrive/Desktop/Virtual_Wear_Simulation/backend/reports/)

---

## Quick Start & Developer Commands (`Makefile`)

Start dev server or run tests using `make` from root:

```bash
make run        # Start FastAPI dev server (http://localhost:8000)
make test       # Run unit and API integration tests
make smoke      # Run automated smoke test suite
make validate   # Validate JSON datasets against schemas
make benchmark  # Run recommendation engine benchmark
make report     # Generate performance & latency report
```

---

## Interactive OpenAPI Documentation

- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`
- **OpenAPI Schema**: `http://localhost:8000/openapi.json`

---

## Docker Deployment

```bash
# Build Docker image
docker build -t virtual-wear-backend .

# Launch container with Docker Compose
docker-compose up -d
```
