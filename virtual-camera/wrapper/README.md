# VirtuCore Wrapper DLL

## نمای کلی

این DLL یک wrapper ساده و کارآمد برای ارتباط با درایورهای VirtuCore است.

## ویژگی‌ها

- API ساده و C-compatible
- مدیریت خطای کامل
- Thread-safe
- عملکرد بهینه
- قابل استفاده از Python, C++, C#, و هر زبانی که از DLL پشتیبانی کند

## ساختار

```
wrapper/
├── VirtuCoreAPI.h         # API عمومی
├── VirtuCoreCamera.cpp    # پیاده‌سازی Camera
├── VirtuCoreMicrophone.cpp # پیاده‌سازی Microphone
├── VirtuCoreError.cpp     # مدیریت خطا
├── DllMain.cpp            # نقطه ورود DLL
├── CMakeLists.txt         # Build system
└── README.md              # این فایل
```

## ساخت (Build)

### پیش‌نیازها
- Visual Studio 2019 یا جدیدتر
- CMake 3.15+
- Windows SDK 10.0.19041.0+

### مراحل

```bash
# ایجاد پوشه build
mkdir build
cd build

# کانفیگ CMake
cmake .. -G "Visual Studio 16 2019" -A x64

# Build
cmake --build . --config Release

# خروجی: VirtuCore.dll در build/Release/
```

## استفاده

### از C++

```cpp
#include "VirtuCoreAPI.h"

// Camera
VCAM_HANDLE camera = VirtuCore_OpenCamera();
if (camera) {
    VirtuCore_SendFrame(camera, buffer, 1920, 1080, VCAM_FORMAT_RGB24);
    VirtuCore_CloseCamera(camera);
}

// Microphone
VMIC_CONFIG config = { 48000, 2, VMIC_FORMAT_PCM16 };
VMIC_HANDLE mic = VirtuCore_OpenMicrophone(&config);
if (mic) {
    VirtuCore_SendAudio(mic, audioBuffer, audioSize);
    VirtuCore_CloseMicrophone(mic);
}
```

### از Python

```python
from ctypes import CDLL, c_void_p, c_uint32, c_bool, POINTER

dll = CDLL("VirtuCore.dll")

# Camera
dll.VirtuCore_OpenCamera.restype = c_void_p
camera = dll.VirtuCore_OpenCamera()

dll.VirtuCore_SendFrame.argtypes = [c_void_p, POINTER(c_ubyte), c_uint32, c_uint32, c_uint32]
dll.VirtuCore_SendFrame(camera, buffer, 1920, 1080, 0)

dll.VirtuCore_CloseCamera(camera)
```

## API Reference

مستندات کامل در `VirtuCoreAPI.h` موجود است.

### Camera Functions
- `VirtuCore_OpenCamera()` - باز کردن
- `VirtuCore_CloseCamera()` - بستن
- `VirtuCore_SendFrame()` - ارسال فریم
- `VirtuCore_GetCameraStatus()` - دریافت وضعیت
- `VirtuCore_SetCameraFormat()` - تنظیم فرمت
- `VirtuCore_IsCameraDriverInstalled()` - بررسی نصب

### Microphone Functions
- `VirtuCore_OpenMicrophone()` - باز کردن
- `VirtuCore_CloseMicrophone()` - بستن
- `VirtuCore_SendAudio()` - ارسال صدا
- `VirtuCore_GetMicrophoneInfo()` - دریافت اطلاعات
- `VirtuCore_IsMicrophoneDriverInstalled()` - بررسی نصب

### Error Handling
- `VirtuCore_GetLastError()` - کد خطا
- `VirtuCore_GetLastErrorMessage()` - پیام خطا

### Version Info
- `VirtuCore_GetVersion()` - اطلاعات نسخه

## وضعیت توسعه

- ✅ API Design - کامل
- 🚧 Implementation - در حال توسعه
- ⏳ Testing - منتظر
- ⏳ Documentation - منتظر

## مجوز

این پروژه تحت مجوز Open Source منتشر شده است.

