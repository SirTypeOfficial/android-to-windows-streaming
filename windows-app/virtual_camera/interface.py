import logging
import numpy as np
from .virtucore_camera import VirtuCoreCamera

logger = logging.getLogger(__name__)

class VirtualCameraInterface:
    def __init__(self):
        self.camera = VirtuCoreCamera()
        self.is_running = False
        self.width = 1920
        self.height = 1080
        
    def start(self) -> bool:
        """راه‌اندازی دوربین مجازی VirtuCore"""
        try:
            if self.camera.open():
                self.is_running = True
                logger.info("✓ دوربین مجازی VirtuCore فعال شد")
                return True
            else:
                logger.error("خطا در باز کردن درایور دوربین")
                return False
        except Exception as e:
            logger.error(f"خطای virtual camera: {e}")
            return False
    
    def stop(self):
        """توقف دوربین مجازی"""
        if self.camera:
            try:
                self.camera.close()
            except:
                pass
        self.is_running = False
    
    def send_frame(self, frame: np.ndarray):
        """ارسال فریم به دوربین مجازی"""
        if not self.is_running:
            return
        
        try:
            self.camera.send_frame(frame, self.width, self.height)
        except Exception as e:
            logger.error(f"خطا در ارسال فریم: {e}")
    
    def is_active(self) -> bool:
        """بررسی وضعیت فعال بودن"""
        return self.is_running
    
    def get_status(self) -> dict:
        """دریافت وضعیت درایور"""
        if self.is_running:
            return self.camera.get_status()
        return None

