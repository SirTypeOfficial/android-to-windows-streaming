# Quick Start Guide - Testing Surface-Based Camera Control

## Prerequisites

### Android Device
- Android 8.0 (API 26) or higher
- Camera with Camera2 API support
- USB cable or WiFi connection

### Development Environment
- Android Studio (for building Android app)
- Python 3.8+ (for Windows app)
- ADB tools (for USB connection)

## Step 1: Build and Install Android App

```bash
cd android-app
# Open in Android Studio and build, or use gradlew:
./gradlew assembleDebug

# Install on device
adb install -r build/outputs/apk/debug/app-debug.apk
```

## Step 2: Setup Windows App

```bash
cd windows-app
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

## Step 3: Test Surface-Based Encoding

### 3.1 Start Android App
1. Open app on Android device
2. Grant camera and microphone permissions
3. Select WiFi or USB connection method
4. Tap "Start Streaming"

### 3.2 Connect from Windows
1. Run Windows app: `python main.py`
2. For WiFi: Enter Android device IP and click "Connect WiFi"
3. For USB: Click "Connect USB" (ensure ADB is working)

### 3.3 Verify Surface Encoding
**Expected behavior:**
- Video appears on Windows app within 1-2 seconds
- Android screen shows camera preview
- Lower CPU usage compared to previous version
- Smooth, artifact-free video

**Check Android logs:**
```bash
adb logcat | grep -E "VideoEncoder|CameraManager"
```

You should see:
```
VideoEncoder: Video encoder started with Surface input: 1280x720 @ 30fps
CameraManager: Encoder surface set, restarting camera
CameraManager: Camera started successfully
```

## Step 4: Test Auto Mode Controls

### 4.1 Zoom Control
1. Ensure "Auto" mode is selected in Windows app
2. Move "Zoom" slider
3. **Expected:** Camera zooms smoothly on Android device
4. **Verify:** Value label updates (e.g., "2.5x")

### 4.2 Exposure Compensation
1. Move "EV" slider in Auto Mode group
2. **Expected:** Image becomes brighter (positive) or darker (negative)
3. **Verify:** Value label shows -2.0 to +2.0

### 4.3 Flash/Torch
1. Check "Flash" checkbox
2. **Expected:** Device flashlight turns on
3. **Verify:** Uncheck turns it off

## Step 5: Test Manual Mode Controls

### 5.1 Switch to Manual Mode
1. Click "Manual" radio button
2. **Expected:** 
   - Auto Mode controls disappear
   - Manual Mode controls appear
   - Android logs show: `CameraManager: Manual mode: true`

### 5.2 ISO Control
1. Move "ISO" slider (100-3200)
2. **Expected:** Image sensitivity changes
3. **Test:** In low light, higher ISO = brighter but noisier
4. **Verify:** Value label updates

### 5.3 Shutter Speed Control
1. Move "Shutter Speed" slider
2. **Expected:** Exposure time changes
3. **Test:** 
   - Slow shutter (1/15s or slower) = brighter, motion blur
   - Fast shutter (1/1000s or faster) = darker, frozen motion
4. **Verify:** Display shows fraction (1/125) or seconds (2.5s)

### 5.4 Focus Distance Control
1. Move "Focus Distance" slider
2. **Expected:** Focus point changes
3. **Test:**
   - 0% = Focus on distant objects (infinity)
   - 100% = Focus on very close objects (macro)
4. **Verify:** Label shows "∞", percentage, or "Macro"

### 5.5 White Balance Control
1. Change "White Balance" dropdown
2. **Expected:** Color temperature changes
3. **Test:**
   - Daylight = Warmer tones
   - Tungsten = Cooler tones (compensates for warm bulbs)
   - Fluorescent = Greenish compensation

## Step 6: Test Mode Switching

1. Start in Auto mode
2. Adjust zoom and exposure
3. Switch to Manual mode
4. Adjust ISO and shutter
5. Switch back to Auto mode
6. **Expected:** No crashes, smooth transitions
7. **Verify:** Controls work immediately after switching

## Step 7: Test Camera Capabilities

1. Click "Get Camera Capabilities" button
2. **Check Android logs:**
```bash
adb logcat | grep "CameraManager"
```

Expected output:
```
CameraManager: Camera capabilities: {"zoom_min":1.0,"zoom_max":8.0,...}
```

## Step 8: Test Dual Preview

### Verify Both Previews Work
1. **Android Screen:** Should show live camera preview
2. **Windows App:** Should show same video with minimal delay
3. **Expected:** Both displays update simultaneously
4. **Test:** Move camera around, both previews should match

## Step 9: Performance Testing

### CPU Usage Test
1. Open Android device settings > Developer Options > CPU usage
2. Start streaming
3. **Expected:** Lower CPU usage than before (15-25% vs 45-60%)
4. **Verify:** App remains responsive, no frame drops

### Latency Test
1. Use a stopwatch on computer screen
2. Point Android camera at it
3. Compare time on computer vs time shown in Windows app
4. **Expected:** 80-120ms latency (improved from 150-200ms)

### Quality Test
1. Point camera at detailed scene (text, patterns)
2. **Expected:** Sharp, clear image with no color banding
3. **Compare:** Should be noticeably better than previous version

## Step 10: Stress Testing

### Resolution Changes
1. Change resolution: 480p → 720p → 1080p
2. **Expected:** Stream restarts smoothly
3. **Verify:** No crashes, video resumes

### Camera Switching
1. Click "Switch Camera" (front/back)
2. **Expected:** Camera switches, stream continues
3. **Verify:** All controls still work

### Rapid Control Changes
1. Rapidly move sliders back and forth
2. **Expected:** Smooth operation, no lag
3. **Verify:** No command queue overflow

### Extended Streaming
1. Stream for 30+ minutes
2. **Expected:** No memory leaks, stable performance
3. **Monitor:** Android battery temperature, CPU usage

## Troubleshooting

### Problem: No video appears on Windows

**Check:**
1. Android logs: `adb logcat | grep VideoEncoder`
2. Verify Surface created: Look for "Video encoder started with Surface input"
3. Check network connection (ping Android IP)
4. Verify firewall not blocking port 55555

**Solution:**
- Restart both apps
- Check camera permissions on Android
- Try USB connection instead of WiFi

### Problem: Controls don't work

**Check:**
1. Connection established (status shows "Connected")
2. Android logs: `adb logcat | grep ControlHandler`
3. Verify commands received: Look for "Received command: set_zoom"

**Solution:**
- Click "Get Camera Capabilities" to verify communication
- Check Windows logs for command send errors
- Restart connection

### Problem: Manual mode crashes

**Check:**
1. Device supports Camera2 API: `adb shell getprop ro.hardware.camera`
2. Android logs: `adb logcat | grep -E "CameraManager|Camera2"`

**Solution:**
- Some devices don't support full manual control
- Try reducing control ranges
- Fall back to Auto mode

### Problem: Poor video quality

**Check:**
1. Resolution setting (higher = better quality)
2. Bitrate in VideoEncoder.kt (default 2000000)
3. Network bandwidth (WiFi signal strength)

**Solution:**
- Increase bitrate: Modify `VideoEncoder.kt` line 14
- Use USB instead of WiFi
- Reduce resolution for better frame rate

## Expected Results Summary

| Test | Expected Result | Pass/Fail |
|------|----------------|-----------|
| Surface encoding working | Video appears, low CPU usage | ☐ |
| Dual preview functional | Both Android and Windows show video | ☐ |
| Auto zoom control | Smooth zoom in/out | ☐ |
| Auto exposure control | Brightness adjusts | ☐ |
| Flash toggle | Torch on/off works | ☐ |
| Manual mode switch | Controls change, no crash | ☐ |
| Manual ISO control | Sensitivity changes | ☐ |
| Manual shutter control | Exposure time changes | ☐ |
| Manual focus control | Focus point changes | ☐ |
| White balance control | Color temperature changes | ☐ |
| Mode switching | Smooth transition both ways | ☐ |
| Camera capabilities | Data retrieved successfully | ☐ |
| Camera switch | Front/back swap works | ☐ |
| Resolution change | Stream restarts cleanly | ☐ |
| Extended streaming | No leaks after 30+ min | ☐ |

## Performance Benchmarks

Record your results:

| Metric | Target | Actual | Notes |
|--------|--------|--------|-------|
| CPU Usage | 15-25% | _____% | |
| Latency | 80-120ms | _____ms | |
| Frame Rate | 30 fps | _____ fps | |
| Memory Usage | Stable | _____ MB | |
| Battery Drain | Moderate | _____% /hr | |

## Reporting Issues

If you encounter problems:

1. **Collect logs:**
```bash
adb logcat > android_logs.txt
# Let it run during the problem, then Ctrl+C
```

2. **Check Windows logs:**
```bash
# Windows app logs to console, redirect to file:
python main.py > windows_logs.txt 2>&1
```

3. **Note device info:**
- Android version
- Device model
- Camera capabilities

4. **Describe the issue:**
- Steps to reproduce
- Expected vs actual behavior
- Frequency (always, sometimes, rarely)

## Success Criteria

Implementation is successful if:
- ✅ Video streams with Surface-based encoding
- ✅ CPU usage reduced by 30%+ compared to ImageProxy method
- ✅ Both Auto and Manual camera controls work
- ✅ Mode switching is smooth and stable
- ✅ Dual preview works (Android + Windows)
- ✅ No crashes during normal operation
- ✅ No memory leaks during extended use
- ✅ All controls respond within 100ms

## Next Steps After Testing

Once testing is complete:
1. Document any device-specific issues
2. Fine-tune control ranges based on your camera
3. Adjust bitrate/resolution for your use case
4. Consider adding custom presets for different scenarios
5. Implement any additional features from "Future Enhancements"

---

**Testing Date:** _____________
**Tester:** _____________
**Device:** _____________
**Result:** ☐ PASS  ☐ FAIL  ☐ PARTIAL
**Notes:** _____________________________________________

