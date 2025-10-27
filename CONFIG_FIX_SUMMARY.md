# Config Packet Fix Summary

## Problem Identified

The logs showed a critical issue: The Windows application was receiving ONLY audio frames (type=17) but **never receiving config packets or video frames**. This caused:

1. **Config packets were lost**: Config packets (SPS/PPS for video, extradata for audio) were sent immediately when `INFO_OUTPUT_FORMAT_CHANGED` occurred, which typically happens BEFORE a client connects. These packets were sent to a disconnected socket buffer and lost.

2. **Decoder not initialized**: The Windows decoder was waiting for config packets to initialize, but never received them. This caused the endless "Audio codec not yet configured, skipping frame" warnings seen in the logs.

3. **No video frames**: The logs show that no video packets were being sent or received, only audio packets.

## Root Cause

The encoder produces config data when the codec format changes, but this happens:
- Immediately after starting the encoder
- Often before any client connects to receive the data
- Only once (the `configSent` flag prevented re-sending)

## Solution Implemented

### Android Side Changes

1. **VideoEncoder.kt**
   - Added `cachedConfigData` to store the config data
   - Modified config generation to always cache the data (not just when sending)
   - Added `resendConfig()` method to send cached config on demand
   - Config is cleared when encoder stops

2. **AudioEncoder.kt**
   - Same changes as VideoEncoder
   - Added `cachedConfigData` to store extradata
   - Added `resendConfig()` method
   - Config is cleared when encoder stops

3. **StreamingService.kt**
   - Added `onClientConnectedCallback` and `onClientDisconnectedCallback` for external code
   - Modified `onClientConnected` handlers to call `resendConfig()` on both encoders
   - This ensures config is sent every time a client connects
   - Added `getAudioEncoder()` method

4. **MainActivity.kt**
   - Simplified callback handling
   - Now uses the callbacks from StreamingService instead of overwriting them
   - Config resend happens automatically via StreamingService

### How It Works Now

1. Encoder starts and processes frames
2. First format change triggers config generation (cached in `cachedConfigData`)
3. Config is sent to the streamer
4. If no client is connected, config is lost (but cached)
5. When client connects:
   - `onClientConnected` callback is triggered
   - Calls `videoEncoder.resendConfig()` and `audioEncoder.resendConfig()`
   - Config packets are sent to the connected client
   - Windows decoder receives config and initializes properly
   - Streaming works correctly

### Additional Fix: Broken Pipe Errors

Added connection checks before sending any data to prevent "Broken pipe" errors:
- Check `clientSocket?.isConnected` before attempting to send
- Suppress error logging when socket is already closed
- Prevents flood of error messages when connection is lost

### Expected Behavior

- Config packets will be resent every time a new client connects
- Windows decoder will receive config packets and initialize properly
- Video preview should display correctly
- Audio should play correctly
- Virtual camera and audio devices should work properly

## Files Modified

- `android-app/src/main/java/com/streamapp/encoder/VideoEncoder.kt`
- `android-app/src/main/java/com/streamapp/encoder/AudioEncoder.kt`
- `android-app/src/main/java/com/streamapp/StreamingService.kt`
- `android-app/src/main/java/com/streamapp/MainActivity.kt`
- `android-app/src/main/java/com/streamapp/network/USBStreamer.kt`
- `android-app/src/main/java/com/streamapp/network/NetworkStreamer.kt`

## Testing Required

1. Start the Android app and start streaming
2. Connect from Windows app
3. Verify config packets are received (check logs)
4. Verify video preview displays
5. Verify audio plays
6. Test virtual camera and audio devices

## Additional Notes

The Windows side decoder code appears correct - it was simply waiting for config packets that never arrived. With config packets now being properly sent, the decoder should initialize and decode frames correctly.

