import pyaudio
import numpy as np
import logging
from typing import Optional

logger = logging.getLogger(__name__)

class VirtuCoreMicrophone:
    def __init__(self):
        self.pa = pyaudio.PyAudio()
        self.render_device_index = None
        self.stream: Optional[pyaudio.Stream] = None
        self.is_open = False
        
        self.sample_rate = 48000
        self.channels = 2
        self.format = pyaudio.paInt16
        
    def check_driver_installed(self) -> bool:
        """بررسی نصب درایور میکروفون مجازی"""
        try:
            self._find_virtual_mic_device()
            return self.render_device_index is not None
        except Exception as e:
            logger.error(f"خطا در بررسی درایور میکروفون: {e}")
            return False
    
    def _find_virtual_mic_device(self):
        """پیدا کردن دستگاه Virtual Microphone Input"""
        for i in range(self.pa.get_device_count()):
            try:
                info = self.pa.get_device_info_by_index(i)
                device_name = info['name']
                
                if "Virtual Microphone Input" in device_name or "Virtual Mic Input" in device_name:
                    if info['maxOutputChannels'] > 0:
                        self.render_device_index = i
                        logger.debug(f"Virtual Microphone Input یافت شد: {device_name}")
                        return
            except Exception as e:
                continue
        
        logger.warning("Virtual Microphone Input یافت نشد")
    
    def open(self) -> bool:
        """باز کردن stream صوتی"""
        if self.is_open:
            return True
        
        try:
            self._find_virtual_mic_device()
            
            if self.render_device_index is None:
                logger.error("Virtual Microphone Input یافت نشد")
                return False
            
            self.stream = self.pa.open(
                format=self.format,
                channels=self.channels,
                rate=self.sample_rate,
                output=True,
                output_device_index=self.render_device_index,
                frames_per_buffer=1024
            )
            
            self.is_open = True
            logger.info("✓ اتصال به میکروفون مجازی VirtuCore برقرار شد")
            return True
            
        except Exception as e:
            logger.error(f"خطا در باز کردن میکروفون مجازی: {e}")
            return False
    
    def close(self):
        """بستن stream صوتی"""
        if self.stream:
            try:
                self.stream.stop_stream()
                self.stream.close()
                logger.info("اتصال به میکروفون مجازی بسته شد")
            except:
                pass
            self.stream = None
        
        self.is_open = False
    
    def send_audio(self, audio_data: np.ndarray) -> bool:
        """
        ارسال داده صوتی به میکروفون مجازی
        
        Args:
            audio_data: آرایه numpy شامل sample های صوتی (int16)
        """
        if not self.is_open or not self.stream:
            return False
        
        try:
            if isinstance(audio_data, np.ndarray):
                audio_bytes = audio_data.tobytes()
            else:
                audio_bytes = audio_data
            
            self.stream.write(audio_bytes)
            return True
            
        except Exception as e:
            logger.error(f"خطا در ارسال صدا: {e}")
            return False
    
    def list_audio_devices(self):
        """لیست تمام دستگاه‌های صوتی (برای debugging)"""
        logger.info("=== دستگاه‌های صوتی موجود ===")
        for i in range(self.pa.get_device_count()):
            try:
                info = self.pa.get_device_info_by_index(i)
                logger.info(f"{i}: {info['name']}")
                logger.info(f"   Input Channels: {info['maxInputChannels']}")
                logger.info(f"   Output Channels: {info['maxOutputChannels']}")
            except:
                continue
    
    def __enter__(self):
        self.open()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
        return False
    
    def __del__(self):
        """پاکسازی هنگام حذف شیء"""
        self.close()
        try:
            self.pa.terminate()
        except:
            pass

