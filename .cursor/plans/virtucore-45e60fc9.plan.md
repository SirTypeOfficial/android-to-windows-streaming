<!-- 45e60fc9-ad06-4742-9170-175814a45622 ae925a60-84b3-4270-954f-14f05ac07e76 -->
# یکپارچه‌سازی StreamLink با درایورهای VirtuCore

## فاز 1: یکپارچه‌سازی اولیه (Python + ctypes)

### 1.1 آماده‌سازی و تحلیل

- بررسی دقیق `virtual-camera/examples/python_camera_example.py` و `python_microphone_example.py`
- مطالعه `virtual-camera/ARCHITECTURE.md` برای درک کامل IOCTL interface
- بررسی فایل‌های هدر: `virtual-camera/avstream-camera/inc/vcam_common.h` و `portcls-microphone/inc/vmic_common.h`

### 1.2 حذف وابستگی OBS

- حذف تمام کدهای مرتبط با OBS از:
  - `windows-app/virtual_camera/obs_controller.py`
  - `windows-app/virtual_camera/device_manager.py`
  - `windows-app/main.py`
- حذف `pyvirtualcam` از `requirements.txt`
- آپدیت مستندات (`START_HERE.md`, `QUICK_START.md`, `OBS_SETUP.md`)

### 1.3 پیاده‌سازی ماژول VirtuCore Camera

**فایل جدید:** `windows-app/virtual_camera/virtucore_camera.py`

- کپسوله‌سازی IOCTL communication با درایور AVStream
- پیاده‌سازی کلاس `VirtuCoreCamera`:
  - `open()`: باز کردن `//.//VirtualCamera`
  - `send_frame(frame, width, height)`: ارسال RGB24 frame
  - `get_status()`: دریافت وضعیت
  - `set_format()`: تنظیم فرمت
  - `close()`: بستن handle
- استفاده از `ctypes.windll.kernel32` برای `CreateFileW`, `DeviceIoControl`
- الگوبرداری از `virtual-camera/examples/python_camera_example.py`

### 1.4 یکپارچه‌سازی با UI

- آپدیت `windows-app/virtual_camera/interface.py`:
  - جایگزینی `pyvirtualcam` با `VirtuCoreCamera`
  - تبدیل BGR (از OpenCV) به RGB (برای درایور)
- آپدیت `windows-app/ui/main_window.py`:
  - حذف منطق OBS
  - فعال‌سازی خودکار virtual camera در startup

### 1.5 تست و دیباگ دوربین

- تست با Camera app ویندوز
- تست با Zoom/Teams
- رفع باگ‌های احتمالی

### 1.6 پیاده‌سازی ماژول VirtuCore Microphone

**فایل جدید:** `windows-app/virtual_camera/virtucore_microphone.py`

- پیاده‌سازی کلاس `VirtuCoreMicrophone`:
  - شناسایی "Virtual Microphone Input" با WASAPI
  - `open()`: باز کردن audio client
  - `send_audio(samples)`: ارسال PCM audio
  - `close()`: بستن
- استفاده از `comtypes` و `pycaw` برای WASAPI
- الگوبرداری از `virtual-camera/examples/python_microphone_example.py`

### 1.7 یکپارچه‌سازی Audio Decoder

- آپدیت `windows-app/streaming/decoder.py`:
  - در `AudioDecoder.decode()`:
    - به جای پخش مستقیم با PyAudio
    - ارسال به `VirtuCoreMicrophone.send_audio()`
- آپدیت `windows-app/virtual_camera/audio_setup.py` (حذف VB-Cable)

### 1.8 تست و دیباگ صدا

- تست با Sound Recorder ویندوز
- تست با Zoom/Teams
- بررسی latency و quality

### 1.9 پاکسازی و مستندات

- حذف فایل‌های اضافی (OBS-related)
- آپدیت README و OVERVIEW
- آپدیت quick_start.bat

---

## فاز 2: ساخت DLL Wrapper (C++)

### 2.1 طراحی API

**فایل:** `virtual-camera/wrapper/VirtuCoreAPI.h`

```cpp
// Camera API
VIRTUCORE_API HANDLE VirtuCore_OpenCamera();
VIRTUCORE_API BOOL VirtuCore_SendFrame(HANDLE handle, BYTE* buffer, UINT32 width, UINT32 height);
VIRTUCORE_API BOOL VirtuCore_GetStatus(HANDLE handle, ...);
VIRTUCORE_API void VirtuCore_CloseCamera(HANDLE handle);

// Microphone API
VIRTUCORE_API BOOL VirtuCore_OpenMicrophone(UINT32 sampleRate, UINT32 channels);
VIRTUCORE_API BOOL VirtuCore_SendAudio(BYTE* samples, UINT32 size);
VIRTUCORE_API void VirtuCore_CloseMicrophone();
```

### 2.2 پیاده‌سازی Camera DLL

**فایل:** `virtual-camera/wrapper/VirtuCoreCamera.cpp`

- Wrapper برای IOCTL communication
- مدیریت errors و validation
- Thread safety

### 2.3 پیاده‌سازی Microphone DLL

**فایل:** `virtual-camera/wrapper/VirtuCoreMicrophone.cpp`

- Wrapper برای WASAPI
- Buffer management
- Format conversion

### 2.4 Build System

- ایجاد CMakeLists.txt برای DLL
- کانفیگ Visual Studio
- Build script: `virtual-camera/wrapper/build.bat`

### 2.5 Python Wrapper

**فایل:** `windows-app/virtual_camera/virtucore_dll.py`

- استفاده از `ctypes.CDLL` برای لود کردن DLL
- Wrapper functions
- Error handling

### 2.6 Refactor Python App

- جایگزینی `virtucore_camera.py` و `virtucore_microphone.py` با `virtucore_dll.py`
- تست کامل

---

## فاز 3: Installer نهایی

### 3.1 آماده‌سازی Assets

- جمع‌آوری تمام فایل‌های لازم:
  - `windows-app/` (Python app)
  - `virtual-camera/avstream-camera/` (built driver)
  - `virtual-camera/portcls-microphone/` (built driver)
  - `virtual-camera/wrapper/VirtuCore.dll`
  - Certificate برای test signing

### 3.2 ساخت Installer با Inno Setup

**فایل:** `installer/setup.iss`

- نصب درایورها (با pnputil)
- نصب DLL (در System32 یا app folder)
- نصب Python app
- نصب dependencies (VC++ Redistributable)
- ایجاد shortcuts

### 3.3 اسکریپت‌های نصب/حذف

- Pre-install: بررسی Windows version، test signing
- Post-install: ثبت درایورها
- Uninstall: حذف کامل تمام اجزا

### 3.4 تست Installer

- تست روی سیستم clean
- بررسی install/uninstall
- بررسی عملکرد بعد از نصب

### 3.5 مستندات نهایی

- راهنمای نصب برای کاربر نهایی
- Troubleshooting guide
- Release notes

---

## فایل‌های کلیدی که تغییر می‌کنند:

### حذف:

- `windows-app/virtual_camera/obs_controller.py`
- `windows-app/enable_obs_camera.bat`
- `windows-app/OBS_SETUP.md`

### ایجاد:

- `windows-app/virtual_camera/virtucore_camera.py`
- `windows-app/virtual_camera/virtucore_microphone.py`
- `windows-app/virtual_camera/virtucore_dll.py` (فاز 2)
- `virtual-camera/wrapper/` (کل پوشه در فاز 2)
- `installer/` (کل پوشه در فاز 3)

### ویرایش:

- `windows-app/virtual_camera/interface.py`
- `windows-app/virtual_camera/device_manager.py`
- `windows-app/streaming/decoder.py`
- `windows-app/main.py`
- `windows-app/requirements.txt`
- مستندات مختلف

### To-dos

- [ ] بررسی examples و مستندات درایورها برای درک IOCTL و WASAPI interfaces
- [ ] حذف تمام وابستگی‌های OBS از کد و مستندات
- [ ] پیاده‌سازی virtucore_camera.py با ctypes برای ارتباط با درایور AVStream
- [ ] یکپارچه‌سازی VirtuCoreCamera با interface.py و main_window.py
- [ ] تست دوربین مجازی با Camera app و Zoom/Teams
- [ ] پیاده‌سازی virtucore_microphone.py با WASAPI برای ارتباط با درایور PortCls
- [ ] یکپارچه‌سازی VirtuCoreMicrophone با decoder.py برای routing صدا
- [ ] تست میکروفون مجازی با Sound Recorder و Zoom/Teams
- [ ] پاکسازی کد و آپدیت مستندات
- [ ] طراحی C++ API برای DLL (header files و function signatures)
- [ ] پیاده‌سازی VirtuCore.dll در C++ با wrapper برای Camera و Microphone
- [ ] ساخت Python wrapper (virtucore_dll.py) و refactor اپلیکیشن
- [ ] تست کامل اپلیکیشن با DLL جدید
- [ ] جمع‌آوری و آماده‌سازی تمام فایل‌های لازم برای installer
- [ ] ساخت installer با Inno Setup شامل درایورها، DLL، app و dependencies
- [ ] تست نصب و حذف روی سیستم clean
- [ ] تکمیل مستندات نهایی برای محصول