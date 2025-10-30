# Android Stream Receiver با یکپارچه‌سازی VirtuCore

## خلاصه تغییرات

این نسخه از اپلیکیشن به طور کامل با درایورهای **VirtuCore** (دوربین و میکروفون مجازی سطح کرنل) یکپارچه شده است.

## تغییرات اصلی

### ✅ حذف شده
- وابستگی به OBS Studio
- وابستگی به pyvirtualcam
- وابستگی به VB-Audio Cable

### ✅ اضافه شده
- پشتیبانی کامل از VirtuCore Camera Driver (AVStream)
- پشتیبانی کامل از VirtuCore Microphone Driver (PortCls)
- ارتباط مستقیم با درایورهای کرنل از طریق IOCTL و WASAPI

## پیش‌نیازها

### 1. نصب درایورهای VirtuCore

قبل از اجرای برنامه، درایورهای VirtuCore باید نصب شوند:

```powershell
# فعال‌سازی Test Signing (PowerShell با Admin)
bcdedit /set testsigning on

# Restart سیستم
shutdown /r /t 0

# نصب درایور دوربین
cd ..\virtual-camera\avstream-camera
.\install.bat

# نصب درایور میکروفون
cd ..\portcls-microphone
.\install.bat
```

### 2. نصب وابستگی‌های Python

```bash
pip install -r requirements.txt
```

## اجرای برنامه

```bash
python main.py
```

## معماری جدید

```
┌─────────────────┐
│  Android Device │
│   (H.264/AAC)   │
└────────┬────────┘
         │
         │ Network
         ↓
┌─────────────────────┐
│  Windows App        │
│  ├─ VideoDecoder    │
│  └─ AudioDecoder    │
└──────┬──────────┬───┘
       │          │
       ↓          ↓
┌──────────┐ ┌──────────┐
│ VirtuCore│ │ VirtuCore│
│  Camera  │ │    Mic   │
│  (IOCTL) │ │ (WASAPI) │
└──────────┘ └──────────┘
       │          │
       ↓          ↓
   Zoom/Teams/OBS
```

## ماژول‌های جدید

### 1. `virtucore_camera.py`
- ارتباط با درایور دوربین از طریق IOCTL
- ارسال فریم‌های RGB24 به درایور
- مدیریت handle و error handling

### 2. `virtucore_microphone.py`
- ارتباط با درایور میکروفون از طریق WASAPI
- شناسایی "Virtual Microphone Input"
- ارسال PCM audio samples

### 3. تغییرات در `decoder.py`
- AudioDecoder حالا مستقیماً به VirtuCore Microphone ارسال می‌کند
- پشتیبانی از fallback به PyAudio در صورت عدم دسترسی به درایور

### 4. تغییرات در `device_manager.py`
- حذف کامل کدهای OBS
- بررسی نصب درایورهای VirtuCore
- راهنمای نصب درایورها

## تست

### دوربین مجازی
1. برنامه را اجرا کنید
2. به اندروید متصل شوید
3. دکمه "فعال‌سازی دوربین مجازی" را بزنید
4. در Zoom/Teams، دوربین "Virtual Camera" را انتخاب کنید

### میکروفون مجازی
1. صدا به صورت خودکار به درایور ارسال می‌شود
2. در Zoom/Teams، میکروفون "Virtual Microphone" را انتخاب کنید
3. یا با Sound Recorder تست کنید

## عیب‌یابی

### خطا: "درایور دوربین VirtuCore نصب نیست"
- مطمئن شوید درایور را با دسترسی Administrator نصب کرده‌اید
- Device Manager را چک کنید (Imaging devices)
- لاگ نصب را بررسی کنید

### خطا: "Virtual Microphone Input یافت نشد"
- درایور میکروفون را نصب کنید
- Settings > Sound را چک کنید
- دستگاه "Virtual Microphone Input" باید موجود باشد

### برنامه شروع نمی‌شود
- Test Signing را فعال کرده و سیستم را Restart کنید
- لاگ `android_stream.log` را بررسی کنید

## ساختار فایل‌ها

```
windows-app/
├── main.py                          # نقطه ورود اصلی
├── requirements.txt                 # وابستگی‌های Python
├── virtual_camera/
│   ├── virtucore_camera.py         # 🆕 ماژول دوربین
│   ├── virtucore_microphone.py     # 🆕 ماژول میکروفون
│   ├── interface.py                # آپدیت شده
│   └── device_manager.py           # آپدیت شده
├── streaming/
│   └── decoder.py                  # آپدیت شده
└── ui/
    └── main_window.py              # آپدیت شده
```

## مزایای یکپارچه‌سازی VirtuCore

### عملکرد
- ✅ تاخیر کمتر (بدون middleware)
- ✅ کیفیت بهتر (بدون تبدیل اضافی)
- ✅ CPU usage کمتر

### قابلیت اطمینان
- ✅ مستقل از نرم‌افزارهای شخص ثالث
- ✅ کنترل کامل بر روی pipeline
- ✅ Error handling دقیق‌تر

### سازگاری
- ✅ با تمام برنامه‌های ویندوز کار می‌کند
- ✅ استاندارد DirectShow/Media Foundation
- ✅ پشتیبانی از WASAPI

## توسعه بیشتر (فاز ۲)

در فاز بعدی، یک DLL در C++ ساخته خواهد شد که:
- Performance بهتر
- Error handling قوی‌تر
- Thread safety کامل
- قابلیت استفاده مجدد

## مشارکت

برای گزارش مشکلات یا پیشنهادات، لطفاً issue ایجاد کنید.

## مجوز

این پروژه تحت مجوز Open Source منتشر شده است.

