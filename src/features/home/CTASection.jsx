import { useNavigate } from 'react-router-dom';
import { Sparkles, ArrowRight } from 'lucide-react';
import { Button } from '@/components/ui/Button';

export const CTASection = () => {
  const navigate = useNavigate();

  return (
    <section className="py-12">
      <div className="glass-panel rounded-3xl p-8 md:p-14 text-center border border-slate-800 bg-gradient-to-b from-slate-900/90 to-slate-950/90 relative overflow-hidden">
        <div className="max-w-2xl mx-auto space-y-4">
          <div className="w-12 h-12 rounded-2xl bg-indigo-600/20 text-indigo-400 flex items-center justify-center mx-auto mb-2 border border-indigo-500/30">
            <Sparkles size={24} />
          </div>
          <h2 className="text-3xl font-extrabold text-white">
            Ready to Try Virtual Apparel Simulation?
          </h2>
          <p className="text-sm text-slate-400">
            Upload your avatar and garment imagery to preview high-fidelity virtual try-on in seconds.
          </p>
          <div className="pt-4 flex items-center justify-center gap-4">
            <Button
              variant="gradient"
              size="lg"
              rightIcon={<ArrowRight size={18} />}
              onClick={() => navigate('/upload')}
            >
              Go to Upload Station
            </Button>
          </div>
        </div>
      </div>
    </section>
  );
};
