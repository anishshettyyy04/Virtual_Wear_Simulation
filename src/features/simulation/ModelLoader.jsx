import { Sparkles } from 'lucide-react';
import { Loader } from '@/components/ui/Loader';

export const ModelLoader = ({
  stepText = 'Processing 3D Garment Deformation & Pose Fit...',
}) => {
  return (
    <div className="glass-panel rounded-3xl p-12 text-center border border-indigo-500/30 flex flex-col items-center justify-center min-h-[400px]">
      <div className="w-16 h-16 rounded-2xl bg-indigo-600/20 text-indigo-400 border border-indigo-500/40 flex items-center justify-center mb-6 animate-bounce">
        <Sparkles size={32} />
      </div>
      <h3 className="text-xl font-extrabold text-white mb-2 font-display">
        AI Neural Engine Simulation Active
      </h3>
      <p className="text-xs text-slate-400 max-w-sm mb-8">{stepText}</p>
      <Loader size="lg" text="Deforming Garment Mesh to Body Pose..." />
    </div>
  );
};
