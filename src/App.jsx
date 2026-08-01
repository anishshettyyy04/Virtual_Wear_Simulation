import { BrowserRouter } from 'react-router-dom';
import { ErrorBoundary } from '@/components/common/ErrorBoundary';
import { AuthProvider, SimulationProvider } from '@/context';
import { AppRoutes } from '@/routes/AppRoutes';


export default function App() {
  return (
    <ErrorBoundary>
      <AuthProvider>
        <SimulationProvider>
          <BrowserRouter>
            <AppRoutes />
          </BrowserRouter>
        </SimulationProvider>
      </AuthProvider>
    </ErrorBoundary>
  );
}
