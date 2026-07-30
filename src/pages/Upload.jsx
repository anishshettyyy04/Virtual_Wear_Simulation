import { useState } from 'react';
import { useNavigate } from 'react';
import { ArrowRight, User, Shirt, Camera } from 'lucide-react';
import { SEO } from '@/components/common/SEO';
import { useSimulation } from '@/hooks/useSimulation';
import { SectionTitle } from '@/components/ui/SectionTitle';
import { Button } from '@/components/ui/Button';
import { ErrorMessage } from '@/components/ui/ErrorMessage';
import { Dropzone } from '@/features/upload/Dropzone';
import { ImagePreviewCard } from '@/features/upload/ImagePreviewCard';
import { GarmentSelector } from '@/features/upload/GarmentSelector';
import { SimulationSettingsForm } from '@/features/upload/SimulationSettingsForm';
import { AIModelStatusCard } from '@/features/simulation/AIModelStatusCard';
import { ModelLoader } from '@/features/simulation/ModelLoader';
import { WebcamCaptureModal } from '@/features/upload/WebcamCaptureModal';

export default function Upload() {
  const navigate = useNavigate();
  const {
    userAvatar,
    setUserAvatar,
    garmentImage,
    setGarmentImage,
    settings,
    updateSettings,
    isProcessing,
    error,
    setError,
    modelStatus,
    runSimulation,
  } = useSimulation();

  const [isWebcamOpen, setIsWebcamOpen] = useState(false);

  const handleStartSimulation = async () => {
    if (!userAvatar) {
      setError('Please upload or select an avatar image first.');
      return;
    }
    if (!garmentImage) {
      setError('Please select or upload a garment image to try on.');
      return;
    }

    const result = await runSimulation();
    if (result) {
      navigate('/result');
    }
  };

  if (isProcessing) {
    return (
      <div className="max-w-4xl mx-auto py-8">
        <SEO title="Simulating Try-On..." />
        <ModelLoader />
      </div>
    );
  }

  return (
    <div className="space-y-8 max-w-6xl mx-auto">
      <SEO
        title="Upload & Prepare"
        description="Upload your model avatar and garment image to configure Virtual Wear AI parameters."
      />

      <SectionTitle
        badge="Virtual Wear Studio"
        title="Upload Avatar & Garment Image"
        subtitle="Prepare your input images and customize fit settings for neural try-on processing."
      />

      <AIModelStatusCard status={modelStatus} />

      {error && <ErrorMessage title="Simulation Error" message={error} onRetry={() => setError(null)} />}

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Left Column: Avatar Upload & Webcam Capture */}
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2 text-white font-bold text-sm">
              <User size={18} className="text-indigo-400" />
              <span>1. User Avatar Image</span>
            </div>
            {!userAvatar && (
              <Button
                variant="outline"
                size="sm"
                leftIcon={<Camera size={14} />}
                onClick={() => setIsWebcamOpen(true)}
              >
                Take Webcam Photo
              </Button>
            )}
          </div>

          {userAvatar ? (
            <ImagePreviewCard
              title="Selected Model Avatar"
              imageData={userAvatar}
              onRemove={() => setUserAvatar(null)}
            />
          ) : (
            <Dropzone
              label="Upload Person / Avatar Image"
              subtitle="Clear full-body or half-body portrait photo"
              onImageSelected={(data) => setUserAvatar(data)}
            />
          )}
        </div>

        {/* Right Column: Garment Upload / Presets */}
        <div className="space-y-4">
          <div className="flex items-center gap-2 text-white font-bold text-sm">
            <Shirt size={18} className="text-pink-400" />
            <span>2. Apparel Garment Image</span>
          </div>

          {garmentImage ? (
            <ImagePreviewCard
              title="Selected Garment Image"
              imageData={garmentImage}
              onRemove={() => setGarmentImage(null)}
            />
          ) : (
            <div className="space-y-6">
              <Dropzone
                label="Upload Custom Garment Photo"
                subtitle="Flat-lay garment or apparel product image"
                onImageSelected={(data) => setGarmentImage(data)}
              />
              <GarmentSelector
                selectedGarment={garmentImage}
                onSelectGarment={(garment) => setGarmentImage(garment)}
              />
            </div>
          )}
        </div>
      </div>

      {/* Parameter Settings Form */}
      <SimulationSettingsForm settings={settings} onChangeSettings={updateSettings} />

      {/* Start Simulation Action Bar */}
      <div className="glass-panel p-6 rounded-2xl border border-indigo-500/20 flex flex-col sm:flex-row items-center justify-between gap-4">
        <div className="text-xs text-slate-300">
          <span className="font-semibold text-white block">Ready for Simulation?</span>
          <span>Both avatar and garment images configured.</span>
        </div>

        <Button
          variant="gradient"
          size="lg"
          rightIcon={<ArrowRight size={20} />}
          isDisabled={!userAvatar || !garmentImage}
          onClick={handleStartSimulation}
          className="w-full sm:w-auto"
        >
          Start AI Wear Simulation
        </Button>
      </div>

      {/* Webcam Modal Overlay */}
      <WebcamCaptureModal
        isOpen={isWebcamOpen}
        onClose={() => setIsWebcamOpen(false)}
        onPhotoCaptured={(photo) => setUserAvatar(photo)}
      />
    </div>
  );
}
