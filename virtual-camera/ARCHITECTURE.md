# معماری درایورهای دوربین و میکروفون مجازی

## نمای کلی

این پروژه شامل دو درایور سطح کرنل ویندوز است:
1. **AVStream Camera Driver**: درایور دوربین مجازی
2. **PortCls Audio Driver**: درایور میکروفون مجازی با قابلیت Loopback

## درایور دوربین مجازی (AVStream)

### معماری

```
User-Mode Application
        |
        | (IOCTL)
        ↓
[IOCTL Handler] ← → [Circular Frame Buffer]
        ↓
[AVStream Filter]
        ↓
[Capture Pin] → [Stream Pointer] → Media Foundation/DirectShow
```

### اجزای اصلی

#### 1. Device Management (`vcam_driver.c`)
- **DriverEntry**: نقطه ورود اصلی درایور
- **DeviceAdd**: ایجاد دستگاه و تخصیص منابع
- **DeviceStart/Stop**: مدیریت چرخه حیات دستگاه

#### 2. Filter Descriptor (`vcam_filter.c`)
- تعریف توپولوژی فیلتر
- تعریف Pin descriptors
- ارتباط با KS (Kernel Streaming)

#### 3. Format Support (`vcam_formats.c`)
- پشتیبانی از فرمت‌های:
  - RGB24 (640×480, 1280×720, 1920×1080)
  - NV12 (1920×1080)
  - YUY2 (1920×1080)
- هر فرمت با frame rate های 30fps و 60fps

#### 4. Capture Pin (`vcam_pin.c`)
- **PinCreate/Close**: مدیریت چرخه حیات Pin
- **PinSetDeviceState**: تغییر حالت (Stop → Pause → Run)
- **PinProcess**: تولید و ارسال فریم‌ها
- **IntersectHandler**: مذاکره فرمت با برنامه‌های کاربردی

#### 5. IOCTL Interface (`vcam_ioctl.c`)
- **IOCTL_VCAM_SEND_FRAME**: دریافت فریم از User-Mode
- **IOCTL_VCAM_GET_STATUS**: ارسال وضعیت درایور
- **IOCTL_VCAM_SET_FORMAT**: تنظیم فرمت
- Circular buffer با ۵ فریم برای پایداری

### جریان داده

```
1. برنامه User-Mode فریم را آماده می‌کند
2. از طریق IOCTL_VCAM_SEND_FRAME فریم را می‌فرستد
3. درایور فریم را در Circular Buffer ذخیره می‌کند
4. وقتی برنامه کاربردی (مثل Zoom) فریم می‌خواهد:
   - PinProcess فراخوانی می‌شود
   - آخرین فریم از Buffer خوانده می‌شود
   - در Stream Pointer قرار می‌گیرد
   - به برنامه کاربردی تحویل داده می‌شود
```

### Thread Safety

- استفاده از `KSPIN_LOCK` برای محافظت از Circular Buffer
- `KeAcquireSpinLock` و `KeReleaseSpinLock` برای دسترسی ایمن
- تمام دسترسی‌ها به Buffer در DISPATCH_LEVEL

## درایور میکروفون مجازی (PortCls)

### معماری

```
User-Mode Audio Application (WASAPI)
        |
        ↓
[Render Endpoint] → [Loopback Buffer] → [Capture Endpoint]
        ↑                                        ↓
   (Write Audio)                           (Read Audio)
        |                                        |
   Playback Apps                          Recording Apps
```

### اجزای اصلی

#### 1. Driver Management (`vmic_driver.c`)
- **DriverEntry**: ثبت با PortCls
- **AddDevice**: ایجاد Audio Adapter
- **PnP/Power**: مدیریت توان و Plug and Play

#### 2. Topology (`vmic_topology.c`)
- تعریف دو Pin:
  - **Render Sink**: ورودی صدا (Playback)
  - **Capture Source**: خروجی صدا (Recording)
- اتصال داخلی از طریق Loopback Node
- پشتیبانی از PCM:
  - 44.1 kHz و 48 kHz
  - 16-bit و 24-bit
  - Stereo

#### 3. WaveRT Miniport (`vmic_miniport.c`)
- پیاده‌سازی `IMiniportWaveRT`
- **Init**: مقداردهی اولیه miniport
- **NewStream**: ایجاد stream جدید
- مدیریت Loopback Buffer مشترک

#### 4. Stream Management (`vmic_stream.c`)
- پیاده‌سازی `IMiniportWaveRTStream`
- **AllocateAudioBuffer**: تخصیص بافر صوتی
- **SetState**: مدیریت حالت stream
- **GetPosition**: موقعیت فعلی در بافر
- جداسازی Render و Capture streams

#### 5. Loopback Buffer (`vmic_loopback.c`)
- Circular buffer با اندازه ۱ ثانیه (48kHz stereo 16-bit)
- **Write**: نوشتن صدا از Render stream
- **Read**: خواندن صدا برای Capture stream
- مدیریت Overflow/Underrun

### جریان داده

```
1. برنامه پخش صدا (مثل پخش‌کننده موسیقی):
   - صدا را به "Virtual Microphone Input" می‌فرستد
   - داده در Render Stream نوشته می‌شود
   
2. Loopback:
   - داده از Render Stream به Circular Buffer کپی می‌شود
   - با استفاده از Spin Lock برای thread safety
   
3. برنامه ضبط صدا (مثل Zoom):
   - از "Virtual Microphone" صدا می‌خواهد
   - داده از Circular Buffer خوانده می‌شود
   - به Capture Stream تحویل داده می‌شود
```

### Thread Safety

- استفاده از `KSPIN_LOCK` برای Loopback Buffer
- تمام عملیات Read/Write atomic هستند
- مدیریت Write/Read positions به صورت circular

## تعامل با User-Mode

### برای دوربین

```c
// ارسال فریم به درایور
HANDLE hDevice = CreateFile("\\\\.\\VirtualCamera", ...);

VCAM_FRAME_HEADER header = {
    .Width = 1920,
    .Height = 1080,
    .Format = 0,  // RGB24
    .BufferSize = 1920 * 1080 * 3,
    .Timestamp = ...
};

BYTE frameData[1920 * 1080 * 3];
// پر کردن frameData...

DeviceIoControl(hDevice, IOCTL_VCAM_SEND_FRAME, 
    &combinedBuffer, sizeof(header) + sizeof(frameData), 
    NULL, 0, NULL, NULL);
```

### برای میکروفون

```c
// استفاده از WASAPI برای پخش به ورودی مجازی
IMMDeviceEnumerator* enumerator;
IMMDevice* device;
IAudioClient* audioClient;

// پیدا کردن "Virtual Microphone Input"
// ایجاد Audio Client
// نوشتن داده به render buffer

// صدا به صورت خودکار به Capture endpoint loop می‌شود
```

## نکات عملکردی

### بهینه‌سازی حافظه
- استفاده از NonPagedPool برای بافرهای critical
- MDL (Memory Descriptor List) برای DMA
- حداقل‌سازی کپی داده

### مدیریت تأخیر
- دوربین: تأخیر < 33ms (1 frame در 30fps)
- میکروفون: تأخیر < 10ms (بسته به buffer size)

### پایداری
- اعتبارسنجی تمام ورودی‌های User-Mode
- مدیریت صحیح منابع (no memory leaks)
- تست با Driver Verifier

## محدودیت‌ها و بهبودهای آینده

### محدودیت‌های فعلی
- دوربین: فقط یک client در یک زمان
- میکروفون: بافر ثابت (۱ ثانیه)
- فرمت‌های محدود

### بهبودهای پیشنهادی
- پشتیبانی از multiple clients
- بافر دینامیک قابل تنظیم
- فرمت‌های بیشتر (H.264, AAC)
- Hardware acceleration
- Power management بهبود یافته

