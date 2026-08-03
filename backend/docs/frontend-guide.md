# Frontend Developer Integration Guide — React Frontend

Welcome to the frontend integration guide for the **AI Virtual Wear Simulation** project! This guide is prepared specifically for **Ashwin** to enable seamless integration between the React Frontend and the Python FastAPI Backend.

---

## 1. Backend Server Configuration

- **Base URL**: `http://localhost:8000` (Local Dev) / `http://backend:8000` (Docker)
- **API Version**: `v1` (`/api/v1/`)
- **Interactive Swagger Docs**: `http://localhost:8000/docs`
- **ReDoc Technical Docs**: `http://localhost:8000/redoc`

---

## 2. Standardized API Response Envelope

Every endpoint returns JSON wrapped inside a standard `BaseResponse` envelope:

```typescript
export interface BaseResponse<T> {
  success: boolean;
  message: string;
  data: T;
  timestamp: string;
  requestId: string;
}
```

---

## 3. Recommended Axios Instance Setup

Create a centralized Axios instance in your React project (`src/api/client.ts`):

```typescript
import axios from 'axios';

export const apiClient = axios.create({
  baseURL: process.env.REACT_APP_API_BASE_URL || 'http://localhost:8000',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Response interceptor for automatic data unwrapping & request tracking logging
apiClient.interceptors.response.use(
  (response) => response.data,
  (error) => {
    const errorEnvelope = error.response?.data || {
      success: false,
      message: 'Network error or backend unreachable',
      data: null,
      timestamp: new Date().toISOString(),
      requestId: null,
    };
    return Promise.reject(errorEnvelope);
  }
);
```

---

## 4. Endpoint Reference Catalog

### A. Products Catalog API

#### `GET /api/v1/products`
Fetch apparel catalog with optional filtering.

- **Query Parameters**:
  - `category` (optional, string): e.g. `"tshirt"`, `"jeans"`, `"jacket"`, `"shirt"`
  - `gender` (optional, string): e.g. `"men"`, `"women"`, `"unisex"`
- **Example Call**: `apiClient.get('/api/v1/products?category=tshirt')`

#### `GET /api/v1/products/{productId}`
Fetch a single product by ID.

- **Example Call**: `apiClient.get('/api/v1/products/TS001')`

---

### B. User Preferences API

#### `GET /api/v1/users/{userId}`
Fetch user preference profile and body metrics.

- **Example Call**: `apiClient.get('/api/v1/users/USR001')`

---

### C. Recommendation Engine API

#### `POST /api/v1/recommendations`
Generate personalized product recommendations.

- **Request Payload**:
  ```json
  {
    "userId": "USR001",
    "limit": 10,
    "forceRefresh": false
  }
  ```
- **Example Call**: `apiClient.post('/api/v1/recommendations', { userId: 'USR001', limit: 10 })`

---

### D. System Health & Metrics API

#### `GET /api/v1/health`
Check backend subsystem operational readiness.

#### `GET /api/v1/metrics`
Retrieve recommendation benchmark statistics and category analytics.

---

## 5. React Integration Tips (TanStack Query / SWR Example)

```typescript
import { useQuery } from '@tanstack/react-query';
import { apiClient } from '../api/client';

export const useRecommendations = (userId: string) => {
  return useQuery({
    queryKey: ['recommendations', userId],
    queryFn: () => apiClient.post('/api/v1/recommendations', { userId, limit: 10 }),
    enabled: Boolean(userId),
  });
};
```

---

## 6. Authentication Placeholder

Currently endpoints do not enforce bearer tokens. Authentication headers can be attached to `apiClient`:

```typescript
apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem('auth_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});
```
