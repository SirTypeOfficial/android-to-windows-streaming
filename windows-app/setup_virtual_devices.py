"""
اسکریپت راه‌اندازی دستگاه‌های مجازی
"""
import sys
import logging
from virtual_camera.device_manager import VirtualDeviceManager

logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

def main():
    print("=" * 60)
    print("     راه‌اندازی دستگاه‌های مجازی     ")
    print("=" * 60)
    print()
    
    device_manager = VirtualDeviceManager()
    
    # بررسی Virtual Camera
    print("🎥 بررسی Virtual Camera...")
    camera_ok = device_manager.setup_obs_virtual_camera()
    print()
    
    # بررسی Virtual Audio
    print("🔊 بررسی Virtual Audio...")
    audio_ok = device_manager.setup_virtual_audio()
    print()
    
    # خلاصه نتایج
    print("=" * 60)
    print("     خلاصه نتایج     ")
    print("=" * 60)
    
    if camera_ok:
        print("✓ Virtual Camera: آماده")
    else:
        print("❌ Virtual Camera: نیاز به راه‌اندازی دستی")
    
    if audio_ok:
        print("✓ Virtual Audio: آماده")
    else:
        print("⚠ Virtual Audio: از دستگاه پیش‌فرض استفاده می‌شود")
    
    print()
    print("برای اجرای برنامه اصلی: python main.py")
    print()
    
    device_manager.cleanup()

if __name__ == "__main__":
    main()

