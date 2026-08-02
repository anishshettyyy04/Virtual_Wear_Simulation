import api from './api';
import { API_ENDPOINTS } from '@/constants/apiEndpoints';

export const authService = {
  /**
   * Log in user with credentials.
   * @param {{ email?: string; username?: string; password?: string }} credentials
   * @returns {Promise<{ user: object; token: string }>}
   */
  async login(credentials) {
    const isMock = import.meta.env.VITE_ENABLE_AUTH_MOCK === 'true';

    if (isMock) {
      await new Promise((resolve) => setTimeout(resolve, 600));
      const mockUser = {
        id: 'usr_demo_123',
        name: credentials.email ? credentials.email.split('@')[0] : 'Demo User',
        email: credentials.email || 'demo@virtualwear.ai',
        role: 'Creator',
      };
      const mockToken = 'mock_jwt_token_' + Date.now();
      return { user: mockUser, token: mockToken };
    }

    try {
      const response = await api.post(API_ENDPOINTS.AUTH.LOGIN, credentials);
      const data = response.data;
      return {
        user: data.user || data.data?.user || data,
        token: data.token || data.access_token || data.data?.token,
      };
    } catch (error) {
      // Fallback for development if backend auth endpoints are not live yet
      if (import.meta.env.DEV && (!error.status || error.status === 404)) {
        const fallbackUser = {
          id: 'usr_fallback_' + Date.now(),
          name: credentials.email ? credentials.email.split('@')[0] : 'Guest User',
          email: credentials.email || 'guest@virtualwear.ai',
          role: 'Creator',
        };
        const fallbackToken = 'fallback_jwt_token_' + Date.now();
        return { user: fallbackUser, token: fallbackToken };
      }
      throw error;
    }
  },

  /**
   * Register new user account.
   * @param {{ name?: string; email?: string; password?: string }} userData
   * @returns {Promise<{ user: object; token: string }>}
   */
  async register(userData) {
    const isMock = import.meta.env.VITE_ENABLE_AUTH_MOCK === 'true';

    if (isMock) {
      await new Promise((resolve) => setTimeout(resolve, 600));
      const mockUser = {
        id: 'usr_reg_' + Date.now(),
        name: userData.name || 'New User',
        email: userData.email || 'newuser@virtualwear.ai',
        role: 'Creator',
      };
      const mockToken = 'mock_jwt_token_' + Date.now();
      return { user: mockUser, token: mockToken };
    }

    try {
      const response = await api.post(API_ENDPOINTS.AUTH.REGISTER, userData);
      const data = response.data;
      return {
        user: data.user || data.data?.user || data,
        token: data.token || data.access_token || data.data?.token,
      };
    } catch (error) {
      if (import.meta.env.DEV && (!error.status || error.status === 404)) {
        const fallbackUser = {
          id: 'usr_reg_' + Date.now(),
          name: userData.name || 'Registered User',
          email: userData.email || 'user@virtualwear.ai',
          role: 'Creator',
        };
        const fallbackToken = 'fallback_jwt_token_' + Date.now();
        return { user: fallbackUser, token: fallbackToken };
      }
      throw error;
    }
  },

  /**
   * Validate current session token & get user profile.
   * @param {string} token
   * @returns {Promise<object>}
   */
  async getCurrentUser(token) {
    if (!token) return null;

    // Handle mock or fallback tokens in dev mode
    if (token.startsWith('mock_jwt_') || token.startsWith('fallback_jwt_')) {
      return {
        id: 'usr_restored_123',
        name: 'Restored User',
        email: 'user@virtualwear.ai',
        role: 'Creator',
      };
    }

    try {
      const response = await api.get(API_ENDPOINTS.AUTH.ME, {
        headers: { Authorization: `Bearer ${token}` },
      });
      return response.data?.user || response.data;
    } catch (error) {
      if (import.meta.env.DEV && (!error.status || error.status === 404)) {
        return {
          id: 'usr_restored_123',
          name: 'Restored User',
          email: 'user@virtualwear.ai',
          role: 'Creator',
        };
      }
      throw error;
    }
  },

  /**
   * Log out user session remotely.
   */
  async logout() {
    try {
      await api.post(API_ENDPOINTS.AUTH.LOGOUT);
    } catch {
      // Ignore remote logout failure
    }
  },
};

export default authService;
