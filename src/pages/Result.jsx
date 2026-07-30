import { useState } from 'react';
import { useNavigate } from 'react';
import { ArrowLeft } from 'lucide-react';
import { SEO } from '@/components/common/SEO';
import { useSimulation } from '@/hooks/useSimulation';
import { SectionTitle } from '@/components/ui/SectionTitle';
import { Button } from '@/components/ui/Button';
import { BeforeAfterSlider } from '@/features/result/BeforeAfterSlider';
import { FitSummaryCard } from '@/features/result/FitSummaryCard';
import { ActionToolbar } from '@/features/result/ActionToolbar';
import { DownloadShareModal } from '@/features/result/DownloadShareModal';

export default function Result() {
  const navigate = useNavigate();
  const { simulationResult, userAvatar, garmentImage, runSimulation, resetSimulation } =
    useSimulation();
  const [isShareModalOpen, setIsShareModalOpen] = useState(false);

  // Fallback default sample preview if page visited directly without upload
  const displayResult = simulationResult || {
    originalImageUrl:
      userAvatar?.previewUrl ||
      'https://images.unsplash.com/photo-1534528741775-53994a69daeb?auto=format&fit=crop&q=80&w=1000',
    renderedImageUrl:
      'https://images.unsplash.com/photo-1515886657613-9f3515b0c78f?auto=format&fit=crop&q=80&w=1000',
    fitConfidence: 0.94,
    metrics: {
      shoulderFit: '98% Alignment',
      waistDrape: 'Optimal Tension',
    },
  };

  const handleRetrySimulation = async () => {
    if (userAvatar && garmentImage) {
      await runSimulation();
    } else {
      navigate('/upload');
    }
  };

  const handleNewUpload = () => {
    resetSimulation();
    navigate('/upload');
  };

  return (
    <div className="space-y-8 max-w-6xl mx-auto">
      <SEO
        title="Simulation Result"
        description="Inspect high-fidelity 3D virtual try-on render and fit confidence metrics."
      />

      <div className="flex items-center justify-between">
        <Button
          variant="ghost"
          size="sm"
          leftIcon={<ArrowLeft size={16} />}
          onClick={() => navigate('/upload')}
        >
          Back to Upload Station
        </Button>
        <span className="text-xs font-mono text-slate-500">ID: {displayResult.id || 'demo_sim_01'}</span>
      </div>

      <SectionTitle
        badge="Simulation Output"
        title="Virtual Try-On Result & Analytics"
        subtitle="Compare original avatar photo against AI virtual wear render."
      />

      {/* Main Before/After Split Comparison View */}
      <BeforeAfterSlider
        originalImage={displayResult.originalImageUrl}
        simulatedImage={displayResult.renderedImageUrl}
      />

      {/* Action Toolbar Buttons */}
      <ActionToolbar
        onDownload={() => setIsShareModalOpen(true)}
        onShare={() => setIsShareModalOpen(true)}
        onRetry={handleRetrySimulation}
        onNewUpload={handleNewUpload}
      />

      {/* AI Fit Analytics Card */}
      <FitSummaryCard result={displayResult} />

      {/* Share & Download Modal */}
      <DownloadShareModal
        isOpen={isShareModalOpen}
        onClose={() => setIsShareModalOpen(false)}
        imageUrl={displayResult.renderedImageUrl}
      />
    </div>
  );
}
