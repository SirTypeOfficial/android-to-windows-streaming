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
    logger.info("Android Stream Receiver با VirtuCore")
    logger.info("=" * 50)
    
    device_manager = VirtualDeviceManager()
    
    # بررسی نصب درایورهای VirtuCore
    drivers_ok = device_manager.setup_virtucore_drivers()
    
    if not drivers_ok:
        logger.error("برنامه بدون درایورهای VirtuCore قابل اجرا نیست")
        input("\nEnter را بزنید برای خروج...")
        sys.exit(1)
    
    app = QApplication(sys.argv)
    app.setApplicationName("Android Stream Receiver - VirtuCore")
    
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

