import { useNavigate } from 'react-router-dom';
import { Upload as UploadIcon, ArrowRight, RefreshCw, Sparkles, Loader2, CheckCircle2 } from 'lucide-react';
import { SEO } from '@/components/common/SEO';
import { SectionTitle } from '@/components/ui/SectionTitle';
import { Button } from '@/components/ui/Button';
import { Card } from '@/components/ui/Card';
import { Badge } from '@/components/ui/Badge';
import { ImageUploadSection } from '@/features/upload/ImageUploadSection';
import { GarmentSelector } from '@/features/upload/GarmentSelector';
import { UploadInfo } from '@/components/upload/UploadInfo';
import { useSimulation } from '@/hooks/useSimulation';

export default function Upload() {
  const navigate = useNavigate();
  const {
    personImage,
    setPersonImage,
    setGarmentImage,
    selectedGarment,
    setSelectedGarment,
    runSimulation,
    isProcessing,
    simulationStatus,
    progress,
    error,
  } = useSimulation();


  // Preset sample model avatars for testing
  const sampleAvatars = [
    { id: 1, name: 'Model #1 (Casual)', url: 'https://images.unsplash.com/photo-1534528741775-53994a69daeb?auto=format&fit=crop&q=80&w=600' },
    { id: 2, name: 'Model #2 (Studio)', url: 'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?auto=format&fit=crop&q=80&w=600' },
    { id: 3, name: 'Model #3 (Urban)', url: 'https://images.unsplash.com/photo-1517841905240-472988babdf9?auto=format&fit=crop&q=80&w=600' },
  ];

  const handleImageChange = (fileOrNull) => {
    if (fileOrNull) {
      console.log('[UPLOAD:STORED_CONTEXT]', fileOrNull);
      setPersonImage(fileOrNull);
    } else {
      setPersonImage(null);
    }
  };

  const handleSelectSampleAvatar = (avatar) => {
    const avatarData = { previewUrl: avatar.url, file: null };
    console.log('[UPLOAD:STORED_CONTEXT]', avatarData);
    setPersonImage(avatarData);
  };

  const handleSelectGarment = (garment) => {
    setSelectedGarment(garment);
    setGarmentImage(garment);
  };

  const handleStartSimulation = async () => {
    // Guard against duplicate clicks while processing
    if (isProcessing) return;

    console.log('[SIMULATION:START]', {
      hasPersonImage: Boolean(personImage?.previewUrl || personImage?.file),
      hasGarment: Boolean(selectedGarment),
      garmentId: selectedGarment?.id,
    });

    // Default to sample avatar if user hasn't uploaded one
    if (!personImage?.previewUrl && !personImage?.file) {
      setPersonImage({ previewUrl: sampleAvatars[0].url, file: null });
    }
    const result = await runSimulation();
    if (result) {
      navigate('/result');
    }
  };

  // Determine processing stage label for UX
  const getStageLabel = () => {
    if (simulationStatus === 'uploading') return 'Uploading images...';
    if (simulationStatus === 'processing' && progress < 60) return 'Preparing AI pipeline...';
    if (simulationStatus === 'processing' && progress < 90) return 'Running AI inference (~30s)...';
    if (simulationStatus === 'processing') return 'Rendering final output...';
    return 'Processing...';
  };

  return (
    <div className="space-y-8 max-w-6xl mx-auto">
      <SEO
        title="Upload Image"
        description="Upload model avatar or garment photo for Virtual Wear AI fitting simulation."
      />

      <SectionTitle
        badge="Upload Station"
        title="Upload Image & Select Apparel"
        subtitle="Upload your model photo, select preset garments from the live catalog, and run AI Virtual Wear simulation."
      />

      {/* Error Alert */}
      {error && (
        <div className="p-4 bg-rose-950/40 border border-rose-800 rounded-xl text-xs text-rose-300 flex items-center justify-between">
          <span>{error}</span>
        </div>
      )}

      {/* Main 2-Panel Layout */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
        
        {/* LEFT PANEL: Interactive Upload & Garment Selector */}
        <div className="lg:col-span-7 space-y-6">
          <Card hover={false} className="border border-slate-800 bg-slate-900/60 p-6 space-y-6">
            <div className="flex items-center justify-between border-b border-slate-800/80 pb-4">
              <div className="flex items-center gap-2">
                <div className="w-8 h-8 rounded-lg bg-blue-600/20 text-blue-400 flex items-center justify-center font-bold">
                  <UploadIcon size={18} />
                </div>
                <h3 className="text-base font-bold text-white">1. Avatar Photo Upload</h3>
              </div>
              <Badge variant="primary" size="sm">
                Step 1 of 2
              </Badge>
            </div>

            {/* Interactive Image Upload Area */}
            <ImageUploadSection onImageChange={handleImageChange} />

            {/* Garment Catalog Selector from backend GET /api/v1/products */}
            <div className="pt-4 border-t border-slate-800/80 space-y-3">
              <div className="flex items-center justify-between">
                <h4 className="text-sm font-bold text-white">2. Select Apparel Garment</h4>
                <Badge variant="neutral" size="sm">Step 2 of 2</Badge>
              </div>
              <GarmentSelector
                selectedGarment={selectedGarment}
                onSelectGarment={handleSelectGarment}
              />
            </div>

            {/* Run Simulation CTA Button */}
            <div className="pt-4 flex flex-col sm:flex-row items-center justify-between gap-3 text-xs text-slate-400 border-t border-slate-800/80">
              <div className="flex items-center gap-2">
                {isProcessing ? (
                  <span className="text-blue-400 font-semibold flex items-center gap-1">
                    <Loader2 size={14} className="animate-spin" /> {getStageLabel()}
                  </span>
                ) : selectedGarment ? (
                  <span className="text-emerald-400 font-semibold flex items-center gap-1">
                    <CheckCircle2 size={14} /> Garment Selected: {selectedGarment.title}
                  </span>
                ) : (
                  <span>Select a garment or run directly to get top recommendations.</span>
                )}
              </div>
              <Button
                variant="primary"
                size="md"
                disabled={isProcessing}
                leftIcon={isProcessing ? <Loader2 size={16} className="animate-spin" /> : <Sparkles size={16} />}
                rightIcon={!isProcessing && <ArrowRight size={14} />}
                onClick={handleStartSimulation}
              >
                {isProcessing ? getStageLabel() : 'Run AI Simulation'}
              </Button>
            </div>
          </Card>
        </div>

        {/* RIGHT PANEL: Sample Avatars & Specs */}
        <div className="lg:col-span-5 space-y-6">
          <UploadInfo />

          {/* Sample Avatars Selector */}
          <Card hover={false} className="border border-slate-800 bg-slate-900/60 p-6 space-y-4">
            <h4 className="text-xs font-bold text-slate-200 uppercase tracking-wider flex items-center justify-between">
              <span>Preset Sample Avatars</span>
              <RefreshCw size={12} className="text-slate-500" />
            </h4>

            <p className="text-xs text-slate-400">
              Click any sample avatar below to test fitting speed instantly:
            </p>

            <div className="grid grid-cols-3 gap-2">
              {sampleAvatars.map((avatar) => {
                const isSelected = personImage?.previewUrl === avatar.url;
                return (
                  <button
                    key={avatar.id}
                    type="button"
                    onClick={() => handleSelectSampleAvatar(avatar)}
                    className={`aspect-square rounded-xl bg-slate-950 border overflow-hidden relative flex flex-col items-center justify-center p-1 transition-all ${
                      isSelected
                        ? 'border-blue-500 ring-2 ring-blue-500/30'
                        : 'border-slate-800 hover:border-slate-700'
                    }`}
                  >
                    <img src={avatar.url} alt={avatar.name} className="w-full h-full object-cover rounded-lg" />
                    <div className="absolute inset-0 bg-gradient-to-t from-slate-950/80 via-transparent to-transparent flex items-end justify-center p-1">
                      <span className="text-[9px] font-mono text-white truncate">{avatar.name}</span>
                    </div>
                  </button>
                );
              })}
            </div>
          </Card>
        </div>

      </div>
    </div>
  );
}

