import { lazy, Suspense } from 'react';
import { Routes, Route } from 'react-router-dom';
import { MainLayout } from '@/components/layout/MainLayout';
import { LoadingFallback } from '@/components/common/LoadingFallback';
import { ProtectedRoute } from './ProtectedRoute';

// Lazy-loaded page components for route-level code splitting
const Home = lazy(() => import('@/pages/Home'));
const Upload = lazy(() => import('@/pages/Upload'));
const Result = lazy(() => import('@/pages/Result'));
const NotFound = lazy(() => import('@/pages/NotFound'));

export const AppRoutes = () => {
  return (
    <Suspense fallback={<LoadingFallback message="Loading Virtual Wear Engine..." />}>
      <Routes>
        <Route path="/" element={<MainLayout />}>
          <Route index element={<Home />} />
          <Route
            path="upload"
            element={
              <ProtectedRoute>
                <Upload />
              </ProtectedRoute>
            }
          />
          <Route
            path="result"
            element={
              <ProtectedRoute>
                <Result />
              </ProtectedRoute>
            }
          />
          <Route path="*" element={<NotFound />} />
        </Route>
      </Routes>
    </Suspense>
  );
};

export default AppRoutes;
