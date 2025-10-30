import sys
import logging
from PyQt6.QtWidgets import QApplication
from ui.main_window import MainWindow
from virtual_camera.device_manager import VirtualDeviceManager

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('android_stream.log', encoding='utf-8')
    ]
)

logger = logging.getLogger(__name__)

def main():
    logger.info("=" * 50)
    logger.info("Android Stream Receiver")
    logger.info("=" * 50)
    
    device_manager = VirtualDeviceManager()
    
    # راه‌اندازی virtual camera
    camera_ok = device_manager.setup_obs_virtual_camera()
    
    # راه‌اندازی virtual audio
    audio_ok = device_manager.setup_virtual_audio()
    
    if not camera_ok:
        logger.warning("⚠ Virtual camera در دسترس نیست")
    
    app = QApplication(sys.argv)
    app.setApplicationName("Android Stream Receiver")
    
    window = MainWindow()
    window.device_manager = device_manager
    window.show()
    
    try:
        exit_code = app.exec()
    finally:
        logger.info("پاکسازی...")
        device_manager.cleanup()
    
    sys.exit(exit_code)

if __name__ == "__main__":
    main()

