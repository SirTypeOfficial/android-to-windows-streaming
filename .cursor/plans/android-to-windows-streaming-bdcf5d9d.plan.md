<!-- bdcf5d9d-bb58-48aa-a86a-fd3d089d7b6b 2de6e941-5c2f-4b55-b79b-042fe79e8b0b -->
# پلن پیاده‌سازی سیستم استریم اندروید به ویندوز

## ساختار کلی پروژه

```
New folder/
├── android-app/          # اپلیکیشن اندروید
├── windows-app/          # اپلیکیشن ویندوز Python
├── virtual-camera/       # DirectShow filter (C++)
└── protocol/            # مستندات پروتکل ارتباطی
```

## مرحله 1: پروتکل ارتباطی و ساختار پیام

ایجاد پروتکل مشترک برای ارتباط بین اندروید و ویندوز:

- فرمت پکت‌ها: Header (نوع، سایز، timestamp) + Payload
- کانال کنترل: JSON commands برای تنظیمات دوربین
- کانال داده: H.264 NAL units + AAC frames
- Handshake و احراز هویت با pairing code

## مرحله 2: اپلیکیشن اندروید

**تکنولوژی‌ها**: Kotlin، CameraX، MediaCodec، Socket/USB

**کامپوننت‌ها**:

- **CameraManager**: مدیریت دوربین با CameraX، سوییچ جلو/عقب
- **VideoEncoder**: فشرده‌سازی H.264 با MediaCodec
- **AudioCapture**: ضبط صدا از میکروفون
- **AudioEncoder**: فشرده‌سازی AAC
- **NetworkStreamer**: ارسال داده از طریق WiFi (Socket Server)
- **USBStreamer**: ارسال داده از طریق USB با Android Open Accessory یا ADB reverse
- **ControlHandler**: دریافت و اعمال دستورات کنترلی
- **UI**: نمایش پیش‌نمایش، وضعیت اتصال، تنظیمات

## مرحله 3: اپلیکیشن ویندوز (Python)

**تکنولوژی‌ها**: Python 3.11+، PyQt6، OpenCV، FFmpeg-python، pyaudio

**ماژول‌ها**:

- **ConnectionManager**: مدیریت اتصال WiFi و USB
  - WiFi: Socket client
  - USB: ADB forward/reverse
- **StreamReceiver**: دریافت و parse کردن پکت‌ها
- **VideoDecoder**: دیکود H.264 با FFmpeg
- **AudioDecoder**: دیکود AAC
- **VideoDisplay**: نمایش ویدیو در UI با PyQt6
- **AudioPlayer**: پخش صدا با pyaudio
- **ControlPanel**: UI برای:
  - انتخاب رزولوشن (480p, 720p, 1080p)
  - تنظیم FPS (15, 30, 60)
  - سوییچ دوربین
  - کنترل فوکوس، فلش، روشنایی
  - نمایش latency و bitrate
- **VirtualCameraInterface**: ارسال فریم‌ها به Virtual Camera

## مرحله 4: DirectShow Virtual Camera Driver (C++)

**تکنولوژی**: C++، DirectShow SDK، Windows Media Foundation

**کامپوننت‌ها**:

- **Filter Registration**: ثبت فیلتر در سیستم
- **Source Filter**: پیاده‌سازی IBaseFilter
- **Output Pin**: پیاده‌سازی IPin برای خروجی ویدیو
- **Shared Memory**: دریافت فریم از Python app
- **Format Negotiation**: پشتیبانی از RGB24, YUY2, NV12

**روش ارتباط با Python**:

- Named Pipe یا Shared Memory برای انتقال فریم‌ها
- Python می‌نویسد، DirectShow می‌خواند

## مرحله 5: Integration و Testing

- تست اتصال WiFi
- تست اتصال USB
- تست Virtual Camera در Zoom/Skype/Teams
- تست latency و quality
- بهینه‌سازی buffer management

## فایل‌های کلیدی

**Android** (Kotlin):

- `MainActivity.kt`: UI اصلی
- `CameraManager.kt`: مدیریت دوربین
- `StreamingService.kt`: سرویس استریم در background
- `EncoderManager.kt`: مدیریت encoders

**Windows** (Python):

- `main.py`: Entry point
- `ui/main_window.py`: UI اصلی با PyQt6
- `streaming/receiver.py`: دریافت استریم
- `streaming/decoder.py`: دیکود ویدیو/صدا
- `control/commands.py`: ارسال دستورات کنترلی
- `virtual_camera/interface.py`: ارتباط با driver

**Virtual Camera** (C++):

- `VCamFilter.cpp`: پیاده‌سازی فیلتر
- `VCamPin.cpp`: پیاده‌سازی output pin
- `SharedMemory.cpp`: مدیریت حافظه مشترک
- `Register.cpp`: ثبت/حذف فیلتر

## ملاحظات مهم

1. **Security**: احراز هویت با pairing code 6 رقمی
2. **Performance**: استفاده از hardware encoder در اندروید
3. **Latency**: حداقل buffering برای کاهش تاخیر
4. **Error Handling**: reconnection خودکار در قطعی
5. **Battery**: بهینه‌سازی مصرف باتری در اندروید

### To-dos

- [ ] طراحی پروتکل ارتباطی و ساختار پیام‌ها (JSON schema برای کنترل، binary format برای media)
- [ ] راه‌اندازی پروژه اندروید در Android Studio با Kotlin و dependencies مورد نیاز
- [ ] پیاده‌سازی CameraX برای capture ویدیو با قابلیت سوییچ دوربین و کنترل تنظیمات
- [ ] پیاده‌سازی VideoEncoder با MediaCodec برای فشرده‌سازی H.264
- [ ] پیاده‌سازی AudioCapture و AudioEncoder برای ضبط و فشرده‌سازی صدا (AAC)
- [ ] پیاده‌سازی NetworkStreamer برای ارسال استریم از طریق WiFi (Socket Server)
- [ ] پیاده‌سازی USBStreamer برای ارسال استریم از طریق USB
- [ ] پیاده‌سازی ControlHandler برای دریافت و اعمال دستورات کنترلی از ویندوز
- [ ] طراحی و پیاده‌سازی UI اندروید با پیش‌نمایش و کنترل‌ها
- [ ] راه‌اندازی پروژه Python با PyQt6، requirements.txt و ساختار پروژه
- [ ] پیاده‌سازی ConnectionManager برای اتصال WiFi و USB (با ADB)
- [ ] پیاده‌سازی StreamReceiver برای دریافت و parse پکت‌ها
- [ ] پیاده‌سازی VideoDecoder و AudioDecoder با FFmpeg
- [ ] پیاده‌سازی VideoDisplay و AudioPlayer برای نمایش و پخش
- [ ] طراحی و پیاده‌سازی UI ویندوز با PyQt6 (control panel، نمایش ویدیو، تنظیمات)
- [ ] پیاده‌سازی ارسال دستورات کنترلی به اندروید
- [ ] راه‌اندازی پروژه C++ برای DirectShow Virtual Camera با Visual Studio
- [ ] پیاده‌سازی DirectShow Filter و Output Pin
- [ ] پیاده‌سازی Shared Memory یا Named Pipe برای دریافت فریم از Python
- [ ] پیاده‌سازی installer/uninstaller برای ثبت فیلتر در سیستم
- [ ] پیاده‌سازی VirtualCameraInterface در Python برای ارسال فریم به Virtual Camera
- [ ] تست کامل سیستم (اتصال، استریم، کنترل، virtual camera)