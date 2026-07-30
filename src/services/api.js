import axios from 'axios';
import { parseApiError } from '@/utils/apiErrorParser';

const baseURL = import.meta.env.VITE_API_URL || 'http://localhost:5000/api';
const timeout = Number(import.meta.env.VITE_API_TIMEOUT) || 15000;

export const api = axios.create({
  baseURL,
  timeout,
  headers: {
    'Content-Type': 'application/json',
    Accept: 'application/json',
  },
});

// Request Interceptor: attach authorization tokens or dynamic request headers
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('auth_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response Interceptor: parse backend error payloads consistently
api.interceptors.response.use(
  (response) => response,
  (error) => {
    const parsedError = parseApiError(error);
    return Promise.reject(parsedError);
  }
);

export default api;
