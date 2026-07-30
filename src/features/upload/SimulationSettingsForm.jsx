import { SlidersHorizontal, Shield } from 'lucide-react';
import { Card, CardHeader, CardBody } from '@/components/ui/Card';

export const SimulationSettingsForm = ({ settings, onChangeSettings }) => {
  const fitOptions = [
    { value: 'slim', label: 'Slim Fit' },
    { value: 'regular', label: 'Regular Fit' },
    { value: 'relaxed', label: 'Relaxed Fit' },
    { value: 'oversized', label: 'Oversized' },
  ];

  const poseOptions = [
    { value: 'auto_align', label: 'Auto Posture Align' },
    { value: 'strict_pose', label: 'Strict Skeleton Warp' },
    { value: 'full_body', label: 'Full Body Mesh' },
  ];

  const fabricOptions = [
    { value: 'light', label: 'Lightweight (Silk/Linen)' },
    { value: 'medium', label: 'Medium (Cotton/Polyester)' },
    { value: 'heavy', label: 'Heavyweight (Denim/Wool)' },
  ];

  return (
    <Card hover={false} className="bg-slate-900/50 border border-slate-800">
      <CardHeader className="flex items-center justify-between pb-3">
        <div className="flex items-center gap-2 text-white font-bold text-sm">
          <SlidersHorizontal size={18} className="text-indigo-400" />
          <span>Simulation Parameters</span>
        </div>
        <span className="text-[10px] px-2 py-0.5 rounded bg-indigo-500/10 text-indigo-400 font-mono">
          AI v2.0
        </span>
      </CardHeader>

      <CardBody className="space-y-4 text-xs">
        {/* Fit Profile Selector */}
        <div>
          <label className="block text-slate-300 font-semibold mb-1.5 uppercase tracking-wider text-[11px]">
            Fit Profile Tension
          </label>
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-2">
            {fitOptions.map((opt) => (
              <button
                key={opt.value}
                type="button"
                onClick={() => onChangeSettings({ FIT_TYPE: opt.value })}
                className={`py-2 px-3 rounded-xl border font-medium transition-all ${
                  settings.FIT_TYPE === opt.value
                    ? 'bg-indigo-600 border-indigo-500 text-white shadow-md'
                    : 'bg-slate-900 border-slate-800 text-slate-400 hover:text-white'
                }`}
              >
                {opt.label}
              </button>
            ))}
          </div>
        </div>

        {/* Pose Alignment Mode */}
        <div>
          <label className="block text-slate-300 font-semibold mb-1.5 uppercase tracking-wider text-[11px]">
            Neural Pose Alignment Mode
          </label>
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-2">
            {poseOptions.map((opt) => (
              <button
                key={opt.value}
                type="button"
                onClick={() => onChangeSettings({ POSE_MODE: opt.value })}
                className={`py-2 px-3 rounded-xl border text-left font-medium transition-all ${
                  settings.POSE_MODE === opt.value
                    ? 'bg-purple-600/20 border-purple-500 text-purple-300'
                    : 'bg-slate-900 border-slate-800 text-slate-400 hover:text-white'
                }`}
              >
                {opt.label}
              </button>
            ))}
          </div>
        </div>

        {/* Fabric Weight */}
        <div>
          <label className="block text-slate-300 font-semibold mb-1.5 uppercase tracking-wider text-[11px]">
            Fabric Weight & Stiffness Physics
          </label>
          <select
            value={settings.FABRIC_WEIGHT}
            onChange={(e) => onChangeSettings({ FABRIC_WEIGHT: e.target.value })}
            className="w-full bg-slate-900 border border-slate-800 text-slate-200 rounded-xl p-2.5 outline-none focus:border-indigo-500"
          >
            {fabricOptions.map((opt) => (
              <option key={opt.value} value={opt.value}>
                {opt.label}
              </option>
            ))}
          </select>
        </div>

        {/* Info Note */}
        <div className="pt-2 flex items-center gap-2 text-[11px] text-slate-400 bg-slate-950/60 p-2.5 rounded-xl border border-slate-800/80">
          <Shield size={14} className="text-emerald-400 shrink-0" />
          <span>Image data processed in ephemeral memory and discarded post-simulation.</span>
        </div>
      </CardBody>
    </Card>
  );
};
