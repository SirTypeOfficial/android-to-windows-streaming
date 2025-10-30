# 🚀 شروع کنید اینجا!

## یکپارچه‌سازی VirtuCore ✅

این برنامه حالا مستقیماً با درایورهای **VirtuCore** (دوربین و میکروفون مجازی سطح کرنل) کار می‌کند.

## 📋 تغییرات مهم

### ✅ حذف شده:
- وابستگی به OBS Studio
- وابستگی به pyvirtualcam
- وابستگی به VB-Audio Cable

### ✅ اضافه شده:
- پشتیبانی مستقیم از VirtuCore Camera Driver
- پشتیبانی مستقیم از VirtuCore Microphone Driver
- عملکرد بهتر و تاخیر کمتر

## 🏃 سریع شروع کنید

### گام 1: نصب درایورهای VirtuCore

**مهم: این مرحله الزامی است!**

```powershell
# 1. فعال‌سازی Test Signing (PowerShell با Admin)
bcdedit /set testsigning on

# 2. Restart سیستم
shutdown /r /t 0

# 3. نصب درایور دوربین (با Admin)
cd ..\virtual-camera\avstream-camera
.\install.bat

# 4. نصب درایور میکروفون (با Admin)
cd ..\portcls-microphone  
.\install.bat
```

### گام 2: نصب وابستگی‌های Python

```bash
cd windows-app
pip install -r requirements.txt
```

### گام 3: اجرای برنامه

```bash
python main.py
```

## 🎯 استفاده

1. برنامه را اجرا کنید
2. به اندروید متصل شوید (WiFi یا USB)
3. دکمه "فعال‌سازی دوربین مجازی" را بزنید
4. در Zoom/Teams/OBS:
   - دوربین: **Virtual Camera** را انتخاب کنید
   - میکروفون: **Virtual Microphone** را انتخاب کنید

## 🔍 بررسی نصب درایورها

### دوربین:
```
Device Manager > Imaging devices > Virtual Camera
```

### میکروفون:
```
Settings > Sound > Virtual Microphone Input (output)
Settings > Sound > Virtual Microphone (input)
```

## 🆘 عیب‌یابی

### خطا: "درایور دوربین VirtuCore نصب نیست"
- با دسترسی Admin نصب کنید
- Test Signing را فعال کرده و Restart کنید
- Device Manager را چک کنید

### خطا: "Virtual Microphone Input یافت نشد"  
- درایور میکروفون را نصب کنید
- Sound Settings را چک کنید

### برنامه شروع نمی‌شود
- فایل `android_stream.log` را بررسی کنید
- مطمئن شوید Test Signing فعال است

## 📚 مستندات

### اطلاعات کامل:
```
VIRTUCORE_README.md
```

### راهنمای درایورها:
```
..\virtual-camera\README.md
..\virtual-camera\BUILD_INSTRUCTIONS.md
```

## ✅ چک‌لیست

- [ ] Python 3.8+ نصب است
- [ ] Test Signing فعال و سیستم Restart شده
- [ ] درایور دوربین نصب شده
- [ ] درایور میکروفون نصب شده
- [ ] وابستگی‌های Python نصب شده

## 🎉 آماده‌اید!

```bash
python main.py
```

---

**مشکل؟** `android_stream.log` را بررسی کنید
**سوال؟** `VIRTUCORE_README.md` را بخوانید
**کمک؟** مستندات درایورها را مطالعه کنید

