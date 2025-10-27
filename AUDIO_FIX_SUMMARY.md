# Audio Decoding Fix Summary

## Problem
The Windows application was receiving audio packets but failing to decode them with the error:
```
[Errno 1094995529] Invalid data found when processing input: 'avcodec_send_packet()'
```

This error occurred because the AAC audio decoder wasn't properly configured with the codec-specific configuration data (extradata/CSD) required for AAC decoding.

## Root Cause
- Android's MediaCodec outputs raw AAC frames along with codec configuration data (CSD-0)
- The Windows PyAV AAC decoder requires this configuration data (extradata) to properly decode AAC frames
- The original implementation was not capturing or transmitting this configuration data

## Solution
Implemented a codec configuration exchange mechanism:

### 1. Protocol Changes
- Added new packet types: `VIDEO_CONFIG (0x03)` and `AUDIO_CONFIG (0x04)`
- Updated protocol specification to document codec configuration exchange

**Files Modified:**
- `protocol/protocol.py`
- `protocol/protocol_spec.json`
- `windows-app/protocol/protocol.py`
- `android-app/src/main/java/com/streamapp/protocol/Protocol.kt`

### 2. Android Encoder Changes
Modified `AudioEncoder.kt` to:
- Detect when MediaCodec outputs codec configuration data (`INFO_OUTPUT_FORMAT_CHANGED`)
- Extract the CSD-0 buffer from the output format
- Send configuration data via new `onConfigData` callback
- Skip codec config buffers in the regular frame output (they're sent separately)

**Files Modified:**
- `android-app/src/main/java/com/streamapp/encoder/AudioEncoder.kt`

### 3. Android Streaming Changes
Updated streaming infrastructure to handle audio config:
- Added `sendAudioConfig()` methods to NetworkStreamer and USBStreamer
- Wired up `onConfigData` callback in StreamingService

**Files Modified:**
- `android-app/src/main/java/com/streamapp/StreamingService.kt`
- `android-app/src/main/java/com/streamapp/network/NetworkStreamer.kt`
- `android-app/src/main/java/com/streamapp/network/USBStreamer.kt`

### 4. Windows Decoder Changes
Enhanced `AudioDecoder` to:
- Added `set_config()` method to receive and apply extradata
- Codec automatically configures itself from extradata (sample_rate, channels, layout)
- Added `codec_opened` flag to ensure codec is configured before decoding
- Added dynamic audio stream recreation if codec parameters differ from defaults
- Improved audio format conversion to properly handle s16 format
- Added proper array reshaping for multi-dimensional audio data
- Fixed AttributeError by removing attempts to set read-only codec properties

**Files Modified:**
- `windows-app/streaming/decoder.py`

### 5. Windows Receiver Changes
Updated `StreamReceiver` to:
- Handle `AUDIO_CONFIG` packet type
- Added `on_audio_config` callback
- Properly route audio configuration to decoder

**Files Modified:**
- `windows-app/streaming/receiver.py`

### 6. Windows UI Changes
Connected audio config callback in MainWindow:
- Wired `stream_receiver.on_audio_config` to `audio_decoder.set_config`

**Files Modified:**
- `windows-app/ui/main_window.py`

## How It Works

1. **Android Side:**
   - AudioEncoder starts and MediaCodec generates codec configuration (CSD-0)
   - Configuration is sent via AUDIO_CONFIG packet to Windows
   - Regular audio frames are sent via AUDIO_FRAME packets

2. **Windows Side:**
   - Receives AUDIO_CONFIG packet and calls `audio_decoder.set_config()`
   - Decoder sets extradata and opens the codec
   - Subsequent AUDIO_FRAME packets are decoded successfully
   - Audio frames are converted to s16 format and played via PyAudio

## Expected Behavior
- Audio config packet is sent once when streaming starts
- Audio frames are decoded successfully after config is received
- Audio plays through the default audio output device
- Logs show: "Audio codec configured with extradata: X bytes"

## Testing
To verify the fix:
1. Start the Android app and begin streaming
2. Connect from Windows app (WiFi or USB)
3. Check logs for "Audio config sent" message on Android
4. Check logs for "Audio codec configured with extradata" on Windows
5. Verify no more "Invalid data found" errors
6. Audio should play correctly

## Files Changed Summary
- **Protocol:** 4 files (Android + Windows protocol definitions)
- **Android:** 4 files (AudioEncoder, StreamingService, NetworkStreamer, USBStreamer)
- **Windows:** 3 files (decoder, receiver, main_window)
- **Documentation:** 1 file (protocol_spec.json)

Total: 12 files modified

## Notes
- The fix maintains backward compatibility structure
- Only AAC audio codec is affected; video streaming remains unchanged
- The codec configuration is sent automatically when encoding starts
- No user interaction required for the configuration exchange

