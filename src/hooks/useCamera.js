import { useState, useRef, useCallback, useEffect } from 'react';

export const useCamera = () => {
  const videoRef = useRef(null);
  const [stream, setStream] = useState(null);
  const [isCameraActive, setIsCameraActive] = useState(false);
  const [cameraError, setCameraError] = useState(null);
  const [facingMode, setFacingMode] = useState('user'); // 'user' (front) or 'environment' (back)
  const [capturedImage, setCapturedImage] = useState(null);

  // Start webcam stream
  const startCamera = useCallback(async () => {
    setCameraError(null);
    try {
      if (!navigator.mediaDevices?.getUserMedia) {
        throw new Error('Webcam access is not supported by your browser.');
      }

      const mediaStream = await navigator.mediaDevices.getUserMedia({
        video: {
          facingMode,
          width: { ideal: 1280 },
          height: { ideal: 720 },
        },
        audio: false,
      });

      setStream(mediaStream);
      setIsCameraActive(true);

      if (videoRef.current) {
        videoRef.current.srcObject = mediaStream;
      }
    } catch (err) {
      const msg =
        err.name === 'NotAllowedError' || err.name === 'PermissionDeniedError'
          ? 'Camera permission denied. Please allow access in browser settings.'
          : err.name === 'NotFoundError' || err.name === 'DevicesNotFoundError'
            ? 'No webcam device found on your system.'
            : err.message || 'Failed to initialize camera.';
      setCameraError(msg);
      setIsCameraActive(false);
    }
  }, [facingMode]);

  // Stop webcam stream
  const stopCamera = useCallback(() => {
    if (stream) {
      stream.getTracks().forEach((track) => track.stop());
      setStream(null);
    }
    setIsCameraActive(false);
  }, [stream]);

  // Switch between front and rear cameras
  const toggleFacingMode = useCallback(() => {
    setFacingMode((prev) => (prev === 'user' ? 'environment' : 'user'));
  }, []);

  // Capture current video frame to image file
  const capturePhoto = useCallback(() => {
    if (!videoRef.current) return null;

    const video = videoRef.current;
    const canvas = document.createElement('canvas');
    canvas.width = video.videoWidth || 640;
    canvas.height = video.videoHeight || 480;

    const ctx = canvas.getContext('2d');
    if (facingMode === 'user') {
      // Mirror front camera preview for realistic selfie feel
      ctx.translate(canvas.width, 0);
      ctx.scale(-1, 1);
    }
    ctx.drawImage(video, 0, 0, canvas.width, canvas.height);

    const dataUrl = canvas.toDataURL('image/jpeg', 0.92);

    // Convert DataURL to File object for upload compatibility
    const arr = dataUrl.split(',');
    const mime = arr[0].match(/:(.*?);/)[1];
    const bstr = atob(arr[1]);
    let n = bstr.length;
    const u8arr = new Uint8Array(n);
    while (n--) {
      u8arr[n] = bstr.charCodeAt(n);
    }
    const file = new File([u8arr], `camera-avatar-${Date.now()}.jpg`, { type: mime });

    const photoData = {
      file,
      previewUrl: dataUrl,
      name: file.name,
      size: file.size,
    };

    setCapturedImage(photoData);
    return photoData;
  }, [facingMode]);

  // Cleanup media tracks on unmount
  useEffect(() => {
    return () => {
      if (stream) {
        stream.getTracks().forEach((track) => track.stop());
      }
    };
  }, [stream]);

  return {
    videoRef,
    isCameraActive,
    cameraError,
    facingMode,
    capturedImage,
    setCapturedImage,
    startCamera,
    stopCamera,
    toggleFacingMode,
    capturePhoto,
  };
};
