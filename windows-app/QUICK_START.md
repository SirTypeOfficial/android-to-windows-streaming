# راهنمای سریع راه‌اندازی

## مرحله 1: نصب نیازمندی‌ها

```bash
pip install -r requirements.txt
```

## مرحله 2: بررسی دستگاه‌های مجازی

```bash
python setup_virtual_devices.py
```

این اسکریپت:
- بررسی می‌کند OBS Virtual Camera نصب است یا نه
- بررسی می‌کند Virtual Audio Device موجود است یا نه  
- راهنمای لازم را نمایش می‌دهد

## مرحله 3: راه‌اندازی OBS Virtual Camera

### روش 1: خودکار
اسکریپت `setup_virtual_devices.py` به صورت خودکار OBS را راه‌اندازی می‌کند

### روش 2: دستی
1. OBS Studio را باز کنید
2. Tools > Start Virtual Camera
3. OBS را minimize کنید

## مرحله 4: اجرای برنامه

```bash
python main.py
```

## تست Virtual Camera

### در ویندوز:
```
Settings > Bluetooth & devices > Cameras
```
شما باید "OBS Virtual Camera" را ببینید

### در برنامه‌های دیگر:
اکنون می‌توانید در هر برنامه‌ای که از دوربین استفاده می‌کند، "OBS Virtual Camera" را انتخاب کنید:
- Zoom
- Microsoft Teams
- Discord
- Skype
- و غیره

## نکات مهم

### Virtual Camera:
- OBS باید در حال اجرا باشد (می‌تواند minimize باشد)
- "Start Virtual Camera" در OBS فعال باشد
- فقط یک برنامه در هر زمان می‌تواند از Virtual Camera استفاده کند

### Virtual Audio:
- برای routing صدا به برنامه‌های دیگر نیاز به VB-Audio Cable دارید
- بدون VB-Audio Cable، صدا از بلندگوی پیش‌فرض پخش می‌شود
- دانلود: https://vb-audio.com/Cable/

## عیب‌یابی

### مشکل: Virtual Camera یافت نمی‌شود
**راه‌حل:**
```bash
# 1. بررسی نصب OBS
dir "C:\Program Files\obs-studio"

# 2. اجرای OBS و فعال کردن Virtual Camera
enable_obs_camera.bat

# 3. اجرای مجدد برنامه
python main.py
```

### مشکل: صدا پخش نمی‌شود
**راه‌حل:**
```
Settings > System > Sound > Output Device
بررسی کنید دستگاه صدای صحیح انتخاب شده است
```

### مشکل: خطای import
**راه‌حل:**
```bash
pip install --upgrade -r requirements.txt
```

## ساختار پروژه

```
windows-app/
├── main.py                          # نقطه ورود اصلی
├── setup_virtual_devices.py         # اسکریپت بررسی و راه‌اندازی
├── enable_obs_camera.bat            # راه‌انداز OBS (Windows)
├── virtual_camera/
│   ├── interface.py                 # رابط دوربین مجازی
│   ├── device_manager.py            # مدیریت دستگاه‌های مجازی
│   ├── obs_controller.py            # کنترل کننده OBS
│   └── audio_setup.py               # راه‌انداز صدای مجازی
└── ...
```

## وابستگی‌ها

### ضروری:
- Python 3.8+
- PyQt6
- opencv-python
- numpy
- pyaudio
- pyvirtualcam

### اختیاری (برای عملکرد کامل):
- OBS Studio (برای Virtual Camera)
- VB-Audio Virtual Cable (برای Virtual Audio)

## پشتیبانی

در صورت بروز مشکل:
1. فایل `android_stream.log` را بررسی کنید
2. مستندات کامل را در `OBS_SETUP.md` مطالعه کنید
3. اسکریپت `setup_virtual_devices.py` را اجرا کنید تا راهنمای دقیق دریافت کنید

