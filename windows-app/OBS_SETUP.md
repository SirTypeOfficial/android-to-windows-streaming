# راهنمای راه‌اندازی OBS Virtual Camera

## مشکل
پس از نصب OBS Studio، دستگاه Virtual Camera به ویندوز اضافه نمی‌شود.

## علت
OBS Virtual Camera فقط زمانی فعال است که:
1. OBS Studio باز باشد
2. از منوی Tools گزینه "Start Virtual Camera" انتخاب شده باشد

## راه‌حل

### مرحله 1: نصب OBS Studio
```
دانلود: https://obsproject.com/
نسخه توصیه شده: 30.x یا بالاتر
```

### مرحله 2: فعال‌سازی Virtual Camera در OBS
1. OBS Studio را باز کنید
2. Tools > Start Virtual Camera
3. OBS را باز نگه دارید (می‌توانید minimize کنید)

### مرحله 3: اجرای برنامه
```bash
python main.py
```

## تست Virtual Camera

### در ویندوز:
```
Settings > Bluetooth & devices > Cameras
```
باید "OBS Virtual Camera" را ببینید

### در برنامه‌های دیگر:
- Zoom: Settings > Video > Camera > OBS Virtual Camera
- Teams: Settings > Devices > Camera > OBS Virtual Camera
- Discord: User Settings > Voice & Video > Camera > OBS Virtual Camera

## نکات مهم

1. **OBS باید باز باشد**: تا زمانی که از Virtual Camera استفاده می‌کنید، OBS باید اجرا باشد
2. **یک instance در هر زمان**: فقط یک برنامه می‌تواند به Virtual Camera متصل شود
3. **بستن صحیح**: قبل از بستن OBS، ابتدا "Stop Virtual Camera" کنید

## خطاهای رایج

### خطا: "No virtual camera found"
**راه‌حل:**
1. OBS را ببندید و دوباره باز کنید
2. Tools > Start Virtual Camera
3. برنامه را restart کنید

### خطا: "Camera already in use"
**راه‌حل:**
1. برنامه‌های دیگری که از OBS Virtual Camera استفاده می‌کنند را ببندید
2. برنامه را restart کنید

### خطا: "pyvirtualcam import error"
**راه‌حل:**
```bash
pip install --upgrade pyvirtualcam
```

## Virtual Audio Setup

برای صدا، برنامه از دستگاه پیش‌فرض ویندوز استفاده می‌کند.

برای routing صدا به نرم‌افزارهای دیگر:
1. نصب VB-Audio Virtual Cable: https://vb-audio.com/Cable/
2. در ویندوز: Sound Settings > Output Device > CABLE Input

## پشتیبانی
در صورت مشکل:
1. لاگ‌ها را بررسی کنید: `android_stream.log`
2. OBS را با دسترسی Administrator اجرا کنید
3. نصب مجدد OBS Studio

