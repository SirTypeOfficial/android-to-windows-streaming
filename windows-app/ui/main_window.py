import logging
import cv2
import numpy as np
from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                              QPushButton, QLabel, QComboBox, QSlider, QGroupBox,
                              QLineEdit, QMessageBox, QCheckBox)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QImage, QPixmap
from streaming.connection import ConnectionManager
from streaming.receiver import StreamReceiver
from streaming.decoder import VideoDecoder, AudioDecoder
from control.commands import ControlCommands
from virtual_camera.interface import VirtualCameraInterface

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MainWindow(QMainWindow):
    frame_received = pyqtSignal(np.ndarray)
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Android Stream Receiver")
        self.setGeometry(100, 100, 1200, 800)
        
        self.connection_manager = ConnectionManager()
        self.stream_receiver = StreamReceiver(self.connection_manager)
        self.video_decoder = VideoDecoder()
        self.audio_decoder = AudioDecoder()
        self.control_commands = ControlCommands(self.connection_manager)
        self.virtual_camera = VirtualCameraInterface()
        
        self.is_streaming = False
        self.current_frame = None
        
        self.setup_ui()
        self.setup_connections()
        
        self.frame_received.connect(self.update_frame)
        
    def setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QHBoxLayout(central_widget)
        
        left_panel = self.create_video_panel()
        right_panel = self.create_control_panel()
        
        main_layout.addWidget(left_panel, stretch=3)
        main_layout.addWidget(right_panel, stretch=1)
    
    def create_video_panel(self):
        panel = QGroupBox("پیش‌نمایش ویدیو")
        layout = QVBoxLayout()
        
        self.video_label = QLabel()
        self.video_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.video_label.setStyleSheet("background-color: black;")
        self.video_label.setMinimumSize(640, 480)
        self.video_label.setText("در انتظار اتصال...")
        
        layout.addWidget(self.video_label)
        
        info_layout = QHBoxLayout()
        self.status_label = QLabel("وضعیت: قطع شده")
        self.fps_label = QLabel("FPS: 0")
        self.latency_label = QLabel("تأخیر: 0ms")
        
        info_layout.addWidget(self.status_label)
        info_layout.addStretch()
        info_layout.addWidget(self.fps_label)
        info_layout.addWidget(self.latency_label)
        
        layout.addLayout(info_layout)
        panel.setLayout(layout)
        
        return panel
    
    def create_control_panel(self):
        panel = QWidget()
        layout = QVBoxLayout()
        
        connection_group = self.create_connection_group()
        layout.addWidget(connection_group)
        
        settings_group = self.create_settings_group()
        layout.addWidget(settings_group)
        
        camera_group = self.create_camera_group()
        layout.addWidget(camera_group)
        
        vcam_group = self.create_vcam_group()
        layout.addWidget(vcam_group)
        
        layout.addStretch()
        panel.setLayout(layout)
        
        return panel
    
    def create_connection_group(self):
        group = QGroupBox("اتصال")
        layout = QVBoxLayout()
        
        wifi_layout = QHBoxLayout()
        wifi_label = QLabel("آدرس IP:")
        self.ip_input = QLineEdit()
        self.ip_input.setPlaceholderText("192.168.1.100")
        wifi_layout.addWidget(wifi_label)
        wifi_layout.addWidget(self.ip_input)
        layout.addLayout(wifi_layout)
        
        self.connect_wifi_btn = QPushButton("اتصال WiFi")
        self.connect_wifi_btn.clicked.connect(self.connect_wifi)
        layout.addWidget(self.connect_wifi_btn)
        
        self.connect_usb_btn = QPushButton("اتصال USB")
        self.connect_usb_btn.clicked.connect(self.connect_usb)
        layout.addWidget(self.connect_usb_btn)
        
        self.disconnect_btn = QPushButton("قطع اتصال")
        self.disconnect_btn.clicked.connect(self.disconnect)
        self.disconnect_btn.setEnabled(False)
        layout.addWidget(self.disconnect_btn)
        
        group.setLayout(layout)
        return group
    
    def create_settings_group(self):
        group = QGroupBox("تنظیمات")
        layout = QVBoxLayout()
        
        res_layout = QHBoxLayout()
        res_label = QLabel("رزولوشن:")
        self.resolution_combo = QComboBox()
        self.resolution_combo.addItems(["480p (640x480)", "720p (1280x720)", "1080p (1920x1080)"])
        self.resolution_combo.setCurrentIndex(1)
        self.resolution_combo.currentIndexChanged.connect(self.change_resolution)
        res_layout.addWidget(res_label)
        res_layout.addWidget(self.resolution_combo)
        layout.addLayout(res_layout)
        
        fps_layout = QHBoxLayout()
        fps_label = QLabel("FPS:")
        self.fps_combo = QComboBox()
        self.fps_combo.addItems(["15", "30", "60"])
        self.fps_combo.setCurrentIndex(1)
        self.fps_combo.currentIndexChanged.connect(self.change_fps)
        fps_layout.addWidget(fps_label)
        fps_layout.addWidget(self.fps_combo)
        layout.addLayout(fps_layout)
        
        brightness_layout = QVBoxLayout()
        brightness_label = QLabel("روشنایی:")
        self.brightness_slider = QSlider(Qt.Orientation.Horizontal)
        self.brightness_slider.setMinimum(0)
        self.brightness_slider.setMaximum(100)
        self.brightness_slider.setValue(50)
        self.brightness_slider.valueChanged.connect(self.change_brightness)
        brightness_layout.addWidget(brightness_label)
        brightness_layout.addWidget(self.brightness_slider)
        layout.addLayout(brightness_layout)
        
        group.setLayout(layout)
        return group
    
    def create_camera_group(self):
        group = QGroupBox("کنترل دوربین")
        layout = QVBoxLayout()
        
        self.switch_camera_btn = QPushButton("تغییر دوربین")
        self.switch_camera_btn.clicked.connect(self.switch_camera)
        layout.addWidget(self.switch_camera_btn)
        
        self.flash_checkbox = QCheckBox("فلش")
        self.flash_checkbox.stateChanged.connect(self.toggle_flash)
        layout.addWidget(self.flash_checkbox)
        
        group.setLayout(layout)
        return group
    
    def create_vcam_group(self):
        group = QGroupBox("دوربین مجازی")
        layout = QVBoxLayout()
        
        self.vcam_status_label = QLabel("وضعیت: غیرفعال")
        layout.addWidget(self.vcam_status_label)
        
        self.vcam_toggle_btn = QPushButton("فعال‌سازی دوربین مجازی")
        self.vcam_toggle_btn.clicked.connect(self.toggle_virtual_camera)
        layout.addWidget(self.vcam_toggle_btn)
        
        group.setLayout(layout)
        return group
    
    def setup_connections(self):
        self.connection_manager.on_connected = self.on_connected
        self.connection_manager.on_disconnected = self.on_disconnected
        
        self.video_decoder.on_frame_decoded = self.on_frame_decoded
        
        self.stream_receiver.on_video_frame = self.video_decoder.decode
        self.stream_receiver.on_audio_frame = self.audio_decoder.decode
    
    def connect_wifi(self):
        ip = self.ip_input.text().strip()
        if not ip:
            QMessageBox.warning(self, "خطا", "لطفاً آدرس IP را وارد کنید")
            return
        
        if self.connection_manager.connect_wifi(ip):
            self.stream_receiver.start()
        else:
            QMessageBox.critical(self, "خطا", "اتصال WiFi ناموفق بود")
    
    def connect_usb(self):
        if self.connection_manager.connect_usb():
            self.stream_receiver.start()
        else:
            QMessageBox.critical(self, "خطا", "اتصال USB ناموفق بود. مطمئن شوید که ADB نصب است و دستگاه متصل است")
    
    def disconnect(self):
        self.stream_receiver.stop()
        self.connection_manager.disconnect()
    
    def on_connected(self):
        self.status_label.setText("وضعیت: متصل")
        self.connect_wifi_btn.setEnabled(False)
        self.connect_usb_btn.setEnabled(False)
        self.disconnect_btn.setEnabled(True)
        self.is_streaming = True
        logger.info("Connected to Android device")
    
    def on_disconnected(self):
        self.status_label.setText("وضعیت: قطع شده")
        self.connect_wifi_btn.setEnabled(True)
        self.connect_usb_btn.setEnabled(True)
        self.disconnect_btn.setEnabled(False)
        self.is_streaming = False
        self.video_label.setText("در انتظار اتصال...")
        logger.info("Disconnected from Android device")
    
    def on_frame_decoded(self, frame: np.ndarray):
        self.current_frame = frame
        self.frame_received.emit(frame)
        
        if self.virtual_camera.is_active():
            self.virtual_camera.send_frame(frame)
    
    def update_frame(self, frame: np.ndarray):
        height, width, channel = frame.shape
        bytes_per_line = 3 * width
        
        q_image = QImage(frame.data, width, height, bytes_per_line, QImage.Format.Format_BGR888)
        pixmap = QPixmap.fromImage(q_image)
        
        scaled_pixmap = pixmap.scaled(
            self.video_label.size(),
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        )
        
        self.video_label.setPixmap(scaled_pixmap)
    
    def change_resolution(self):
        index = self.resolution_combo.currentIndex()
        resolutions = [(640, 480), (1280, 720), (1920, 1080)]
        width, height = resolutions[index]
        self.control_commands.set_resolution(width, height)
    
    def change_fps(self):
        fps = int(self.fps_combo.currentText())
        self.control_commands.set_fps(fps)
    
    def change_brightness(self):
        value = self.brightness_slider.value() / 100.0
        self.control_commands.set_brightness(value)
    
    def switch_camera(self):
        self.control_commands.switch_camera("back")
    
    def toggle_flash(self):
        enabled = self.flash_checkbox.isChecked()
        self.control_commands.set_flash(enabled)
    
    def toggle_virtual_camera(self):
        if self.virtual_camera.is_active():
            self.virtual_camera.stop()
            self.vcam_status_label.setText("وضعیت: غیرفعال")
            self.vcam_toggle_btn.setText("فعال‌سازی دوربین مجازی")
        else:
            if self.virtual_camera.start():
                self.vcam_status_label.setText("وضعیت: فعال")
                self.vcam_toggle_btn.setText("غیرفعال‌سازی دوربین مجازی")
            else:
                QMessageBox.warning(self, "خطا", "فعال‌سازی دوربین مجازی ناموفق بود")
    
    def closeEvent(self, event):
        self.disconnect()
        self.virtual_camera.stop()
        self.video_decoder.close()
        self.audio_decoder.close()
        event.accept()

