import { useState } from 'react';
import { useNavigate } from 'react';
import { Download, Share2, RefreshCw, Sparkles, CheckCircle2, Clock, Shirt, BarChart3, Image as ImageIcon } from 'lucide-react';
import { SEO } from '@/components/common/SEO';
import { SectionTitle } from '@/components/ui/SectionTitle';
import { Button } from '@/components/ui/Button';
import { Card } from '@/components/ui/Card';
import { Badge } from '@/components/ui/Badge';
import { Modal } from '@/components/ui/Modal';

export default function Result() {
  const navigate = useNavigate();
  const [isShareModalOpen, setIsShareModalOpen] = useState(false);

  // Result metadata placeholders
  const resultInfo = {
    status: 'Completed',
    processingTime: '1.42s',
    selectedOutfit: 'Classic Denim Jacket & Cotton Tee',
    confidence: '94.8%',
  };

  return (
    <div className="space-y-8 max-w-6xl mx-auto">
      <SEO
        title="Simulation Result"
        description="Inspect AI Virtual Wear comparison result, fit confidence, and processing metrics."
      />

      <SectionTitle
        badge="Comparison View"
        title="AI Virtual Try-On Result"
        subtitle="Compare original avatar image against AI Virtual Wear simulation output."
      />

      {/* COMPARISON INTERFACE: Original Image | AI Result */}
      <Card hover={false} className="border border-slate-800 bg-slate-900/60 p-6 space-y-4">
        <div className="flex items-center justify-between pb-3 border-b border-slate-800">
          <div className="flex items-center gap-2">
            <Sparkles size={18} className="text-blue-400" />
            <h3 className="text-base font-bold text-white">Side-by-Side Comparison</h3>
          </div>
          <Badge variant="success" size="sm" icon={<CheckCircle2 size={12} />}>
            Render Status: {resultInfo.status}
          </Badge>
        </div>

        {/* Side-by-Side Image Display */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 pt-2">
          
          {/* Left: Original Image Container */}
          <div className="space-y-2">
            <div className="flex items-center justify-between text-xs font-semibold text-slate-300">
              <span>Original Image</span>
              <span className="text-[10px] text-slate-500 font-mono">Input Photo</span>
            </div>

            <div className="relative aspect-[3/4] rounded-2xl bg-slate-950 border border-slate-800 overflow-hidden flex flex-col items-center justify-center p-6 text-center group">
              <div className="w-20 h-20 rounded-2xl bg-slate-900 border border-slate-800 flex items-center justify-center text-slate-500 mb-3 group-hover:scale-105 transition-transform">
                <ImageIcon size={36} className="text-slate-400" />
              </div>
              <span className="text-xs font-semibold text-slate-300 mb-1">Original Model Avatar</span>
              <span className="text-[11px] text-slate-500 max-w-xs">
                Placeholder image box representing input user photo before virtual wear application.
              </span>
              <div className="absolute top-3 left-3">
                <Badge variant="neutral" size="sm">Original</Badge>
              </div>
            </div>
          </div>

          {/* Right: AI Result Container */}
          <div className="space-y-2">
            <div className="flex items-center justify-between text-xs font-semibold text-slate-300">
              <span className="text-blue-400 font-bold">AI Result</span>
              <span className="text-[10px] text-purple-400 font-mono">Virtual Wear Render</span>
            </div>

            <div className="relative aspect-[3/4] rounded-2xl bg-slate-950 border-2 border-blue-500/40 overflow-hidden flex flex-col items-center justify-center p-6 text-center group shadow-xl shadow-blue-600/10">
              <div className="w-20 h-20 rounded-2xl bg-gradient-to-tr from-blue-600/20 to-purple-600/20 border border-blue-500/30 flex items-center justify-center text-blue-400 mb-3 group-hover:scale-105 transition-transform">
                <Sparkles size={36} className="text-blue-400" />
              </div>
              <span className="text-xs font-semibold text-white mb-1">AI Simulated Virtual Try-On</span>
              <span className="text-[11px] text-slate-400 max-w-xs">
                Placeholder image box representing high-fidelity AI apparel drape output.
              </span>
              <div className="absolute top-3 right-3">
                <Badge variant="primary" size="sm" icon={<Sparkles size={10} />}>AI Render</Badge>
              </div>
            </div>
          </div>

        </div>
      </Card>

      {/* RESULT INFORMATION CARD */}
      <Card hover={false} className="border border-slate-800 bg-slate-900/60 p-6 space-y-6">
        <div className="flex items-center justify-between pb-3 border-b border-slate-800">
          <div className="flex items-center gap-2">
            <BarChart3 size={18} className="text-purple-400" />
            <h3 className="text-base font-bold text-white">Result Information Card</h3>
          </div>
          <span className="text-xs font-mono text-slate-500">Pipeline ID: sim_v0.1_demo</span>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          
          {/* Status */}
          <div className="bg-slate-950/80 p-4 rounded-xl border border-slate-800/80 space-y-1">
            <span className="text-[11px] font-bold text-slate-400 uppercase tracking-wider block">
              Status
            </span>
            <div className="flex items-center gap-2">
              <span className="w-2.5 h-2.5 rounded-full bg-emerald-500 animate-pulse"></span>
              <span className="text-base font-bold text-white font-mono">{resultInfo.status}</span>
            </div>
          </div>

          {/* Processing Time */}
          <div className="bg-slate-950/80 p-4 rounded-xl border border-slate-800/80 space-y-1">
            <span className="text-[11px] font-bold text-slate-400 uppercase tracking-wider flex items-center gap-1">
              <Clock size={12} className="text-blue-400" /> Processing Time
            </span>
            <span className="text-base font-bold text-blue-400 font-mono">{resultInfo.processingTime}</span>
          </div>

          {/* Selected Outfit */}
          <div className="bg-slate-950/80 p-4 rounded-xl border border-slate-800/80 space-y-1 sm:col-span-2 lg:col-span-1">
            <span className="text-[11px] font-bold text-slate-400 uppercase tracking-wider flex items-center gap-1">
              <Shirt size={12} className="text-purple-400" /> Selected Outfit
            </span>
            <span className="text-xs font-bold text-slate-200 truncate block">{resultInfo.selectedOutfit}</span>
          </div>

          {/* Confidence */}
          <div className="bg-slate-950/80 p-4 rounded-xl border border-slate-800/80 space-y-1">
            <span className="text-[11px] font-bold text-slate-400 uppercase tracking-wider flex items-center gap-1">
              <Sparkles size={12} className="text-amber-400" /> Fit Confidence
            </span>
            <span className="text-base font-bold text-emerald-400 font-mono">{resultInfo.confidence} Match</span>
          </div>

        </div>
      </Card>

      {/* ACTION BUTTONS: Download | Try Another | Share */}
      <div className="glass-card p-4 rounded-2xl border border-slate-800 flex flex-wrap items-center justify-between gap-4">
        <div className="flex items-center gap-3">
          {/* Download Button */}
          <Button
            variant="primary"
            size="md"
            leftIcon={<Download size={18} />}
            onClick={() => {
              /* Download handler placeholder */
            }}
          >
            Download
          </Button>

          {/* Share (placeholder) Button */}
          <Button
            variant="secondary"
            size="md"
            leftIcon={<Share2 size={18} />}
            onClick={() => setIsShareModalOpen(true)}
          >
            Share (placeholder)
          </Button>
        </div>

        {/* Try Another Button */}
        <Button
          variant="outline"
          size="md"
          leftIcon={<RefreshCw size={16} />}
          onClick={() => navigate('/upload')}
        >
          Try Another
        </Button>
      </div>

      {/* Share Modal Placeholder */}
      <Modal
        isOpen={isShareModalOpen}
        onClose={() => setIsShareModalOpen(false)}
        title="Share Simulation Result"
      >
        <div className="space-y-4 py-2">
          <p className="text-xs text-slate-300">
            Share placeholder modal for exporting or copying result link once backend integration is live.
          </p>
          <div className="p-3 bg-slate-950 rounded-xl border border-slate-800 text-xs font-mono text-slate-400 truncate">
            https://virtualwear.ai/share/demo_result_01
          </div>
          <div className="flex justify-end pt-2">
            <Button variant="secondary" size="sm" onClick={() => setIsShareModalOpen(false)}>
              Close
            </Button>
          </div>
        </div>
      </Modal>

    </div>
  );
}
