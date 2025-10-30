import logging
import subprocess
import os
import time
import winreg
from pathlib import Path

logger = logging.getLogger(__name__)

class OBSController:
    def __init__(self):
        self.obs_path = self._find_obs_path()
        self.obs_process = None
        
    def _find_obs_path(self) -> str:
        """یافتن مسیر نصب OBS"""
        paths = [
            r"C:\Program Files\obs-studio\bin\64bit\obs64.exe",
            r"C:\Program Files (x86)\obs-studio\bin\64bit\obs64.exe",
        ]
        
        for path in paths:
            if os.path.exists(path):
                logger.info(f"✓ OBS یافت شد: {path}")
                return path
        
        # بررسی registry
        try:
            key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\OBS Studio")
            value, _ = winreg.QueryValueEx(key, "")
            winreg.CloseKey(key)
            return os.path.join(value, "bin", "64bit", "obs64.exe")
        except:
            pass
        
        logger.warning("OBS Studio یافت نشد")
        return None
    
    def is_obs_installed(self) -> bool:
        """بررسی نصب OBS"""
        return self.obs_path is not None and os.path.exists(self.obs_path)
    
    def start_obs_minimized(self) -> bool:
        """راه‌اندازی OBS به صورت minimize"""
        if not self.is_obs_installed():
            logger.error("OBS نصب نیست")
            return False
        
        try:
            # بررسی اگر قبلاً در حال اجرا است
            result = subprocess.run(
                ["tasklist", "/FI", "IMAGENAME eq obs64.exe"],
                capture_output=True,
                text=True
            )
            
            if "obs64.exe" in result.stdout:
                logger.info("OBS قبلاً در حال اجرا است")
                return True
            
            # راه‌اندازی OBS
            self.obs_process = subprocess.Popen(
                [self.obs_path, "--minimize-to-tray"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            
            time.sleep(3)  # زمان برای بارگذاری
            logger.info("✓ OBS راه‌اندازی شد")
            return True
            
        except Exception as e:
            logger.error(f"خطا در راه‌اندازی OBS: {e}")
            return False
    
    def check_virtual_camera_status(self) -> bool:
        """بررسی وضعیت Virtual Camera"""
        try:
            import pyvirtualcam
            devices = pyvirtualcam.Camera.get_devices()
            return len(devices) > 0
        except:
            return False
    
    def get_setup_instructions(self) -> str:
        """راهنمای راه‌اندازی"""
        if not self.is_obs_installed():
            return """
❌ OBS Studio نصب نشده است

مراحل نصب:
1. دانلود از: https://obsproject.com/
2. نصب با تنظیمات پیش‌فرض
3. اجرای مجدد این برنامه
"""
        
        return """
✓ OBS Studio نصب شده است

برای فعال‌سازی Virtual Camera:
1. OBS را باز کنید
2. Tools > Start Virtual Camera
3. OBS را minimize کنید (نبندید)
4. برنامه را اجرا کنید

نکته: OBS باید در پس‌زمینه باز باشد
"""

