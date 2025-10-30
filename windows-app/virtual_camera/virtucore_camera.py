import ctypes
import struct
import numpy as np
import cv2
import time
import logging
from ctypes import wintypes

logger = logging.getLogger(__name__)

GENERIC_READ = 0x80000000
GENERIC_WRITE = 0x40000000
OPEN_EXISTING = 3
INVALID_HANDLE_VALUE = -1

IOCTL_VCAM_SEND_FRAME = 0x222000
IOCTL_VCAM_GET_STATUS = 0x222001
IOCTL_VCAM_SET_FORMAT = 0x222002

FORMAT_RGB24 = 0
FORMAT_NV12 = 1
FORMAT_YUY2 = 2

class VirtuCoreCamera:
    def __init__(self, device_path="\\\\.\\VirtualCamera"):
        self.kernel32 = ctypes.windll.kernel32
        self.device_path = device_path
        self.handle = None
        self.is_open = False
        
    def check_driver_installed(self) -> bool:
        """بررسی نصب درایور"""
        try:
            handle = self.kernel32.CreateFileW(
                self.device_path,
                GENERIC_READ,
                0, None, OPEN_EXISTING, 0, None
            )
            
            if handle == INVALID_HANDLE_VALUE:
                return False
            
            self.kernel32.CloseHandle(handle)
            return True
        except Exception as e:
            logger.error(f"خطا در بررسی درایور: {e}")
            return False
    
    def open(self) -> bool:
        """باز کردن اتصال به درایور"""
        if self.is_open:
            return True
        
        try:
            self.handle = self.kernel32.CreateFileW(
                self.device_path,
                GENERIC_READ | GENERIC_WRITE,
                0, None, OPEN_EXISTING, 0, None
            )
            
            if self.handle == INVALID_HANDLE_VALUE:
                error_code = self.kernel32.GetLastError()
                logger.error(f"خطا در باز کردن درایور دوربین. کد خطا: {error_code}")
                return False
            
            self.is_open = True
            logger.info("✓ اتصال به درایور دوربین VirtuCore برقرار شد")
            return True
            
        except Exception as e:
            logger.error(f"خطا در open: {e}")
            return False
    
    def close(self):
        """بستن اتصال"""
        if self.handle and self.handle != INVALID_HANDLE_VALUE:
            try:
                self.kernel32.CloseHandle(self.handle)
                logger.info("اتصال به درایور دوربین بسته شد")
            except:
                pass
        
        self.handle = None
        self.is_open = False
    
    def send_frame(self, frame: np.ndarray, width: int = None, height: int = None) -> bool:
        """
        ارسال یک فریم به درایور
        
        Args:
            frame: آرایه numpy در فرمت BGR (OpenCV)
            width: عرض فریم (اختیاری، از shape استخراج می‌شود)
            height: ارتفاع فریم (اختیاری، از shape استخراج می‌شود)
        """
        if not self.is_open or self.handle == INVALID_HANDLE_VALUE:
            logger.warning("درایور دوربین باز نیست")
            return False
        
        try:
            h, w = frame.shape[:2]
            if width is None:
                width = w
            if height is None:
                height = h
            
            # تبدیل BGR به RGB
            if len(frame.shape) == 3 and frame.shape[2] == 3:
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            else:
                frame_rgb = frame
            
            # Resize اگر لازم باشد
            if w != width or h != height:
                frame_rgb = cv2.resize(frame_rgb, (width, height))
            
            frame_bytes = frame_rgb.tobytes()
            
            # ساخت header
            header = struct.pack('IIIIQ', 
                width,
                height,
                FORMAT_RGB24,
                len(frame_bytes),
                int(time.time() * 1e7)
            )
            
            # ترکیب header و داده
            buffer = header + frame_bytes
            bytes_returned = wintypes.DWORD()
            
            # ارسال به درایور
            result = self.kernel32.DeviceIoControl(
                self.handle,
                IOCTL_VCAM_SEND_FRAME,
                buffer,
                len(buffer),
                None, 0,
                ctypes.byref(bytes_returned),
                None
            )
            
            if not result:
                error_code = self.kernel32.GetLastError()
                logger.error(f"خطا در ارسال فریم. کد خطا: {error_code}")
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"خطا در send_frame: {e}")
            return False
    
    def get_status(self) -> dict:
        """دریافت وضعیت درایور"""
        if not self.is_open or self.handle == INVALID_HANDLE_VALUE:
            return None
        
        try:
            status_buffer = ctypes.create_string_buffer(20)
            bytes_returned = wintypes.DWORD()
            
            result = self.kernel32.DeviceIoControl(
                self.handle,
                IOCTL_VCAM_GET_STATUS,
                None, 0,
                status_buffer,
                len(status_buffer),
                ctypes.byref(bytes_returned),
                None
            )
            
            if not result:
                return None
            
            is_streaming, width, height, format_type, frames_delivered = struct.unpack(
                'IIIII', status_buffer.raw
            )
            
            return {
                'is_streaming': bool(is_streaming),
                'width': width,
                'height': height,
                'format': format_type,
                'frames_delivered': frames_delivered
            }
            
        except Exception as e:
            logger.error(f"خطا در get_status: {e}")
            return None
    
    def __enter__(self):
        self.open()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
        return False

