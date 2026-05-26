import { useEffect, useRef, useState, useCallback } from 'react';

export function useMediaPipe(videoRef, canvasRef) {
  const [isLoading, setIsLoading] = useState(true);
  const [fps, setFps] = useState(0);
  const landmarksCallback = useRef(null);
  const frameCount = useRef(0);
  const lastFpsTime = useRef(Date.now());

  const setOnLandmarks = useCallback((cb) => {
    landmarksCallback.current = cb;
  }, []);

  useEffect(() => {
    if (!videoRef.current || !canvasRef.current) return;

    const video = videoRef.current;
    const canvas = canvasRef.current;
    const ctx = canvas.getContext('2d');
    let poseInstance = null;
    let cameraInstance = null;
    let animationId = null;
    let stopped = false;

    const initMediaPipe = async () => {
      // Wait for MediaPipe to load from CDN
      while (!window.Pose && !stopped) {
        await new Promise(r => setTimeout(r, 100));
      }
      if (stopped) return;

      poseInstance = new window.Pose({
        locateFile: (file) => {
          return `https://cdn.jsdelivr.net/npm/@mediapipe/pose@0.5.1675469404/${file}`;
        }
      });

      poseInstance.setOptions({
        modelComplexity: 1,
        smoothLandmarks: true,
        enableSegmentation: false,
        minDetectionConfidence: 0.5,
        minTrackingConfidence: 0.5,
      });

      poseInstance.onResults((results) => {
        if (stopped) return;

        // Update FPS
        frameCount.current++;
        const now = Date.now();
        if (now - lastFpsTime.current >= 1000) {
          setFps(frameCount.current);
          frameCount.current = 0;
          lastFpsTime.current = now;
        }

        // Draw on canvas
        ctx.save();
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        ctx.drawImage(results.image, 0, 0, canvas.width, canvas.height);

        if (results.poseLandmarks) {
          // Draw connections
          if (window.drawConnectors && window.POSE_CONNECTIONS) {
            window.drawConnectors(ctx, results.poseLandmarks, window.POSE_CONNECTIONS, {
              color: 'rgba(59, 130, 246, 0.4)',
              lineWidth: 2,
            });
          }
          // Draw landmarks
          if (window.drawLandmarks) {
            window.drawLandmarks(ctx, results.poseLandmarks, {
              color: '#3b82f6',
              lineWidth: 1,
              radius: 3,
            });
          }

          // Send landmarks to callback
          if (landmarksCallback.current) {
            const landmarks = results.poseLandmarks.map(lm => ({
              x: lm.x, y: lm.y, z: lm.z, visibility: lm.visibility
            }));
            landmarksCallback.current(landmarks);
          }
        }
        ctx.restore();
      });

      try {
        // Start camera
        const stream = await navigator.mediaDevices.getUserMedia({
          video: { width: 1280, height: 720, facingMode: 'user' }
        });
        if (stopped) {
          stream.getTracks().forEach(t => t.stop());
          return;
        }
        video.srcObject = stream;
        await video.play();

        // Set canvas dimensions
        canvas.width = video.videoWidth || 1280;
        canvas.height = video.videoHeight || 720;

        // Use Camera utility from CDN if available, otherwise manual loop
        if (window.Camera) {
          cameraInstance = new window.Camera(video, {
            onFrame: async () => {
              if (!stopped && poseInstance) {
                await poseInstance.send({ image: video });
              }
            },
            width: 1280,
            height: 720,
          });
          cameraInstance.start();
        } else {
          // Fallback: manual frame loop
          const processFrame = async () => {
            if (stopped) return;
            if (video.readyState >= 2 && poseInstance) {
              await poseInstance.send({ image: video });
            }
            animationId = requestAnimationFrame(processFrame);
          };
          processFrame();
        }

        setIsLoading(false);
      } catch (err) {
        console.error('Camera access error:', err);
        setIsLoading(false);
      }
    };

    initMediaPipe();

    return () => {
      stopped = true;
      if (cameraInstance) cameraInstance.stop();
      if (animationId) cancelAnimationFrame(animationId);
      if (poseInstance) {
        try { poseInstance.close(); } catch(e) { /* ignore */ }
      }
      if (video.srcObject) {
        video.srcObject.getTracks().forEach(t => t.stop());
      }
    };
  }, [videoRef, canvasRef]);

  return { isLoading, fps, setOnLandmarks };
}
