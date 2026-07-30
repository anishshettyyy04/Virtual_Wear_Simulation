import { useEffect } from 'react';
import { Camera, RefreshCw, Check, FlipHorizontal } from 'lucide-react';
import { Modal } from '@/components/ui/Modal';
import { Button } from '@/components/ui/Button';
import { ErrorMessage } from '@/components/ui/ErrorMessage';
import { useCamera } from '@/hooks/useCamera';

export const WebcamCaptureModal = ({ isOpen, onClose, onPhotoCaptured }) => {
  const {
    videoRef,
    isCameraActive,
    cameraError,
    capturedImage,
    setCapturedImage,
    startCamera,
    stopCamera,
    toggleFacingMode,
    capturePhoto,
  } = useCamera();

  useEffect(() => {
    if (isOpen) {
      startCamera();
    } else {
      stopCamera();
      setCapturedImage(null);
    }
  }, [isOpen, startCamera, stopCamera, setCapturedImage]);

  const handleCapture = () => {
    capturePhoto();
  };

  const handleRetake = () => {
    setCapturedImage(null);
  };

  const handleConfirm = () => {
    if (capturedImage && onPhotoCaptured) {
      onPhotoCaptured(capturedImage);
      onClose();
    }
  };

  return (
    <Modal isOpen={isOpen} onClose={onClose} title="Live Camera Avatar Capture" maxWidth="max-w-2xl">
      <div className="space-y-4">
        {cameraError ? (
          <ErrorMessage title="Camera Error" message={cameraError} onRetry={startCamera} />
        ) : (
          <div className="relative w-full h-[360px] sm:h-[420px] rounded-2xl overflow-hidden bg-slate-950 border border-slate-800 flex items-center justify-center">
            {capturedImage ? (
              <img
                src={capturedImage.previewUrl}
                alt="Captured Avatar"
                className="w-full h-full object-contain"
              />
            ) : (
              <video
                ref={videoRef}
                autoPlay
                playsInline
                muted
                className="w-full h-full object-contain"
              />
            )}

            {/* Live Camera Badge */}
            {isCameraActive && !capturedImage && (
              <div className="absolute top-4 left-4 bg-slate-900/80 backdrop-blur-md px-3 py-1 rounded-full border border-slate-800 text-[11px] font-semibold text-emerald-400 flex items-center gap-2">
                <span className="relative flex h-2 w-2">
                  <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
                  <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-500"></span>
                </span>
                <span>Webcam Stream Active</span>
              </div>
            )}
          </div>
        )}

        {/* Controls */}
        <div className="flex items-center justify-between pt-2">
          {!capturedImage ? (
            <>
              <Button
                variant="secondary"
                size="sm"
                leftIcon={<FlipHorizontal size={16} />}
                onClick={toggleFacingMode}
                isDisabled={!isCameraActive}
              >
                Switch Camera
              </Button>

              <Button
                variant="gradient"
                size="md"
                leftIcon={<Camera size={18} />}
                onClick={handleCapture}
                isDisabled={!isCameraActive}
              >
                Take Photo
              </Button>
            </>
          ) : (
            <>
              <Button variant="outline" size="sm" leftIcon={<RefreshCw size={16} />} onClick={handleRetake}>
                Retake Photo
              </Button>

              <Button variant="gradient" size="md" leftIcon={<Check size={18} />} onClick={handleConfirm}>
                Use Photo as Avatar
              </Button>
            </>
          )}
        </div>
      </div>
    </Modal>
  );
};
