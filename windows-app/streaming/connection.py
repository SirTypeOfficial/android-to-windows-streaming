import socket
import subprocess
import logging
from typing import Optional, Callable
from threading import Thread

logger = logging.getLogger(__name__)

class ConnectionManager:
    def __init__(self):
        self.socket: Optional[socket.socket] = None
        self.is_connected = False
        self.connection_thread: Optional[Thread] = None
        self.on_connected: Optional[Callable] = None
        self.on_disconnected: Optional[Callable] = None
        
    def connect_wifi(self, host: str, port: int = 8888) -> bool:
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((host, port))
            self.is_connected = True
            logger.info(f"Connected to {host}:{port} via WiFi")
            if self.on_connected:
                self.on_connected()
            return True
        except Exception as e:
            logger.error(f"Failed to connect via WiFi: {e}")
            return False
    
    def connect_usb(self, port: int = 8889) -> bool:
        try:
            devices_result = subprocess.run(
                ['adb', 'devices'],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if devices_result.returncode != 0:
                logger.error(f"ADB devices command failed: {devices_result.stderr}")
                return False
            
            devices_output = devices_result.stdout.strip().split('\n')
            connected_devices = [line for line in devices_output[1:] if line.strip() and '\tdevice' in line]
            
            if not connected_devices:
                logger.error("No Android devices connected via USB")
                return False
            
            logger.info(f"Found {len(connected_devices)} device(s) connected")
            
            result = subprocess.run(
                ['adb', 'reverse', f'tcp:{port}', f'tcp:{port}'],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode != 0:
                logger.error(f"ADB reverse failed: {result.stderr}")
                return False
            
            logger.info(f"ADB reverse tcp:{port} successful")
            
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.settimeout(10)
            self.socket.connect(('localhost', port))
            self.socket.settimeout(None)
            self.is_connected = True
            logger.info(f"Connected via USB on port {port}")
            if self.on_connected:
                self.on_connected()
            return True
        except FileNotFoundError:
            logger.error("ADB not found. Make sure Android SDK platform-tools is installed and in PATH")
            return False
        except socket.timeout:
            logger.error("Connection timeout. Make sure the Android app is running and streaming is started")
            return False
        except Exception as e:
            logger.error(f"Failed to connect via USB: {e}")
            return False
    
    def disconnect(self):
        if self.socket:
            try:
                self.socket.close()
            except:
                pass
            self.socket = None
        
        self.is_connected = False
        logger.info("Disconnected")
        if self.on_disconnected:
            self.on_disconnected()
    
    def send_data(self, data: bytes) -> bool:
        if not self.is_connected or not self.socket:
            return False
        
        try:
            self.socket.sendall(data)
            return True
        except Exception as e:
            logger.error(f"Failed to send data: {e}")
            self.disconnect()
            return False
    
    def receive_data(self, size: int) -> Optional[bytes]:
        if not self.is_connected or not self.socket:
            return None
        
        try:
            data = b''
            while len(data) < size:
                chunk = self.socket.recv(size - len(data))
                if not chunk:
                    raise ConnectionError("Connection closed")
                data += chunk
            return data
        except Exception as e:
            logger.error(f"Failed to receive data: {e}")
            self.disconnect()
            return None

