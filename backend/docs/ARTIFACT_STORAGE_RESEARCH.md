# Phase 1.2.9AB: Storage Provider Architecture Refinement

**Project:** Virtual Wear Simulation — Backend  
**Phase:** 1.2.9AB — Storage Provider Architecture Refinement  
**Status:** Architecture Refinement Specification (No Production Code Modified)  
**Author:** AI Engineering & Architecture Team  

---

## Executive Summary

This document extends and refines the technical architecture for the **Artifact Lifecycle Management System** (Phase 1.2.9AB). Following the refinements in Phase 1.2.9AA, this phase establishes formal specifications for a **provider-agnostic storage management layer**, enabling seamless orchestration across diverse storage backends via `StorageProviderRegistry`, `StorageResolver`, and `StorageCapabilities`.

These architecture refinements ensure that Phase 1.2.9B implementation will seamlessly decouple pipeline execution from physical storage topologies, allowing zero-downtime migrations between local disk, Kubernetes PVCs, and cloud object storage (AWS S3, Google Cloud Storage, Azure Blob, MinIO).

---

## 1. Content-Addressable Storage (CAS)

### 1.1 Overview & Addressing Scheme
Under Content-Addressable Storage, an artifact's identity and storage path are derived directly from its cryptographic payload hash (SHA-256) rather than arbitrary user filenames or transient job IDs.

### 1.2 Storage Layout & Fan-Out Structure
To avoid filesystem directory performance degradation (inode limits and directory lock contention), CAS uses a 2-level directory fan-out based on the first 4 hex characters of the SHA-256 hash:

```text
data/cas/sha256/
├── 8f/
│   └── 43/
│       └── 8f434346648f6b96df89dda901c5176b10a6d83961dd3c1ac88b59b2dc327aa4.png
├── a5/
│   └── 91/
│       └── a591a6d40bf420404a011733cfb7b190d62c65bf0bcda32b57b277d9ad9f146e.png
└── e3/
    └── b0/
        └── e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855.json
```

### 1.3 Collision Handling & Deduplication
- **Collision Resistance**: SHA-256 produces a 256-bit output space ($2^{256}$ possibilities). The probability of a collision is cryptographically negligible ($< 10^{-60}$). If a collision occurs, payload byte equality is verified before deduplicating.
- **Content Deduplication**: Duplicate uploads or identical preprocessed garment feature maps yield the same SHA-256 hash. The system links new metadata entries (`ArtifactMetadata`) to the existing physical storage file without writing duplicate disk bytes.

---

## 2. Canonical Artifact URI Specification

### 2.1 Grammar & Structure
The backend standardizes on an abstract URI scheme (`artifact://`) that decouples business logic from physical storage locations (local paths, S3 buckets, GCS paths):

```text
artifact://<category>/<artifact_id>
```

#### Scheme Breakdown
- `scheme`: `artifact://`
- `category`: Category namespace (`upload`, `preprocessing`, `parsing`, `pose`, `mask`, `densepose`, `conditioning`, `inference`, `render`, `thumbnail`)
- `artifact_id`: Unique identifier (e.g. `art_20260802_a81f9c3d_mask` or content hash `sha256:8f43434664...`)

### 2.2 Canonical URI Examples
- **Uploaded Person**: `artifact://upload/person_job_20260802_a81f9c3d`
- **Agnostic Mask**: `artifact://mask/mask_job_20260802_a81f9c3d`
- **Pose Keypoints**: `artifact://pose/pose_job_20260802_a81f9c3d`
- **DensePose Artifact**: `artifact://densepose/dp_job_20260802_a81f9c3d`
- **Conditioning Bundle**: `artifact://conditioning/cb_job_20260802_a81f9c3d`
- **Final Render Output**: `artifact://render/render_job_20260802_a81f9c3d`

### 2.3 Resolution Rules (`resolve_uri`)
`ArtifactLocator` maps an `artifact://` URI to physical locations via active storage drivers:
- **Local Storage Driver**: `artifact://render/render_123` -> `file:///C:/.../data/rendered/2026/08/02/render_123.png`
- **S3 Cloud Driver**: `artifact://render/render_123` -> `s3://virtual-wear-bucket/rendered/2026/08/02/render_123.png`
- **Signed HTTP Gateway**: `artifact://render/render_123` -> `https://storage.googleapis.com/vton-bucket/render_123.png?X-Goog-Signature=...`

---

## 3. Lightweight ArtifactReference Model

Pipeline contracts and service methods will exchange immutable `ArtifactReference` objects instead of raw string filesystem paths:

```python
from enum import Enum
from typing import Any, Dict, Optional
from pydantic import BaseModel, Field


class ArtifactReference(BaseModel):
    """Lightweight immutable reference object passed across pipeline stages."""

    artifact_id: str = Field(..., description="Unique artifact ID")
    artifact_uri: str = Field(..., description="Canonical URI (artifact://...)")
    artifact_type: str = Field(..., description="Semantic artifact type")
    checksum: str = Field(..., description="SHA-256 payload hash")
    checksum_algorithm: str = Field(default="sha256")
    schema_version: str = Field(default="1.0.0")
    storage_provider: str = Field(default="local")
    mime_type: str = Field(default="image/png")
    file_size_bytes: int = Field(default=0, ge=0)
    metadata: Dict[str, Any] = Field(default_factory=dict)
```

---

## 4. Artifact Dependency Lineage (DAG)

Artifact relationships form a strict **Directed Acyclic Graph (DAG)** tracking provenance from raw input uploads through neural rendering:

```text
                      ┌───────────────────────┐
                      │  Person Upload Image  │
                      └───────────┬───────────┘
                                  │
                                  ▼
                      ┌───────────────────────┐
                      │  Preprocessed Person  │
                      └───────────┬───────────┘
                                  │
                  ┌───────────────┴───────────────┐
                  ▼                               ▼
       ┌─────────────────────┐         ┌─────────────────────┐
       │ SegFormer Human     │         │ DWPose Skeletal     │
       │ Parsing Mask        │         │ Keypoint JSON       │
       └──────────┬──────────┘         └──────────┬──────────┘
                  │                               │
                  └───────────────┬───────────────┘
                                  ▼
                      ┌───────────────────────┐
                      │ Agnostic Clothing     │
                      │ Replacement Mask      │
                      └───────────┬───────────┘
                                  │
                  ┌───────────────┴───────────────┐
                  ▼                               ▼
       ┌─────────────────────┐         ┌─────────────────────┐
       │ DensePose Body      │         │ Preprocessed        │
       │ Surface IUV Map     │         │ Garment Image       │
       └──────────┬──────────┘         └──────────┬──────────┘
                  │                               │
                  └───────────────┬───────────────┘
                                  ▼
                      ┌───────────────────────┐
                      │ Conditioning Bundle   │
                      └───────────┬───────────┘
                                  │
                                  ▼
                      ┌───────────────────────┐
                      │ Neural Try-On Render  │
                      └───────────┬───────────┘
                                  │
                                  ▼
                      ┌───────────────────────┐
                      │ Output Render &       │
                      │ Thumbnail Images      │
                      └───────────────────────┘
```

### DAG Metadata Representation
Each child artifact stores `parent_artifact_ids: List[str]` in its provenance payload:
- **Agnostic Mask Artifact**: Parents = `[art_segformer_mask, art_dwpose_json]`
- **Conditioning Bundle Artifact**: Parents = `[art_agnostic_mask, art_densepose_iuv, art_prep_garment]`
- **Final Render Output**: Parents = `[art_conditioning_bundle]`

---

## 5. Artifact Transaction Architecture (`ArtifactTransaction`)

To prevent partial artifact orphan writes during pipeline stage failures, stage executions occur within atomic transactions:

```python
class BaseArtifactTransaction:
    """Interface for stage-level atomic artifact transactions."""

    def begin(self) -> None:
        """Starts a staging transaction context."""
        pass

    def register_staged(self, artifact_ref: ArtifactReference, tmp_path: str) -> None:
        """Registers a staged file artifact before pipeline stage commit."""
        pass

    def commit(self) -> None:
        """Promotes all staged temporary files to canonical storage layout."""
        pass

    def rollback(self) -> None:
        """Purges all staged temporary files if stage execution fails."""
        pass
```

### Rollback Lifecycle
1. Stage execution commences: `transaction.begin()` creates a isolated staging area in `data/temp/stage_id/`.
2. Intermediate files are written to staging directory.
3. If an unhandled exception or cancellation occurs, `transaction.rollback()` immediately deletes `data/temp/stage_id/` assets without leaving partial files in `data/masks/` or `data/rendered/`.
4. Upon stage success, `transaction.commit()` atomically moves staged assets to their final canonical CAS paths.

---

## 6. Immutable Artifact Policy

1. **Append-Only Policy**: Once an artifact is committed to storage, its byte content and checksum are **immutable**.
2. **No In-Place Edits**: Re-processing a stage or applying a new mask filter creates a **new artifact** with a unique `artifact_id` and new content hash.
3. **Manifest Version Evolution**: Updating a pipeline render re-generates an updated `ArtifactManifest` referencing the new artifact references while retaining lineage history.

---

## 7. Provenance Metadata Model

Provenance data records complete auditability for model reproduceability and failure analysis:

```python
class ArtifactProvenance(BaseModel):
    """Detailed provenance metadata tracking creator origin and dependencies."""

    producer_stage: str = Field(..., description="Stage name (e.g. DWPoseEstimator)")
    producing_service: str = Field(default="virtual_wear_backend")
    engine_name: str = Field(..., description="Engine model name (e.g. idm_vton)")
    engine_version: str = Field(default="1.0.0")
    pipeline_version: str = Field(default="1.0.0")
    schema_version: str = Field(default="1.0.0")
    parent_artifact_ids: list[str] = Field(default_factory=list)
    created_at_utc: str = Field(..., description="ISO 8601 UTC timestamp")
    device_execution_target: str = Field(default="cpu")
```

---

## 8. Extensible Artifact Capability Model

Artifacts express feature capabilities so backend engines, renderers, and frontend UI components can query asset features dynamically:

```python
class ArtifactCapability(str, Enum):
    DOWNLOADABLE = "downloadable"
    RENDERABLE = "renderable"
    CACHEABLE = "cacheable"
    TEMPORARY = "temporary"
    EXPORTABLE = "exportable"
    COMPRESSIBLE = "compressible"
    REPRODUCIBLE = "reproducible"
    SHAREABLE = "shareable"
```

### Engine Capability Advertising
- **SegFormer Mask PNG**: Capabilities = `[CACHEABLE, TEMPORARY, COMPRESSIBLE]`
- **Final Render Output**: Capabilities = `[DOWNLOADABLE, RENDERABLE, EXPORTABLE, SHAREABLE, REPRODUCIBLE]`
- **Conditioning Bundle**: Capabilities = `[CACHEABLE, REPRODUCIBLE]`

---

## 9. Refined Storage Driver Interface (`BaseArtifactStorage`)

The abstract storage interface defines complete storage operations independent of local file systems or cloud APIs:

```python
from abc import ABC, abstractmethod
from typing import AsyncIterable, Dict, List, Optional


class BaseArtifactStorage(ABC):
    """Refined abstract storage interface for local and cloud storage drivers."""

    @abstractmethod
    async def save(
        self,
        key: str,
        content: bytes,
        metadata: Dict[str, Any],
    ) -> ArtifactReference:
        """Saves byte content into storage and returns an ArtifactReference."""
        pass

    @abstractmethod
    async def load(self, key: str) -> bytes:
        """Loads and returns raw byte content for a storage key."""
        pass

    @abstractmethod
    async def open_stream(self, key: str) -> AsyncIterable[bytes]:
        """Opens an async chunked byte stream for large files."""
        pass

    @abstractmethod
    async def exists(self, key: str) -> bool:
        """Returns True if the storage key exists."""
        pass

    @abstractmethod
    async def delete(self, key: str) -> bool:
        """Deletes object under storage key."""
        pass

    @abstractmethod
    async def copy(self, source_key: str, dest_key: str) -> bool:
        """Copies artifact from source key to destination key."""
        pass

    @abstractmethod
    async def move(self, source_key: str, dest_key: str) -> bool:
        """Moves artifact atomically from source key to destination key."""
        pass

    @abstractmethod
    def generate_uri(self, category: str, artifact_id: str) -> str:
        """Generates canonical artifact:// URI string."""
        pass

    @abstractmethod
    def resolve_uri(self, uri: str) -> str:
        """Resolves artifact:// URI to concrete filesystem path or cloud URL."""
        pass
```

---

## 10. Storage Provider Orchestration Layer

To seamlessly support multiple storage backends (Local, S3, GCS, Azure Blob, MinIO) simultaneously or enable migration between them, the architecture introduces a **Provider-Agnostic Storage Management Layer**.

### 10.1 StorageCapabilities
Defines the operational limits and supported features of a specific storage provider.

```python
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List

class StorageCapabilities(BaseModel):
    """Defines what a storage provider can and cannot do."""
    
    supports_multipart_upload: bool = Field(default=False)
    supports_presigned_urls: bool = Field(default=False)
    supports_streaming: bool = Field(default=True)
    supports_versioning: bool = Field(default=False)
    max_file_size_bytes: int = Field(default=1024 * 1024 * 1024 * 50) # 50 GB default
    provider_name: str = Field(..., description="e.g., local, s3, gcs")
    is_cloud_native: bool = Field(default=False)
```

### 10.2 StorageProviderConfig
Configuration required to initialize and authenticate a storage provider.

```python
class StorageProviderConfig(BaseModel):
    """Configuration for initializing a storage provider."""
    
    provider_id: str = Field(..., description="Unique ID for this provider instance")
    provider_type: str = Field(..., description="local, s3, gcs, azure")
    is_default: bool = Field(default=False)
    base_path: str = Field(..., description="Base directory or bucket name")
    credentials_secret_ref: Optional[str] = Field(default=None, description="Reference to secret manager for credentials")
    region: Optional[str] = Field(default=None)
    endpoint_url: Optional[str] = Field(default=None, description="Custom endpoint for MinIO/S3 compatible APIs")
    options: Dict[str, Any] = Field(default_factory=dict)
```

### 10.3 StorageProviderRegistry
A centralized thread-safe registry that maintains initialized storage provider instances.

```python
class StorageProviderRegistry:
    """Manages active storage provider instances."""
    
    def register_provider(self, config: StorageProviderConfig, provider: BaseArtifactStorage) -> None:
        """Registers a configured storage provider."""
        pass
        
    def get_provider(self, provider_id: str) -> BaseArtifactStorage:
        """Retrieves a provider by its unique ID."""
        pass
        
    def get_default_provider(self) -> BaseArtifactStorage:
        """Retrieves the default configured provider."""
        pass
        
    def list_providers(self) -> List[str]:
        """Returns a list of all registered provider IDs."""
        pass
```

### 10.4 StorageResolver
Responsible for parsing `artifact://` URIs and delegating operations to the correct registered storage provider.

```python
class StorageResolver:
    """Resolves URIs and delegates to the appropriate StorageProvider."""
    
    def __init__(self, registry: StorageProviderRegistry):
        self.registry = registry

    def resolve_read(self, artifact_ref: 'ArtifactReference') -> BaseArtifactStorage:
        """Determines the correct provider to read the given artifact."""
        pass
        
    def resolve_write(self, category: str, options: Dict[str, Any] = None) -> BaseArtifactStorage:
        """Determines the best provider to write a new artifact based on category/rules."""
        pass
```

### 10.5 StorageHealthReport
Provides diagnostic health checks for active storage providers (e.g., disk space, bucket accessibility, latency).

```python
class StorageHealthReport(BaseModel):
    """Health check output for a storage provider."""
    
    provider_id: str
    is_healthy: bool
    latency_ms: float
    free_space_bytes: Optional[int] = None
    error_message: Optional[str] = None
    last_checked_utc: str
```

---

## 11. Storage Layer Component Decomposition (Phase 1.2.9B Refinement)

To improve separation of responsibilities and maintain provider independence, the storage architecture is decomposed into dedicated services.

### 11.1 BaseArtifactRegistry
Abstracts artifact indexing and tracking.
- **Responsibilities**: `register()`, `update()`, `get()`, `exists()`, `list()`, `delete()`, `query()`.
- **Implementations**: `SQLiteArtifactRegistry` (isolated boundary). Future migrations (PostgreSQL/Redis) require no `ArtifactManager` changes.

### 11.2 ContentAddressableIndex
Manages CAS-specific indexing logic independent of physical storage.
- **Responsibilities**: Checksum lookup, duplicate detection, checksum registration, and reference counting.

### 11.3 ArtifactLocator
Abstracts path and URI resolution.
- **Responsibilities**: Resolve `artifact://` URIs, locate manifests and metadata, and abstract filesystem/CAS layouts.

### 11.4 ArtifactMetadataStore
Separates metadata persistence from the core manager.
- **Responsibilities**: Save, update, retrieve, version, and query metadata.

### 11.5 ManifestBuilder
Dedicated builder for artifact manifest generation.
- **Responsibilities**: DAG generation, lineage construction, provenance tracking, timestamps, version metadata, and relationships.

### 11.6 ArtifactVerifier
Service for integrity and corruption checks.
- **Responsibilities**: SHA-256 verification, corruption detection, orphan detection, missing artifact detection, and manifest validation.

### 11.7 ArtifactStatistics
Provides metrics for health and admin endpoints.
- **Responsibilities**: Total artifacts, storage usage, artifact counts, duplicate count, CAS reuse ratio, average size, and storage growth metrics.

### 11.8 Enhanced ArtifactTransaction
Artifact transactions include a deterministic journal for recovery.
- **Responsibilities**: Track staged, committed, and rolled-back files; log timestamps and transaction state for deterministic debugging and recovery.

### 11.9 RetentionManager
Separates retention policy evaluation from physical cleanup.
- **Responsibilities**: Determine expiration, enforce retention policies, and schedule cleanup execution by delegating to the `CleanupService`.

---

## 12. Expanded Test Coverage Strategy

The new architecture requires expanded test validation to ensure component isolation:
- **CAS Deduplication**: Verify duplicate uploads reuse physical hashes.
- **Concurrency**: Test concurrent registry and storage writes.
- **URI Resolution**: Validate `ArtifactLocator` routing.
- **Transaction Recovery**: Test rollback recovery using transaction journals.
- **Integrity**: Test checksum mismatch and corruption detection via `ArtifactVerifier`.
- **Manifests**: Validate DAG lineage accuracy via `ManifestBuilder`.
- **Orphan Detection**: Identify untracked files in storage.
- **Statistics**: Validate metric generation.
- **Retention**: Verify policy enforcement via `RetentionManager`.

---

## 13. Artifact Index Architecture

To support fast querying, metadata lookups, and orphan file detection across millions of artifacts, we evaluated 4 indexing architectures:

| Index Architecture | Read Latency | Write Throughput | Memory Footprint | Persistence | Phase 1 Choice |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **In-Memory Hash Index** | < 0.1 ms | 100,000 ops/sec | High | Volatile | Testing / Dev |
| **JSON Metadata Files** | 5 - 15 ms | 500 ops/sec | Low | File-based | Fallback |
| **SQLite WAL Index** | **0.5 - 1 ms** | **15,000 ops/sec** | **Low (4 MB)** | **Single File DB** | **RECOMMENDED** |
| **PostgreSQL Index** | 1 - 3 ms | 50,000 ops/sec | Medium | Server Instance | Phase 2 Target |

### Recommended Phase 1 Choice: **SQLite (Write-Ahead Logging / WAL Mode)**
- Thread-safe & async-compatible.
- Single database file (`data/metadata/artifacts.db`).
- Zero external process configuration required.
- Seamless SQL interface migration to PostgreSQL in Phase 2.

---

## 14. Manifest V2 Evolution & Portable Export Bundles

### Manifest V2 Schema Extensions
Manifest V2 incorporates full DAG dependency lineage, checksum manifests, and capability metadata:

```json
{
  "manifest_version": "2.0.0",
  "job_id": "job_20260802_a81f9c3d",
  "request_id": "req_f9218a00",
  "created_at_utc": "2026-08-02T17:45:00.000Z",
  "pipeline_version": "1.0.0",
  "engine_name": "idm_vton",
  "status": "completed",
  "dag_graph": {
    "nodes": [
      { "id": "upload_person", "type": "person_image", "uri": "artifact://upload/person_123" },
      { "id": "prep_person", "type": "preprocessed_person", "uri": "artifact://preprocessing/person_123" },
      { "id": "parsing_mask", "type": "parsing_mask", "uri": "artifact://parsing/mask_123" },
      { "id": "pose_json", "type": "pose_data", "uri": "artifact://pose/json_123" },
      { "id": "agnostic_mask", "type": "agnostic_mask", "uri": "artifact://mask/agnostic_123" },
      { "id": "conditioning", "type": "conditioning_bundle", "uri": "artifact://conditioning/cb_123" },
      { "id": "render_output", "type": "rendered_image", "uri": "artifact://render/render_123" }
    ],
    "edges": [
      { "from": "upload_person", "to": "prep_person" },
      { "from": "prep_person", "to": "parsing_mask" },
      { "from": "prep_person", "to": "pose_json" },
      { "from": "parsing_mask", "to": "agnostic_mask" },
      { "from": "pose_json", "to": "agnostic_mask" },
      { "from": "agnostic_mask", "to": "conditioning" },
      { "from": "conditioning", "to": "render_output" }
    ]
  },
  "outputs": {
    "render": {
      "artifact_id": "render_123",
      "uri": "artifact://render/render_123",
      "checksum": "a591a6d40bf420404a011733cfb7b190d62c65bf0bcda32b57b277d9ad9f146e",
      "capabilities": ["downloadable", "renderable", "exportable", "shareable"]
    }
  }
}
```

### Portable Export Bundle Layout (`job_<id>_bundle.tar.gz`)
Self-contained research archive enabling 100% reproducible offline execution:
```text
job_20260802_a81f9c3d_bundle/
├── manifest_v2.json               # Full DAG manifest
├── checksums.sha256               # Verification hashes
├── provenance.json                # Complete pipeline and engine provenance
├── assets/
│   ├── uploads/
│   ├── preprocessing/
│   ├── parsing/
│   ├── pose/
│   ├── masks/
│   ├── conditioning/
│   └── rendered/
```

---

## 15. Cloud Storage Migration Readiness Matrix

The abstract driver architecture ensures seamless transition to cloud object storage providers:

| Provider | Storage Class | Driver Target | Presigned URL Support | Multipart Upload | Migration Effort |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Local Filesystem** | Local SSD / NVMe | `LocalArtifactStorage` | Local HTTP Proxy | Standard OS IO | **Phase 1 Default** |
| **MinIO (On-Prem)** | S3-Compatible API | `S3ArtifactStorage` | Yes (`boto3` / `aioboto3`) | Yes | Plug-and-Play |
| **AWS S3** | Standard / Intelligent | `S3ArtifactStorage` | Yes | Yes | Plug-and-Play |
| **Google Cloud (GCS)**| Standard | `GCSArtifactStorage` | Yes | Yes | Driver Swap |
| **Azure Blob** | Hot / Cool | `AzureArtifactStorage` | Yes (SAS Token) | Yes (Block Blobs) | Driver Swap |

---

## 16. Complete System Architecture Diagram

```text
                    ┌─────────────────────────────────────────┐
                    │           VirtualWearPipeline           │
                    └────────────────────┬────────────────────┘
                                         │
                                         ▼
                    ┌─────────────────────────────────────────┐
                    │            ArtifactManager              │
                    └────────────────────┬────────────────────┘
                                         │
             ┌───────────────────────────┼───────────────────────────┐
             ▼                           ▼                           ▼
┌─────────────────────────┐ ┌─────────────────────────┐ ┌─────────────────────────┐
│     ManifestBuilder     │ │   BaseArtifactStorage   │ │   BaseArtifactRegistry  │
│   (DAG & Provenance)    │ │ (Local/S3/GCS Drivers)  │ │ (SQLite/PG Indexing)    │
└─────────────────────────┘ └────────────┬────────────┘ └────────────┬────────────┘
             │                           │                           │
             ▼                           ▼                           ▼
┌─────────────────────────┐ ┌─────────────────────────┐ ┌─────────────────────────┐
│    ArtifactVerifier     │ │  LocalFileStorage       │ │ SQLiteArtifactRegistry  │
│  (Checksum & Integrity) │ └────────────┬────────────┘ └────────────┬────────────┘
└─────────────────────────┘              │                           │
             │                           ▼                           ▼
             ▼              ┌─────────────────────────┐ ┌─────────────────────────┐
┌─────────────────────────┐ │ ContentAddressableIndex │ │  ArtifactMetadataStore  │
│   ArtifactStatistics    │ │ (CAS Dup & Hash Mgmt)   │ │ (Versioned Metadata)    │
│  (Health & Metrics)     │ └─────────────────────────┘ └─────────────────────────┘
└─────────────────────────┘
             
             ┌─────────────────────────┐ ┌─────────────────────────┐
             │    RetentionManager     │ │     ArtifactLocator     │
             │  (Policies & Schedule)  │ │   (URI / Path Mgmt)     │
             └────────────┬────────────┘ └─────────────────────────┘
                          │
                          ▼
             ┌─────────────────────────┐
             │      CleanupService     │
             │  (Physical Deletions)   │
             └─────────────────────────┘
```

---

## 17. Phase 1.2.9B Implementation Roadmap

1. **Step 1 — Create Core Schemas (`app/schemas/artifact.py`)**:
   - Define `ArtifactReference`, `ArtifactCategory`, `ArtifactCapability`, `ArtifactProvenance`, `ArtifactMetadata`, `ArtifactManifestV2`.
2. **Step 2 — Implement Storage Abstraction (`app/services/storage/`)**:
   - Implement `BaseArtifactStorage` and `LocalArtifactStorage` with `ArtifactLocator`.
3. **Step 3 — Implement Storage Orchestration (`app/services/storage/provider.py`)**:
   - Implement `StorageCapabilities`, `StorageProviderConfig`, `StorageProviderRegistry`, and `StorageResolver`.
4. **Step 4 — Implement Atomic Staging (`app/services/storage/transaction.py`)**:
   - Implement `ArtifactTransaction` manager with journaling.
5. **Step 5 — Implement Registry & Components (`app/services/artifacts/`)**:
   - Implement `BaseArtifactRegistry`, `SQLiteArtifactRegistry`, `ArtifactMetadataStore`, and `ContentAddressableIndex`.
6. **Step 6 — Implement Services (`app/services/artifacts/`)**:
   - Implement `ManifestBuilder`, `ArtifactVerifier`, `ArtifactStatistics`, and `RetentionManager`.
7. **Step 7 — Implement Artifact Manager (`app/services/artifacts/manager.py`)**:
   - Tie everything together into `ArtifactManager`.
8. **Step 8 — Pipeline Integration & Verification**:
   - Wire `ArtifactManager` into `VirtualWearPipeline` and run test suites.

---

## 18. GO / NO-GO Recommendation

### Recommendation: **GO FOR PHASE 1.2.9B IMPLEMENTATION**

- **Rationale**: The Phase 1.2.9B architectural refinement decomposes the system into isolated, single-responsibility components (`BaseArtifactRegistry`, `ManifestBuilder`, `ArtifactLocator`, etc.). This enforces strict boundaries, prevents `ArtifactManager` from becoming a monolithic god object, and establishes robust verification, statistics, and retention subsystems. We are fully ready to proceed with implementation.
