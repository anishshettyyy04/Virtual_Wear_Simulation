import { useState, useCallback, useEffect, useRef, useMemo, useContext } from 'react';
import { APP_CONFIG } from '@/constants/appConfig';
import { simulationService } from '@/services/simulationService';
import { validateImageFile } from '@/utils/imageValidation';
import { SimulationContext } from './SimulationContext';
import { AuthContext } from './AuthContext';

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

// Helper to generate dynamic guest session ID
function getGuestSessionId() {
  try {
    let guestId = sessionStorage.getItem('virtual_wear_guest_session_id');
    if (!guestId) {
      guestId = `GUEST_SESSION_${Date.now().toString(36)}_${Math.random().toString(36).substring(2, 7)}`;
      sessionStorage.setItem('virtual_wear_guest_session_id', guestId);
    }
    return guestId;
  } catch {
    return `GUEST_SESSION_${Date.now()}`;
  }
}

// Helper to create a fallback image File if fetching preview URL fails
const createFallbackImageFile = (filename, label = 'Sample') => {
  const canvas = document.createElement('canvas');
  canvas.width = 512;
  canvas.height = 512;
  const ctx = canvas.getContext('2d');
  if (ctx) {
    ctx.fillStyle = '#1e293b';
    ctx.fillRect(0, 0, 512, 512);
    ctx.fillStyle = '#38bdf8';
    ctx.font = '24px sans-serif';
    ctx.textAlign = 'center';
    ctx.fillText(label, 256, 256);
  }
  const dataUrl = canvas.toDataURL('image/jpeg');
  const arr = dataUrl.split(',');
  const mime = arr[0].match(/:(.*?);/)[1];
  const bstr = atob(arr[1]);
  let n = bstr.length;
  const u8arr = new Uint8Array(n);
  while (n--) {
    u8arr[n] = bstr.charCodeAt(n);
  }
  return new File([u8arr], filename, { type: mime });
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
  const [error, setErrorState] = useState(null);

  const setError = useCallback((err) => {
    if (!err) {
      setErrorState(null);
    } else if (typeof err === 'object') {
      setErrorState(err.message || JSON.stringify(err));
    } else {
      setErrorState(String(err));
    }
  }, []);

  const [settings, setSettings] = useState(APP_CONFIG.SIMULATION_DEFAULTS);
  const [modelStatus, setModelStatus] = useState({ isReady: false, name: 'Connecting...' });
  const auth = useContext(AuthContext);
  const user = auth?.user;

  // Fetch model status on mount
  useEffect(() => {
    let isMounted = true;
    const fetchStatus = async () => {
      const status = await simulationService.checkModelStatus();
      if (isMounted) {
        setModelStatus(status);
      }
    };
    fetchStatus();
    return () => { isMounted = false; };
  }, []);

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
          // Always create a context-owned blob URL from File to survive
          // component unmounts (e.g. navigating from Upload → Result).
          // The upload hook's blob URL gets revoked on unmount, breaking display.
          if (file) {
            previewUrl = createTrackedObjectURL(file);
          } else {
            previewUrl = input.previewUrl || null;
          }
        }

        return { file, previewUrl };
      });

      setError(null);
      setSimulationStatus((prevStatus) =>
        prevStatus === 'completed' || prevStatus === 'failed' ? 'idle' : prevStatus
      );
    },
    [createTrackedObjectURL, releaseTrackedObjectURL, setError]
  );

  // Action: Remove Person Image
  const removePersonImage = useCallback(() => {
    setPersonImageState((prev) => {
      if (prev?.previewUrl) {
        releaseTrackedObjectURL(prev.previewUrl);
      }
      return null;
    });
    setSimulationStatus('idle');
  }, [releaseTrackedObjectURL]);

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
          if (file) {
            previewUrl = createTrackedObjectURL(file);
          } else {
            previewUrl = input.previewUrl || null;
          }
        }

        return { file, previewUrl, id, title };
      });

      setError(null);
      setSimulationStatus((prevStatus) =>
        prevStatus === 'completed' || prevStatus === 'failed' ? 'idle' : prevStatus
      );
    },
    [createTrackedObjectURL, releaseTrackedObjectURL, setError]
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
  }, [releaseTrackedObjectURL, setError]);

  // Action: Update Settings
  const updateSettings = useCallback((newSettings) => {
    setSettings((prev) => ({ ...prev, ...newSettings }));
  }, []);

  // Action: Set Simulation Error
  const setSimulationError = useCallback((errorMsg) => {
    setError(errorMsg);
    setSimulationStatus('failed');
    setProgress(0);
  }, [setError]);

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

      const userId = user?.id || user?.userId || getGuestSessionId();
      const currentCategory = selectedCategory || selectedGarment?.category || 'upper_body';
      const currentProductId = selectedGarment?.id || selectedGarment?.productId;
      
      // 1. Fetch Context-Aware Recommendations
      const recommendationResult = await simulationService.processSimulation({
        userId,
        limit: 10,
        forceRefresh: false,
        selectedCategory: currentCategory,
        selectedProductId: currentProductId,
      });

      // 2. Prepare File Objects for AI TryOn Pipeline (POST /api/v1/tryon)
      let pFile = personImage?.file;
      if (!pFile && personImage?.previewUrl) {
        try {
          const blobRes = await fetch(personImage.previewUrl);
          if (blobRes.ok) {
            const blobData = await blobRes.blob();
            pFile = new File([blobData], 'user_avatar.jpg', { type: blobData.type || 'image/jpeg' });
          }
        } catch {
          pFile = null;
        }
      }
      if (!pFile) {
        pFile = createFallbackImageFile('user_avatar.jpg', 'User Avatar');
      }

      let gFile = garmentImage?.file;
      const garmentRefUrl = garmentImage?.previewUrl || selectedGarment?.image || selectedGarment?.previewUrl;
      if (!gFile && garmentRefUrl) {
        try {
          const blobRes = await fetch(garmentRefUrl);
          if (blobRes.ok) {
            const blobData = await blobRes.blob();
            gFile = new File([blobData], 'garment_item.jpg', { type: blobData.type || 'image/jpeg' });
          }
        } catch {
          gFile = null;
        }
      }
      if (!gFile) {
        gFile = createFallbackImageFile('garment_item.jpg', 'Garment Item');
      }

      console.log('[TRYON:PREPARED_FILES]', {
        personFileName: pFile.name,
        personFileSize: pFile.size,
        garmentFileName: gFile.name,
        garmentFileSize: gFile.size
      });

      // 3. Execute Core AI TryOn Neural Pipeline (POST /api/v1/tryon)
      let tryonResult = null;
      let renderedImageUrl = null;
      if (pFile && gFile) {
        try {
          const category = selectedCategory || selectedGarment?.category || 'upper_body';
          tryonResult = await simulationService.executeTryOn({
            personFile: pFile,
            garmentFile: gFile,
            garmentCategory: category === 'pants' || category === 'jeans' ? 'lower_body' : category === 'dress' ? 'full_body' : 'upper_body',
            engine: 'idm_vton',
            sync: true
          });

          if (tryonResult?.image_ref) {
            const apiBase = import.meta.env.VITE_API_BASE_URL || import.meta.env.VITE_API_URL || 'http://localhost:8000';
            const serverBase = apiBase.replace(/\/api\/v1\/?$/, '').replace(/\/api\/?$/, '');
            const cleanPath = tryonResult.image_ref.replace(/\\/g, '/').replace(/^\//, '');
            // Add cache-busting timestamp to prevent browser from serving stale cached image
            renderedImageUrl = `${serverBase}/${cleanPath}?t=${Date.now()}`;
            console.log('[TRYON:IMAGE_REF]', tryonResult.image_ref);
            console.log('[TRYON:RENDERED_URL]', renderedImageUrl);
          } else {
            console.warn('[TRYON:RESPONSE] No image_ref in response:', tryonResult);
          }
        } catch (tryonErr) {
          // Surface error to user instead of silently falling back to recommendation image
          const errMsg = tryonErr?.message || 'AI Try-On inference failed. Please try again.';
          console.error('[TRYON:ERROR]', errMsg, tryonErr);
          setError(errMsg);
        }
      }

      const topRecImage = recommendationResult?.recommendations?.[0]?.image;
      const finalImage = renderedImageUrl || topRecImage || personImage?.previewUrl;

      const finalResult = {
        ...recommendationResult,
        tryon: tryonResult,
        renderedImageUrl: finalImage,
        originalImageUrl: personImage.previewUrl,
        garmentImageUrl: garmentImage.previewUrl || selectedGarment?.image,
      };

      setSimulationResult(finalResult);
      setResultImage(finalImage);
      setSimulationStatus('completed');
      setProgress(100);

      return finalResult;
    } catch (err) {
      const errorMsg = typeof err === 'object' ? (err.message || 'Simulation process failed. Please try again.') : String(err);
      setError(errorMsg);
      setSimulationStatus('failed');
      setProgress(0);
      return null;
    }
  }, [personImage, garmentImage, selectedGarment, selectedCategory, settings, user, setError]);

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
