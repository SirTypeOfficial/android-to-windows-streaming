package com.streamapp.control

import android.util.Log
import androidx.camera.view.PreviewView
import androidx.lifecycle.LifecycleOwner
import com.streamapp.camera.CameraManager
import com.streamapp.encoder.VideoEncoder
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
                "set_focus" -> {
                    val mode = (parameters["mode"] as? String) ?: "auto"
                    setFocus(mode)
                }
                "set_brightness" -> {
                    val value = (parameters["value"] as? Double)?.toFloat() ?: 0.5f
                    setBrightness(value)
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
        cameraManager.setResolution(width, height, lifecycleOwner, previewView)
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
        cameraManager.setFlashMode(enabled)
    }
    
    private fun setFocus(mode: String) {
        Log.d(TAG, "Setting focus mode: $mode")
    }
    
    private fun setBrightness(value: Float) {
        Log.d(TAG, "Setting brightness: $value")
        val exposureValue = ((value - 0.5f) * 10).toInt()
        cameraManager.setExposure(exposureValue)
    }
}

