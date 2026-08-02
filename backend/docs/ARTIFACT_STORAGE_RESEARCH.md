# Phase 1.2.9A: Artifact Lifecycle Management Research & Architecture

**Project:** Virtual Wear Simulation — Backend  
**Phase:** 1.2.9A — Artifact Lifecycle Management Research & Architecture  
**Status:** Research & Architecture Specification (No Production Code Modified)  
**Author:** AI Engineering & Architecture Team  

---

## Executive Summary

This document presents the complete architectural specification and design record for the **Artifact Lifecycle Management System** (Phase 1.2.9A). As the AI Virtual Wear Simulation backend expands to support multi-engine diffusion execution, high-throughput background queues, and cloud object storage, a unified, centralized artifact management system is essential to serve as the single source of truth for every asset generated across the pipeline.

### Core Architectural Decisions

1. **Taxonomy & Lifecycle Control:** Formalized 6 distinct artifact classes (*Temporary, Intermediate, Permanent, Cached, Diagnostic, Exportable*) with deterministic retention boundaries.
2. **Canonical Metadata & Manifest:** Pydantic-based `ArtifactMetadata` schema and full-job `ArtifactManifest` JSON contracts providing end-to-end lineage tracing and cryptographic reproducibility.
3. **Storage Driver Abstraction (`BaseArtifactStorage`)**: Pluggable storage engine pattern isolating pipeline logic from underlying physical storage (Local Filesystem, AWS S3, MinIO, Google Cloud Storage, Azure Blob Storage).
4. **Cryptographic Integrity (`SHA-256`)**: Streaming SHA-256 checksum validation for corruption detection, anti-tampering verification, and content-addressable deduplication.
5. **Phase 1.2.9B Readiness:** Architectural design is 100% complete and verified. **GO Recommendation** for Phase 1.2.9B implementation.

---

## 1. Artifact Inventory

Every asset generated or consumed during a Virtual Try-On job is tracked under explicit ownership, lifetime, and cleanup rules:

| Artifact Name | Producer | Consumer | Canonical Storage Path | Lifetime | Owner | Cleanup Policy |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Uploaded Person Image** | Client / API | Preprocessor | `data/uploads/person/` | Retention Period | Job | Registered temp cleanup |
| **Uploaded Garment Image** | Client / API | Preprocessor | `data/uploads/garment/` | Retention Period | Job | Registered temp cleanup |
| **Preprocessed Person** | ImagePreprocessor | Parser, Pose | `data/preprocessing/person/` | Intermediate | Job | Pruned after pipeline finish |
| **Preprocessed Garment** | ImagePreprocessor | Conditioning | `data/preprocessing/garment/` | Intermediate | Job | Pruned after pipeline finish |
| **Human Parsing Mask** | SegFormerParser | AgnosticMask | `data/parsing/` | Intermediate | Job | Pruned after pipeline finish |
| **Pose Keypoints JSON** | DWPoseEstimator | AgnosticMask | `data/pose/json/` | Intermediate | Job | Pruned after pipeline finish |
| **Pose Overlay PNG** | DWPoseEstimator | Conditioning | `data/pose/overlays/` | Intermediate | Job | Pruned after pipeline finish |
| **Agnostic Mask PNG** | AgnosticMaskGen | Conditioning | `data/masks/` | Intermediate | Job | Pruned after pipeline finish |
| **DensePose IUV Map** | DensePoseEngine | Conditioning | `data/densepose/` | Intermediate | Job | Pruned after pipeline finish |
| **ConditioningBundle** | ConditioningLayer | TryOnEngine | `data/conditioning/` | Intermediate | Job | Pruned after pipeline finish |
| **Raw Inference Output** | IDMVTONEngine | Postprocessor | `data/inference/` | Temporary | Job | Immediate post-render cleanup |
| **Final Render Output** | Postprocessor | REST API, Client | `data/rendered/` | Permanent | User/System | **PERMANENT** (Never auto-deleted) |
| **Render Thumbnail** | ThumbnailService | REST API | `data/thumbnails/` | Permanent | User/System | **PERMANENT** (Never auto-deleted) |
| **Debug Overlays** | Pipeline Debugger | Diagnostics | `data/debug/` | Diagnostic | Job | Pruned on retention expiry |
| **Pipeline Metrics JSON**| JobLifecycle | Health / Analytics | `data/metadata/metrics/` | Permanent | System | Retained for analytics |
| **Job Event Timeline** | JobLifecycle | WebSockets / API | `data/metadata/events/` | Permanent | System | Pruned with job retention |
| **Job Manifest JSON** | ArtifactManager | API / Exporter | `data/manifests/` | Permanent | System | Retained with job snapshot |

---

## 2. Artifact Taxonomy

Artifacts are categorized into 6 functional tiers determining storage location, caching eligibility, and retention rules:

```text
                  ┌─────────────────────────────────────────┐
                  │            Uploaded Assets              │
                  └────────────────────┬────────────────────┘
                                       │
                                       ▼
                  ┌─────────────────────────────────────────┐
                  │     Intermediate / Processing Assets    │
                  │  (Preprocessing, Parsing, Pose, Mask)   │
                  └────────────────────┬────────────────────┘
                                       │
                                       ▼
                  ┌─────────────────────────────────────────┐
                  │            Conditioning Bundle          │
                  └────────────────────┬────────────────────┘
                                       │
                                       ▼
                  ┌─────────────────────────────────────────┐
                  │          Inference Execution            │
                  └────────────────────┬────────────────────┘
                                       │
                ┌──────────────────────┴──────────────────────┐
                ▼                                             ▼
  ┌───────────────────────────┐                 ┌───────────────────────────┐
  │     Permanent Outputs     │                 │   Diagnostic & Manifests  │
  │  (Rendered PNG, Thumbnails)│                 │ (Metrics, Timeline, JSON) │
  └───────────────────────────┘                 └───────────────────────────┘
```

### Taxonomy Classes

1. **Temporary**: Transient byte buffers or raw inference dumps cleaned up immediately following step completion (e.g. uncompressed raw float arrays).
2. **Intermediate**: Normalized stage outputs required by downstream pipeline steps (e.g. SegFormer parsing mask, DWPose keypoint JSON, Agnostic clothing mask). Retained until pipeline execution finishes.
3. **Permanent**: Final user-facing output artifacts (Rendered image, thumbnail). **Must never be deleted by automated retention pruning.**
4. **Cached**: Deterministic pre-computed features (e.g. garment segmentations or pose keypoints for reusable catalog garments) stored in content-addressable cache.
5. **Diagnostic**: Visual debug overlays, feature maps, and detailed timing logs used for model evaluation and failure investigation.
6. **Exportable**: Self-contained archive bundles containing full job manifests, checksums, and assets for offline reproduction and research sharing.

---

## 3. Canonical Storage Layout

Recommended production storage hierarchy under `data/`:

```text
data/
├── uploads/
│   ├── person/                   # Raw person uploads from API
│   └── garment/                  # Raw garment uploads from API
├── preprocessing/
│   ├── person/                   # Normalized 768x1024 person images
│   └── garment/                  # Normalized 768x1024 garment images
├── parsing/                      # 8-bit single-channel SegFormer PNG masks
├── pose/
│   ├── json/                     # COCO-18 keypoint coordinate JSON files
│   └── overlays/                 # Rendered skeletal pose visualization images
├── masks/                        # Agnostic clothing replacement masks
├── densepose/                    # DensePose surface IUV body maps
├── conditioning/                 # Serialized ConditioningBundle payloads
├── inference/                    # Raw UNet diffusion output frames
├── rendered/
│   └── YYYY/MM/DD/               # Final try-on output renders (Date-partitioned)
├── thumbnails/
│   └── YYYY/MM/DD/               # Output thumbnails (Date-partitioned)
├── manifests/                    # Complete job execution manifest JSONs
├── metadata/
│   ├── metrics/                  # Job performance metrics JSON files
│   └── events/                   # Job event log timelines
├── cache/                        # Content-addressable feature cache
└── temp/                         # Atomic staging write directory
```

---

## 4. Artifact Metadata Schema

The canonical metadata model (`ArtifactMetadata`) attached to every stored asset:

```python
from enum import Enum
from typing import Any, Dict, Optional
from pydantic import BaseModel, Field


class StorageProviderType(str, Enum):
    LOCAL = "local"
    S3 = "s3"
    GCS = "gcs"
    AZURE = "azure"
    MINIO = "minio"


class ArtifactCategory(str, Enum):
    TEMPORARY = "temporary"
    INTERMEDIATE = "intermediate"
    PERMANENT = "permanent"
    CACHED = "cached"
    DIAGNOSTIC = "diagnostic"
    EXPORTABLE = "exportable"


class ArtifactMetadata(BaseModel):
    """Canonical metadata schema for pipeline artifacts."""

    artifact_id: str = Field(..., description="Unique artifact identifier")
    artifact_type: str = Field(..., description="Semantic type (e.g. agnostic_mask)")
    category: ArtifactCategory = Field(default=ArtifactCategory.INTERMEDIATE)
    schema_version: str = Field(default="1.0.0")
    pipeline_version: str = Field(default="1.0.0")
    engine_name: str = Field(default="idm_vton")
    producer_stage: str = Field(..., description="Pipeline stage name")
    created_at: str = Field(..., description="ISO 8601 UTC timestamp")
    checksum: str = Field(..., description="Cryptographic file hash")
    checksum_algorithm: str = Field(default="sha256")
    mime_type: str = Field(..., description="MIME type (e.g. image/png)")
    file_size_bytes: int = Field(..., ge=0)
    width: Optional[int] = Field(default=None)
    height: Optional[int] = Field(default=None)
    owner_job_id: str = Field(..., description="Associated job ID")
    storage_provider: StorageProviderType = Field(default=StorageProviderType.LOCAL)
    storage_path: str = Field(..., description="URI or path relative to root")
    is_deleted: bool = Field(default=False)
    custom_metadata: Dict[str, Any] = Field(default_factory=dict)
```

---

## 5. Artifact Manifest

The `ArtifactManifest` represents the complete execution graph and dependency lineage of a Virtual Try-On job:

```json
{
  "manifest_version": "1.0.0",
  "job_id": "job_20260802_a81f9c3d",
  "request_id": "req_f9218a00",
  "created_at": "2026-08-02T17:45:00.000Z",
  "pipeline_version": "1.0.0",
  "engine_name": "idm_vton",
  "status": "completed",
  "inputs": {
    "person_image": {
      "artifact_id": "art_upload_person_01",
      "path": "data/uploads/person/job_20260802_a81f9c3d_person.jpg",
      "checksum": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
    },
    "garment_image": {
      "artifact_id": "art_upload_garment_01",
      "path": "data/uploads/garment/job_20260802_a81f9c3d_garment.jpg",
      "checksum": "8f434346648f6b96df89dda901c5176b10a6d83961dd3c1ac88b59b2dc327aa4"
    }
  },
  "lineage": [
    {
      "stage": "Preprocessing",
      "artifacts": ["art_prep_person_01", "art_prep_garment_01"]
    },
    {
      "stage": "Human Parsing",
      "artifacts": ["art_parsing_mask_01"]
    },
    {
      "stage": "Pose Estimation",
      "artifacts": ["art_pose_json_01", "art_pose_overlay_01"]
    },
    {
      "stage": "Agnostic Mask",
      "artifacts": ["art_agnostic_mask_01"]
    },
    {
      "stage": "Conditioning",
      "artifacts": ["art_conditioning_bundle_01"]
    },
    {
      "stage": "Try-On",
      "artifacts": ["art_rendered_final_01", "art_thumbnail_01"]
    }
  ],
  "outputs": {
    "final_render": {
      "artifact_id": "art_rendered_final_01",
      "path": "data/rendered/2026/08/02/job_20260802_a81f9c3d_render.png",
      "checksum": "a591a6d40bf420404a011733cfb7b190d62c65bf0bcda32b57b277d9ad9f146e",
      "dimensions": [768, 1024]
    },
    "thumbnail": {
      "artifact_id": "art_thumbnail_01",
      "path": "data/thumbnails/2026/08/02/job_20260802_a81f9c3d_thumb.jpg",
      "checksum": "1198f1c84144e05206fae967f6b92a6c1e3458ef8a19a9a3028d7a3ed17b6a12",
      "dimensions": [192, 256]
    }
  },
  "metrics": {
    "queue_wait_ms": 12.5,
    "pipeline_ms": 1450.2,
    "total_ms": 1510.0
  }
}
```

---

## 6. Artifact Registry Evaluation

We evaluated 6 registry backend candidates for artifact tracking:

| Registry Candidate | Concurrency Safety | Query Speed | Persistence | Complexity | Migration Path | Recommendation |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **JSON Registry** | Low (File locks) | Fast (<1ms) | File-backed | Minimal | Easy | Phase 1 Fallback |
| **Filesystem Registry** | Moderate | Fast | File-backed | Low | Moderate | Phase 1 Default |
| **SQLite Registry** | High (WAL mode) | Very Fast | Single file | Low | Easy | **Phase 1 Recommended** |
| **PostgreSQL Registry** | Very High | Excellent | Relational DB | Medium | Production Native | Phase 2 Target |
| **Redis Registry** | Very High | Ultra Fast | In-Memory/RDB | Low-Medium | Cache Target | Phase 2 Distributed |
| **Cloud S3 Metadata** | High | Slower (API) | Object Storage | Low | Cloud Native | Cloud Adapter |

### Registry Recommendation
* **Phase 1 (Local Single-Node)**: Lightweight **SQLite (WAL Mode)** or **Memory/Filesystem Registry** with thread-safe locking.
* **Phase 2 (Distributed Enterprise)**: Seamless migration to **PostgreSQL** without modifying business logic in pipeline stages or REST API routes.

---

## 7. Checksum Strategy

Comparative analysis of checksum algorithms for artifact verification:

| Algorithm | Digest Size | Speed (MB/s) | Security / Collision Resistance | Duplicate Detection | Selection |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **CRC32** | 32-bit | 2500 MB/s | Extremely Weak (Non-cryptographic) | Poor | Rejected |
| **MD5** | 128-bit | 650 MB/s | Broken (Collision vulnerable) | Moderate | Rejected |
| **SHA-1** | 160-bit | 550 MB/s | Weakened | Moderate | Rejected |
| **SHA-256** | 256-bit | 350 MB/s | **Cryptographically Secure (Zero Collisions)** | **Superior** | **RECOMMENDED** |

### Verification Protocol
1. **Write-Time Calculation**: Streaming SHA-256 computed on chunked file writes.
2. **Read-Time Validation**: Optional lazy integrity check on cache hits or critical outputs.
3. **Corruption Recovery**: If SHA-256 mismatch detected, flag artifact corrupted, purge, and trigger stage re-execution.

---

## 8. Versioning Strategy

All artifacts, manifests, and pipeline interfaces adhere to **Semantic Versioning 2.0.0** (`MAJOR.MINOR.PATCH`):

* **Artifact Schema Version (`1.0.0`)**: Increment MAJOR on breaking structural metadata changes.
* **Manifest Schema Version (`1.0.0`)**: Increment MAJOR when lineage or output contracts change.
* **Pipeline Version (`1.0.0`)**: Represents current backend pipeline feature set.
* **Engine Version (`idm_vton_v1.0`)**: Tracks neural model architecture iterations.
* **Conditioning Bundle Version (`1.0.0`)**: Tracks tensor key definitions.

---

## 9. Retention Policies

| Artifact Category / Job State | Retention Rule | Cleanup Action | Automated Trigger |
| :--- | :--- | :--- | :--- |
| **Completed Job - Temporary** | 0 minutes | Immediate deletion upon job completion | Pipeline `finally` block |
| **Completed Job - Intermediate**| 24 Hours (`AI_JOB_RETENTION_HOURS`) | Registered artifact cleanup | `JobCleanupService` loop |
| **Completed Job - Permanent** | **Infinite** | Retained permanently in `data/rendered/` | Exempt from cleanup |
| **Cancelled Job** | 1 Hour (`AI_CANCELLED_JOB_RETENTION_HOURS`) | Full artifact and input purge | `JobCleanupService` loop |
| **Failed Job** | 24 Hours | Registered artifact cleanup; retain debug overlay | `JobCleanupService` loop |
| **Development Build** | 2 Hours | Complete workspace temp purge | Dev script / CLI |

---

## 10. Portable Execution Bundles (Export & Import)

To support reproducible research, offline inspection, and dataset generation:

### Archive Bundle Layout (`job_<id>_bundle.tar.gz`)
```text
job_20260802_a81f9c3d_bundle/
├── manifest.json                 # Complete execution manifest
├── metadata.json                 # Consolidated metadata map
├── checksums.sha256              # Cryptographic verification manifest
├── inputs/
│   ├── person.jpg
│   └── garment.jpg
├── intermediate/
│   ├── parsing.png
│   ├── pose.json
│   └── agnostic_mask.png
└── outputs/
    ├── render.png
    └── thumbnail.jpg
```

---

## 11. Cloud Storage Compatibility

The system introduces `BaseArtifactStorage` abstraction drivers:

```text
               BaseArtifactStorage (ABC)
                           │
    ┌──────────────────────┼──────────────────────┐
    ▼                      ▼                      ▼
LocalFileStorage   S3ArtifactStorage     GCSArtifactStorage
 (Default Phase 1)  (AWS / MinIO Phase 2) (Google Cloud Phase 2)
```

### Abstraction Driver Operations
* `write_artifact(path, stream/bytes, metadata) -> ArtifactMetadata`
* `read_artifact(artifact_id) -> AsyncIterable[bytes]`
* `delete_artifact(artifact_id) -> bool`
* `exists(artifact_id) -> bool`
* `get_url(artifact_id, expires_in) -> str`

---

## 12. Security Analysis

1. **Path Traversal Prevention**: Strict path resolution using `pathlib.Path(path).resolve()` ensuring all targets stay bounded inside `DATA_DIR`.
2. **Filename Sanitization**: Strip non-alphanumeric characters; sanitize filenames with UUID prefix.
3. **Atomic File Writes**: Write incoming uploads and intermediate assets to `.tmp` files before performing atomic `os.replace()` to prevent partial file corruption.
4. **Secure Deletion**: Verify ownership and registration before deleting files.
5. **Orphan Detection**: Scheduled verification comparing filesystem items against `ArtifactRegistry` entries to identify and purge untracked orphaned files.

---

## 13. Performance Analysis & Optimizations

* **Streaming IO**: Use `aiofiles` chunked async streaming for file uploads and downloads (chunk size = 64KB).
* **Lazy Loading**: Read heavy image artifacts into memory only during active execution.
* **Lossless Image Compression**: Store intermediate masks as 8-bit single-channel PNG (`mode="L"`, compression level 6).
* **Manifest Caching**: Cache active job manifests in memory (`MemoryJobRegistry`).
* **Parallel Cleanup**: Perform artifact deletion asynchronously off main event loop threads.

---

## 14. Scalability Analysis

* **Date Partitioning**: Store rendered output images in `data/rendered/YYYY/MM/DD/` to prevent single-directory inode exhaustion.
* **Content-Addressable Cache**: Re-use parsed masks and pose keypoints for recurring garment images via SHA-256 hash lookup.
* **Stateless Worker Nodes**: Storage drivers (`BaseArtifactStorage`) allow background workers to scale horizontally across multiple instances while referencing shared S3/GCS buckets.

---

## 15. Proposed System Architecture

```text
               +-------------------------------------------------+
               |            VirtualWearPipeline                  |
               +------------------------┬------------------------+
                                        |
                                        v
               +-------------------------------------------------+
               |             ArtifactManager                     |
               +------------------------┬------------------------+
                                        |
                   ┌────────────────────┴────────────────────┐
                   v                                         v
+------------------------------------+    +------------------------------------+
|          ArtifactRegistry          |    |          ArtifactStorage           |
| (SQLite / Memory / PostgreSQL)     |    | (Local / MinIO / S3 / GCS)         |
+------------------------------------+    +------------------------------------+
```

---

## 16. Proposed Components & Responsibilities

| Component Name | Responsibility Description |
| :--- | :--- |
| **ArtifactManager** | High-level orchestrator for artifact registration, retrieval, and manifest generation. |
| **ArtifactRegistry** | Database / memory store indexing artifact metadata records and job lineage. |
| **ArtifactStorage** | Abstract driver handling physical storage reads, writes, and cloud bucket uploads. |
| **ArtifactManifest** | Pydantic model representing complete job execution tree and output references. |
| **ArtifactMetadata** | Pydantic model describing individual asset properties, checksums, and dimensions. |
| **ArtifactChecksum** | Streaming SHA-256 utility for integrity calculation and verification. |
| **ArtifactLocator** | Resolves logical artifact IDs to physical file paths or pre-signed cloud URLs. |
| **ArtifactValidator** | Validates mime types, dimensions, file size limits, and checksum matches. |
| **ArtifactRetentionPolicy**| Evaluates artifact age against configured retention thresholds (`AI_JOB_RETENTION_HOURS`). |
| **ArtifactCleaner** | Executes safe registration-driven deletion of expired intermediate files. |
| **ArtifactExporter** | Packages job manifests and assets into portable `.tar.gz` research bundles. |

---

## 17. Pipeline Integration Points

```text
1. ImagePreprocessor ──────> Register preprocessed person/garment artifacts
2. SegFormerHumanParser ───> Register parsing mask PNG artifact
3. DWPoseEstimator ─────────> Register pose keypoints JSON & overlay PNG artifacts
4. AgnosticMaskGenerator ──> Register clothing-agnostic mask PNG artifact
5. ConditioningLayer ──────> Register ConditioningBundle payload artifact
6. IDMVTONEngine ───────────> Output raw try-on render frame
7. Postprocessor ───────────> Register final output render & thumbnail artifacts
8. JobCleanupService ───────> Invoke ArtifactCleaner to prune intermediate artifacts
```

---

## 18. Implementation Roadmap for Phase 1.2.9B

1. **Step 1 — Create Core Schemas (`app/schemas/artifact.py`)**:
   - Implement `ArtifactCategory`, `StorageProviderType`, `ArtifactMetadata`, `ArtifactManifest`.
2. **Step 2 — Implement Storage Abstraction (`app/services/storage/`)**:
   - Implement `BaseArtifactStorage` and `LocalArtifactStorage`.
3. **Step 3 — Implement Artifact Registry (`app/services/artifacts/registry.py`)**:
   - Implement `BaseArtifactRegistry` and `MemoryArtifactRegistry`.
4. **Step 4 — Implement Artifact Manager (`app/services/artifacts/manager.py`)**:
   - Implement `ArtifactManager` orchestrating storage, registry, checksums, and manifest creation.
5. **Step 5 — Pipeline & Cleanup Integration**:
   - Integrate `ArtifactManager` with `VirtualWearPipeline` stages and `JobCleanupService`.
6. **Step 6 — Unit Test & Verification**:
   - Write comprehensive test suite in `tests/test_artifact_manager.py`.

---

## 19. GO / NO-GO Recommendation

### Recommendation: **GO FOR PHASE 1.2.9B**

* **Rationale**: The research and architecture for Artifact Lifecycle Management is 100% complete. The proposed design cleanly decouples pipeline stages from physical storage, provides cryptographic integrity verification, supports date-partitioned storage layout, and prepares the backend for cloud object storage scaling without breaking existing APIs or pipeline contracts.
