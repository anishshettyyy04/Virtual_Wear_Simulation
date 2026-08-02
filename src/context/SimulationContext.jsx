import { useState, useCallback, useEffect, useRef, useMemo } from 'react';
import { APP_CONFIG } from '@/constants/appConfig';
import { simulationService } from '@/services/simulationService';
import { validateImageFile } from '@/utils/imageValidation';
import { SimulationContext } from './SimulationContext';

// Helper to revoke blob URLs safely
const revokeBlobUrl = (url) => {
  if (url && typeof url === 'string' && url.startsWith('blob:')) {
    try {
      URL.revokeObjectURL(url);
    } catch {
      // Ignore URL revocation errors
    }
  }
};

export const SimulationProvider = ({ children }) => {
  const [personImage, setPersonImageState] = useState(null); // { file, previewUrl }
  const [garmentImage, setGarmentImageState] = useState(null); // { file, previewUrl, id, title }
  const [selectedGarment, setSelectedGarment] = useState(null);
  const [selectedCategory, setSelectedCategory] = useState('tops');

  // Single status workflow model: 'idle' | 'ready' | 'uploading' | 'processing' | 'completed' | 'failed'
  const [simulationStatus, setSimulationStatus] = useState('idle');
  const [progress, setProgress] = useState(0);

  const [simulationResult, setSimulationResult] = useState(null);
  const [resultImage, setResultImage] = useState(null);
  const [error, setError] = useState(null);
  const [settings, setSettings] = useState(APP_CONFIG.SIMULATION_DEFAULTS);
  const [modelStatus, setModelStatus] = useState({ isReady: true, name: 'VirtualWear-v2' });

  // Keep track of all active Object URLs for unmount cleanup
  const activeBlobUrlsRef = useRef(new Set());

  // Track & create Object URL safely
  const createTrackedObjectURL = useCallback((file) => {
    if (!file) return null;
    const url = URL.createObjectURL(file);
    activeBlobUrlsRef.current.add(url);
    return url;
  }, []);

  // Safely release a tracked Object URL
  const releaseTrackedObjectURL = useCallback((url) => {
    if (!url) return;
    if (activeBlobUrlsRef.current.has(url)) {
      activeBlobUrlsRef.current.delete(url);
    }
    revokeBlobUrl(url);
  }, []);

  // Cleanup all active Object URLs when provider unmounts
  useEffect(() => {
    const activeUrls = activeBlobUrlsRef.current;
    return () => {
      activeUrls.forEach((url) => {
        revokeBlobUrl(url);
      });
      activeUrls.clear();
    };
  }, []);

  // Action: Set Person Image & manage Object URL lifecycle
  const setPersonImage = useCallback(
    (input) => {
      setPersonImageState((prev) => {
        if (prev?.previewUrl) {
          releaseTrackedObjectURL(prev.previewUrl);
        }

        if (!input) return null;

        let file = null;
        let previewUrl = null;

        if (input instanceof File) {
          file = input;
          previewUrl = createTrackedObjectURL(file);
        } else if (typeof input === 'object') {
          file = input.file || null;
          previewUrl = input.previewUrl || (file ? createTrackedObjectURL(file) : null);
        }

        return { file, previewUrl };
      });

      setError(null);
      setSimulationStatus((prevStatus) =>
        prevStatus === 'completed' || prevStatus === 'failed' ? 'idle' : prevStatus
      );
    },
    [createTrackedObjectURL, releaseTrackedObjectURL]
  );

  // Action: Remove Person Image
  const removePersonImage = useCallback(() => {
    setPersonImageState((prev) => {
      if (prev?.previewUrl) {
        releaseTrackedObjectURL(prev.previewUrl);
      }
      return null;
    });
    setSimulationStatus((prevStatus) => (garmentImage ? 'idle' : 'idle'));
  }, [releaseTrackedObjectURL, garmentImage]);

  // Action: Set Garment Image & manage Object URL lifecycle
  const setGarmentImage = useCallback(
    (input) => {
      setGarmentImageState((prev) => {
        if (prev?.previewUrl) {
          releaseTrackedObjectURL(prev.previewUrl);
        }

        if (!input) return null;

        let file = null;
        let previewUrl = null;
        let id = input.id || null;
        let title = input.title || null;

        if (input instanceof File) {
          file = input;
          previewUrl = createTrackedObjectURL(file);
        } else if (typeof input === 'object') {
          file = input.file || null;
          previewUrl = input.previewUrl || (file ? createTrackedObjectURL(file) : null);
        }

        return { file, previewUrl, id, title };
      });

      setError(null);
      setSimulationStatus((prevStatus) =>
        prevStatus === 'completed' || prevStatus === 'failed' ? 'idle' : prevStatus
      );
    },
    [createTrackedObjectURL, releaseTrackedObjectURL]
  );

  // Action: Remove Garment Image
  const removeGarmentImage = useCallback(() => {
    setGarmentImageState((prev) => {
      if (prev?.previewUrl) {
        releaseTrackedObjectURL(prev.previewUrl);
      }
      return null;
    });
    setSelectedGarment(null);
  }, [releaseTrackedObjectURL]);

  // Action: Reset Simulation state & release all preview Object URLs
  const resetSimulation = useCallback(() => {
    setPersonImageState((prev) => {
      if (prev?.previewUrl) releaseTrackedObjectURL(prev.previewUrl);
      return null;
    });
    setGarmentImageState((prev) => {
      if (prev?.previewUrl) releaseTrackedObjectURL(prev.previewUrl);
      return null;
    });
    setSelectedGarment(null);
    setSimulationResult(null);
    setResultImage(null);
    setError(null);
    setProgress(0);
    setSimulationStatus('idle');
  }, [releaseTrackedObjectURL]);

  // Action: Update Settings
  const updateSettings = useCallback((newSettings) => {
    setSettings((prev) => ({ ...prev, ...newSettings }));
  }, []);

  // Action: Set Simulation Error
  const setSimulationError = useCallback((errorMsg) => {
    setError(errorMsg);
    setSimulationStatus('failed');
    setProgress(0);
  }, []);

  // Action: Update Progress
  const updateProgress = useCallback((val) => {
    setProgress(Math.min(100, Math.max(0, val)));
  }, []);

  // Action: Set Result
  const setResult = useCallback((resultData) => {
    setSimulationResult(resultData);
    setResultImage(resultData?.renderedImageUrl || resultData?.url || null);
    setSimulationStatus('completed');
    setProgress(100);
  }, []);

  // Action: Trigger Virtual Try-On Processing
  const runSimulation = useCallback(async () => {
    if (!personImage?.previewUrl && !personImage?.file) {
      const errMsg = 'Please upload or select an avatar/person image first.';
      setError(errMsg);
      setSimulationStatus('failed');
      return null;
    }

    if (!garmentImage?.previewUrl && !garmentImage?.file && !selectedGarment) {
      const errMsg = 'Please select or upload a garment image.';
      setError(errMsg);
      setSimulationStatus('failed');
      return null;
    }

    // Validate person image file if provided
    if (personImage.file) {
      const personValidation = validateImageFile(personImage.file);
      if (!personValidation.isValid) {
        setError(personValidation.error);
        setSimulationStatus('failed');
        return null;
      }
    }

    // Validate garment image file if provided
    if (garmentImage.file) {
      const garmentValidation = validateImageFile(garmentImage.file);
      if (!garmentValidation.isValid) {
        setError(garmentValidation.error);
        setSimulationStatus('failed');
        return null;
      }
    }

    setError(null);
    setSimulationStatus('uploading');
    setProgress(20);

    try {
      const formData = new FormData();
      if (personImage.file) formData.append('userAvatar', personImage.file);
      if (garmentImage.file) formData.append('garmentImage', garmentImage.file);
      if (selectedCategory) formData.append('category', selectedCategory);
      if (settings?.FIT_TYPE) formData.append('fitType', settings.FIT_TYPE);
      if (settings?.POSE_MODE) formData.append('poseMode', settings.POSE_MODE);
      if (settings?.FABRIC_WEIGHT) formData.append('fabricWeight', settings.FABRIC_WEIGHT);

      setSimulationStatus('processing');
      setProgress(55);

      const result = await simulationService.processSimulation(formData);

      const finalResult = {
        ...result,
        originalImageUrl: personImage.previewUrl,
        garmentImageUrl: garmentImage.previewUrl,
      };

      setSimulationResult(finalResult);
      setResultImage(finalResult.renderedImageUrl || finalResult.url || null);
      setSimulationStatus('completed');
      setProgress(100);

      return finalResult;
    } catch (err) {
      const errorMsg = err.message || 'Simulation process failed. Please try again.';
      setError(errorMsg);
      setSimulationStatus('failed');
      setProgress(0);
      return null;
    }
  }, [personImage, garmentImage, selectedGarment, selectedCategory, settings]);

  // Derived state flags for backward compatibility
  const isProcessing = simulationStatus === 'uploading' || simulationStatus === 'processing';
  const userAvatar = personImage;
  const setUserAvatar = setPersonImage;

  const value = useMemo(
    () => ({
      // State
      personImage,
      userAvatar,
      garmentImage,
      selectedGarment,
      selectedCategory,
      simulationStatus,
      progress,
      simulationResult,
      resultImage,
      error,
      settings,
      modelStatus,
      isProcessing,

      // Actions
      setPersonImage,
      setUserAvatar,
      removePersonImage,
      setGarmentImage,
      removeGarmentImage,
      setSelectedGarment,
      setSelectedCategory,
      runSimulation,
      startSimulation: runSimulation,
      updateProgress,
      setResult,
      setSimulationError,
      resetSimulation,
      updateSettings,
      setError,
      setModelStatus,
      setSimulationResult,
    }),
    [
      personImage,
      userAvatar,
      garmentImage,
      selectedGarment,
      selectedCategory,
      simulationStatus,
      progress,
      simulationResult,
      resultImage,
      error,
      settings,
      modelStatus,
      isProcessing,
      setPersonImage,
      setUserAvatar,
      removePersonImage,
      setGarmentImage,
      removeGarmentImage,
      setSelectedGarment,
      setSelectedCategory,
      runSimulation,
      updateProgress,
      setResult,
      setSimulationError,
      resetSimulation,
      updateSettings,
      setError,
      setModelStatus,
      setSimulationResult,
    ]
  );

  return (
    <SimulationContext.Provider value={value}>
      {children}
    </SimulationContext.Provider>
  );
};

export default SimulationProvider;
