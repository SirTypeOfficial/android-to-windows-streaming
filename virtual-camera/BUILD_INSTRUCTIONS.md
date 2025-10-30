# دستورالعمل‌های ساخت و نصب درایورهای دوربین و میکروفون مجازی

## پیش‌نیازها

1. **Windows Driver Kit (WDK)**: نسخه مناسب برای Windows 11
2. **Visual Studio**: نسخه 2019 یا جدیدتر با پشتیبانی WDK
3. **Windows SDK**: آخرین نسخه
4. **دسترسی مدیریتی (Administrator)**: برای نصب درایورها

## ساخت درایورها

### روش ۱: استفاده از Visual Studio

#### ساخت درایور دوربین مجازی (AVStream)

```bash
cd avstream-camera
msbuild vcam.sln /p:Configuration=Release /p:Platform=x64
```

#### ساخت درایور میکروفون مجازی (PortCls)

```bash
cd portcls-microphone
msbuild vmic.sln /p:Configuration=Release /p:Platform=x64
```

### روش ۲: استفاده از WDK Build Environment

#### ساخت درایور دوربین

```bash
cd avstream-camera
build -ceZ
```

#### ساخت درایور میکروفون

```bash
cd portcls-microphone
build -ceZ
```

## امضای درایورها

### امضای تستی (Test Signing)

برای توسعه و تست، باید Test Signing را فعال کنید:

```powershell
# به عنوان Administrator اجرا کنید
bcdedit /set testsigning on
```

سپس سیستم را Restart کنید.

### امضای درایورها با گواهی تستی

```powershell
# ایجاد گواهی تستی
makecert -r -pe -ss TestCertStore -n "CN=TestDrivers" TestCert.cer

# امضای درایور دوربین
signtool sign /a /v /s TestCertStore /n TestDrivers /t http://timestamp.digicert.com avstream-camera\vcam.sys

# امضای درایور میکروفون
signtool sign /a /v /s TestCertStore /n TestDrivers /t http://timestamp.digicert.com portcls-microphone\vmic.sys
```

## نصب درایورها

### نصب درایور دوربین مجازی

```powershell
# به عنوان Administrator اجرا کنید
cd avstream-camera
.\install.bat
```

یا به صورت دستی:

```powershell
pnputil /add-driver avstream-camera\inf\vcam.inf /install
devcon install avstream-camera\inf\vcam.inf Root\VirtualCamera
```

### نصب درایور میکروفون مجازی

```powershell
# به عنوان Administrator اجرا کنید
cd portcls-microphone
.\install.bat
```

یا به صورت دستی:

```powershell
pnputil /add-driver portcls-microphone\inf\vmic.inf /install
devcon install portcls-microphone\inf\vmic.inf Root\VirtualMicrophone
```

## حذف درایورها

### حذف درایور دوربین

```powershell
cd avstream-camera
.\uninstall.bat
```

### حذف درایور میکروفون

```powershell
cd portcls-microphone
.\uninstall.bat
```

## بررسی نصب

### بررسی درایور دوربین

1. باز کردن Device Manager
2. مشاهده "Cameras" یا "Imaging devices"
3. باید "Virtual Camera Device" را ببینید

### بررسی درایور میکروفون

1. باز کردن Sound Settings
2. در قسمت Recording devices، باید "Virtual Microphone" را ببینید
3. در قسمت Playback devices، باید "Virtual Microphone Input" را ببینید

## عیب‌یابی

### درایور نصب نمی‌شود

- اطمینان حاصل کنید که Test Signing فعال است
- درایور را با یک گواهی معتبر امضا کنید
- لاگ‌های نصب را در Event Viewer بررسی کنید

### دستگاه در Device Manager ظاهر نمی‌شود

- از devcon برای ایجاد دستی Device Node استفاده کنید:
  ```powershell
  devcon install <path-to-inf> <hardware-id>
  ```

### BSOD یا سیستم ناپایدار

- از Driver Verifier برای تشخیص مشکلات استفاده کنید:
  ```powershell
  verifier /standard /driver vcam.sys
  verifier /standard /driver vmic.sys
  ```
- لاگ‌های kernel را با WinDbg بررسی کنید

## تست درایورها

### تست با Driver Verifier

```powershell
# فعال‌سازی Driver Verifier
verifier /standard /driver vcam.sys vmic.sys

# غیرفعال‌سازی پس از تست
verifier /reset
```

### تست با برنامه‌های کاربردی

- **دوربین**: Zoom, Microsoft Teams, Discord, OBS Studio
- **میکروفون**: هر برنامه ضبط صدا یا VoIP

## ساختار فایل‌ها

```
project-root/
├── avstream-camera/
│   ├── src/           # سورس کدهای درایور دوربین
│   ├── inc/           # فایل‌های header
│   ├── inf/           # فایل INF
│   ├── install.bat    # اسکریپت نصب
│   ├── uninstall.bat  # اسکریپت حذف
│   └── sources        # فایل build
├── portcls-microphone/
│   ├── src/           # سورس کدهای درایور میکروفون
│   ├── inc/           # فایل‌های header
│   ├── inf/           # فایل INF
│   ├── install.bat    # اسکریپت نصب
│   ├── uninstall.bat  # اسکریپت حذف
│   └── sources        # فایل build
└── BUILD_INSTRUCTIONS.md
```

## توجه

- این درایورها برای اهداف توسعه و تست طراحی شده‌اند
- برای استفاده در محیط production، باید با یک گواهی معتبر امضا شوند
- همیشه قبل از تست، از سیستم خود Backup تهیه کنید

