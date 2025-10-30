# درایورهای دوربین و میکروفون مجازی برای ویندوز

این پروژه شامل دو درایور سطح کرنل ویندوز برای ایجاد دستگاه‌های دوربین و میکروفون مجازی است که توسط برنامه‌های مختلف (Zoom, Teams, Discord, OBS و غیره) به عنوان دستگاه‌های واقعی شناسایی می‌شوند.

## ویژگی‌های کلیدی

### 🎥 درایور دوربین مجازی (AVStream)
- ✅ پشتیبانی از فرمت‌های متعدد: RGB24, NV12, YUY2
- ✅ رزولوشن‌های مختلف: 640×480, 1280×720, 1920×1080
- ✅ Frame rate های 30fps و 60fps
- ✅ رابط IOCTL برای ارسال فریم از User-Mode
- ✅ Circular buffer برای پایداری
- ✅ Thread-safe با استفاده از Spin Locks

### 🎤 درایور میکروفون مجازی (PortCls)
- ✅ پشتیبانی از PCM 16-bit و 24-bit
- ✅ Sample rate های 44.1 kHz و 48 kHz
- ✅ صدای Stereo (2 کانال)
- ✅ معماری Loopback (Render → Capture)
- ✅ Circular buffer با تأخیر کم
- ✅ مدیریت Overflow/Underrun

## ساختار پروژه

```
project-root/
├── avstream-camera/          # درایور دوربین مجازی
│   ├── src/                  # سورس کدها
│   ├── inc/                  # Header files
│   ├── inf/                  # فایل INF
│   └── install.bat           # اسکریپت نصب
│
├── portcls-microphone/       # درایور میکروفون مجازی
│   ├── src/                  # سورس کدها
│   ├── inc/                  # Header files
│   ├── inf/                  # فایل INF
│   └── install.bat           # اسکریپت نصب
│
├── examples/                 # مثال‌های Python
│   ├── python_camera_example.py
│   ├── python_microphone_example.py
│   └── requirements.txt
│
├── BUILD_INSTRUCTIONS.md     # راهنمای ساخت و نصب
├── ARCHITECTURE.md           # معماری و طراحی
├── TESTING_GUIDE.md          # راهنمای تست
└── README.md                 # این فایل
```

## نیازمندی‌های سیستم

- **سیستم‌عامل**: Windows 11 x64 (22000 یا جدیدتر)
- **برای توسعه**:
  - Windows Driver Kit (WDK)
  - Visual Studio 2019/2022 با پشتیبانی C/C++
  - Windows SDK
- **برای استفاده**:
  - دسترسی Administrator برای نصب
  - Test Signing فعال (برای نسخه توسعه)

## شروع سریع

### ۱. ساخت درایورها

```bash
# ساخت درایور دوربین
cd avstream-camera
build -ceZ

# ساخت درایور میکروفون
cd portcls-microphone
build -ceZ
```

جزئیات بیشتر در [BUILD_INSTRUCTIONS.md](BUILD_INSTRUCTIONS.md)

### ۲. نصب درایورها

```powershell
# فعال‌سازی Test Signing
bcdedit /set testsigning on
# Restart سیستم

# نصب دوربین
cd avstream-camera
.\install.bat

# نصب میکروفون
cd portcls-microphone
.\install.bat
```

### ۳. استفاده با Python

```bash
# نصب وابستگی‌ها
cd examples
pip install -r requirements.txt

# اجرای مثال دوربین
python python_camera_example.py

# اجرای مثال میکروفون
python python_microphone_example.py
```

## مثال‌های کاربردی

### ارسال فریم به دوربین

```python
from python_camera_example import VirtualCamera
import numpy as np

camera = VirtualCamera()
camera.open()

# ایجاد یک فریم ساده
frame = np.zeros((1080, 1920, 3), dtype=np.uint8)
frame[:, :] = [255, 0, 0]  # آبی در BGR

camera.send_frame(frame, 1920, 1080)
camera.close()
```

### پخش صدا به میکروفون

```python
from python_microphone_example import VirtualMicrophone
import numpy as np

mic = VirtualMicrophone()

# تولید موج سینوسی 440 Hz
sample_rate = 48000
t = np.linspace(0, 2, sample_rate * 2)
signal = np.sin(2 * np.pi * 440 * t)
audio = np.column_stack([signal, signal])  # Stereo
audio = (audio * 32767).astype(np.int16)

mic.play_audio(audio, sample_rate, 2)
mic.close()
```

## معماری

### جریان داده دوربین

```
User Application (Python/C++)
        ↓ (IOCTL)
Kernel Driver (AVStream)
        ↓
Circular Buffer (5 frames)
        ↓
Media Foundation / DirectShow
        ↓
Applications (Zoom, Teams, etc.)
```

### جریان داده میکروفون

```
User Application (WASAPI)
        ↓
Render Endpoint (Input)
        ↓
Loopback Buffer (Circular)
        ↓
Capture Endpoint (Microphone)
        ↓
Applications (Recording apps)
```

جزئیات کامل در [ARCHITECTURE.md](ARCHITECTURE.md)

## تست

راهنمای کامل تست در [TESTING_GUIDE.md](TESTING_GUIDE.md) موجود است.

### تست سریع دوربین

```powershell
# باز کردن Camera app ویندوز
start microsoft.windows.camera:

# یا استفاده از OBS Studio
```

### تست سریع میکروفون

```powershell
# باز کردن Sound Settings
start ms-settings:sound

# بررسی "Virtual Microphone" و "Virtual Microphone Input"
```

## برنامه‌های سازگار

✅ **تست شده و کار می‌کند**:
- Zoom Desktop Client
- Microsoft Teams
- Discord
- OBS Studio
- Google Chrome (WebRTC)
- Mozilla Firefox (WebRTC)
- Windows Camera App
- Audacity

## مشکلات شناخته شده

1. **دوربین**: فعلاً فقط یک برنامه می‌تواند همزمان از دوربین استفاده کند
2. **میکروفون**: Buffer size ثابت است (بهینه‌سازی نشده)
3. **هر دو**: نیاز به Test Signing در حالت توسعه

## مشارکت

این پروژه برای اهداف آموزشی و توسعه طراحی شده است. برای استفاده در محیط production:

1. درایورها را با گواهی معتبر امضا کنید
2. تست‌های جامع با Driver Verifier انجام دهید
3. مدیریت خطا را بهبود دهید
4. Power management را پیاده‌سازی کنید

## مجوز و مسئولیت

- این نرم‌افزار "AS-IS" ارائه می‌شود
- مسئولیت استفاده بر عهده کاربر است
- قبل از نصب درایورهای kernel-mode، حتماً backup تهیه کنید
- برای استفاده در محیط production، مشاوره با متخصصان امنیتی توصیه می‌شود

## منابع مفید

- [Windows Driver Kit Documentation](https://docs.microsoft.com/en-us/windows-hardware/drivers/)
- [AVStream Minidriver Documentation](https://docs.microsoft.com/en-us/windows-hardware/drivers/stream/avstream-minidrivers-design-guide)
- [Audio Miniport Drivers](https://docs.microsoft.com/en-us/windows-hardware/drivers/audio/audio-miniport-drivers)
- [Sysinternals Tools](https://docs.microsoft.com/en-us/sysinternals/)

## پشتیبانی

برای سوالات و مشکلات:
1. [BUILD_INSTRUCTIONS.md](BUILD_INSTRUCTIONS.md) را مطالعه کنید
2. [TESTING_GUIDE.md](TESTING_GUIDE.md) را بررسی کنید
3. لاگ‌های Kernel را با DebugView چک کنید
4. Event Viewer را برای خطاهای سیستم بررسی کنید

---

**توجه**: این درایورها برای توسعه و تست طراحی شده‌اند. برای استفاده در محیط production، امضای معتبر و تست‌های جامع الزامی است.

