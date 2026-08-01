import { useState, useCallback } from 'react';
import { APP_CONFIG } from '@/constants/appConfig';
import { simulationService } from '@/services/simulationService';
import { SimulationContext } from './SimulationContext';

export const SimulationProvider = ({ children }) => {
  const [userAvatar, setUserAvatar] = useState(null); // { file, previewUrl }
  const [garmentImage, setGarmentImage] = useState(null); // { file, previewUrl, id, title }
  const [settings, setSettings] = useState(APP_CONFIG.SIMULATION_DEFAULTS);
  const [isProcessing, setIsProcessing] = useState(false);
  const [simulationResult, setSimulationResult] = useState(null);
  const [error, setError] = useState(null);
  const [modelStatus, setModelStatus] = useState({ isReady: true, name: 'VirtualWear-v2' });

  // Reset current upload state
  const resetSimulation = useCallback(() => {
    setUserAvatar(null);
    setGarmentImage(null);
    setSimulationResult(null);
    setError(null);
  }, []);

  // Update simulation settings
  const updateSettings = useCallback((newSettings) => {
    setSettings((prev) => ({ ...prev, ...newSettings }));
  }, []);

  // Trigger virtual try-on processing
  const runSimulation = useCallback(async () => {
    if (!userAvatar?.previewUrl) {
      setError('Please upload or select an avatar image first.');
      return null;
    }
    if (!garmentImage?.previewUrl) {
      setError('Please select or upload a garment image.');
      return null;
    }

    setIsProcessing(true);
    setError(null);

    try {
      const formData = new FormData();
      if (userAvatar.file) formData.append('userAvatar', userAvatar.file);
      if (garmentImage.file) formData.append('garmentImage', garmentImage.file);
      formData.append('fitType', settings.FIT_TYPE);
      formData.append('poseMode', settings.POSE_MODE);
      formData.append('fabricWeight', settings.FABRIC_WEIGHT);

      const result = await simulationService.processSimulation(formData);

      // Inject fallback preview URLs if mock images are used
      const finalResult = {
        ...result,
        originalImageUrl: userAvatar.previewUrl,
        garmentImageUrl: garmentImage.previewUrl,
      };

      setSimulationResult(finalResult);
      setIsProcessing(false);
      return finalResult;
    } catch (err) {
      setError(err.message || 'Simulation process failed. Please try again.');
      setIsProcessing(false);
      return null;
    }
  }, [userAvatar, garmentImage, settings]);

  const value = {
    userAvatar,
    setUserAvatar,
    garmentImage,
    setGarmentImage,
    settings,
    updateSettings,
    isProcessing,
    simulationResult,
    setSimulationResult,
    error,
    setError,
    modelStatus,
    setModelStatus,
    resetSimulation,
    runSimulation,
  };

  return (
    <SimulationContext.Provider value={value}>
      {children}
    </SimulationContext.Provider>
  );
};
