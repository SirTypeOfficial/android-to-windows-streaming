# مثال‌های استفاده از درایورهای دوربین و میکروفون مجازی

این پوشه شامل مثال‌هایی برای استفاده از درایورهای دوربین و میکروفون مجازی با Python است.

## نصب وابستگی‌ها

```bash
pip install -r requirements.txt
```

## مثال‌های دوربین (`python_camera_example.py`)

### ویژگی‌ها
- ارسال تصویر ثابت به دوربین مجازی
- فوروارد کردن وبکم واقعی
- انیمیشن ساده
- پخش فایل ویدیو
- دریافت وضعیت درایور

### استفاده

```bash
python python_camera_example.py
```

### مثال کد

```python
from python_camera_example import VirtualCamera
import numpy as np

# باز کردن دوربین
camera = VirtualCamera()
camera.open()

# ایجاد یک تصویر
image = np.zeros((1080, 1920, 3), dtype=np.uint8)
image[:, :] = [0, 0, 255]  # قرمز

# ارسال فریم
camera.send_frame(image, 1920, 1080)

# بستن
camera.close()
```

## مثال‌های میکروفون (`python_microphone_example.py`)

### ویژگی‌ها
- پخش موج سینوسی
- پخش فایل WAV
- تست Loopback
- استریم زنده
- فوروارد کردن میکروفون واقعی
- تبدیل متن به گفتار (TTS)

### استفاده

```bash
python python_microphone_example.py
```

### مثال کد

```python
from python_microphone_example import VirtualMicrophone
import numpy as np

# باز کردن میکروفون
mic = VirtualMicrophone()

# تولید صدا (440 Hz sine wave)
sample_rate = 48000
duration = 2
t = np.linspace(0, duration, int(sample_rate * duration))
signal = np.sin(2 * np.pi * 440 * t)
audio_data = np.column_stack([signal, signal])  # Stereo
audio_data = (audio_data * 32767).astype(np.int16)

# پخش
mic.play_audio(audio_data, sample_rate, 2)

# بستن
mic.close()
```

## نکات مهم

1. **دسترسی به درایورها**: اطمینان حاصل کنید که درایورها نصب و فعال هستند.

2. **فرمت‌های پشتیبانی شده**:
   - دوربین: RGB24, NV12, YUY2
   - میکروفون: PCM 16/24-bit, 44.1/48 kHz, Stereo

3. **عملکرد**: برای بهترین عملکرد:
   - دوربین: ارسال فریم با rate ثابت (30 یا 60 fps)
   - میکروفون: استفاده از buffer size مناسب (1024-4096)

4. **مدیریت خطا**: همیشه از try-finally برای بستن منابع استفاده کنید.

## عیب‌یابی

### دوربین
- **"Failed to open device"**: درایور نصب نیست یا دسترسی denied است
- **"Failed to send frame"**: فرمت فریم نامعتبر است یا اندازه اشتباه است

### میکروفون
- **"Device not found"**: درایور نصب نیست یا نام دستگاه اشتباه است
- **"No sound"**: بررسی کنید که به دستگاه درست (Input/Output) متصل هستید

## لاگ‌گیری

برای دیدن لاگ‌های درایور از DebugView استفاده کنید:
1. دانلود DebugView از Sysinternals
2. اجرا به عنوان Administrator
3. Capture → Capture Kernel
4. لاگ‌های "VCam:" و "VMic:" را ببینید

## منابع بیشتر

- [OpenCV Documentation](https://docs.opencv.org/)
- [PyAudio Documentation](https://people.csail.mit.edu/hubert/pyaudio/docs/)
- [NumPy Documentation](https://numpy.org/doc/)

