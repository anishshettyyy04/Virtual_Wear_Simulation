import { useNavigate } from 'react';
import { Sparkles, ArrowRight, ShieldCheck, Zap, Layers } from 'lucide-react';
import { Button } from '@/components/ui/Button';
import { Badge } from '@/components/ui/Badge';
import { APP_CONFIG } from '@/constants/appConfig';

export const HeroSection = () => {
  const navigate = useNavigate();

  return (
    <section className="relative overflow-hidden py-10 lg:py-16">
      {/* Background Radial Glow */}
      <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[550px] h-[320px] bg-blue-600/15 rounded-full blur-[120px] pointer-events-none -z-10 animate-pulse-glow" />

      <div className="text-center max-w-4xl mx-auto space-y-6">
        <Badge variant="primary" size="md" icon={<Sparkles size={14} />}>
          {APP_CONFIG.SLOGAN}
        </Badge>

        <h1 className="text-4xl sm:text-5xl lg:text-6xl font-black text-white tracking-tight leading-[1.15] font-display">
          AI Virtual Wear Simulation <br />
          <span className="text-gradient">Next-Gen Apparel Fitting</span>
        </h1>

        <p className="text-sm sm:text-base lg:text-lg text-slate-300 max-w-2xl mx-auto leading-relaxed">
          Create photorealistic 3D virtual apparel try-ons with AI pose alignment, drape analysis, and instant fit comparison metrics.
        </p>

        <div className="pt-4 flex flex-col sm:flex-row items-center justify-center gap-4">
          <Button
            variant="gradient"
            size="lg"
            rightIcon={<ArrowRight size={20} />}
            onClick={() => navigate('/upload')}
          >
            Get Started
          </Button>

          <Button
            variant="secondary"
            size="lg"
            onClick={() => {
              const el = document.getElementById('workflow-section');
              el?.scrollIntoView({ behavior: 'smooth' });
            }}
          >
            Explore Workflow
          </Button>
        </div>

        {/* Feature Highlights */}
        <div className="pt-8 grid grid-cols-2 md:grid-cols-4 gap-3 text-xs font-semibold text-slate-400 max-w-3xl mx-auto">
          <div className="glass-card p-3 rounded-xl flex items-center justify-center gap-2">
            <Zap size={16} className="text-amber-400" />
            <span>Fast Rendering</span>
          </div>
          <div className="glass-card p-3 rounded-xl flex items-center justify-center gap-2">
            <ShieldCheck size={16} className="text-emerald-400" />
            <span>Secure & Private</span>
          </div>
          <div className="glass-card p-3 rounded-xl flex items-center justify-center gap-2">
            <Layers size={16} className="text-blue-400" />
            <span>Pose Alignment</span>
          </div>
          <div className="glass-card p-3 rounded-xl flex items-center justify-center gap-2">
            <Sparkles size={16} className="text-purple-400" />
            <span>Fabric Physics</span>
          </div>
        </div>
      </div>
    </section>
  );
};
