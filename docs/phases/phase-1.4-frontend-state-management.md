# Phase 1.4 — Frontend State Management & Application Integration

## Objective
Establish a centralized, predictable, and robust frontend state-management and application-integration layer for the AI Virtual Wear Simulation application. This phase delivers authentication state, session persistence, centralized API Bearer token integration, route protection, virtual try-on workflow state management with Object URL memory safety, and seamless layout integration without UI redesigns or breaking existing architectures.

---

## Authentication Architecture
Authentication is implemented via a single source of truth managed by `AuthContext` and `AuthProvider` (`src/context/AuthContext.jsx`).

- **State Model:**
  - `user`: Authenticated user object or `null`.
  - `token`: JWT authentication token string or `null`.
  - `isAuthenticated`: Derived boolean (`Boolean(token && user)`).
  - `isLoading`: Session initialization & loading flag.
  - `error`: User-facing auth error message or `null`.

- **Actions:**
  - `login(credentials)`: Authenticates user credentials via `authService`, sets token and user state, persists to `localStorage`, and returns user session.
  - `register(userData)`: Registers a new user account and initializes session.
  - `logout()`: Clears auth state, removes persistent storage, resets simulation state, and redirects user safely.
  - `clearError()`: Clears active error messages.

---

## Authentication Persistence
Session persistence is handled automatically upon application initialization:

1. When `AuthProvider` mounts, it inspects `localStorage` for `auth_token` and `auth_user`.
2. If token and user data are found, session validity is validated via `authService.getCurrentUser(token)`.
3. If valid, auth state is restored seamlessly.
4. If missing, invalid, or expired, persistent storage is cleared, user state resolves to unauthenticated (`null`), and `isLoading` sets to `false`.
5. Sensitive data (passwords, raw keys) is never stored in `localStorage` or printed to browser console logs.

---

## API Authentication Integration
The central Axios instance (`src/services/api.js`) provides automated request and response interception:

- **Bearer Token Attachment:** A request interceptor attaches `Authorization: Bearer <token>` dynamically to outgoing API requests if an `auth_token` is present.
- **Environment Configuration:** Supports both `VITE_API_BASE_URL` and `VITE_API_URL`.
- **401 Unauthorized Interception:** Global response interceptor dispatches a window event (`auth:unauthorized`) upon encountering 401 response codes, allowing `AuthContext` to handle session expiration without infinite redirect loops.

---

## Protected Routes
Route protection is enforced by `ProtectedRoute` (`src/routes/ProtectedRoute.jsx`):

- Unauthenticated access to protected routes (`/upload`, `/result`) redirects users to the home route (`/`).
- Respects `isLoading` auth initialization state, rendering `<LoadingFallback />` to prevent auth redirect flicker during page refreshes.
- Preserves intended target route using React Router location state (`state={{ from: location }}`).

---

## Simulation State Architecture
The virtual try-on simulation state is managed by `SimulationContext` (`src/context/SimulationContext.jsx`):

- **State Fields:**
  - `personImage`: `{ file, previewUrl }`
  - `garmentImage`: `{ file, previewUrl, id, title }`
  - `selectedGarment`: Selected garment metadata
  - `selectedCategory`: Selected apparel category (`'tops'`, `'bottoms'`, etc.)
  - `simulationStatus`: Workflow status enum (`'idle' | 'ready' | 'uploading' | 'processing' | 'completed' | 'failed'`)
  - `progress`: Process completion percentage (0–100)
  - `resultImage`: AI rendered try-on image URL
  - `simulationResult`: Processed simulation payload
  - `error`: Simulation error message or `null`

- **Object URL Memory Management:**
  - `blob:` Object URLs generated via `URL.createObjectURL()` are tracked in an internal reference set.
  - When images are replaced or removed, old Object URLs are automatically revoked via `URL.revokeObjectURL()`.
  - Resetting simulation state or unmounting `SimulationProvider` releases all active Object URLs to prevent browser memory leaks.

---

## Simulation Lifecycle
Workflow execution follows a strict status model:

$$\text{idle} \xrightarrow{\text{set images}} \text{ready} \xrightarrow{\text{start}} \text{uploading} \xrightarrow{\text{API processing}} \text{processing} \xrightarrow{\text{success}} \text{completed}$$

In case of error, the state transitions to `failed` and resets progress cleanly.

- **Validation:** Pre-simulation validation verifies image existence, file formats (PNG, JPG, WEBP), size thresholds (10MB max), and category selections before triggering API calls.

---

## Provider Architecture
Provider hierarchy in `src/App.jsx`:

```jsx
<ErrorBoundary>
  <BrowserRouter>
    <AuthProvider>
      <SimulationProvider>
        <AppRoutes />
      </SimulationProvider>
    </AuthProvider>
  </BrowserRouter>
</ErrorBoundary>
```

- Clean separation between Router, AuthContext, and SimulationContext.
- Prevents circular provider dependencies and duplicate router instances.

---

## Layout Integration
- **Navbar (`src/components/layout/Navbar.jsx`):** Integrated with `useAuth` and `useSimulation`. Displays user indicator and Sign Out action when authenticated.
- **MobileDrawer (`src/components/layout/MobileDrawer.jsx`):** Integrated with auth actions while maintaining focus trap, ESC key closing, and keyboard navigation.

---

## Error Handling
- User-facing human-readable errors for authentication and simulation failures.
- No raw stack traces displayed to users.
- Stale errors are cleared automatically before initiating new operations.

---

## Performance Considerations
- Stable context values wrapped in `useMemo` and `useCallback` to minimize unnecessary component re-renders.
- Object URLs released immediately upon image state mutations to ensure optimal browser memory consumption.

---

## Files Added
- `src/services/authService.js`
- `docs/phases/phase-1.4-frontend-state-management.md`

## Files Modified
- `src/constants/apiEndpoints.js`
- `src/services/api.js`
- `src/context/AuthContext.jsx`
- `src/context/SimulationContext.jsx`
- `src/routes/ProtectedRoute.jsx`
- `src/routes/AppRoutes.jsx`
- `src/App.jsx`
- `src/components/layout/Navbar.jsx`
- `src/components/layout/MobileDrawer.jsx`

---

## Verification Results
- **Authentication State:** Tested login, session restoration via `localStorage`, and logout.
- **Persistence:** Session restores correctly after page refresh.
- **Protected Routes:** Unauthorized access to `/upload` and `/result` redirects to `/` without redirect flicker.
- **Simulation Lifecycle:** Object URL creation and `URL.revokeObjectURL` cleanup verified.
- **Accessibility:** Keyboard tab navigation, ESC closing, focus trap in drawer verified.

---

## Known Limitations
- Real backend authorization service endpoints (`/auth/login`, `/auth/register`, `/auth/me`) revert to development fallback sessions when backend is offline or unintegrated.

---

## Deferred Phase 1.5 Work
- Full Virtual Try-On inference integration, mask generation pipeline, DensePose conditioning, and try-on results persistence deferred to Phase 1.5.

---

## Final Status
**PHASE 1.4 COMPLETE**
