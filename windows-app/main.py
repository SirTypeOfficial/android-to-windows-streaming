import sys
import logging
from PyQt6.QtWidgets import QApplication
from ui.main_window import MainWindow

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('android_stream.log', encoding='utf-8')
    ]
)

def main():
    app = QApplication(sys.argv)
    app.setApplicationName("Android Stream Receiver")
    
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()

