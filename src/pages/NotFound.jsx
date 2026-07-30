import { useNavigate } from 'react';
import { Home, AlertTriangle } from 'lucide-react';
import { SEO } from '@/components/common/SEO';
import { Button } from '@/components/ui/Button';

export default function NotFound() {
  const navigate = useNavigate();

  return (
    <div className="min-h-[60vh] flex flex-col items-center justify-center text-center p-8">
      <SEO title="404 - Page Not Found" />
      <div className="w-16 h-16 rounded-2xl bg-amber-500/10 text-amber-400 border border-amber-500/20 flex items-center justify-center mb-6">
        <AlertTriangle size={32} />
      </div>
      <h1 className="text-4xl font-extrabold text-white mb-2 font-display">404 - Page Not Found</h1>
      <p className="text-sm text-slate-400 max-w-sm mb-6">
        The route you are trying to access does not exist or has been moved.
      </p>
      <Button variant="primary" size="md" leftIcon={<Home size={18} />} onClick={() => navigate('/')}>
        Back to Home
      </Button>
    </div>
  );
}
