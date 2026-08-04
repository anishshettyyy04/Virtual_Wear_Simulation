# Software Bill of Materials (SBOM) — Version v1.0.0-phase1

**Project**: AI Virtual Wear Simulation
**Release**: `v1.0.0-phase1`
**Runtime Environment**: Python 3.11+ (CPython)
**Container Base**: `python:3.11-slim` (Debian Bookworm)

---

## 1. System Runtime & Dependency Inventory

| Package Name | Version Constraint | Exact Installed | Ecosystem | License | Function / Purpose |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **`fastapi`** | `>=0.100.0` | `0.116.1` | PyPI | MIT | Core REST API Web Framework |
| **`uvicorn`** | `>=0.22.0` | `0.34.0` | PyPI | BSD-3-Clause | ASGI Application Web Server |
| **`pydantic`** | `>=2.0.0` | `2.11.7` | PyPI | MIT | Data Validation & Settings Management |
| **`pydantic-core`**| `2.31.1` | `2.31.1` | PyPI | MIT | Rust Core Validator for Pydantic v2 |
| **`starlette`** | `<0.46.0,>=0.40.0`| `0.45.3` | PyPI | BSD-3-Clause | Low-level ASGI Toolkit for FastAPI |
| **`httpx`** | `>=0.24.0` | `0.28.1` | PyPI | BSD-3-Clause | Async HTTP Client & TestClient Driver |
| **`python-dotenv`**| `>=1.0.0` | `1.1.0` | PyPI | BSD-3-Clause | Load environment variables from `.env` |
| **`pytest`** | `>=7.0.0` | `8.3.5` | PyPI | MIT | Automated Unit & Integration Testing |

---

## 2. Automated SBOM Generation Procedures

To automatically generate CycloneDX SPDX or Syft SBOM JSON manifests for production security compliance pipelines, use the following tools:

### Using CycloneDX Python CLI
```bash
# Install CycloneDX generator
pip install cyclonedx-bom

# Generate CycloneDX JSON SBOM manifest
cyclonedx-py requirements backend/requirements.txt -o docs/security/sbom.cyclonedx.json
```

### Using Anchore Syft
```bash
# Generate SBOM using Syft
syft dir:. -o cyclonedx-json > docs/security/sbom.syft.json
```
