import logging

logger = logging.getLogger(__name__)

class VirtualDeviceManager:
    def __init__(self):
        self.camera = None
        self.microphone = None
        
    def setup_virtucore_drivers(self) -> bool:
        """بررسی نصب درایورهای VirtuCore"""
        try:
            from .virtucore_camera import VirtuCoreCamera
            from .virtucore_microphone import VirtuCoreMicrophone
            
            camera = VirtuCoreCamera()
            mic = VirtuCoreMicrophone()
            
            camera_ok = camera.check_driver_installed()
            mic_ok = mic.check_driver_installed()
            
            if not camera_ok:
                logger.error("❌ درایور دوربین VirtuCore نصب نیست")
                logger.info(self._get_driver_install_instructions())
                return False
            
            if not mic_ok:
                logger.warning("⚠ درایور میکروفون VirtuCore نصب نیست")
            
            logger.info("✓ درایورهای VirtuCore آماده هستند")
            return True
            
        except ImportError as e:
            logger.error(f"خطا در import ماژول‌های VirtuCore: {e}")
            return False
        except Exception as e:
            logger.error(f"خطا در بررسی درایورها: {e}")
            return False
    
    def _get_driver_install_instructions(self) -> str:
        """راهنمای نصب درایورها"""
        return """
╔════════════════════════════════════════════════════════╗
║         نصب درایورهای VirtuCore                      ║
╚════════════════════════════════════════════════════════╝

مراحل نصب:
1. فعال‌سازی Test Signing (در PowerShell با Admin):
   bcdedit /set testsigning on
   
2. Restart سیستم

3. نصب درایور دوربین:
   cd virtual-camera\\avstream-camera
   install.bat (با Admin)

4. نصب درایور میکروفون:
   cd virtual-camera\\portcls-microphone
   install.bat (با Admin)

5. اجرای مجدد این برنامه

برای اطلاعات بیشتر:
virtual-camera\\BUILD_INSTRUCTIONS.md
"""
    
    def cleanup(self):
        """پاکسازی منابع"""
        if self.camera:
            try:
                self.camera.close()
            except:
                pass
        
        if self.microphone:
            try:
                self.microphone.close()
            except:
                pass
        
        logger.info("✓ پاکسازی کامل شد")

