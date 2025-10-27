# Video Config Fix - خلاصه تغییرات

## مشکل اصلی
برنامه ویندوز فقط Audio Frame دریافت می‌کرد و هیچ Video Frame یا Config packet دریافت نمی‌شد. 
خطای اصلی: `Audio codec not yet configured, skipping frame`

## علت مشکل
1. VideoEncoder در اندروید هیچوقت SPS/PPS (Video Config) را ارسال نمی‌کرد
2. بدون SPS/PPS، decoder ویندوز نمی‌توانست فریم‌های H.264 را decode کند
3. AudioEncoder هم CONFIG ارسال نمی‌کرد چون INFO_OUTPUT_FORMAT_CHANGED هرگز رخ نمی‌داد

## تغییرات انجام شده

### اندروید

#### 1. VideoEncoder.kt
```kotlin
// اضافه شده:
var onConfigData: ((ByteArray) -> Unit)? = null
private var configSent = false

// در encodeFrame():
if (outputBufferIndex == MediaCodec.INFO_OUTPUT_FORMAT_CHANGED) {
    val outputFormat = codec.outputFormat
    val csd0 = outputFormat.getByteBuffer("csd-0") // SPS
    val csd1 = outputFormat.getByteBuffer("csd-1") // PPS
    
    if (csd0 != null && csd1 != null && !configSent) {
        val configData = ByteArray(spsSize + ppsSize)
        csd0.get(configData, 0, spsSize)
        csd1.get(configData, spsSize, ppsSize)
        
        onConfigData?.invoke(configData)
        configSent = true
    }
}

// Skip CODEC_CONFIG buffers:
if ((bufferInfo.flags and MediaCodec.BUFFER_FLAG_CODEC_CONFIG) == 0) {
    // Send frame data
}
```

#### 2. USBStreamer.kt
```kotlin
fun sendVideoConfig(configData: ByteArray) {
    scope.launch {
        val packet = Packet(PacketType.VIDEO_CONFIG, configData, 0, 0)
        outputStream?.write(packet.toBytes())
        outputStream?.flush()
    }
}
```

#### 3. NetworkStreamer.kt
```kotlin
fun sendVideoConfig(configData: ByteArray) {
    scope.launch {
        val packet = Packet(PacketType.VIDEO_CONFIG, configData, 0, 0)
        outputStream?.write(packet.toBytes())
        outputStream?.flush()
    }
}
```

#### 4. StreamingService.kt
```kotlin
// اتصال callback:
videoEncoder?.onConfigData = { configData ->
    usbStreamer?.sendVideoConfig(configData)  // یا networkStreamer
}
```

### ویندوز

#### 5. decoder.py - VideoDecoder
```python
def __init__(self):
    self.codec_opened = False  # اضافه شده
    
def set_config(self, config_data: bytes):
    """Set SPS/PPS from Android encoder"""
    self.codec.extradata = config_data
    self.codec.open()
    self.codec_opened = True
    
def decode(self, data: bytes, timestamp: int, is_keyframe: bool):
    if not self.codec_opened:
        logger.warning("Video codec not yet configured, skipping frame")
        return
    # ... decode logic
```

#### 6. receiver.py
```python
# در __init__:
self.on_video_config: Optional[Callable[[bytes], None]] = None

# در _handle_packet:
if header.packet_type == PacketType.VIDEO_CONFIG:
    if self.on_video_config:
        self.on_video_config(payload)
```

#### 7. main_window.py
```python
# در setup_connections:
self.stream_receiver.on_video_config = self.video_decoder.set_config
self.stream_receiver.on_video_frame = self.video_decoder.decode
self.stream_receiver.on_audio_config = self.audio_decoder.set_config
self.stream_receiver.on_audio_frame = self.audio_decoder.decode
```

## جریان کار جدید (Flow)

1. **Android:** VideoEncoder شروع می‌شود
2. **Android:** اولین فریم encode می‌شود → INFO_OUTPUT_FORMAT_CHANGED
3. **Android:** SPS/PPS استخراج و از طریق VIDEO_CONFIG packet ارسال می‌شود
4. **Windows:** VIDEO_CONFIG دریافت می‌شود
5. **Windows:** VideoDecoder.set_config() صدا زده می‌شود
6. **Windows:** Codec با extradata (SPS/PPS) open می‌شود
7. **Windows:** حالا آماده دریافت و decode کردن VIDEO_FRAME است

همینطور برای Audio:
1. **Android:** AudioEncoder شروع می‌شود
2. **Android:** اولین فریم encode می‌شود → INFO_OUTPUT_FORMAT_CHANGED
3. **Android:** CSD-0 (AAC config) استخراج و از طریق AUDIO_CONFIG ارسال می‌شود
4. **Windows:** AUDIO_CONFIG دریافت می‌شود
5. **Windows:** AudioDecoder.set_config() صدا زده می‌شود
6. **Windows:** حالا آماده decode کردن AUDIO_FRAME است

## دستورات Build و نصب

### Build APK
```batch
cd android-app
gradlew.bat clean assembleDebug
```

### نصب APK
```batch
adb install -r build\outputs\apk\debug\android-app-debug.apk
```

### اجرای برنامه ویندوز
```batch
cd windows-app
run.bat
```

## لاگ‌های مورد انتظار

### Android (Logcat)
```
VideoEncoder: Video encoder started: 1280x720 @ 30fps
VideoEncoder: Video config data sent: SPS=XX bytes, PPS=YY bytes
USBStreamer: Video config sent: ZZ bytes
AudioEncoder: Audio encoder started: 44100Hz, 2 channels
AudioEncoder: Audio config data sent: XX bytes
USBStreamer: Audio config sent: XX bytes
```

### Windows (Console)
```
streaming.receiver - INFO - Handling video config: size=XX
streaming.decoder - INFO - Video codec configured with SPS/PPS: XX bytes
streaming.decoder - INFO - Codec parameters: 1280x720, format=yuv420p
streaming.receiver - INFO - Handling audio config: size=XX
streaming.decoder - INFO - Audio codec configured with extradata: XX bytes
streaming.receiver - DEBUG - Handling video frame: size=XXXX
streaming.decoder - DEBUG - Frame decoded successfully: 1280x720
streaming.receiver - DEBUG - Handling audio frame: size=XXX
```

## نکات مهم

1. ✅ حتماً APK جدید را rebuild و reinstall کنید
2. ✅ Config packets قبل از frame packets ارسال می‌شوند
3. ✅ Decoder ها فریم‌ها را تا زمان دریافت config skip می‌کنند
4. ✅ SPS/PPS فقط یک بار در ابتدا ارسال می‌شود (configSent flag)
5. ✅ CODEC_CONFIG buffers در encoder skip می‌شوند (چون جداگانه ارسال شده‌اند)

## فایل‌های تغییر یافته

### Android
- android-app/src/main/java/com/streamapp/encoder/VideoEncoder.kt
- android-app/src/main/java/com/streamapp/network/USBStreamer.kt
- android-app/src/main/java/com/streamapp/network/NetworkStreamer.kt
- android-app/src/main/java/com/streamapp/StreamingService.kt

### Windows
- windows-app/streaming/decoder.py
- windows-app/streaming/receiver.py
- windows-app/ui/main_window.py

## تست

پس از نصب APK جدید:
1. برنامه اندروید را باز کنید
2. USB را انتخاب کنید
3. Start Streaming را بزنید
4. برنامه ویندوز را اجرا کنید (run.bat)
5. در ویندوز روی "USB اتصال" کلیک کنید
6. باید تصویر و صدا را ببینید/بشنوید!

---
تاریخ: 2025-10-27
نسخه: 1.1

