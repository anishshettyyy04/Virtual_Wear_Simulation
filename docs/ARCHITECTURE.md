# Project Architecture & Design System

## System Overview
The **Virtual Wear Simulation** web application is structured with a feature-driven React 19 architecture:

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

## Camera Architecture (Phase 1.1)
- Uses `navigator.mediaDevices.getUserMedia` WebRTC API.
- Live stream bound to HTML5 `<video>` element with hardware acceleration.
- Snapshot rendered onto HTML5 `<canvas>` element and exported via `.toDataURL('image/jpeg')`.
- Converted into `File` object compatible with multipart FormData upload.
