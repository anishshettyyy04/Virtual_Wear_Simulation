# AI Virtual Wear Simulation

![Version](https://img.shields.io/badge/version-v1.0.0--phase1-blue.svg)
![Python](https://img.shields.io/badge/python-3.11-green.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.116.1-009688.svg)
![React](https://img.shields.io/badge/React-19.0-61DAFB.svg)
![TailwindCSS](https://img.shields.io/badge/TailwindCSS-v4.0-38BDF8.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

Welcome to the **AI Virtual Wear Simulation** repository. This system powers an end-to-end e-commerce apparel simulation experience featuring personalized outfit recommendations, user body & style preference modeling, REST APIs, and AI Virtual Try-On execution using IDM-VTON.

---

## 🌟 Release Information (`v1.0.0-phase1`)

**Current Release**: `v1.0.0-phase1` (Phase 1 Complete)

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

## 🌟 Key Features

### Frontend Architecture
- **Feature-Based Scalable Architecture**: Clean modular directory structure designed for team collaboration.
- **Route-Level Code Splitting**: Optimized performance with `React.lazy` and `Suspense`.
- **Axios API Layer**: Pre-configured HTTP client with base URL environment resolution, request authorization interceptors, and standardized error parsing (`parseApiError`).
- **Interactive Try-On Simulation Studio**: Drag-and-drop image upload dropzone with client-side format and size validation.
- **Before/After Split Visualizer**: Interactive slider comparing original avatar image with simulated try-on output.
- **AI Fit Analytics**: Real-time confidence metrics on shoulder alignment, waist drape, and fabric tension.
- **Fast Refresh Clean Architecture**: Context object definitions separated into standalone JS files to eliminate React Fast Refresh linter warnings.
- **Accessibility & UX**: Accessible focus trap in mobile navigation drawer, ESC key listener, focus restoration, keyboard navigation, ARIA dialog accessibility, glassmorphic dark mode palette, and mobile-responsive drawer navigation.

### Backend & Recommendation Subsystem
- **Product Data Catalog**: 25 catalog apparel items across 8 categories validated via Draft-07 JSON Schemas.
- **User Preference Model**: Complex 3D preference model tracking user size, style, budget, climate, and body metrics.
- **Personalized Recommendation Engine**: Sub-5ms latency scoring engine combining rule-based, content-based, and collaborative filtering with in-memory caching.
- **FastAPI REST API**: Fully asynchronous versioned REST API (`/api/v1`) with CORS, rate limiting, request ID tracing, structured JSON logging, and error handling.
- **AI IDM-VTON Pipeline**: Modular image preprocessing, SegFormer human parsing, DWPose keypoint estimation, agnostic mask generation, and IDM-VTON virtual try-on engine integration.

---

## 🚀 Tech Stack

| Domain | Technology | Purpose |
| :--- | :--- | :--- |
| **Frontend UI** | **React 19** | Core UI Library (Functional Components & Custom Hooks) |
| **Frontend Build** | **Vite 6** | Next-Generation Build Tool & HMR Dev Server |
| **Styling Engine** | **Tailwind CSS v4** | `@tailwindcss/vite` Utility-First Styling Engine |
| **Routing** | **React Router DOM 7** | Client-side routing with Shared Layout & Code-Splitting |
| **HTTP Client** | **Axios** | Client API service layer with request interceptors |
| **Backend Framework** | **FastAPI (v0.115+)** | High-performance Python ASGI web framework |
| **Validation** | **Pydantic v2 & JSON Schema** | Strict request/response and dataset validation |
| **AI Inference** | **PyTorch & ONNX Runtime** | SegFormer human parsing & DWPose estimation |
| **Image Processing** | **Pillow & OpenCV** | EXIF normalization, mask generation, and image resizing |

---

## 🏗️ Architecture Overview

```text
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

## 📁 Project Folder Structure

```text
Virtual_Wear_Simulation/
├── backend/
│   ├── api/                     # FastAPI route endpoints & middleware (Phase 1.4)
│   ├── app/                     # AI Pipeline & FastAPI application initialization
│   ├── assets/                  # Product apparel image assets (8 categories)
│   ├── cache/                   # Recommendation engine in-memory cache
│   ├── config/                  # System settings & recommendation config
│   ├── contracts/               # JSON API contract schemas
│   ├── data/                    # Seed datasets (products.json, user_preferences.json)
│   ├── docs/                    # Technical phase specs & integration guides
│   ├── examples/                # Example API request/response JSON payloads
│   ├── models/                  # Pydantic data models & response schemas
│   ├── recommendation/          # Recommendation engine scoring & strategy modules
│   ├── reports/                 # QA audit & system verification reports
│   ├── schemas/                 # JSON Schema Draft-07 definitions
│   ├── scripts/                 # Dataset validation & benchmark scripts
│   ├── services/                # Business logic services & AI pipeline orchestrator
│   ├── tests/                   # Pytest test suite & automated smoke tests
│   └── utils/                   # Image preprocessor & structured logging helpers
├── public/                      # Static web assets & favicon
├── src/                         # React 19 Frontend application source
│   ├── components/              # Common UI primitives & layout wrappers
│   ├── constants/               # API endpoints & theme tokens
│   ├── context/                 # SimulationContext & AuthContext
│   ├── features/                # Domain feature modules (home, upload, simulation, result)
│   ├── hooks/                   # Custom hooks (useImageUpload, useSimulation)
│   ├── pages/                   # Lazy-loaded page components
│   ├── routes/                  # React Router DOM 7 routes
│   └── services/                # Axios API service layer
├── Dockerfile                   # Backend Docker container build instructions
├── docker-compose.yml           # Multi-container orchestration
├── Makefile                     # Developer quick-start targets
├── package.json                 # Node.js dependencies & scripts
└── README.md
```

---

## ⚡ Developer Quick Start

### Backend Quick Start (`Makefile`)

```bash
make run        # Start FastAPI dev server (http://localhost:8000)
make test       # Run unit and API integration tests
make smoke      # Run automated smoke test suite
make validate   # Validate JSON datasets against schemas
make benchmark  # Run recommendation engine benchmark
make report     # Generate performance & latency report
```

### Frontend Quick Start (`npm`)

```bash
# Install dependencies
npm install

# Run Vite HMR dev server
npm run dev

# Build production bundle
npm run build
```

---

## 🌐 Interactive OpenAPI Documentation

- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`
- **OpenAPI Schema**: `http://localhost:8000/openapi.json`

---

## 🐳 Docker Deployment

```bash
# Build Docker image
docker build -t virtual-wear-backend .

# Launch container with Docker Compose
docker-compose up -d
```
