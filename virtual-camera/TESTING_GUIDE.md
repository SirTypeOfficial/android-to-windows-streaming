# راهنمای تست درایورهای دوربین و میکروفون مجازی

## آماده‌سازی محیط تست

### فعال‌سازی Test Signing

```powershell
# اجرا به عنوان Administrator
bcdedit /set testsigning on
# Restart سیستم
```

### نصب Driver Verifier

Driver Verifier یک ابزار قدرتمند برای تشخیص مشکلات درایور است.

```powershell
# فعال‌سازی برای درایورهای ما
verifier /standard /driver vcam.sys vmic.sys

# Restart سیستم
```

**توجه**: Driver Verifier می‌تواند باعث BSOD شود اگر مشکلی وجود داشته باشد. قبل از فعال‌سازی از سیستم Backup بگیرید.

## تست درایور دوربین مجازی

### ۱. تست نصب و شناسایی

```powershell
# بررسی نصب درایور
pnputil /enum-drivers | Select-String "vcam"

# بررسی Device Manager
devmgmt.msc
```

در Device Manager باید "Virtual Camera Device" را زیر "Cameras" ببینید.

### ۲. تست با برنامه‌های کاربردی

#### الف) تست با Camera App ویندوز

1. باز کردن Camera app
2. Settings → Camera → انتخاب "Virtual Camera Device"
3. باید یک تصویر سیاه (بدون فریم) ببینید

#### ب) تست با OBS Studio

1. باز کردن OBS Studio
2. Add Source → Video Capture Device
3. انتخاب "Virtual Camera Device"
4. Preview را فعال کنید

#### ج) تست با Zoom

1. باز کردن Zoom
2. Settings → Video
3. انتخاب "Virtual Camera Device" از لیست دوربین‌ها

#### د) تست با Microsoft Teams

1. باز کردن Teams
2. Settings → Devices
3. انتخاب "Virtual Camera Device" برای Camera

### ۳. تست ارسال فریم (با Python)

یک اسکریپت Python ساده برای تست ارسال فریم:

```python
import ctypes
import struct
import numpy as np
from ctypes import wintypes

# باز کردن دستگاه
GENERIC_READ = 0x80000000
GENERIC_WRITE = 0x40000000
OPEN_EXISTING = 3

kernel32 = ctypes.windll.kernel32
hDevice = kernel32.CreateFileW(
    "\\\\.\\VirtualCamera",
    GENERIC_READ | GENERIC_WRITE,
    0, None, OPEN_EXISTING, 0, None
)

if hDevice == -1:
    print("Failed to open device")
    exit(1)

# آماده‌سازی فریم (RGB24 1920x1080)
width, height = 1920, 1080
frame = np.zeros((height, width, 3), dtype=np.uint8)

# رسم یک مربع قرمز در وسط
frame[400:680, 800:1120] = [0, 0, 255]  # BGR format

# ساخت header
IOCTL_VCAM_SEND_FRAME = 0x222000

header = struct.pack('IIIIQ', 
    width,           # Width
    height,          # Height
    0,               # Format (0=RGB24)
    len(frame.tobytes()),  # BufferSize
    0                # Timestamp
)

# ارسال فریم
buffer = header + frame.tobytes()
bytes_returned = wintypes.DWORD()

result = kernel32.DeviceIoControl(
    hDevice,
    IOCTL_VCAM_SEND_FRAME,
    buffer,
    len(buffer),
    None, 0,
    ctypes.byref(bytes_returned),
    None
)

kernel32.CloseHandle(hDevice)

if result:
    print("Frame sent successfully")
else:
    print("Failed to send frame")
```

### ۴. بررسی لاگ‌های Kernel

```powershell
# استفاده از DebugView از Sysinternals
# دانلود: https://docs.microsoft.com/en-us/sysinternals/downloads/debugview

# یا استفاده از Event Viewer
eventvwr.msc
# بررسی Windows Logs → System
```

## تست درایور میکروفون مجازی

### ۱. تست نصب و شناسایی

```powershell
# بررسی نصب
pnputil /enum-drivers | Select-String "vmic"

# بررسی Sound Settings
mmsys.cpl
```

در Sound Settings باید:
- **Recording**: "Virtual Microphone" را ببینید
- **Playback**: "Virtual Microphone Input" را ببینید

### ۲. تست Loopback

#### تست ساده

1. باز کردن Sound Settings (Win + I → System → Sound)
2. در Playback، "Virtual Microphone Input" را Default کنید
3. یک موسیقی پخش کنید
4. در Recording، "Virtual Microphone" را انتخاب کنید
5. Properties → Listen → "Listen to this device" را فعال کنید
6. باید صدا را از اسپیکرهای واقعی بشنوید

#### تست با Audacity

1. باز کردن Audacity
2. Recording Device: "Virtual Microphone"
3. Playback Device: "Virtual Microphone Input"
4. یک موسیقی در پس‌زمینه پخش کنید
5. Record را در Audacity بزنید
6. باید صدای موسیقی ضبط شود

### ۳. تست با برنامه‌های VoIP

#### الف) تست با Zoom

1. باز کردن Zoom
2. Settings → Audio
3. Microphone: "Virtual Microphone"
4. Speaker: "Virtual Microphone Input"
5. Test Mic - باید صدای خودتان را بشنوید

#### ب) تست با Discord

1. باز کردن Discord
2. User Settings → Voice & Video
3. Input Device: "Virtual Microphone"
4. Output Device: "Virtual Microphone Input"
5. Let's Check - برای تست میکروفون

#### ج) تست با Microsoft Teams

1. باز کردن Teams
2. Settings → Devices
3. Microphone: "Virtual Microphone"
4. Speaker: "Virtual Microphone Input"
5. Make a test call

### ۴. تست با Python (WASAPI)

```python
import pyaudio
import numpy as np

# پیکربندی
SAMPLE_RATE = 48000
CHUNK = 1024
CHANNELS = 2

# ایجاد PyAudio instance
p = pyaudio.PyAudio()

# پیدا کردن دستگاه‌های مجازی
for i in range(p.get_device_count()):
    info = p.get_device_info_by_index(i)
    if "Virtual Microphone" in info['name']:
        print(f"Found: {info['name']} (index {i})")

# باز کردن stream برای پخش به Virtual Microphone Input
stream_out = p.open(
    format=pyaudio.paInt16,
    channels=CHANNELS,
    rate=SAMPLE_RATE,
    output=True,
    output_device_index=<input_device_index>
)

# تولید یک سیگنال sine wave
duration = 3  # ثانیه
frequency = 440  # Hz (نت A)

t = np.linspace(0, duration, int(SAMPLE_RATE * duration))
signal = np.sin(2 * np.pi * frequency * t)
audio_data = (signal * 32767).astype(np.int16)

# استریم کردن
stream_out.write(audio_data.tobytes())

stream_out.close()
p.terminate()

print("Audio streamed successfully")
```

## تست‌های پیشرفته

### ۱. تست عملکرد (Performance)

```powershell
# استفاده از Windows Performance Analyzer
xperf -start <session_name> -on <providers>
# اجرای برنامه تست
xperf -stop <session_name> -d output.etl
```

### ۲. تست استرس

#### برای دوربین

```python
# ارسال مداوم فریم‌ها با frame rate بالا
for i in range(1000):
    send_frame(...)
    time.sleep(1/60)  # 60 fps
```

#### برای میکروفون

```python
# پخش مداوم صدا به مدت طولانی
while True:
    stream.write(audio_data)
```

### ۳. تست چند‌رشته‌ای (Multi-threading)

```python
import threading

def camera_thread():
    while True:
        send_frame_to_camera()

def audio_thread():
    while True:
        send_audio_to_microphone()

t1 = threading.Thread(target=camera_thread)
t2 = threading.Thread(target=audio_thread)

t1.start()
t2.start()
```

## عیب‌یابی مشکلات رایج

### دوربین

#### مشکل: "Device not found"
- بررسی نصب درایور در Device Manager
- اجرای مجدد install.bat

#### مشکل: "Black screen in applications"
- فریمی ارسال نشده است
- بررسی IOCTL با DebugView

#### مشکل: BSOD هنگام استفاده
- غیرفعال کردن Driver Verifier
- بررسی لاگ‌ها با WinDbg
- بررسی کد برای memory leaks

### میکروفون

#### مشکل: "No sound in capture"
- بررسی پخش صدا به "Virtual Microphone Input"
- بررسی وضعیت Loopback Buffer

#### مشکل: "Crackling or distortion"
- کاهش sample rate
- افزایش اندازه buffer
- بررسی CPU usage

#### مشکل: "High latency"
- کاهش اندازه buffer
- بهینه‌سازی Loopback logic

## چک‌لیست تست نهایی

### درایور دوربین
- [ ] نصب موفق
- [ ] شناسایی در Device Manager
- [ ] شناسایی در Camera app
- [ ] تست با OBS Studio
- [ ] تست با Zoom
- [ ] تست با Teams
- [ ] تست ارسال فریم از Python
- [ ] تست بدون BSOD با Driver Verifier

### درایور میکروفون
- [ ] نصب موفق
- [ ] شناسایی در Sound Settings (Render و Capture)
- [ ] تست Loopback ساده
- [ ] تست با Audacity
- [ ] تست با Zoom
- [ ] تست با Discord
- [ ] تست با Teams
- [ ] تست استریم صدا از Python
- [ ] تست بدون BSOD با Driver Verifier

## منابع مفید

- [Windows Driver Kit Documentation](https://docs.microsoft.com/en-us/windows-hardware/drivers/)
- [Sysinternals Tools](https://docs.microsoft.com/en-us/sysinternals/)
- [Debugging Tools for Windows](https://docs.microsoft.com/en-us/windows-hardware/drivers/debugger/)

