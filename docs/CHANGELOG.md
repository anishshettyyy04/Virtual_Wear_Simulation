# Changelog

All notable changes to this project will be documented in this file.

## [1.1.0] - 2026-07-30
### Added
- **Webcam Media Stream Hook (`useCamera.js`)**: Real-time video stream initialization, facing mode toggle, snapshot capture to File object, and permission handling.
- **Webcam Capture Modal (`WebcamCaptureModal.jsx`)**: Live video stream modal with snapshot preview, retake options, and avatar selection.
- **Upload Integration**: Added "Take Webcam Photo" trigger button to Upload studio page.

## [1.0.0] - 2026-07-30
### Added
- Production-grade frontend architecture initialized with React 19, Vite, Tailwind CSS v4, Axios, and ESLint flat config.
- Shared `MainLayout`, sticky `Navbar`, responsive `Footer`, and `MobileDrawer`.
- Route-level lazy loading for Home, Upload, Result, and 404 pages.
- `SimulationContext` state management for try-on parameters and results.
