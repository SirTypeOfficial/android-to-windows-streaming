# اصلاح خطای "Broken pipe"

## مشکل
در لاگ‌های Android خطای `java.net.SocketException: Broken pipe` هنگام ارسال داده‌های صوتی و تصویری مشاهده می‌شد. این خطا زمانی رخ می‌دهد که سعی می‌کنیم روی socket بسته شده بنویسیم.

## راه حل
در هر دو فایل `USBStreamer.kt` و `NetworkStreamer.kt`:

1. **چک اتصال قبل از ارسال**: قبل از نوشتن داده‌ها روی socket، بررسی می‌کنیم که client متصل است یا خیر.
2. **Suppress کردن خطای "Broken pipe"**: خطای "Broken pipe" را catch می‌کنیم و log نمی‌کنیم تا لاگ‌ها تمیز بمانند.

### تغییرات در `sendVideoFrame` و `sendAudioFrame`:

```kotlin
fun sendAudioFrame(data: ByteArray, timestamp: Long) {
    scope.launch {
        try {
            // Check if client is connected
            if (clientSocket?.isConnected != true) {
                return@launch
            }
            
            val packet = Packet(PacketType.AUDIO_FRAME, data, timestamp, 0)
            outputStream?.write(packet.toBytes())
            outputStream?.flush()
        } catch (e: Exception) {
            // Don't log "Broken pipe" errors when socket is disconnected
            if (e is java.net.SocketException && e.message?.contains("Broken pipe") == true) {
                return@launch
            }
            Log.e(TAG, "Error sending audio frame", e)
        }
    }
}
```

## فایل‌های تغییر یافته
- `android-app/src/main/java/com/streamapp/network/USBStreamer.kt`
- `android-app/src/main/java/com/streamapp/network/NetworkStreamer.kt`

## نحوه تست
1. اپلیکیشن Android را در Android Studio باز کنید.
2. `Build > Rebuild Project` را اجرا کنید.
3. اپلیکیشن را بر روی دستگاه Android نصب کنید.
4. اپلیکیشن Windows را اجرا کنید و به دستگاه Android متصل شوید.
5. اتصال را قطع کنید و دوباره متصل شوید.
6. بررسی کنید که خطای "Broken pipe" دیگر در لاگ‌ها ظاهر نمی‌شود.

