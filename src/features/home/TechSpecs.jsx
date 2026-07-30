import { Cpu, Zap, Eye, Database } from 'lucide-react';
import { Card } from '@/components/ui/Card';

export const TechSpecs = () => {
  return (
    <section className="py-12 border-t border-slate-900">
      <div className="glass-panel rounded-3xl p-8 lg:p-12 border border-indigo-500/20 relative overflow-hidden">
        <div className="max-w-3xl">
          <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-semibold bg-indigo-500/10 text-indigo-400 border border-indigo-500/20 mb-4">
            <Cpu size={14} /> AI Architecture Preparedness
          </span>
          <h2 className="text-2xl md:text-4xl font-extrabold text-white mb-4">
            Designed for Real-Time & Offline Model Inference
          </h2>
          <p className="text-sm text-slate-300 leading-relaxed mb-8">
            The frontend layout is architected to seamlessly integrate with TensorFlow.js, WebGL shader pipelines, OpenCV landmark detection, or remote PyTorch diffusion API servers.
          </p>

          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
            <Card hover={false} className="bg-slate-900/80 p-4 rounded-xl border border-slate-800">
              <div className="flex items-center gap-2 text-indigo-400 font-bold text-sm mb-1">
                <Zap size={16} /> WebGL Shaders
              </div>
              <p className="text-[11px] text-slate-400">GPU accelerated texture mapping and deformation.</p>
            </Card>

            <Card hover={false} className="bg-slate-900/80 p-4 rounded-xl border border-slate-800">
              <div className="flex items-center gap-2 text-purple-400 font-bold text-sm mb-1">
                <Eye size={16} /> Pose Landmark Detection
              </div>
              <p className="text-[11px] text-slate-400">33-keypoint human posture alignment.</p>
            </Card>

            <Card hover={false} className="bg-slate-900/80 p-4 rounded-xl border border-slate-800">
              <div className="flex items-center gap-2 text-emerald-400 font-bold text-sm mb-1">
                <Database size={16} /> Python / PHP Ready
              </div>
              <p className="text-[11px] text-slate-400">Axios API service layer ready for REST/gRPC endpoints.</p>
            </Card>
          </div>
        </div>
      </div>
    </section>
  );
};
