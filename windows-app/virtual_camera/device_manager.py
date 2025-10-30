import logging
import pyaudio
from .obs_controller import OBSController
from .audio_setup import VirtualAudioSetup

logger = logging.getLogger(__name__)

class VirtualDeviceManager:
    def __init__(self):
        self.audio_interface = None
        self.virtual_audio_output = None
        self.obs_controller = OBSController()
        self.audio_setup = VirtualAudioSetup()
        
    def setup_obs_virtual_camera(self) -> bool:
        # بررسی نصب OBS
        if not self.obs_controller.is_obs_installed():
            logger.error("❌ OBS Studio نصب نیست")
            logger.info(self.obs_controller.get_setup_instructions())
            return False
        
        # بررسی Virtual Camera
        if self.obs_controller.check_virtual_camera_status():
            logger.info("✓ Virtual Camera آماده است")
            return True
        
        # راهنمای فعال‌سازی
        logger.warning("Virtual Camera فعال نیست")
        logger.info(self.obs_controller.get_setup_instructions())
        
        # تلاش برای راه‌اندازی خودکار OBS
        logger.info("تلاش برای راه‌اندازی خودکار OBS...")
        if self.obs_controller.start_obs_minimized():
            logger.info("✓ OBS راه‌اندازی شد")
            logger.warning("لطفاً در OBS از منوی Tools گزینه Start Virtual Camera را انتخاب کنید")
            return True
        
        return False
    
    def setup_virtual_audio(self) -> bool:
        try:
            self.audio_interface = pyaudio.PyAudio()
            
            # بررسی Virtual Audio
            if self.audio_setup.is_virtual_audio_installed():
                logger.info("✓ Virtual Audio Device یافت شد")
                self._setup_audio_output()
                return True
            
            # راهنمای نصب
            logger.warning("Virtual Audio Device یافت نشد")
            logger.info(self.audio_setup.get_manual_install_instructions())
            
            # استفاده از صدای پیش‌فرض
            logger.info("استفاده از دستگاه صدای پیش‌فرض سیستم")
            self._setup_audio_output()
            return True
            
        except Exception as e:
            logger.error(f"خطای audio: {e}")
            return False
    
    def _setup_audio_output(self):
        """راه‌اندازی خروجی صدا"""
        try:
            default_output = self.audio_interface.get_default_output_device_info()
            
            self.virtual_audio_output = self.audio_interface.open(
                format=pyaudio.paInt16,
                channels=2,
                rate=48000,
                output=True,
                output_device_index=default_output['index'],
                frames_per_buffer=1024
            )
            
            logger.info(f"خروجی صدا: {default_output['name']}")
        except Exception as e:
            logger.warning(f"خطا در راه‌اندازی صدا: {e}")
    
    def play_audio(self, audio_data: bytes):
        """پخش داده صوتی"""
        if self.virtual_audio_output and audio_data:
            try:
                self.virtual_audio_output.write(audio_data)
            except:
                pass
    
    def cleanup(self):
        if self.virtual_audio_output:
            try:
                self.virtual_audio_output.stop_stream()
                self.virtual_audio_output.close()
            except:
                pass
        
        if self.audio_interface:
            try:
                self.audio_interface.terminate()
            except:
                pass
        
        self.audio_setup.cleanup()
        logger.info("✓ پاکسازی کامل شد")

