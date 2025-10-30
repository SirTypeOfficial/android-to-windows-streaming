package com.streamapp.control

import android.util.Log
import androidx.camera.view.PreviewView
import androidx.lifecycle.LifecycleOwner
import com.streamapp.camera.CameraManager
import com.streamapp.protocol.ControlCommand
import org.json.JSONObject

class ControlHandler(
    private val cameraManager: CameraManager,
    private val lifecycleOwner: LifecycleOwner,
    private val previewView: PreviewView
) {
    private val TAG = "ControlHandler"
    
    var onResolutionChanged: ((Int, Int) -> Unit)? = null
    var onFpsChanged: ((Int) -> Unit)? = null
    var onCapabilitiesResponse: ((String) -> Unit)? = null
    
    fun handleCommand(jsonCommand: String) {
        try {
            val (command, parameters) = ControlCommand.parseCommand(jsonCommand)
            Log.d(TAG, "Received command: $command with parameters: $parameters")
            
            when (command) {
                "set_resolution" -> {
                    val width = (parameters["width"] as? Int) ?: 1280
                    val height = (parameters["height"] as? Int) ?: 720
                    setResolution(width, height)
                }
                "set_fps" -> {
                    val fps = (parameters["fps"] as? Int) ?: 30
                    setFps(fps)
                }
                "switch_camera" -> {
                    switchCamera()
                }
                "set_flash" -> {
                    val enabled = (parameters["enabled"] as? Boolean) ?: false
                    setFlash(enabled)
                }
                "set_brightness" -> {
                    val value = (parameters["value"] as? Double)?.toFloat() ?: 0.5f
                    setBrightness(value)
                }
                "set_zoom" -> {
                    val ratio = (parameters["ratio"] as? Double)?.toFloat() ?: 1.0f
                    setZoom(ratio)
                }
                "set_manual_mode" -> {
                    val enabled = (parameters["enabled"] as? Boolean) ?: false
                    setManualMode(enabled)
                }
                "set_manual_iso" -> {
                    val iso = (parameters["iso"] as? Int) ?: 800
                    setManualISO(iso)
                }
                "set_manual_shutter" -> {
                    val nanos = (parameters["nanos"] as? Long) ?: 10000000L
                    setManualShutter(nanos)
                }
                "set_manual_focus" -> {
                    val distance = (parameters["distance"] as? Double)?.toFloat() ?: 0.0f
                    setManualFocus(distance)
                }
                "set_white_balance" -> {
                    val mode = (parameters["mode"] as? String) ?: "auto"
                    val kelvin = (parameters["kelvin"] as? Int) ?: 5500
                    setWhiteBalance(mode, kelvin)
                }
                "set_tap_focus" -> {
                    val x = (parameters["x"] as? Double)?.toFloat() ?: 0.5f
                    val y = (parameters["y"] as? Double)?.toFloat() ?: 0.5f
                    val width = (parameters["screenWidth"] as? Int) ?: 1280
                    val height = (parameters["screenHeight"] as? Int) ?: 720
                    setTapFocus(x, y, width, height)
                }
                "get_camera_capabilities" -> {
                    getCameraCapabilities()
                }
                else -> {
                    Log.w(TAG, "Unknown command: $command")
                }
            }
        } catch (e: Exception) {
            Log.e(TAG, "Error handling command", e)
        }
    }
    
    private fun setResolution(width: Int, height: Int) {
        Log.d(TAG, "Setting resolution: ${width}x${height}")
        onResolutionChanged?.invoke(width, height)
    }
    
    private fun setFps(fps: Int) {
        Log.d(TAG, "Setting FPS: $fps")
        onFpsChanged?.invoke(fps)
    }
    
    private fun switchCamera() {
        Log.d(TAG, "Switching camera")
        cameraManager.switchCamera(lifecycleOwner, previewView)
    }
    
    private fun setFlash(enabled: Boolean) {
        Log.d(TAG, "Setting flash: $enabled")
        cameraManager.enableTorch(enabled)
    }
    
    private fun setBrightness(value: Float) {
        Log.d(TAG, "Setting brightness: $value")
        val exposureValue = ((value - 0.5f) * 10).toInt()
        cameraManager.setExposureCompensation(exposureValue)
    }
    
    private fun setZoom(ratio: Float) {
        Log.d(TAG, "Setting zoom: ${ratio}x")
        cameraManager.setZoom(ratio)
    }
    
    private fun setManualMode(enabled: Boolean) {
        Log.d(TAG, "Setting manual mode: $enabled")
        cameraManager.setManualMode(enabled)
    }
    
    private fun setManualISO(iso: Int) {
        Log.d(TAG, "Setting manual ISO: $iso")
        cameraManager.setManualISO(iso)
    }
    
    private fun setManualShutter(nanos: Long) {
        Log.d(TAG, "Setting manual shutter: ${nanos}ns")
        cameraManager.setManualShutterSpeed(nanos)
    }
    
    private fun setManualFocus(distance: Float) {
        Log.d(TAG, "Setting manual focus: $distance")
        cameraManager.setManualFocusDistance(distance)
    }
    
    private fun setWhiteBalance(mode: String, kelvin: Int) {
        Log.d(TAG, "Setting white balance: $mode ($kelvin K)")
        cameraManager.setWhiteBalance(mode, kelvin)
    }
    
    private fun setTapFocus(x: Float, y: Float, width: Int, height: Int) {
        Log.d(TAG, "Setting tap focus at ($x, $y) for screen ${width}x${height}")
        cameraManager.setTapToFocus(x, y, width, height)
    }
    
    private fun getCameraCapabilities() {
        Log.d(TAG, "Getting camera capabilities")
        val capabilities = cameraManager.getCameraCapabilities()
        val json = JSONObject(capabilities).toString()
        onCapabilitiesResponse?.invoke(json)
        Log.d(TAG, "Camera capabilities: $json")
    }
}
