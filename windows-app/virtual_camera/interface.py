import logging
import mmap
import numpy as np
from typing import Optional

logger = logging.getLogger(__name__)

class VirtualCameraInterface:
    def __init__(self):
        self.shared_memory: Optional[mmap.mmap] = None
        self.is_running = False
        self.frame_size = 1920 * 1080 * 3
        self.shared_memory_name = "VirtualCameraSharedMemory"
        
    def start(self) -> bool:
        try:
            self.shared_memory = mmap.mmap(-1, self.frame_size, self.shared_memory_name)
            self.is_running = True
            logger.info("Virtual camera interface started")
            return True
        except Exception as e:
            logger.error(f"Failed to start virtual camera interface: {e}")
            return False
    
    def stop(self):
        if self.shared_memory:
            try:
                self.shared_memory.close()
            except:
                pass
            self.shared_memory = None
        
        self.is_running = False
        logger.info("Virtual camera interface stopped")
    
    def send_frame(self, frame: np.ndarray):
        if not self.is_running or not self.shared_memory:
            return
        
        try:
            height, width, channels = frame.shape
            
            if width != 1920 or height != 1080:
                frame = np.array(frame)
                import cv2
                frame = cv2.resize(frame, (1920, 1080))
            
            frame_bytes = frame.tobytes()
            
            self.shared_memory.seek(0)
            self.shared_memory.write(frame_bytes[:self.frame_size])
            
        except Exception as e:
            logger.error(f"Error sending frame to virtual camera: {e}")
    
    def is_active(self) -> bool:
        return self.is_running

