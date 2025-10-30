<!-- aaefaf54-594d-4210-851f-2fbd74f67454 7e0824ca-7d54-42bc-b788-ff7f10da3e07 -->
# طرح توسعه درایورهای دوربین و میکروفون مجازی

## نمای کلی

این پروژه شامل بازنویسی کامل سیستم Virtual Camera موجود (که مبتنی بر DirectShow است) به یک راهکار کامل مبتنی بر درایورهای سطح کرنل ویندوز است. کد موجود می‌تواند به عنوان مرجع برای مفاهیمی مانند Shared Memory استفاده شود، اما معماری اصلی باید از ابتدا با WDK نوشته شود.

## فاز ۱: درایور دوربین مجازی (AVStream Minidriver)

### ۱.۱ راه‌اندازی پروژه WDK

- ایجاد یک پروژه جدید Kernel Mode Driver (WDM) در Visual Studio
- تنظیم Target Platform به Windows 11 x64
- اضافه کردن وابستگی‌های AVStream (ks.lib, ksguid.lib)
- ایجاد ساختار دایرکتوری: 
- `avstream-camera/src/` برای فایل‌های .c/.cpp
- `avstream-camera/inc/` برای فایل‌های .h
- `avstream-camera/inf/` برای فایل INF

### ۱.۲ پیاده‌سازی Device و Filter Descriptor

- تعریف `KSDEVICE_DESCRIPTOR` برای دستگاه اصلی
- پیاده‌سازی توابع Callback:
- `DriverEntry()`: نقطه ورود درایور
- `DeviceAdd()`: ایجاد دستگاه جدید
- `DeviceStart()`: راه‌اندازی دستگاه
- `DeviceStop()`: توقف دستگاه
- تعریف `KSFILTER_DESCRIPTOR` برای فیلتر Capture
- تعریف Pin Descriptor برای Output Pin

### ۱.۳ پشتیبانی از فرمت‌ها و رزولوشن‌ها

- تعریف آرایه `KSDATARANGE_VIDEO` برای:
- RGB24 (640×480, 1280×720, 1920×1080) در 30fps و 60fps
- NV12 (640×480, 1280×720, 1920×1080) در 30fps و 60fps
- YUY2 (640×480, 1280×720, 1920×1080) در 30fps و 60fps
- پیاده‌سازی `IntersectHandler()` برای مذاکره فرمت
- پیاده‌سازی `SetDataFormat()` برای تنظیم فرمت انتخابی

### ۱.۴ پیاده‌سازی Video Capture Pin

- تعریف ساختار Context برای Pin (فریم فعلی، تایمینگ، فرمت)
- پیاده‌سازی `PinCreate()` و `PinClose()`
- پیاده‌سازی `PinSetDeviceState()` برای Start/Stop
- پیاده‌سازی `PinProcess()` برای تولید فریم‌ها:
- خواندن از Shared Memory یا IOCTL Buffer
- تبدیل فرمت در صورت نیاز
- پر کردن Stream Pointers

### ۱.۵ رابط IOCTL برای User-Mode

- تعریف IOCTL کدهای سفارشی:
- `IOCTL_VCAM_SEND_FRAME`: ارسال یک فریم کامل
- `IOCTL_VCAM_GET_STATUS`: دریافت وضعیت درایور
- `IOCTL_VCAM_SET_FORMAT`: تنظیم فرمت پیش‌فرض
- پیاده‌سازی `DispatchDeviceControl()` با اعتبارسنجی ورودی
- استفاده از `ExAllocatePoolWithTag()` برای بافرهای داخلی
- پیاده‌سازی یک Circular Buffer در Kernel برای نگهداری ۳-۵ فریم آخر
- استفاده از Spin Lock برای thread safety

### ۱.۶ فایل INF و نصب

- ایجاد فایل `vcam.inf` با اطلاعات کامل:
- Class = Camera
- ClassGuid = {ca3e7ab9-b4c3-4ae6-8251-579ef933890f}
- تعریف Service و Device Instance
- امضای درایور با Test Certificate برای حالت توسعه
- اسکریپت نصب/حذف با `pnputil`

## فاز ۲: درایور میکروفون مجازی (PortCls Minidriver)

### ۲.۱ راه‌اندازی پروژه PortCls

- ایجاد پروژه Kernel Mode Driver جدید
- اضافه کردن وابستگی‌های PortCls (portcls.lib)
- ساختار دایرکتوری مشابه فاز ۱

### ۲.۲ پیاده‌سازی Miniport Topology

- تعریف Topology با دو Endpoint:
- Capture Endpoint (میکروفون مجازی - خروجی)
- Render Endpoint (ورودی صدا - Loopback)
- تعریف `PCFILTER_DESCRIPTOR` و `PCPIN_DESCRIPTOR`
- اتصال Render به Capture از طریق Internal Connection

### ۲.۳ پیاده‌سازی WaveRT Miniport

- پیاده‌سازی `IMiniportWaveRT` برای Capture Pin:
- `NewStream()`: ایجاد جریان جدید
- `GetPosition()`: موقعیت فعلی در بافر
- `AllocateAudioBuffer()`: تخصیص Cyclic Buffer
- پیاده‌سازی `IMiniportWaveRT` برای Render Pin
- پیاده‌سازی `IMiniportWaveRTStream` با توابع:
- `SetFormat()`: تنظیم PCM 16/24-bit, 44.1/48 kHz, Stereo
- `SetState()`: Start/Stop/Pause
- کپی داده از Render Buffer به Capture Buffer (Loopback)

### ۲.۴ مدیریت بافر و تایمینگ

- استفاده از `KeSetTimerEx()` برای تایمر دقیق
- پیاده‌سازی DPC Routine برای کپی داده
- مدیریت موقعیت‌های Read/Write در Circular Buffer
- اطمینان از عدم Underrun/Overrun

### ۲.۵ فایل INF و نصب

- ایجاد `vmic.inf`:
- Class = MEDIA
- ClassGuid = {4d36e96c-e325-11ce-bfc1-08002be10318}
- تعریف دو Endpoint (Render و Capture)
- امضا و اسکریپت نصب

## ملاحظات مهم

### امنیت و پایداری

- تمام ورودی‌های User-Mode باید با `ProbeForRead()` و `ProbeForWrite()` اعتبارسنجی شوند
- استفاده از `try-except` برای هندل کردن exceptionها
- تست کامل با Driver Verifier برای تشخیص memory leakها

### سازگاری

- تست با Media Foundation Transform (MFT)
- تست با DirectShow
- تست با WebRTC در مرورگرها
- تست با برنامه‌های معروف (Zoom, Teams, Discord, OBS)

### عملکرد

- حداقل‌سازی کپی حافظه با استفاده از MDL (Memory Descriptor List)
- اجرای عملیات سنگین در DPC Level نه IRQL بالاتر
- پروفایل کردن با WPA (Windows Performance Analyzer)

## فایل‌های کلیدی مورد نیاز

### درایور دوربین

- `vcam_driver.c`: DriverEntry و Device Management
- `vcam_filter.c`: Filter Descriptor و Pin Descriptors
- `vcam_pin.c`: Pin Callbacks و Frame Generation
- `vcam_ioctl.c`: IOCTL Handler و بافر مدیریت
- `vcam_formats.c`: تعاریف KSDATARANGE و تبدیل فرمت
- `vcam.inf`: فایل نصب

### درایور میکروفون

- `vmic_driver.c`: DriverEntry و Adapter Management
- `vmic_topology.c`: Topology Descriptor
- `vmic_wavert.c`: WaveRT Miniport Implementation
- `vmic_stream.c`: Stream Management و Loopback Logic
- `vmic.inf`: فایل نصب

### مستندات (در فاز ۳)

- معماری درایورها
- راهنمای IOCTL API
- نحوه استفاده از WASAPI برای صدا

## نکات از کد موجود قابل استفاده

- مفهوم Shared Memory در `SharedMemory.cpp` می‌تواند برای ارتباط User-Kernel الهام باشد
- مقادیر ثابت در `common.h` (رزولوشن، FPS) می‌توانند به عنوان پیش‌فرض استفاده شوند
- منطق FillBuffer در `VCamPin.cpp` (تایمینگ فریم) قابل ترجمه به Kernel است

### To-dos

- [ ] راه‌اندازی پروژه WDK برای AVStream Camera Driver با ساختار دایرکتوری مناسب
- [ ] پیاده‌سازی Device و Filter Descriptors با توابع Callback اصلی
- [ ] تعریف KSDATARANGE برای فرمت‌ها و رزولوشن‌های مختلف (RGB24, NV12, YUY2)
- [ ] پیاده‌سازی Video Capture Pin با توابع Process و State Management
- [ ] پیاده‌سازی رابط IOCTL با Circular Buffer و thread safety
- [ ] ایجاد فایل INF و اسکریپت‌های نصب/حذف برای دوربین
- [ ] راه‌اندازی پروژه WDK برای PortCls Microphone Driver
- [ ] پیاده‌سازی Topology با Render و Capture Endpoints
- [ ] پیاده‌سازی WaveRT Miniport برای Render و Capture Pins
- [ ] پیاده‌سازی منطق Loopback و مدیریت بافر صوتی
- [ ] ایجاد فایل INF و اسکریپت‌های نصب/حذف برای میکروفون
- [ ] تست کامل هر دو درایور با Driver Verifier و برنامه‌های مختلف