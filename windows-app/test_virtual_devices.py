"""
تست دستگاه‌های مجازی
"""
import sys
import logging
import time
import numpy as np

logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_imports():
    """تست import کتابخانه‌ها"""
    print("\n" + "="*60)
    print("تست 1: بررسی imports")
    print("="*60)
    
    try:
        import pyvirtualcam
        print("✓ pyvirtualcam")
    except ImportError as e:
        print(f"❌ pyvirtualcam: {e}")
        return False
    
    try:
        import pyaudio
        print("✓ pyaudio")
    except ImportError as e:
        print(f"❌ pyaudio: {e}")
        return False
    
    try:
        import cv2
        print("✓ opencv (cv2)")
    except ImportError as e:
        print(f"❌ opencv: {e}")
        return False
    
    try:
        import numpy
        print("✓ numpy")
    except ImportError as e:
        print(f"❌ numpy: {e}")
        return False
    
    return True

def test_obs_controller():
    """تست کنترل کننده OBS"""
    print("\n" + "="*60)
    print("تست 2: OBS Controller")
    print("="*60)
    
    try:
        from virtual_camera.obs_controller import OBSController
        
        obs = OBSController()
        
        if obs.is_obs_installed():
            print(f"✓ OBS نصب شده: {obs.obs_path}")
        else:
            print("❌ OBS نصب نشده")
            return False
        
        if obs.check_virtual_camera_status():
            print("✓ Virtual Camera در دسترس است")
            return True
        else:
            print("⚠ Virtual Camera فعال نیست")
            print("  راهنما: OBS > Tools > Start Virtual Camera")
            return False
            
    except Exception as e:
        print(f"❌ خطا: {e}")
        return False

def test_audio_setup():
    """تست راه‌اندازی صدا"""
    print("\n" + "="*60)
    print("تست 3: Audio Setup")
    print("="*60)
    
    try:
        from virtual_camera.audio_setup import VirtualAudioSetup
        
        audio = VirtualAudioSetup()
        
        if audio.is_virtual_audio_installed():
            print("✓ Virtual Audio Device یافت شد")
            return True
        else:
            print("⚠ Virtual Audio Device یافت نشد")
            print("  برنامه از دستگاه پیش‌فرض استفاده می‌کند")
            return True  # Not critical
            
    except Exception as e:
        print(f"❌ خطا: {e}")
        return False

def test_device_manager():
    """تست مدیر دستگاه‌ها"""
    print("\n" + "="*60)
    print("تست 4: Device Manager")
    print("="*60)
    
    try:
        from virtual_camera.device_manager import VirtualDeviceManager
        
        manager = VirtualDeviceManager()
        
        camera_ok = manager.setup_obs_virtual_camera()
        audio_ok = manager.setup_virtual_audio()
        
        if camera_ok:
            print("✓ Virtual Camera راه‌اندازی شد")
        else:
            print("❌ Virtual Camera راه‌اندازی نشد")
        
        if audio_ok:
            print("✓ Virtual Audio راه‌اندازی شد")
        else:
            print("⚠ Virtual Audio با مشکل مواجه شد")
        
        manager.cleanup()
        return camera_ok
        
    except Exception as e:
        print(f"❌ خطا: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_virtual_camera():
    """تست ارسال فریم به دوربین مجازی"""
    print("\n" + "="*60)
    print("تست 5: Virtual Camera Interface")
    print("="*60)
    
    try:
        from virtual_camera.interface import VirtualCameraInterface
        
        camera = VirtualCameraInterface()
        
        if not camera.start():
            print("❌ راه‌اندازی Virtual Camera ناموفق")
            return False
        
        print("✓ Virtual Camera راه‌اندازی شد")
        
        # ارسال چند فریم تست
        print("ارسال فریم‌های تست...")
        for i in range(5):
            # ایجاد یک فریم رنگی تست
            color = (i * 50, 100, 200 - i * 40)
            frame = np.full((1080, 1920, 3), color, dtype=np.uint8)
            
            camera.send_frame(frame)
            print(f"  فریم {i+1}/5 ارسال شد")
            time.sleep(0.1)
        
        camera.stop()
        print("✓ تست کامل شد")
        return True
        
    except Exception as e:
        print(f"❌ خطا: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    print("\n" + "="*60)
    print("    تست سیستم دستگاه‌های مجازی")
    print("="*60)
    
    results = []
    
    # اجرای تست‌ها
    results.append(("Imports", test_imports()))
    results.append(("OBS Controller", test_obs_controller()))
    results.append(("Audio Setup", test_audio_setup()))
    results.append(("Device Manager", test_device_manager()))
    
    # تست Virtual Camera فقط اگر OBS در دسترس باشد
    if results[1][1]:  # OBS Controller OK
        results.append(("Virtual Camera", test_virtual_camera()))
    
    # نمایش خلاصه
    print("\n" + "="*60)
    print("    خلاصه نتایج")
    print("="*60)
    
    passed = 0
    failed = 0
    
    for name, result in results:
        if result:
            print(f"✓ {name}")
            passed += 1
        else:
            print(f"❌ {name}")
            failed += 1
    
    print()
    print(f"موفق: {passed}/{len(results)}")
    print(f"ناموفق: {failed}/{len(results)}")
    
    if failed == 0:
        print("\n🎉 همه تست‌ها موفق بودند!")
        print("برای اجرای برنامه: python main.py")
    else:
        print("\n⚠ برخی تست‌ها ناموفق بودند")
        print("لطفاً راهنماها را مطالعه کنید:")
        print("  - QUICK_START.md")
        print("  - OBS_SETUP.md")
        print("  - VIRTUAL_DEVICES_README.md")
    
    print()

if __name__ == "__main__":
    main()

