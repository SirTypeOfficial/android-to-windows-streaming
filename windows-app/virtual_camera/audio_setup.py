import logging
import subprocess
import os
import winreg
import urllib.request
import zipfile
import tempfile
from pathlib import Path

logger = logging.getLogger(__name__)

class VirtualAudioSetup:
    def __init__(self):
        self.vb_cable_url = "https://download.vb-audio.com/Download_CABLE/VBCABLE_Driver_Pack43.zip"
        self.temp_dir = Path(tempfile.gettempdir()) / "vb_audio_setup"
        
    def is_virtual_audio_installed(self) -> bool:
        """بررسی نصب VB-Audio Virtual Cable"""
        try:
            import pyaudio
            p = pyaudio.PyAudio()
            
            for i in range(p.get_device_count()):
                info = p.get_device_info_by_index(i)
                name = info['name'].lower()
                
                if 'cable' in name or 'vb-audio' in name or 'virtual' in name:
                    p.terminate()
                    logger.info(f"✓ Virtual audio یافت شد: {info['name']}")
                    return True
            
            p.terminate()
            return False
        except:
            return False
    
    def download_vb_cable(self) -> bool:
        """دانلود VB-Audio Cable"""
        try:
            logger.info("در حال دانلود VB-Audio Cable...")
            self.temp_dir.mkdir(parents=True, exist_ok=True)
            
            zip_path = self.temp_dir / "vb_cable.zip"
            
            urllib.request.urlretrieve(self.vb_cable_url, zip_path)
            logger.info("✓ دانلود کامل شد")
            
            # استخراج
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(self.temp_dir)
            
            logger.info("✓ فایل‌ها استخراج شدند")
            return True
            
        except Exception as e:
            logger.error(f"خطا در دانلود: {e}")
            return False
    
    def install_vb_cable(self) -> bool:
        """نصب VB-Audio Cable"""
        try:
            installer_path = self.temp_dir / "VBCABLE_Setup_x64.exe"
            
            if not installer_path.exists():
                logger.error("فایل نصب یافت نشد")
                return False
            
            logger.info("در حال نصب VB-Audio Cable...")
            logger.warning("نیاز به دسترسی Administrator است")
            
            # اجرای نصاب
            result = subprocess.run(
                [str(installer_path), "/S"],  # Silent install
                check=False
            )
            
            if result.returncode == 0:
                logger.info("✓ نصب کامل شد")
                logger.info("لطفاً سیستم را restart کنید")
                return True
            else:
                logger.error("نصب ناموفق بود")
                return False
                
        except Exception as e:
            logger.error(f"خطا در نصب: {e}")
            return False
    
    def get_manual_install_instructions(self) -> str:
        """راهنمای نصب دستی"""
        return """
╔════════════════════════════════════════════════════════╗
║         نصب Virtual Audio Device (اختیاری)           ║
╚════════════════════════════════════════════════════════╝

برای routing صدا به نرم‌افزارهای دیگر:

نصب دستی:
1. دانلود: https://vb-audio.com/Cable/
2. اجرای فایل VBCABLE_Setup_x64.exe
3. Restart سیستم
4. اجرای مجدد برنامه

تنظیمات:
- در ویندوز: Settings > System > Sound
- Output Device: CABLE Input
- Input Device: CABLE Output

نکته: بدون Virtual Audio Cable، صدا از بلندگوی پیش‌فرض سیستم پخش می‌شود
"""
    
    def cleanup(self):
        """پاکسازی فایل‌های موقت"""
        try:
            import shutil
            if self.temp_dir.exists():
                shutil.rmtree(self.temp_dir)
                logger.info("✓ فایل‌های موقت پاک شدند")
        except:
            pass

