# Project Architecture & Design System

## System Overview
The **Virtual Wear Simulation** web application is structured with a feature-driven React 19 frontend and a modular FastAPI microservice backend.

```
src/
├── components/ (common wrappers, layout, reusable UI primitives)
├── constants/ (endpoints, application config, theme tokens)
├── context/ (SimulationContext for try-on state management)
├── features/
│   ├── home/ (Landing hero, capabilities, workflow)
│   ├── upload/ (Dropzone, GarmentSelector, WebcamCaptureModal)
│   ├── simulation/ (AIModelStatusCard, ModelLoader)
│   └── result/ (BeforeAfterSlider, FitSummaryCard, ActionToolbar)
├── hooks/ (useCamera, useImageUpload, useSimulation, useDebounce, useMediaQuery)
├── pages/ (Home, Upload, Result, NotFound)
├── routes/ (AppRoutes with React.lazy & Suspense)
└── services/ (Axios client, simulationService)
```

---

## Backend Job Subsystem Architecture (Phase 1.2.8)

The backend asynchronous job system provides non-blocking virtual try-on execution, progress tracking, and registration-driven cleanup while remaining abstract and future-ready for distributed scaling.

```
+------------------+         +------------------+         +--------------------+
|  REST API Route  | ------> |  JobLifecycle    | ------> |  BaseJobRegistry   |
| (JobSnapshot)    |         |  Transition      |         | (MemoryJobRegistry)|
+------------------+         +------------------+         +--------------------+
          |                           ^                             ^
          v                           |                             |
+------------------+         +------------------+                   |
|   BaseJobQueue   | ------> | BackgroundWorker | ------------------+
| (InMemoryQueue)  |         |  (WorkerState)   |
+------------------+         +------------------+
```

### Key Architectural Components

1. **BaseJobQueue Interface (`BaseJobQueue`)**:
   - Abstract contract (`put`, `get`, `size`, `empty`, `cancel`).
   - `InMemoryJobQueue` default implementation; ready for future `RedisJobQueue` or `RabbitMQQueue` replacement.

2. **Concurrency-Safe Job Registry (`BaseJobRegistry`)**:
   - Isolated state storage with `asyncio.Lock` protection for concurrent requests.
   - Default `MemoryJobRegistry` backend; extensible for `PostgreSQLJobRegistry` or `MongoJobRegistry`.

3. **WorkerState Lifecycle (`WorkerState`)**:
   - Formal state machine (`INITIALIZING`, `RUNNING`, `PAUSED`, `STOPPING`, `STOPPED`).
   - Configurable polling interval via `AI_WORKER_POLL_INTERVAL_MS`.
   - Graceful shutdown sequence ensuring in-flight completion and clean resource release.

4. **Immutable API Snapshots (`JobSnapshot`)**:
   - Internal `JobModel` objects are never exposed over REST API routes.
   - `JobSnapshot.from_job(job)` produces immutable snapshots for serialization.

5. **Centralized Job Lifecycle (`JobLifecycle`)**:
   - All state transitions pass through `JobLifecycle.transition()`.
   - Manages timestamps (`started_at`, `completed_at`), calculates stage progress using `PipelineProgressProfile`, and appends `JobEvent` log entries.

6. **Registration-Driven Cleanup (`JobCleanupService`)**:
   - Stages explicitly `register(job_id, path)` temporary input/intermediate files.
   - Completed output render files are preserved permanently; intermediate artifacts are pruned automatically upon retention expiry.

7. **Future Distributed Architecture Roadmap**:
   - **Queue**: Swap `InMemoryJobQueue` for Redis/RabbitMQ.
   - **Registry**: Swap `MemoryJobRegistry` for PostgreSQL/MongoDB/Redis.
   - **Workers**: Deploy `BackgroundWorker` instances across distributed Kubernetes pods without changing API controllers or pipeline adapters.
