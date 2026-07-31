import { Info, CheckCircle, Shield, FileText, HardDrive, Sparkles } from 'lucide-react';
import { Card } from '@/components/ui/Card';
import { APP_CONFIG } from '@/constants/appConfig';

/**
 * Reusable UploadInfo component providing guidance, image specs, fitting tips,
 * and format requirements.
 */
export const UploadInfo = ({ className = '' }) => {
  return (
    <Card hover={false} className={`border border-slate-800 bg-slate-900/60 p-6 space-y-6 ${className}`}>
      {/* Title */}
      <div className="flex items-center gap-2 pb-3 border-b border-slate-800">
        <Info size={18} className="text-purple-400" />
        <h3 className="text-base font-bold text-white">Upload Guidelines & Specs</h3>
      </div>

      {/* Image Requirements List */}
      <div className="space-y-3">
        <h4 className="text-xs font-bold text-slate-200 uppercase tracking-wider flex items-center gap-1.5">
          <CheckCircle size={14} className="text-emerald-400" /> Image Requirements
        </h4>
        <ul className="space-y-2 text-xs text-slate-400">
          <li className="flex items-start gap-2 bg-slate-950/40 p-2 rounded-lg border border-slate-800/60">
            <span className="text-blue-400 font-bold">•</span>
            <span>Full-body or waist-up portrait photo in an upright standing posture.</span>
          </li>
          <li className="flex items-start gap-2 bg-slate-950/40 p-2 rounded-lg border border-slate-800/60">
            <span className="text-blue-400 font-bold">•</span>
            <span>Evenly lit photo with neutral background and minimal harsh shadows.</span>
          </li>
          <li className="flex items-start gap-2 bg-slate-950/40 p-2 rounded-lg border border-slate-800/60">
            <span className="text-blue-400 font-bold">•</span>
            <span>Garment images work best when photographed flat-lay or catalog style.</span>
          </li>
        </ul>
      </div>

      {/* Tips for AI Fitting */}
      <div className="space-y-2 pt-2 border-t border-slate-800/60">
        <h4 className="text-xs font-bold text-slate-200 uppercase tracking-wider flex items-center gap-1.5">
          <Shield size={14} className="text-amber-400" /> Tips for Best AI Fitting
        </h4>
        <p className="text-xs text-slate-400 leading-relaxed">
          Higher resolution inputs yield superior fabric texture rendering, pose keypoint accuracy, and seamless clothing alignment.
        </p>
      </div>

      {/* Specs Badges */}
      <div className="grid grid-cols-2 gap-3 pt-2 border-t border-slate-800/60 text-xs">
        <div className="bg-slate-950/80 p-3 rounded-xl border border-slate-800 flex flex-col justify-center">
          <span className="text-[11px] text-slate-400 flex items-center gap-1 mb-1 font-medium">
            <FileText size={12} className="text-blue-400" /> Formats
          </span>
          <span className="font-semibold text-slate-200 font-mono">PNG, JPG, WEBP</span>
        </div>
        <div className="bg-slate-950/80 p-3 rounded-xl border border-slate-800 flex flex-col justify-center">
          <span className="text-[11px] text-slate-400 flex items-center gap-1 mb-1 font-medium">
            <HardDrive size={12} className="text-purple-400" /> Max Size
          </span>
          <span className="font-semibold text-purple-400 font-mono">
            {APP_CONFIG.UPLOAD.MAX_FILE_SIZE_MB} MB
          </span>
        </div>
      </div>

      {/* Recommended Resolution Banner */}
      <div className="p-3 rounded-xl bg-indigo-950/40 border border-indigo-500/20 text-xs text-indigo-300 flex items-center gap-2.5">
        <Sparkles size={16} className="text-indigo-400 flex-shrink-0" />
        <span>Recommended resolution: 1080×1440 px or higher for optimal quality.</span>
      </div>
    </Card>
  );
};
