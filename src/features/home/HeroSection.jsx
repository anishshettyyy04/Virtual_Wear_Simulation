import { useNavigate } from 'react';
import { Sparkles, ArrowRight, ShieldCheck, Zap, Layers } from 'lucide-react';
import { Button } from '@/components/ui/Button';
import { Badge } from '@/components/ui/Badge';

export const HeroSection = () => {
  const navigate = useNavigate();

  return (
    <section className="relative overflow-hidden py-12 lg:py-20">
      {/* Glow effect background */}
      <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[600px] h-[350px] bg-indigo-600/20 rounded-full blur-[120px] pointer-events-none -z-10 animate-pulse-glow" />

      <div className="text-center max-w-4xl mx-auto space-y-6">
        <Badge variant="primary" size="md" icon={<Sparkles size={14} />}>
          Next-Gen AI Apparel Engine v2.0
        </Badge>

        <h1 className="text-4xl sm:text-6xl font-black text-white tracking-tight leading-[1.15] font-display">
          Experience Apparel Virtually with <br />
          <span className="text-gradient">AI-Powered Wear Simulation</span>
        </h1>

        <p className="text-base sm:text-xl text-slate-300 max-w-2xl mx-auto leading-relaxed">
          Upload any person avatar and garment design to experience instant, photorealistic 3D virtual try-on with posture alignment and drape analysis.
        </p>

        <div className="pt-4 flex flex-col sm:flex-row items-center justify-center gap-4">
          <Button
            variant="gradient"
            size="lg"
            rightIcon={<ArrowRight size={20} />}
            onClick={() => navigate('/upload')}
          >
            Start Virtual Simulation
          </Button>

          <Button
            variant="secondary"
            size="lg"
            onClick={() => {
              const el = document.getElementById('workflow-section');
              el?.scrollIntoView({ behavior: 'smooth' });
            }}
          >
            How It Works
          </Button>
        </div>

        {/* Feature Pill Highlights */}
        <div className="pt-10 grid grid-cols-2 md:grid-cols-4 gap-4 text-xs font-semibold text-slate-400 max-w-3xl mx-auto">
          <div className="glass-card p-3 rounded-xl flex items-center justify-center gap-2">
            <Zap size={16} className="text-amber-400" />
            <span>Sub-Second Render</span>
          </div>
          <div className="glass-card p-3 rounded-xl flex items-center justify-center gap-2">
            <ShieldCheck size={16} className="text-emerald-400" />
            <span>Privacy Compliant</span>
          </div>
          <div className="glass-card p-3 rounded-xl flex items-center justify-center gap-2">
            <Layers size={16} className="text-indigo-400" />
            <span>Posture Alignment</span>
          </div>
          <div className="glass-card p-3 rounded-xl flex items-center justify-center gap-2">
            <Sparkles size={16} className="text-pink-400" />
            <span>Fabric Physics</span>
          </div>
        </div>
      </div>
    </section>
  );
};
