import logging
import numpy as np
import cv2

logger = logging.getLogger(__name__)

class VirtualCameraInterface:
    def __init__(self):
        self.camera = None
        self.is_running = False
        self.width = 1920
        self.height = 1080
        self.fps = 30
        
    def start(self) -> bool:
        try:
            import pyvirtualcam
            
            self.camera = pyvirtualcam.Camera(
                width=self.width,
                height=self.height,
                fps=self.fps,
                fmt=pyvirtualcam.PixelFormat.RGB
            )
            self.is_running = True
            logger.info(f"✓ Virtual camera فعال شد: {self.camera.device}")
            return True
        except Exception as e:
            logger.error(f"خطای virtual camera: {e}")
            logger.warning("نصب OBS Studio ضروری است")
            return False
    
    def stop(self):
        if self.camera:
            try:
                self.camera.close()
            except:
                pass
            self.camera = None
        self.is_running = False
    
    def send_frame(self, frame: np.ndarray):
        if not self.is_running or not self.camera:
            return
        
        try:
            h, w = frame.shape[:2]
            if w != self.width or h != self.height:
                frame = cv2.resize(frame, (self.width, self.height))
            
            if len(frame.shape) == 3 and frame.shape[2] == 3:
                self.camera.send(frame)
        except Exception as e:
            logger.error(f"خطا در ارسال فریم: {e}")
    
    def is_active(self) -> bool:
        return self.is_running

