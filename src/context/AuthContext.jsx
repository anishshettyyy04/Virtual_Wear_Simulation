import { useState, useEffect, useCallback, useMemo } from 'react';
import { authService } from '@/services/authService';
import { AuthContext } from './AuthContext';

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [token, setToken] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setErrorState] = useState(null);

  const setError = useCallback((err) => {
    if (!err) {
      setErrorState(null);
    } else if (typeof err === 'object') {
      setErrorState(err.message || JSON.stringify(err));
    } else {
      setErrorState(String(err));
    }
  }, []);

  // Restore persistent authentication session on application initialization
  useEffect(() => {
    let isMounted = true;

    const restoreSession = async () => {
      try {
        const storedToken = localStorage.getItem('auth_token');
        const storedUserJson = localStorage.getItem('auth_user');

        if (!storedToken || !storedUserJson) {
          if (isMounted) {
            setUser(null);
            setToken(null);
            setIsLoading(false);
          }
          return;
        }

        let parsedUser = null;
        try {
          parsedUser = JSON.parse(storedUserJson);
        } catch {
          // Bad JSON structure in localStorage
          localStorage.removeItem('auth_token');
          localStorage.removeItem('auth_user');
          if (isMounted) {
            setUser(null);
            setToken(null);
            setIsLoading(false);
          }
          return;
        }

        // Validate or restore session
        const validatedUser = await authService.getCurrentUser(storedToken);

        if (isMounted) {
          setToken(storedToken);
          setUser(validatedUser || parsedUser);
          setIsLoading(false);
        }
      } catch (err) {
        // Token expired or invalid
        localStorage.removeItem('auth_token');
        localStorage.removeItem('auth_user');
        if (isMounted) {
          setUser(null);
          setToken(null);
          setError(err.message || 'Session expired. Please log in again.');
          setIsLoading(false);
        }
      }
    };

    restoreSession();

    return () => {
      isMounted = false;
    };
  }, [setError]);

  // Clear auth error state
  const clearError = useCallback(() => {
    setError(null);
  }, [setError]);

  // Log out action
  const logout = useCallback(async () => {
    try {
      await authService.logout();
    } catch {
      // Ignore logout API failures
    } finally {
      localStorage.removeItem('auth_token');
      localStorage.removeItem('auth_user');
      setToken(null);
      setUser(null);
      setError(null);
    }
  }, [setError]);

  // Handle global 401 Unauthorized event
  useEffect(() => {
    const handleUnauthorized = () => {
      logout();
    };

    window.addEventListener('auth:unauthorized', handleUnauthorized);
    return () => {
      window.removeEventListener('auth:unauthorized', handleUnauthorized);
    };
  }, [logout]);

  // Log in action
  const login = useCallback(async (credentials) => {
    setIsLoading(true);
    setError(null);
    try {
      const result = await authService.login(credentials);
      if (result?.token && result?.user) {
        localStorage.setItem('auth_token', result.token);
        localStorage.setItem('auth_user', JSON.stringify(result.user));
        setToken(result.token);
        setUser(result.user);
        setIsLoading(false);
        return result;
      }
      throw new Error('Invalid authentication response from server.');
    } catch (err) {
      const errorMsg = typeof err === 'object' ? (err.message || 'Login failed. Please check your credentials.') : String(err);
      setError(errorMsg);
      setIsLoading(false);
      return null;
    }
  }, [setError]);

  // Register action
  const register = useCallback(async (userData) => {
    setIsLoading(true);
    setError(null);
    try {
      const result = await authService.register(userData);
      if (result?.token && result?.user) {
        localStorage.setItem('auth_token', result.token);
        localStorage.setItem('auth_user', JSON.stringify(result.user));
        setToken(result.token);
        setUser(result.user);
        setIsLoading(false);
        return result;
      }
      throw new Error('Registration failed to return valid user credentials.');
    } catch (err) {
      const errorMsg = typeof err === 'object' ? (err.message || 'Registration failed. Please try again.') : String(err);
      setError(errorMsg);
      setIsLoading(false);
      return null;
    }
  }, [setError]);

  const isAuthenticated = Boolean(token && user);

  const value = useMemo(
    () => ({
      user,
      token,
      isAuthenticated,
      isLoading,
      error,
      login,
      register,
      logout,
      clearError,
      setUser,
    }),
    [user, token, isAuthenticated, isLoading, error, login, register, logout, clearError]
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

export default AuthProvider;
