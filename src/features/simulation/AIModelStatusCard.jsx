import { Cpu, CheckCircle2, Activity } from 'lucide-react';
import { Card } from '@/components/ui/Card';

export const AIModelStatusCard = ({ status }) => {
  return (
    <Card hover={false} className="bg-slate-900/80 border border-slate-800 p-4">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 flex items-center justify-center">
            <Cpu size={20} />
          </div>
          <div>
            <h4 className="text-xs font-bold text-white flex items-center gap-1.5">
              <span>{status?.name || 'Diffusion Mesh Transformer'}</span>
              <CheckCircle2 size={14} className="text-emerald-400" />
            </h4>
            <p className="text-[11px] text-slate-400 font-mono">
              Status: Active • Latency: ~120ms
            </p>
          </div>
        </div>

        <div className="hidden sm:flex items-center gap-2 text-[11px] text-slate-400 bg-slate-950 px-3 py-1.5 rounded-lg border border-slate-800">
          <Activity size={14} className="text-indigo-400 animate-pulse" />
          <span>GPU Compute Allocation: 100%</span>
        </div>
      </div>
    </Card>
  );
};
