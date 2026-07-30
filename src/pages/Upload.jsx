import { useState } from 'react';
import { useNavigate } from 'react';
import { Upload as UploadIcon, Image as ImageIcon, Info, CheckCircle, FileText, ArrowRight, Shield, RefreshCw } from 'lucide-react';
import { SEO } from '@/components/common/SEO';
import { SectionTitle } from '@/components/ui/SectionTitle';
import { Button } from '@/components/ui/Button';
import { Card } from '@/components/ui/Card';
import { Badge } from '@/components/ui/Badge';
import { APP_CONFIG } from '@/constants/appConfig';

export default function Upload() {
  const navigate = useNavigate();
  const [isDragOver, setIsDragOver] = useState(false);

  return (
    <div className="space-y-8 max-w-6xl mx-auto">
      <SEO
        title="Upload Image"
        description="Upload your target avatar image for Virtual Wear AI simulation."
      />

      <SectionTitle
        badge="Upload Station"
        title="Upload Image Interface"
        subtitle="Frontend upload UI for selecting model avatars and garment photos for virtual fitting."
      />

      {/* Main 2-Panel Layout */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
        
        {/* LEFT PANEL: Upload Area */}
        <div className="lg:col-span-7 space-y-6">
          <Card hover={false} className="border border-slate-800 bg-slate-900/60 p-6 space-y-6">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <div className="w-8 h-8 rounded-lg bg-blue-600/20 text-blue-400 flex items-center justify-center font-bold">
                  <UploadIcon size={18} />
                </div>
                <h3 className="text-base font-bold text-white">Large Upload Area</h3>
              </div>
              <Badge variant="primary" size="sm">
                UI Mockup Only
              </Badge>
            </div>

            {/* Drag & Drop Upload Zone */}
            <div
              className={`relative border-2 border-dashed rounded-2xl p-8 flex flex-col items-center justify-center text-center transition-all duration-200 ${
                isDragOver
                  ? 'border-blue-500 bg-blue-500/10 scale-[0.99]'
                  : 'border-slate-800 hover:border-blue-500/50 bg-slate-950/60'
              }`}
              onDragOver={(e) => {
                e.preventDefault();
                setIsDragOver(true);
              }}
              onDragLeave={() => setIsDragOver(false)}
              onDrop={(e) => {
                e.preventDefault();
                setIsDragOver(false);
              }}
            >
              {/* Placeholder Image Box */}
              <div className="w-32 h-32 rounded-2xl bg-slate-900 border border-slate-800 flex flex-col items-center justify-center text-slate-500 mb-4 overflow-hidden group shadow-inner">
                <ImageIcon size={40} className="text-slate-600 mb-1 group-hover:scale-110 transition-transform" />
                <span className="text-[10px] font-mono text-slate-500 uppercase">Placeholder</span>
              </div>

              {/* Drag & Drop Area Heading & Description */}
              <h4 className="text-sm font-semibold text-white mb-1">
                Drag & Drop Area
              </h4>
              <p className="text-xs text-slate-400 max-w-xs mb-4">
                Drag your avatar or garment photo here, or click the button below to select from your device.
              </p>

              {/* Upload Button */}
              <Button
                variant="primary"
                size="md"
                leftIcon={<UploadIcon size={16} />}
                onClick={() => {
                  /* Non-functional UI button per phase scope */
                }}
                className="mb-4"
              >
                Upload Button
              </Button>

              {/* Supported Formats Text */}
              <div className="text-[11px] text-slate-500 flex items-center gap-1.5 font-mono">
                <FileText size={12} className="text-blue-400" />
                <span>Supported Formats Text: JPG, PNG, WEBP up to 10MB</span>
              </div>
            </div>

            {/* CTA to view sample Result page */}
            <div className="pt-2 flex items-center justify-between text-xs text-slate-400 border-t border-slate-800/80">
              <span>Ready to inspect the comparison interface?</span>
              <Button
                variant="outline"
                size="sm"
                rightIcon={<ArrowRight size={14} />}
                onClick={() => navigate('/result')}
              >
                Proceed to Result Page
              </Button>
            </div>
          </Card>
        </div>

        {/* RIGHT PANEL: Instructions & Metadata Card */}
        <div className="lg:col-span-5 space-y-6">
          
          {/* Instructions Card */}
          <Card hover={false} className="border border-slate-800 bg-slate-900/60 p-6 space-y-6">
            <div className="flex items-center gap-2 pb-3 border-b border-slate-800">
              <Info size={18} className="text-purple-400" />
              <h3 className="text-base font-bold text-white">Instructions Card</h3>
            </div>

            {/* Image Requirements */}
            <div className="space-y-2">
              <h4 className="text-xs font-bold text-slate-200 uppercase tracking-wider flex items-center gap-1.5">
                <CheckCircle size={14} className="text-emerald-400" /> Image Requirements
              </h4>
              <ul className="space-y-1.5 text-xs text-slate-400">
                <li className="flex items-start gap-2">
                  <span className="text-blue-400 font-bold">•</span>
                  <span>Full-body or half-body portrait photo in upright posture.</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-blue-400 font-bold">•</span>
                  <span>Well-lit environment with minimal heavy shadows or occlusions.</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-blue-400 font-bold">•</span>
                  <span>Garment images should be flat-lay or product catalog style.</span>
                </li>
              </ul>
            </div>

            {/* Tips */}
            <div className="space-y-2 pt-2 border-t border-slate-800/60">
              <h4 className="text-xs font-bold text-slate-200 uppercase tracking-wider flex items-center gap-1.5">
                <Shield size={14} className="text-amber-400" /> Tips for Best AI Fitting
              </h4>
              <p className="text-xs text-slate-400 leading-relaxed">
                For optimal posture detection and fabric drape, ensure high resolution input photos with clear contrast between background and clothing.
              </p>
            </div>

            {/* Supported Formats & Maximum File Size Specs */}
            <div className="grid grid-cols-2 gap-3 pt-2 border-t border-slate-800/60 text-xs">
              <div className="bg-slate-950/80 p-3 rounded-xl border border-slate-800">
                <span className="text-[11px] text-slate-500 block mb-0.5">Supported Formats</span>
                <span className="font-semibold text-slate-200 font-mono">JPG, PNG, WEBP</span>
              </div>
              <div className="bg-slate-950/80 p-3 rounded-xl border border-slate-800">
                <span className="text-[11px] text-slate-500 block mb-0.5">Maximum File Size</span>
                <span className="font-semibold text-blue-400 font-mono">{APP_CONFIG.UPLOAD.MAX_FILE_SIZE_MB} MB</span>
              </div>
            </div>

            {/* Recent Upload Placeholder */}
            <div className="space-y-3 pt-2 border-t border-slate-800/60">
              <h4 className="text-xs font-bold text-slate-200 uppercase tracking-wider flex items-center justify-between">
                <span>Recent Upload Placeholder</span>
                <RefreshCw size={12} className="text-slate-500" />
              </h4>

              <div className="grid grid-cols-3 gap-2">
                {[1, 2, 3].map((item) => (
                  <div
                    key={item}
                    className="aspect-square rounded-xl bg-slate-950 border border-slate-800/80 flex flex-col items-center justify-center p-2 text-slate-600 hover:border-slate-700 transition-colors cursor-pointer group"
                  >
                    <ImageIcon size={20} className="mb-1 group-hover:text-blue-400 transition-colors" />
                    <span className="text-[9px] font-mono text-slate-500">Item #{item}</span>
                  </div>
                ))}
              </div>
            </div>
          </Card>
        </div>

      </div>
    </div>
  );
}
