<!-- c7159cb0-de01-4fa7-953a-039673301745 87866a28-0ead-4200-9b54-245aa4c9263f -->
# Surface-Based Streaming with Complete Camera Control

## Phase 1: Android Encoder Migration (Surface-Based)

### VideoEncoder.kt

- Change from `COLOR_FormatYUV420Flexible` to `COLOR_FormatSurface`
- Create `inputSurface` from `mediaCodec.createInputSurface()`
- Add `getInputSurface(): Surface` method
- Remove `encodeFrame(ImageProxy)` and `imageProxyToNV21()` methods
- Keep only output buffer handling (`dequeueOutputBuffer` loop)

### CameraManager.kt

- Remove `ImageAnalysis` UseCase entirely
- Create two `Preview` UseCases:

  1. `previewForScreen` → connects to PreviewView (for Android display)
  2. `previewForEncoder` → connects to encoder Surface via `SurfaceProvider`

- Add `Camera` reference storage for runtime control
- Add `CameraControl` and `CameraInfo` getters

## Phase 2: Advanced Camera Controls (Auto + Manual)

### CameraManager.kt - Add Control Methods

**Auto Mode Controls:**

- `setZoom(ratio: Float)` - zoom control (1.0 to max)
- `setExposureCompensation(index: Int)` - EV adjustment
- `setTapToFocus(x: Float, y: Float)` - tap-to-focus
- `enableTorch(enabled: Boolean)` - flash/torch

**Manual Mode Controls (Camera2Interop):**

- Add Camera2Interop dependency to `build.gradle.kts`
- `setManualMode(enabled: Boolean)` - toggle between Auto/Manual
- `setManualISO(iso: Int)` - manual ISO sensitivity
- `setManualShutterSpeed(nanos: Long)` - shutter speed
- `setManualFocusDistance(distance: Float)` - manual focus (0.0-1.0)
- `setWhiteBalance(mode: Int, kelvin: Int)` - white balance control

**Add Camera Info Getters:**

- `getZoomRange(): Pair<Float, Float>`
- `getExposureRange(): Pair<Int, Int>`
- `getSupportedISOs(): IntRange`
- `getSupportedShutterSpeeds(): LongRange`

### Build Configuration

Update `android-app/build.gradle.kts`:

```kotlin
dependencies {
    implementation("androidx.camera:camera-camera2:1.3.0")
}
```

## Phase 3: Protocol Extensions

### protocol_spec.json

Add new control commands:

- `SET_ZOOM` - {ratio: float}
- `SET_MANUAL_MODE` - {enabled: bool}
- `SET_MANUAL_ISO` - {iso: int}
- `SET_MANUAL_SHUTTER` - {nanos: long}
- `SET_MANUAL_FOCUS` - {distance: float}
- `SET_WHITE_BALANCE` - {mode: string, kelvin: int}
- `SET_TAP_FOCUS` - {x: float, y: float, screenWidth: int, screenHeight: int}
- `GET_CAMERA_CAPABILITIES` - request camera ranges/limits

### Protocol.kt

Add command builders for all new controls in `ControlCommand` object

### protocol.py (Windows)

Mirror all new command structures in Python `ControlCommand` class

## Phase 4: Android Control Handler

### ControlHandler.kt

Add handlers for new commands:

- `handleZoom(ratio: Float)`
- `handleManualMode(enabled: Boolean)`
- `handleManualISO(iso: Int)`
- `handleManualShutter(nanos: Long)`
- `handleManualFocus(distance: Float)`
- `handleWhiteBalance(mode: String, kelvin: Int)`
- `handleTapFocus(x: Float, y: Float, width: Int, height: Int)`

Add response mechanism to send camera capabilities back to Windows

## Phase 5: Android MainActivity Updates

### MainActivity.kt

- Update streaming initialization to pass encoder Surface to CameraManager
- Remove `onFrameAvailable` callback (no longer needed with Surface)
- Keep Preview on screen for monitoring
- Optional: Add touch listener on PreviewView for tap-to-focus in Auto mode

## Phase 6: Windows Command Layer

### control/commands.py

Add new command methods:

- `set_zoom(ratio: float)`
- `set_manual_mode(enabled: bool)`
- `set_manual_iso(iso: int)`
- `set_manual_shutter(nanos: int)`
- `set_manual_focus(distance: float)`
- `set_white_balance(mode: str, kelvin: int)`
- `set_tap_focus(x: float, y: float, width: int, height: int)`
- `get_camera_capabilities()`

## Phase 7: Windows UI Enhancements

### ui/main_window.py

**Add Auto/Manual Mode Toggle:**

- QRadioButton group for Auto/Manual selection
- Show/hide relevant controls based on mode

**Auto Mode Controls:**

- Zoom slider (1.0x to max, dynamic based on camera)
- Exposure Compensation slider (-2 EV to +2 EV)
- Flash toggle checkbox
- Info label: "Tap on preview for focus" (if tap-to-focus enabled)

**Manual Mode Controls:**

- ISO slider (device-specific range)
- Shutter Speed slider (with labels: 1/8000s to 30s)
- Focus Distance slider (0-100%, 0=infinity, 100=macro)
- White Balance: dropdown (Auto, Daylight, Cloudy, Tungsten, Fluorescent, Custom) + Kelvin input

**UI Organization:**

```
Control Panel Structure:
├── Connection Group
├── Mode Selection (Auto/Manual)
├── Common Controls Group
│   ├── Zoom Slider
│   └── Flash Toggle
├── Auto Mode Group (visible in Auto)
│   ├── Exposure Compensation
│   └── Tap-to-Focus indicator
└── Manual Mode Group (visible in Manual)
    ├── ISO Slider
    ├── Shutter Speed Slider
    ├── Focus Distance Slider
    └── White Balance Controls
```

**Value Display:**

- Show current values next to each slider
- Add reset buttons for each control
- Display camera capabilities when connected

## Phase 8: Testing & Validation

- Test Surface encoding performance vs ImageProxy
- Verify no memory leaks with Surface management
- Test all camera controls in both Auto and Manual modes
- Verify smooth transitions between Auto/Manual
- Test camera capability detection across devices
- Validate Windows UI responsiveness

## Key Files Modified

**Android:**

- `android-app/src/main/java/com/streamapp/encoder/VideoEncoder.kt`
- `android-app/src/main/java/com/streamapp/camera/CameraManager.kt`
- `android-app/src/main/java/com/streamapp/MainActivity.kt`
- `android-app/src/main/java/com/streamapp/control/ControlHandler.kt`
- `android-app/build.gradle.kts`
- `protocol/Protocol.kt`

**Windows:**

- `windows-app/control/commands.py`
- `windows-app/ui/main_window.py`
- `windows-app/protocol/protocol.py`

**Protocol:**

- `protocol/protocol_spec.json`

## Expected Benefits

1. **Performance**: 30-50% less CPU usage, zero-copy path from camera to encoder
2. **Quality**: No color conversion artifacts, native camera format preserved
3. **Control**: Professional-grade manual controls matching native camera apps
4. **Latency**: Reduced by eliminating CPU-based frame processing
5. **Flexibility**: Easy toggle between auto (convenience) and manual (precision)

### To-dos

- [ ] Migrate VideoEncoder to Surface-based input (remove ImageProxy processing)
- [ ] Update CameraManager with dual Preview (screen + encoder Surface)
- [ ] Implement automatic camera controls (zoom, EV, tap-focus, flash)
- [ ] Implement manual camera controls with Camera2Interop (ISO, shutter, focus, WB)
- [ ] Extend protocol with new camera control commands (JSON spec + Kotlin + Python)
- [ ] Update ControlHandler to handle all new camera commands
- [ ] Update MainActivity to use Surface-based encoder and remove ImageProxy callback
- [ ] Add new camera control methods to Windows commands.py
- [ ] Build comprehensive Windows UI with Auto/Manual modes and all control sliders
- [ ] Test Surface performance, camera controls, and mode switching