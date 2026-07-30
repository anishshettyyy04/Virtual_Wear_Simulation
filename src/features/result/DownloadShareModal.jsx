import { useState } from 'react';
import { Copy, Check, Link2, Download } from 'lucide-react';
import { Modal } from '@/components/ui/Modal';
import { Button } from '@/components/ui/Button';

export const DownloadShareModal = ({ isOpen, onClose, imageUrl }) => {
  const [copied, setCopied] = useState(false);
  const shareUrl = window.location.href;

  const handleCopyLink = () => {
    navigator.clipboard.writeText(shareUrl);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const handleTriggerDownload = () => {
    if (!imageUrl) return;
    const a = document.createElement('a');
    a.href = imageUrl;
    a.download = `virtual-wear-tryon-${Date.now()}.jpg`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
  };

  return (
    <Modal isOpen={isOpen} onClose={onClose} title="Export & Share Simulation Render">
      <div className="space-y-4">
        {/* Preview image */}
        {imageUrl && (
          <div className="w-full h-48 rounded-xl overflow-hidden bg-slate-950 border border-slate-800">
            <img src={imageUrl} alt="Simulation Preview" className="w-full h-full object-contain p-2" />
          </div>
        )}

        {/* Shareable Link */}
        <div>
          <label className="block text-xs font-semibold uppercase tracking-wider text-slate-400 mb-1.5">
            Shareable Result URL
          </label>
          <div className="flex items-center gap-2 bg-slate-900 border border-slate-800 rounded-xl p-2">
            <Link2 size={16} className="text-slate-500 shrink-0 ml-1" />
            <input
              type="text"
              readOnly
              value={shareUrl}
              className="bg-transparent text-xs text-slate-300 w-full outline-none font-mono"
            />
            <Button variant="secondary" size="sm" onClick={handleCopyLink}>
              {copied ? <Check size={14} className="text-emerald-400" /> : <Copy size={14} />}
              <span>{copied ? 'Copied' : 'Copy'}</span>
            </Button>
          </div>
        </div>

        {/* Download Buttons */}
        <div className="pt-2 flex items-center justify-end gap-2">
          <Button variant="ghost" size="md" onClick={onClose}>
            Close
          </Button>
          <Button variant="gradient" size="md" leftIcon={<Download size={16} />} onClick={handleTriggerDownload}>
            Download Full Resolution
          </Button>
        </div>
      </div>
    </Modal>
  );
};
