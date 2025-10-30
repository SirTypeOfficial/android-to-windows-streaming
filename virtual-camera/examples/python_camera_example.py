"""
مثال استفاده از درایور دوربین مجازی با Python
این اسکریپت یک تصویر یا ویدیو را به دوربین مجازی ارسال می‌کند
"""

import ctypes
import struct
import numpy as np
import cv2
import time
from ctypes import wintypes

# Constants
GENERIC_READ = 0x80000000
GENERIC_WRITE = 0x40000000
OPEN_EXISTING = 3
IOCTL_VCAM_SEND_FRAME = 0x222000
IOCTL_VCAM_GET_STATUS = 0x222001

# RGB24 format
FORMAT_RGB24 = 0
FORMAT_NV12 = 1
FORMAT_YUY2 = 2

class VirtualCamera:
    def __init__(self, device_path="\\\\.\\VirtualCamera"):
        self.kernel32 = ctypes.windll.kernel32
        self.device_path = device_path
        self.handle = None
        
    def open(self):
        """باز کردن اتصال به درایور"""
        self.handle = self.kernel32.CreateFileW(
            self.device_path,
            GENERIC_READ | GENERIC_WRITE,
            0, None, OPEN_EXISTING, 0, None
        )
        
        if self.handle == -1:
            raise Exception("Failed to open virtual camera device")
        
        print("Virtual camera device opened successfully")
        return True
    
    def close(self):
        """بستن اتصال"""
        if self.handle and self.handle != -1:
            self.kernel32.CloseHandle(self.handle)
            self.handle = None
            print("Virtual camera device closed")
    
    def send_frame(self, frame_bgr, width, height):
        """
        ارسال یک فریم به درایور
        
        Args:
            frame_bgr: آرایه numpy در فرمت BGR (OpenCV format)
            width: عرض فریم
            height: ارتفاع فریم
        """
        if self.handle is None or self.handle == -1:
            raise Exception("Device not opened")
        
        # تبدیل BGR به RGB
        frame_rgb = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)
        frame_bytes = frame_rgb.tobytes()
        
        # ساخت header
        header = struct.pack('IIIIQ', 
            width,                  # Width
            height,                 # Height
            FORMAT_RGB24,           # Format
            len(frame_bytes),       # BufferSize
            int(time.time() * 1e7)  # Timestamp (100-nanosecond units)
        )
        
        # ترکیب header و داده
        buffer = header + frame_bytes
        bytes_returned = wintypes.DWORD()
        
        # ارسال به درایور
        result = self.kernel32.DeviceIoControl(
            self.handle,
            IOCTL_VCAM_SEND_FRAME,
            buffer,
            len(buffer),
            None, 0,
            ctypes.byref(bytes_returned),
            None
        )
        
        if not result:
            error_code = self.kernel32.GetLastError()
            raise Exception(f"Failed to send frame. Error code: {error_code}")
        
        return True
    
    def get_status(self):
        """دریافت وضعیت درایور"""
        if self.handle is None or self.handle == -1:
            raise Exception("Device not opened")
        
        # ساختار برای status
        status_buffer = ctypes.create_string_buffer(20)  # sizeof(VCAM_STATUS)
        bytes_returned = wintypes.DWORD()
        
        result = self.kernel32.DeviceIoControl(
            self.handle,
            IOCTL_VCAM_GET_STATUS,
            None, 0,
            status_buffer,
            len(status_buffer),
            ctypes.byref(bytes_returned),
            None
        )
        
        if not result:
            return None
        
        # Parse status
        is_streaming, width, height, format_type, frames_delivered = struct.unpack('IIIII', status_buffer.raw)
        
        return {
            'is_streaming': bool(is_streaming),
            'width': width,
            'height': height,
            'format': format_type,
            'frames_delivered': frames_delivered
        }


def example_static_image():
    """مثال ۱: ارسال یک تصویر ثابت"""
    print("\n=== Example 1: Static Image ===")
    
    camera = VirtualCamera()
    camera.open()
    
    try:
        # ایجاد یک تصویر ساده (gradient)
        width, height = 1920, 1080
        image = np.zeros((height, width, 3), dtype=np.uint8)
        
        # Gradient افقی
        for x in range(width):
            image[:, x] = [int(255 * x / width), 128, 255 - int(255 * x / width)]
        
        # اضافه کردن متن
        cv2.putText(image, "Virtual Camera Test", (50, 100), 
                   cv2.FONT_HERSHEY_SIMPLEX, 3, (255, 255, 255), 5)
        
        # ارسال مداوم (برای اینکه برنامه‌ها بتوانند ببینند)
        print("Sending static image... Press Ctrl+C to stop")
        while True:
            camera.send_frame(image, width, height)
            time.sleep(1/30)  # 30 fps
            
    except KeyboardInterrupt:
        print("\nStopped by user")
    finally:
        camera.close()


def example_webcam_forward():
    """مثال ۲: فوروارد کردن وبکم واقعی به دوربین مجازی"""
    print("\n=== Example 2: Webcam Forward ===")
    
    camera = VirtualCamera()
    camera.open()
    
    # باز کردن وبکم واقعی
    cap = cv2.VideoCapture(0)
    
    if not cap.isOpened():
        print("Error: Could not open webcam")
        camera.close()
        return
    
    # تنظیم رزولوشن
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)
    
    try:
        print("Forwarding webcam... Press 'q' to stop")
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            # ارسال فریم به دوربین مجازی
            height, width = frame.shape[:2]
            camera.send_frame(frame, width, height)
            
            # نمایش (اختیاری)
            cv2.imshow('Webcam Forward', frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
                
    except Exception as e:
        print(f"Error: {e}")
    finally:
        cap.release()
        cv2.destroyAllWindows()
        camera.close()


def example_animated():
    """مثال ۳: انیمیشن ساده"""
    print("\n=== Example 3: Animated ===")
    
    camera = VirtualCamera()
    camera.open()
    
    try:
        width, height = 1920, 1080
        frame_count = 0
        
        print("Sending animated frames... Press Ctrl+C to stop")
        while True:
            # ایجاد فریم جدید
            image = np.zeros((height, width, 3), dtype=np.uint8)
            
            # رنگ پس‌زمینه متحرک
            color = int(127 + 127 * np.sin(frame_count * 0.05))
            image[:, :] = [color, 128, 255 - color]
            
            # دایره متحرک
            center_x = int(width / 2 + width / 3 * np.cos(frame_count * 0.05))
            center_y = int(height / 2 + height / 3 * np.sin(frame_count * 0.05))
            cv2.circle(image, (center_x, center_y), 100, (255, 255, 255), -1)
            
            # شمارنده فریم
            cv2.putText(image, f"Frame: {frame_count}", (50, 100), 
                       cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 0), 3)
            
            camera.send_frame(image, width, height)
            
            frame_count += 1
            time.sleep(1/30)  # 30 fps
            
    except KeyboardInterrupt:
        print("\nStopped by user")
    finally:
        camera.close()


def example_video_file():
    """مثال ۴: پخش فایل ویدیو"""
    print("\n=== Example 4: Video File Playback ===")
    
    video_path = input("Enter video file path: ")
    
    camera = VirtualCamera()
    camera.open()
    
    cap = cv2.VideoCapture(video_path)
    
    if not cap.isOpened():
        print("Error: Could not open video file")
        camera.close()
        return
    
    fps = cap.get(cv2.CAP_PROP_FPS)
    frame_delay = 1.0 / fps if fps > 0 else 1.0 / 30
    
    try:
        print(f"Playing video at {fps} fps... Press 'q' to stop")
        while True:
            ret, frame = cap.read()
            if not ret:
                # Restart video
                cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                continue
            
            # Resize if needed
            frame = cv2.resize(frame, (1920, 1080))
            
            camera.send_frame(frame, 1920, 1080)
            
            time.sleep(frame_delay)
            
    except KeyboardInterrupt:
        print("\nStopped by user")
    finally:
        cap.release()
        camera.close()


def main():
    """منوی اصلی"""
    print("Virtual Camera Examples")
    print("=" * 50)
    print("1. Static Image")
    print("2. Webcam Forward")
    print("3. Animated")
    print("4. Video File Playback")
    print("5. Get Status")
    print("0. Exit")
    
    choice = input("\nEnter your choice: ")
    
    if choice == "1":
        example_static_image()
    elif choice == "2":
        example_webcam_forward()
    elif choice == "3":
        example_animated()
    elif choice == "4":
        example_video_file()
    elif choice == "5":
        camera = VirtualCamera()
        camera.open()
        status = camera.get_status()
        camera.close()
        print("\nCamera Status:")
        print(f"  Streaming: {status['is_streaming']}")
        print(f"  Resolution: {status['width']}x{status['height']}")
        print(f"  Format: {status['format']}")
        print(f"  Frames Delivered: {status['frames_delivered']}")
    elif choice == "0":
        print("Goodbye!")
    else:
        print("Invalid choice")


if __name__ == "__main__":
    main()

