# راهنمای کامل دستگاه‌های مجازی

## نمای کلی

این برنامه به شما امکان می‌دهد تصویر و صدای دستگاه اندروید را به صورت جریان زنده (stream) دریافت کرده و به عنوان **دوربین مجازی** و **دستگاه صدای مجازی** در ویندوز ارائه دهید.

## معماری سیستم

```
Android Device
      ↓ (WiFi/USB)
Windows App (این برنامه)
      ↓
┌─────────────┬──────────────┐
│   Virtual   │   Virtual    │
│   Camera    │   Audio      │
└─────────────┴──────────────┘
      ↓              ↓
  (Zoom, Teams, Discord, etc.)
```

## پیش‌نیازها

### 1. Python 3.8 یا بالاتر
```bash
python --version
```

### 2. OBS Studio (برای Virtual Camera)
- **دانلود:** https://obsproject.com/
- **نسخه توصیه شده:** 30.x یا جدیدتر
- **نکته:** برای استفاده از Virtual Camera، OBS باید در حال اجرا باشد

### 3. VB-Audio Virtual Cable (اختیاری - برای Virtual Audio)
- **دانلود:** https://vb-audio.com/Cable/
- **نکته:** بدون این، صدا از دستگاه پیش‌فرض سیستم پخش می‌شود

## نصب

### مرحله 1: نصب وابستگی‌های Python
```bash
cd windows-app
pip install -r requirements.txt
```

### مرحله 2: بررسی سیستم
```bash
python setup_virtual_devices.py
```

این دستور:
- ✓ بررسی می‌کند که OBS نصب شده است
- ✓ تلاش می‌کند OBS را به صورت خودکار راه‌اندازی کند
- ✓ بررسی می‌کند که Virtual Audio موجود است
- ✓ راهنمای لازم را نمایش می‌دهد

### مرحله 3: فعال‌سازی Virtual Camera در OBS

#### روش 1: استفاده از اسکریپت (توصیه می‌شود)
```bash
enable_obs_camera.bat
```

#### روش 2: دستی
1. OBS Studio را باز کنید
2. منوی **Tools** > **Start Virtual Camera**
3. OBS را minimize کنید (نبندید!)

## استفاده

### راه‌اندازی برنامه
```bash
python main.py
```

### فرآیند اجرا
1. برنامه باز می‌شود
2. Virtual Camera و Audio راه‌اندازی می‌شوند
3. از طریق WiFi یا USB به دستگاه اندروید متصل شوید
4. استریم شروع می‌شود
5. تصویر و صدا به دستگاه‌های مجازی ارسال می‌شوند

### استفاده در برنامه‌های دیگر

#### Zoom
1. Settings > Video
2. Camera: **OBS Virtual Camera** را انتخاب کنید

#### Microsoft Teams
1. Settings > Devices
2. Camera: **OBS Virtual Camera** را انتخاب کنید

#### Discord
1. User Settings > Voice & Video
2. Camera: **OBS Virtual Camera** را انتخاب کنید

#### هر برنامه دیگری
در تنظیمات دوربین، **OBS Virtual Camera** را انتخاب کنید

## جزئیات فنی

### ساختار ماژول‌ها

```python
virtual_camera/
├── __init__.py              # Exports
├── interface.py             # رابط اصلی برای ارسال فریم
├── device_manager.py        # مدیریت کلی دستگاه‌ها
├── obs_controller.py        # کنترل OBS و Virtual Camera
└── audio_setup.py           # راه‌اندازی Virtual Audio
```

### VirtualCameraInterface
```python
camera = VirtualCameraInterface()
camera.start()              # شروع دوربین مجازی
camera.send_frame(frame)    # ارسال فریم (numpy array)
camera.stop()               # توقف دوربین مجازی
```

### VirtualDeviceManager
```python
manager = VirtualDeviceManager()
manager.setup_obs_virtual_camera()  # راه‌اندازی camera
manager.setup_virtual_audio()       # راه‌اندازی audio
manager.play_audio(audio_data)      # پخش صدا
manager.cleanup()                   # پاکسازی
```

### OBSController
```python
obs = OBSController()
obs.is_obs_installed()              # بررسی نصب OBS
obs.start_obs_minimized()           # راه‌اندازی OBS
obs.check_virtual_camera_status()   # بررسی وضعیت
```

## عیب‌یابی

### مشکل 1: "Virtual camera not found"

**علت:** OBS Virtual Camera فعال نیست

**راه‌حل:**
```bash
# بررسی کنید OBS در حال اجرا است
tasklist | findstr obs64.exe

# اگر نبود، اجرا کنید
enable_obs_camera.bat

# سپس در OBS: Tools > Start Virtual Camera
```

### مشکل 2: "pyvirtualcam import error"

**علت:** کتابخانه نصب نشده یا OBS نصب نیست

**راه‌حل:**
```bash
# نصب مجدد pyvirtualcam
pip install --upgrade pyvirtualcam

# بررسی نصب OBS
dir "C:\Program Files\obs-studio"
```

### مشکل 3: "Camera already in use"

**علت:** برنامه دیگری از Virtual Camera استفاده می‌کند

**راه‌حل:**
- برنامه‌های Zoom, Teams, Discord و غیره را ببندید
- برنامه را restart کنید

### مشکل 4: صدا پخش نمی‌شود

**بررسی:**
```
Windows Settings > System > Sound > Output Device
```

**راه‌حل:**
- بررسی کنید دستگاه صدای صحیح انتخاب شده است
- volume را بالا ببرید
- برای routing به برنامه‌های دیگر، VB-Audio Cable نصب کنید

### مشکل 5: تأخیر (Latency) بالا

**راه‌حل:**
- رزولوشن را کاهش دهید (Settings در برنامه)
- FPS را کاهش دهید
- از اتصال USB به جای WiFi استفاده کنید
- برنامه‌های پس‌زمینه غیرضروری را ببندید

## محدودیت‌ها

### Virtual Camera
- ✓ نیاز به OBS Studio دارد
- ✓ OBS باید در حال اجرا باشد
- ✓ فقط یک برنامه می‌تواند در هر زمان از Virtual Camera استفاده کند

### Virtual Audio
- ✓ بدون VB-Audio Cable فقط از دستگاه پیش‌فرض استفاده می‌شود
- ✓ برای routing به برنامه‌های دیگر، نیاز به نصب VB-Audio Cable

## بهینه‌سازی

### برای کیفیت بهتر:
- رزولوشن: 1080p
- FPS: 60
- اتصال: WiFi 5GHz یا USB

### برای تأخیر کمتر:
- رزولوشن: 720p
- FPS: 30
- اتصال: USB (توصیه می‌شود)

### برای مصرف کمتر منابع:
- رزولوشن: 480p
- FPS: 15
- بستن برنامه‌های پس‌زمینه

## سؤالات متداول

**Q: آیا می‌توانم بدون OBS از Virtual Camera استفاده کنم؟**
A: خیر، در ویندوز به یک virtual camera driver نیاز است. OBS رایگان‌ترین و بهترین گزینه است.

**Q: آیا OBS باید همیشه باز باشد؟**
A: بله، تا زمانی که از Virtual Camera استفاده می‌کنید. می‌توانید آن را minimize کنید.

**Q: آیا می‌توانم چند برنامه همزمان از Virtual Camera استفاده کنند؟**
A: خیر، فقط یک برنامه در هر زمان.

**Q: چرا Virtual Audio یافت نمی‌شود؟**
A: VB-Audio Virtual Cable نصب نیست. برنامه از دستگاه پیش‌فرض استفاده می‌کند.

**Q: آیا این روی macOS/Linux کار می‌کند؟**
A: کد فعلی برای ویندوز بهینه شده است. برای macOS/Linux نیاز به تغییرات دارد.

## مجوز و منابع

### این پروژه
- کد: پروژه شما
- مجوز: بر اساس انتخاب شما

### وابستگی‌های خارجی
- **OBS Studio:** GPL-2.0 | https://obsproject.com/
- **pyvirtualcam:** GPL-2.0 | https://github.com/letmaik/pyvirtualcam
- **VB-Audio Cable:** Freeware | https://vb-audio.com/Cable/

## پشتیبانی

### لاگ‌ها
همه لاگ‌ها در فایل `android_stream.log` ذخیره می‌شوند.

### راهنماها
- `QUICK_START.md` - راهنمای سریع
- `OBS_SETUP.md` - راهنمای تفصیلی OBS
- این فایل - مرجع کامل

### اسکریپت‌های کمکی
- `setup_virtual_devices.py` - بررسی سیستم
- `enable_obs_camera.bat` - راه‌انداز OBS

