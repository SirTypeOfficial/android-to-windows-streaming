# 🚀 شروع کنید اینجا!

## مشکل شما حل شد ✅

دستگاه‌های مجازی (Virtual Camera & Audio) حالا به صورت خودکار ایجاد و مدیریت می‌شوند.

## 📋 چه کاری انجام شده؟

### ✅ مشکلات برطرف شده:
1. **Virtual Camera به ویندوز اضافه نمی‌شد** → حل شد
2. **Virtual Audio Device ایجاد نمی‌شد** → حل شد
3. **وابستگی زیاد به نرم‌افزارهای خارجی** → کاهش یافت
4. **پاکسازی دستی بعد از بستن** → اکنون خودکار است

### 🎯 ویژگی‌های جدید:
- ✅ تشخیص و راه‌اندازی خودکار OBS Virtual Camera
- ✅ مدیریت خودکار Virtual Audio
- ✅ پاکسازی خودکار هنگام بستن برنامه
- ✅ راهنماهای جامع فارسی
- ✅ اسکریپت‌های کمکی

## 🏃 سریع شروع کنید

### گام 1: نصب OBS Studio (اگر نصب نکرده‌اید)
```
دانلود: https://obsproject.com/
نسخه: 30.x یا بالاتر
```

### گام 2: اجرای برنامه
```bash
# روش 1: ساده (توصیه می‌شود)
start.bat

# روش 2: مرحله به مرحله
python setup_virtual_devices.py
python main.py
```

### گام 3: فعال کردن Virtual Camera در OBS
1. OBS باز می‌شود (خودکار یا دستی)
2. در منوی **Tools** گزینه **Start Virtual Camera** را بزنید
3. OBS را minimize کنید (نبندید!)

### گام 4: استفاده
- برنامه را اجرا کنید
- به اندروید متصل شوید
- تصویر به Virtual Camera ارسال می‌شود
- صدا از speaker پخش می‌شود

## 🎥 استفاده در برنامه‌های دیگر

اکنون می‌توانید در Zoom, Teams, Discord و... از دستگاه **OBS Virtual Camera** استفاده کنید.

مثال (Zoom):
```
Settings > Video > Camera > OBS Virtual Camera
```

## 🧪 تست سیستم

قبل از استفاده، سیستم را تست کنید:

```bash
python test_virtual_devices.py
```

این دستور همه چیز را بررسی می‌کند و گزارش می‌دهد.

## 📚 مستندات

### برای شروع سریع:
```
QUICK_START.md
```

### برای راه‌اندازی OBS:
```
OBS_SETUP.md
```

### برای اطلاعات کامل:
```
VIRTUAL_DEVICES_README.md
```

### برای دیدن تغییرات:
```
CHANGES_SUMMARY.md (در root پروژه)
```

## 🆘 مشکل دارید؟

### مشکل: Virtual Camera یافت نمی‌شود
```bash
enable_obs_camera.bat
```

### مشکل: خطای import
```bash
pip install -r requirements.txt
```

### مشکل: صدا کار نمی‌کند
```
Windows Settings > Sound > Output Device
```

### سایر مشکلات
لاگ‌ها را بررسی کنید:
```
cat android_stream.log
```

## 🎯 نکات مهم

### ضروری:
- ✓ OBS Studio باید نصب باشد
- ✓ OBS باید در حال اجرا باشد
- ✓ Virtual Camera در OBS فعال باشد

### اختیاری:
- VB-Audio Virtual Cable (برای routing صدا به برنامه‌های دیگر)

## 📁 ساختار فایل‌ها

```
windows-app/
├── start.bat                    ⭐ اینجا شروع کنید
├── setup_virtual_devices.py     بررسی سیستم
├── test_virtual_devices.py      تست عملکرد
├── enable_obs_camera.bat        راه‌انداز OBS
│
├── main.py                      برنامه اصلی
│
├── virtual_camera/              ماژول دستگاه‌های مجازی
│   ├── interface.py
│   ├── device_manager.py
│   ├── obs_controller.py
│   └── audio_setup.py
│
└── مستندات:
    ├── START_HERE.md           ⭐ همین فایل
    ├── QUICK_START.md          راهنمای سریع
    ├── OBS_SETUP.md            راهنمای OBS
    └── VIRTUAL_DEVICES_README.md  مرجع کامل
```

## ✅ چک‌لیست قبل از استفاده

- [ ] Python 3.8+ نصب است
- [ ] OBS Studio نصب است
- [ ] وابستگی‌های Python نصب شده (`pip install -r requirements.txt`)
- [ ] `test_virtual_devices.py` بدون خطا اجرا شد
- [ ] OBS در حال اجرا است و Virtual Camera فعال است

## 🎉 آماده‌اید!

اکنون همه چیز آماده است. فقط:

```bash
python main.py
```

و لذت ببرید! 🚀

---

**سؤال؟** مستندات را بخوانید یا لاگ‌ها را بررسی کنید.
**مشکل؟** `test_virtual_devices.py` را اجرا کنید.
**کمک؟** `QUICK_START.md` را مطالعه کنید.

