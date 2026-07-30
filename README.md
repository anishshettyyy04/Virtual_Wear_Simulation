# AI Virtual Wear Simulation – Frontend Foundation

A modern, scalable, production-ready frontend architecture for the **AI Virtual Wear Simulation** web application built with **React 19**, **Vite**, **Tailwind CSS v4**, **React Router DOM**, **Axios**, and **Lucide React**.

---

## 🌟 Key Features

- **Feature-Based Scalable Architecture**: Clean modular directory structure designed for team collaboration.
- **Route-Level Code Splitting**: Optimized performance with `React.lazy` and `Suspense`.
- **Axios API Layer**: Pre-configured HTTP client with base URL environment resolution, request authorization interceptors, and standardized error parsing (`parseApiError`).
- **Interactive Try-On Simulation Studio**: Drag-and-drop image upload dropzone with client-side format and size validation.
- **Before/After Split Visualizer**: Interactive slider comparing original avatar image with simulated try-on output.
- **AI Fit Analytics**: Real-time confidence metrics on shoulder alignment, waist drape, and fabric tension.
- **Future AI Integration Readiness**: Architecture built to connect seamlessly with Python/PyTorch diffusion microservices, WebGL shaders, or TensorFlow.js pose estimation models.
- **Accessibility & UX**: Keyboard navigation, ARIA dialog accessibility, glassmorphic dark mode palette, and mobile-responsive drawer navigation.

---

## 🚀 Tech Stack

| Technology | Purpose |
| :--- | :--- |
| **React 19** | Core UI Library (Functional Components & Custom Hooks) |
| **Vite 6** | Next-Generation Build Tool & Dev Server |
| **Tailwind CSS v4** | `@tailwindcss/vite` Utility-First Styling Engine |
| **React Router DOM 7** | Client-side routing with Shared Layout & Code-Splitting |
| **Axios** | HTTP Client for REST API requests |
| **Lucide React** | Modern Iconography |
| **ESLint + Prettier** | Code Quality & Automated Formatting |

---

## 📁 Project Folder Structure

```
Virtual_Wear_Simulation/
├── public/
│   └── favicon.svg
├── src/
│   ├── assets/
│   │   ├── fonts/
│   │   ├── icons/
│   │   └── images/
│   ├── components/
│   │   ├── common/              # Global utility wrappers (ErrorBoundary, SEO, LoadingFallback)
│   │   ├── layout/              # Navbar, Footer, MainLayout, MobileDrawer
│   │   └── ui/                  # Reusable primitives (Button, Card, Input, Modal, Loader, Badge, EmptyState, ErrorMessage, SectionTitle)
│   ├── constants/               # API endpoints, APP CONFIG, Theme design tokens
│   ├── context/                 # SimulationContext (Try-On state), AuthContext
│   ├── features/
│   │   ├── home/                # HeroSection, FeatureGrid, WorkflowSteps, TechSpecs, CTASection
│   │   ├── upload/              # Dropzone, ImagePreviewCard, GarmentSelector, SimulationSettingsForm
│   │   ├── simulation/          # AIModelStatusCard, ModelLoader
│   │   └── result/              # BeforeAfterSlider, FitSummaryCard, ActionToolbar, DownloadShareModal
│   ├── hooks/                   # Custom hooks (useImageUpload, useSimulation, useMediaQuery, useDebounce)
│   ├── pages/                   # Home, Upload, Result, NotFound
│   ├── routes/                  # AppRoutes (Lazy Loaded), ProtectedRoute
│   ├── services/                # api.js (Axios instance), simulationService.js, apiError.js
│   ├── styles/                  # index.css (Tailwind v4 tokens & glassmorphism), custom.css
│   ├── utils/                   # imageValidation, fileHelpers, dateHelpers, apiErrorParser
│   ├── App.jsx
│   └── main.jsx
├── .env.example
├── .env
├── .gitignore
├── .prettierignore
├── .prettierrc
├── eslint.config.js
├── index.html
├── package.json
├── README.md
└── vite.config.js
```

---

## ⚡ Quick Start & Installation

### Prerequisites
- **Node.js**: v18.0.0 or higher
- **npm**: v9.0.0 or higher

### 1. Clone & Install Dependencies

```bash
# Navigate to workspace directory
cd Virtual_Wear_Simulation

# Install npm packages
npm install
```

### 2. Configure Environment Variables

Copy `.env.example` to `.env`:

```bash
cp .env.example .env
```

Ensure `VITE_API_URL` points to your active backend API server:

```env
VITE_API_URL=http://localhost:5000/api
VITE_API_TIMEOUT=15000
VITE_ENABLE_AI_SIMULATION_MOCK=true
```

### 3. Run Development Server

```bash
npm run dev
```

Open [http://localhost:5173](http://localhost:5173) in your browser.

---

## 🛠 Available NPM Scripts

- `npm run dev`: Launch Vite HMR development server.
- `npm run build`: Compile production-ready bundle.
- `npm run preview`: Serve built production static assets locally.
- `npm run lint`: Run ESLint analysis across codebase.
- `npm run format`: Format source files using Prettier.

---

## 🌐 API Layer & Axios Setup

The API service layer is centralized in `src/services/api.js`:

```javascript
import axios from 'axios';

export const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:5000/api',
  timeout: 15000,
});
```

All requests automatically pass through interceptors that inject Bearer auth headers (when present) and parse backend error responses into standardized client-friendly error objects.

---

## 🔮 Future AI Integration Preparedness

The frontend architecture is specifically structured to support upcoming AI extensions:

1. **Webcam Capture & Live Try-On**: Context & hooks are ready to plug in MediaStream streams.
2. **Pose Landmark Estimation**: Pose alignment dropdown and metrics cards ready for TensorFlow.js MediaPipe keypoints.
3. **Diffusion Model Monitoring**: Model status card & polling hooks built-in for tracking remote GPU inferencing jobs.
