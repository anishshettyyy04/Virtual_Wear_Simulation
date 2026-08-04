import { useAuth } from '@/hooks/useAuth';
import { LoadingFallback } from '@/components/common/LoadingFallback';

export const ProtectedRoute = ({ children }) => {
  const { isLoading } = useAuth();

  if (isLoading) {
    return <LoadingFallback message="Verifying session..." />;
  }

  // Allow guest access to Virtual Wear Try-On simulation flow
  return children;
};

export default ProtectedRoute;
