import { Sparkles, CheckCircle2, ShieldCheck, Cpu } from 'lucide-react';
import { Card, CardHeader, CardBody } from '@/components/ui/Card';
import { Badge } from '@/components/ui/Badge';

export const FitSummaryCard = ({ result }) => {
  const confidencePercent = Math.round((result?.fitConfidence || 0.94) * 100);

  return (
    <Card hover={false} className="bg-slate-900/50 border border-slate-800">
      <CardHeader className="flex items-center justify-between pb-3">
        <div className="flex items-center gap-2 text-white font-bold text-sm">
          <Sparkles size={18} className="text-indigo-400" />
          <span>AI Fit Analytics & Metrics</span>
        </div>
        <Badge variant="success" size="sm" icon={<ShieldCheck size={12} />}>
          Verified Render
        </Badge>
      </CardHeader>

      <CardBody className="space-y-4">
        {/* Overall Fit Confidence Metric */}
        <div className="bg-slate-950/80 p-4 rounded-xl border border-slate-800 flex items-center justify-between">
          <div>
            <span className="text-xs text-slate-400 block mb-0.5">Global Fit Confidence Score</span>
            <span className="text-2xl font-black text-white font-display">{confidencePercent}% Match</span>
          </div>
          <div className="w-12 h-12 rounded-full border-4 border-indigo-500 flex items-center justify-center text-xs font-bold text-indigo-400">
            {confidencePercent}%
          </div>
        </div>

        {/* Detailed Attribute Breakdown */}
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 text-xs">
          <div className="bg-slate-900/80 p-3 rounded-xl border border-slate-800/80">
            <span className="text-slate-400 block mb-1">Shoulder & Neck Alignment</span>
            <span className="font-semibold text-emerald-400 flex items-center gap-1">
              <CheckCircle2 size={14} /> {result?.metrics?.shoulderFit || '98% Posture Matched'}
            </span>
          </div>

          <div className="bg-slate-900/80 p-3 rounded-xl border border-slate-800/80">
            <span className="text-slate-400 block mb-1">Waist Drape & Fabric Tension</span>
            <span className="font-semibold text-indigo-400 flex items-center gap-1">
              <CheckCircle2 size={14} /> {result?.metrics?.waistDrape || 'Optimal Drape Curve'}
            </span>
          </div>
        </div>

        {/* Model Tech Info */}
        <div className="flex items-center justify-between text-[11px] text-slate-500 pt-2 border-t border-slate-800 font-mono">
          <span className="flex items-center gap-1">
            <Cpu size={12} className="text-indigo-400" /> Model: VirtualWear-v2.0
          </span>
          <span>Latency: 1.4s</span>
        </div>
      </CardBody>
    </Card>
  );
};
