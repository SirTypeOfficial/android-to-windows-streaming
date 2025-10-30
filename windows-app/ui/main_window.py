import logging
import cv2
import numpy as np
from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                              QPushButton, QLabel, QComboBox, QSlider, QGroupBox,
                              QLineEdit, QMessageBox, QCheckBox, QRadioButton, QButtonGroup,
                              QSpinBox, QScrollArea)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QImage, QPixmap
from streaming.connection import ConnectionManager
from streaming.receiver import StreamReceiver
from streaming.decoder import VideoDecoder, AudioDecoder
from control.commands import ControlCommands
from virtual_camera.interface import VirtualCameraInterface

logger = logging.getLogger(__name__)

class MainWindow(QMainWindow):
    frame_received = pyqtSignal(np.ndarray)
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Android Stream Receiver - Professional Camera Control")
        self.setGeometry(100, 100, 1400, 900)
        
        self.connection_manager = ConnectionManager()
        self.stream_receiver = StreamReceiver(self.connection_manager)
        self.video_decoder = VideoDecoder()
        self.audio_decoder = AudioDecoder()
        self.control_commands = ControlCommands(self.connection_manager)
        self.virtual_camera = VirtualCameraInterface()
        self.device_manager = None
        
        self.is_streaming = False
        self.current_frame = None
        self.is_manual_mode = False
        
        # Camera capabilities
        self.zoom_min = 1.0
        self.zoom_max = 10.0
        self.exposure_min = -2
        self.exposure_max = 2
        self.iso_min = 100
        self.iso_max = 3200
        self.shutter_min_ns = 125000  # 1/8000s
        self.shutter_max_ns = 30000000000  # 30s
        
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
        self.video_label.setMinimumSize(800, 600)
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
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        panel = QWidget()
        layout = QVBoxLayout()
        
        connection_group = self.create_connection_group()
        layout.addWidget(connection_group)
        
        mode_group = self.create_mode_selection_group()
        layout.addWidget(mode_group)
        
        settings_group = self.create_settings_group()
        layout.addWidget(settings_group)
        
        common_group = self.create_common_controls_group()
        layout.addWidget(common_group)
        
        auto_group = self.create_auto_mode_group()
        layout.addWidget(auto_group)
        self.auto_mode_group = auto_group
        
        manual_group = self.create_manual_mode_group()
        layout.addWidget(manual_group)
        self.manual_mode_group = manual_group
        
        camera_group = self.create_camera_group()
        layout.addWidget(camera_group)
        
        vcam_group = self.create_vcam_group()
        layout.addWidget(vcam_group)
        
        layout.addStretch()
        panel.setLayout(layout)
        
        scroll.setWidget(panel)
        return scroll
    
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
    
    def create_mode_selection_group(self):
        group = QGroupBox("حالت کنترل دوربین")
        layout = QVBoxLayout()
        
        self.mode_button_group = QButtonGroup()
        
        self.auto_radio = QRadioButton("حالت خودکار (Auto)")
        self.auto_radio.setChecked(True)
        self.auto_radio.toggled.connect(self.on_mode_changed)
        self.mode_button_group.addButton(self.auto_radio)
        layout.addWidget(self.auto_radio)
        
        self.manual_radio = QRadioButton("حالت دستی (Manual)")
        self.manual_radio.toggled.connect(self.on_mode_changed)
        self.mode_button_group.addButton(self.manual_radio)
        layout.addWidget(self.manual_radio)
        
        group.setLayout(layout)
        return group
    
    def create_settings_group(self):
        group = QGroupBox("تنظیمات پایه")
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
        
        group.setLayout(layout)
        return group
    
    def create_common_controls_group(self):
        group = QGroupBox("کنترل‌های مشترک")
        layout = QVBoxLayout()
        
        # Zoom control
        zoom_layout = QVBoxLayout()
        zoom_header = QHBoxLayout()
        zoom_label = QLabel("زوم (Zoom):")
        self.zoom_value_label = QLabel("1.0x")
        zoom_header.addWidget(zoom_label)
        zoom_header.addStretch()
        zoom_header.addWidget(self.zoom_value_label)
        zoom_layout.addLayout(zoom_header)
        
        self.zoom_slider = QSlider(Qt.Orientation.Horizontal)
        self.zoom_slider.setMinimum(10)
        self.zoom_slider.setMaximum(100)
        self.zoom_slider.setValue(10)
        self.zoom_slider.valueChanged.connect(self.change_zoom)
        zoom_layout.addWidget(self.zoom_slider)
        layout.addLayout(zoom_layout)
        
        # Flash toggle
        self.flash_checkbox = QCheckBox("فلش (Torch)")
        self.flash_checkbox.stateChanged.connect(self.toggle_flash)
        layout.addWidget(self.flash_checkbox)
        
        group.setLayout(layout)
        return group
    
    def create_auto_mode_group(self):
        group = QGroupBox("کنترل‌های خودکار")
        layout = QVBoxLayout()
        
        # Exposure Compensation
        exposure_layout = QVBoxLayout()
        exposure_header = QHBoxLayout()
        exposure_label = QLabel("جبران نوردهی (EV):")
        self.exposure_value_label = QLabel("0")
        exposure_header.addWidget(exposure_label)
        exposure_header.addStretch()
        exposure_header.addWidget(self.exposure_value_label)
        exposure_layout.addLayout(exposure_header)
        
        self.exposure_slider = QSlider(Qt.Orientation.Horizontal)
        self.exposure_slider.setMinimum(-20)
        self.exposure_slider.setMaximum(20)
        self.exposure_slider.setValue(0)
        self.exposure_slider.valueChanged.connect(self.change_exposure)
        exposure_layout.addWidget(self.exposure_slider)
        layout.addLayout(exposure_layout)
        
        # Tap to focus info
        tap_info = QLabel("💡 برای فوکوس، روی تصویر کلیک کنید")
        tap_info.setStyleSheet("color: #666; font-style: italic;")
        layout.addWidget(tap_info)
        
        group.setLayout(layout)
        return group
    
    def create_manual_mode_group(self):
        group = QGroupBox("کنترل‌های دستی")
        layout = QVBoxLayout()
        
        # ISO
        iso_layout = QVBoxLayout()
        iso_header = QHBoxLayout()
        iso_label = QLabel("ISO:")
        self.iso_value_label = QLabel("800")
        iso_header.addWidget(iso_label)
        iso_header.addStretch()
        iso_header.addWidget(self.iso_value_label)
        iso_layout.addLayout(iso_header)
        
        self.iso_slider = QSlider(Qt.Orientation.Horizontal)
        self.iso_slider.setMinimum(100)
        self.iso_slider.setMaximum(3200)
        self.iso_slider.setValue(800)
        self.iso_slider.setSingleStep(100)
        self.iso_slider.valueChanged.connect(self.change_iso)
        iso_layout.addWidget(self.iso_slider)
        layout.addLayout(iso_layout)
        
        # Shutter Speed
        shutter_layout = QVBoxLayout()
        shutter_header = QHBoxLayout()
        shutter_label = QLabel("سرعت شاتر:")
        self.shutter_value_label = QLabel("1/125")
        shutter_header.addWidget(shutter_label)
        shutter_header.addStretch()
        shutter_header.addWidget(self.shutter_value_label)
        shutter_layout.addLayout(shutter_header)
        
        self.shutter_slider = QSlider(Qt.Orientation.Horizontal)
        self.shutter_slider.setMinimum(0)
        self.shutter_slider.setMaximum(100)
        self.shutter_slider.setValue(50)
        self.shutter_slider.valueChanged.connect(self.change_shutter_speed)
        shutter_layout.addWidget(self.shutter_slider)
        layout.addLayout(shutter_layout)
        
        # Focus Distance
        focus_layout = QVBoxLayout()
        focus_header = QHBoxLayout()
        focus_label = QLabel("فاصله فوکوس:")
        self.focus_value_label = QLabel("Auto")
        focus_header.addWidget(focus_label)
        focus_header.addStretch()
        focus_header.addWidget(self.focus_value_label)
        focus_layout.addLayout(focus_header)
        
        self.focus_slider = QSlider(Qt.Orientation.Horizontal)
        self.focus_slider.setMinimum(0)
        self.focus_slider.setMaximum(100)
        self.focus_slider.setValue(0)
        self.focus_slider.valueChanged.connect(self.change_focus_distance)
        focus_layout.addWidget(self.focus_slider)
        layout.addLayout(focus_layout)
        
        # White Balance
        wb_layout = QVBoxLayout()
        wb_label = QLabel("تعادل سفیدی (WB):")
        wb_layout.addWidget(wb_label)
        
        self.wb_combo = QComboBox()
        self.wb_combo.addItems(["Auto", "Daylight", "Cloudy", "Tungsten", "Fluorescent"])
        self.wb_combo.currentIndexChanged.connect(self.change_white_balance)
        wb_layout.addWidget(self.wb_combo)
        layout.addLayout(wb_layout)
        
        group.setLayout(layout)
        group.setVisible(False)  # Hidden by default
        return group
    
    def create_camera_group(self):
        group = QGroupBox("عملیات دوربین")
        layout = QVBoxLayout()
        
        self.switch_camera_btn = QPushButton("تغییر دوربین (جلو/پشت)")
        self.switch_camera_btn.clicked.connect(self.switch_camera)
        layout.addWidget(self.switch_camera_btn)
        
        self.get_capabilities_btn = QPushButton("دریافت قابلیت‌های دوربین")
        self.get_capabilities_btn.clicked.connect(self.get_camera_capabilities)
        layout.addWidget(self.get_capabilities_btn)
        
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
        
        self.stream_receiver.on_video_config = self.video_decoder.set_config
        self.stream_receiver.on_video_frame = self.video_decoder.decode
        self.stream_receiver.on_audio_config = self.audio_decoder.set_config
        self.stream_receiver.on_audio_frame = self.audio_decoder.decode
    
    def on_mode_changed(self):
        self.is_manual_mode = self.manual_radio.isChecked()
        
        # Show/hide appropriate control groups
        self.auto_mode_group.setVisible(not self.is_manual_mode)
        self.manual_mode_group.setVisible(self.is_manual_mode)
        
        # Send command to Android
        self.control_commands.set_manual_mode(self.is_manual_mode)
        logger.info(f"Camera mode changed to: {'Manual' if self.is_manual_mode else 'Auto'}")
    
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
            error_msg = "اتصال USB ناموفق بود.\n\n"
            error_msg += "لطفاً موارد زیر را بررسی کنید:\n"
            error_msg += "1. ADB نصب و در PATH قرار دارد\n"
            error_msg += "2. دستگاه اندروید از طریق USB متصل است\n"
            error_msg += "3. USB Debugging فعال است\n"
            error_msg += "4. برنامه اندروید در حال اجرا و استریمینگ شروع شده است\n\n"
            error_msg += "برای جزئیات بیشتر لاگ‌ها را بررسی کنید."
            QMessageBox.critical(self, "خطا", error_msg)
    
    def disconnect(self):
        self.stream_receiver.stop()
        self.connection_manager.disconnect()
    
    def on_connected(self):
        self.status_label.setText("وضعیت: متصل")
        self.connect_wifi_btn.setEnabled(False)
        self.connect_usb_btn.setEnabled(False)
        self.disconnect_btn.setEnabled(True)
        self.is_streaming = True
        
        # Request camera capabilities
        self.get_camera_capabilities()
        
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
        try:
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
        except Exception as e:
            logger.error(f"Error updating frame display: {e}", exc_info=True)
    
    def change_resolution(self):
        index = self.resolution_combo.currentIndex()
        resolutions = [(640, 480), (1280, 720), (1920, 1080)]
        width, height = resolutions[index]
        self.control_commands.set_resolution(width, height)
        logger.info(f"Resolution changed to: {width}x{height}")
    
    def change_fps(self):
        fps = int(self.fps_combo.currentText())
        self.control_commands.set_fps(fps)
        logger.info(f"FPS changed to: {fps}")
    
    def change_zoom(self):
        value = self.zoom_slider.value()
        # Map slider (10-100) to zoom range (zoom_min to zoom_max)
        ratio = self.zoom_min + (value - 10) / 90.0 * (self.zoom_max - self.zoom_min)
        self.zoom_value_label.setText(f"{ratio:.1f}x")
        self.control_commands.set_zoom(ratio)
    
    def change_exposure(self):
        value = self.exposure_slider.value() / 10.0
        self.exposure_value_label.setText(f"{value:+.1f}")
        
        # Map to exposure compensation index
        ev_index = int(value * 2)
        self.control_commands.set_brightness(value / 2.0 + 0.5)
    
    def change_iso(self):
        iso = self.iso_slider.value()
        self.iso_value_label.setText(str(iso))
        self.control_commands.set_manual_iso(iso)
    
    def change_shutter_speed(self):
        # Map slider (0-100) to shutter speed range (logarithmic)
        value = self.shutter_slider.value()
        
        # Convert to nanoseconds (logarithmic scale)
        log_min = np.log10(self.shutter_min_ns)
        log_max = np.log10(self.shutter_max_ns)
        log_value = log_min + (value / 100.0) * (log_max - log_min)
        nanos = int(10 ** log_value)
        
        # Display as fraction
        seconds = nanos / 1e9
        if seconds < 1:
            display = f"1/{int(1/seconds)}"
        else:
            display = f"{seconds:.1f}s"
        
        self.shutter_value_label.setText(display)
        self.control_commands.set_manual_shutter(nanos)
    
    def change_focus_distance(self):
        value = self.focus_slider.value()
        distance = value / 100.0
        
        if value == 0:
            self.focus_value_label.setText("∞ (Infinity)")
        elif value == 100:
            self.focus_value_label.setText("Macro")
        else:
            self.focus_value_label.setText(f"{value}%")
        
        self.control_commands.set_manual_focus(distance)
    
    def change_white_balance(self):
        mode = self.wb_combo.currentText().lower()
        self.control_commands.set_white_balance(mode, 5500)
        logger.info(f"White balance changed to: {mode}")
    
    def toggle_flash(self):
        enabled = self.flash_checkbox.isChecked()
        self.control_commands.set_flash(enabled)
        logger.info(f"Flash {'enabled' if enabled else 'disabled'}")
    
    def switch_camera(self):
        self.control_commands.switch_camera("back")
        logger.info("Camera switched")
    
    def get_camera_capabilities(self):
        self.control_commands.get_camera_capabilities()
        logger.info("Requested camera capabilities")
    
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
        
        if self.device_manager:
            self.device_manager.cleanup()
        
        event.accept()
