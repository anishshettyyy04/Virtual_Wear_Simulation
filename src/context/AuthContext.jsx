import { useState } from 'react';
import { AuthContext } from './AuthContext';

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState({
    isAuthenticated: true,
    name: 'Demo Guest User',
    role: 'Creator',
  });

  const value = {
    user,
    setUser,
    isAuthenticated: user?.isAuthenticated || false,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};
