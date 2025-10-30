package com.streamapp.camera

import android.content.Context
import android.util.Size
import android.view.Surface
import androidx.camera.core.*
import androidx.camera.camera2.interop.Camera2CameraControl
import androidx.camera.camera2.interop.Camera2Interop
import androidx.camera.camera2.interop.CaptureRequestOptions
import androidx.camera.lifecycle.ProcessCameraProvider
import androidx.camera.view.PreviewView
import androidx.core.content.ContextCompat
import androidx.lifecycle.LifecycleOwner
import android.hardware.camera2.CaptureRequest
import android.util.Log
import android.util.Range
import java.util.concurrent.ExecutorService
import java.util.concurrent.Executors

class CameraManager(private val context: Context) {
    private var cameraProvider: ProcessCameraProvider? = null
    private var camera: Camera? = null
    private var previewForScreen: Preview? = null
    private var previewForEncoder: Preview? = null
    private var lensFacing = CameraSelector.LENS_FACING_BACK
    private val cameraExecutor: ExecutorService = Executors.newSingleThreadExecutor()
    
    var currentResolution = Size(1280, 720)
    
    private var encoderSurface: Surface? = null
    private var manualMode = false
    private var manualISO: Int? = null
    private var manualShutter: Long? = null
    private var manualFocusDistance: Float? = null
    private val TAG = "CameraManager"
    
    fun initialize(lifecycleOwner: LifecycleOwner, previewView: PreviewView, callback: (Boolean) -> Unit) {
        val cameraProviderFuture = ProcessCameraProvider.getInstance(context)
        
        cameraProviderFuture.addListener({
            try {
                cameraProvider = cameraProviderFuture.get()
                startCamera(lifecycleOwner, previewView)
                callback(true)
            } catch (e: Exception) {
                Log.e(TAG, "Error initializing camera", e)
                callback(false)
            }
        }, ContextCompat.getMainExecutor(context))
    }
    
    private fun startCamera(lifecycleOwner: LifecycleOwner, previewView: PreviewView) {
        val provider = cameraProvider ?: return
        
        provider.unbindAll()
        
        // Preview for Android screen
        previewForScreen = Preview.Builder()
            .setTargetResolution(currentResolution)
            .build()
            .also {
                it.setSurfaceProvider(previewView.surfaceProvider)
            }
        
        val cameraSelector = CameraSelector.Builder()
            .requireLensFacing(lensFacing)
            .build()
        
        try {
            // Bind preview for screen first
            if (encoderSurface != null && encoderSurface!!.isValid) {
                // If encoder surface is set and valid, create preview for encoder
                previewForEncoder = Preview.Builder()
                    .setTargetResolution(currentResolution)
                    .build()
                    .also { preview ->
                        preview.setSurfaceProvider(cameraExecutor) { request ->
                            val surface = encoderSurface
                            if (surface != null && surface.isValid) {
                                request.provideSurface(surface, cameraExecutor) { result ->
                                    Log.d(TAG, "Encoder surface released: ${result.resultCode}")
                                }
                            } else {
                                Log.e(TAG, "Encoder surface is null or invalid")
                                request.willNotProvideSurface()
                            }
                        }
                    }
                
                camera = provider.bindToLifecycle(
                    lifecycleOwner,
                    cameraSelector,
                    previewForScreen,
                    previewForEncoder
                )
                
                Log.d(TAG, "Camera started successfully with encoder surface")
            } else {
                // Only screen preview
                camera = provider.bindToLifecycle(
                    lifecycleOwner,
                    cameraSelector,
                    previewForScreen
                )
                
                Log.d(TAG, "Camera started successfully (preview only)")
            }
        } catch (e: Exception) {
            Log.e(TAG, "Error starting camera", e)
        }
    }
    
    fun setEncoderSurface(surface: Surface?, lifecycleOwner: LifecycleOwner, previewView: PreviewView) {
        encoderSurface = surface
        if (surface != null && surface.isValid) {
            Log.d(TAG, "Encoder surface set (valid), restarting camera")
            // Must run on main thread because unbindAll() requires it
            ContextCompat.getMainExecutor(context).execute {
                // Small delay to ensure surface is fully ready
                try {
                    Thread.sleep(100)
                } catch (e: InterruptedException) {
                    Thread.currentThread().interrupt()
                }
                startCamera(lifecycleOwner, previewView)
            }
        } else if (surface == null) {
            Log.d(TAG, "Encoder surface removed, restarting camera")
            // Must run on main thread
            ContextCompat.getMainExecutor(context).execute {
                startCamera(lifecycleOwner, previewView)
            }
        } else {
            Log.e(TAG, "Encoder surface is invalid, cannot start camera")
        }
    }
    
    // Auto Mode Controls
    fun setZoom(ratio: Float) {
        camera?.cameraControl?.setZoomRatio(ratio)
        Log.d(TAG, "Zoom set to: ${ratio}x")
    }
    
    fun setExposureCompensation(index: Int) {
        camera?.cameraControl?.setExposureCompensationIndex(index)
        Log.d(TAG, "Exposure compensation set to: $index")
    }
    
    fun setTapToFocus(x: Float, y: Float, width: Int, height: Int) {
        val factory = SurfaceOrientedMeteringPointFactory(width.toFloat(), height.toFloat())
        val point = factory.createPoint(x, y)
        val action = FocusMeteringAction.Builder(point).build()
        camera?.cameraControl?.startFocusAndMetering(action)
        Log.d(TAG, "Tap to focus at: ($x, $y)")
    }
    
    fun enableTorch(enabled: Boolean) {
        camera?.cameraControl?.enableTorch(enabled)
        Log.d(TAG, "Torch enabled: $enabled")
    }
    
    private fun applyCameraSettings() {
        val camera2Control = Camera2CameraControl.from(camera?.cameraControl ?: return)
        val builder = CaptureRequestOptions.Builder()
        
        if (manualMode) {
            builder.setCaptureRequestOption(CaptureRequest.CONTROL_MODE, CaptureRequest.CONTROL_MODE_OFF)
            builder.setCaptureRequestOption(CaptureRequest.CONTROL_AE_MODE, CaptureRequest.CONTROL_AE_MODE_OFF)
            builder.setCaptureRequestOption(CaptureRequest.CONTROL_AF_MODE, CaptureRequest.CONTROL_AF_MODE_OFF)
            
            manualISO?.let {
                builder.setCaptureRequestOption(CaptureRequest.SENSOR_SENSITIVITY, it)
            }
            
            manualShutter?.let {
                builder.setCaptureRequestOption(CaptureRequest.SENSOR_EXPOSURE_TIME, it)
            }
            
            manualFocusDistance?.let {
                builder.setCaptureRequestOption(CaptureRequest.LENS_FOCUS_DISTANCE, it)
            }
        } else {
            builder.setCaptureRequestOption(CaptureRequest.CONTROL_MODE, CaptureRequest.CONTROL_MODE_AUTO)
            builder.setCaptureRequestOption(CaptureRequest.CONTROL_AE_MODE, CaptureRequest.CONTROL_AE_MODE_ON)
            builder.setCaptureRequestOption(CaptureRequest.CONTROL_AF_MODE, CaptureRequest.CONTROL_AF_MODE_CONTINUOUS_PICTURE)
            builder.setCaptureRequestOption(CaptureRequest.CONTROL_AWB_MODE, CaptureRequest.CONTROL_AWB_MODE_AUTO)
        }
        
        camera2Control.captureRequestOptions = builder.build()
    }
    
    // Manual Mode Controls
    fun setManualMode(enabled: Boolean) {
        manualMode = enabled
        Log.d(TAG, "Manual mode: $enabled")
        
        if (!enabled) {
            manualISO = null
            manualShutter = null
            manualFocusDistance = null
        }
        
        applyCameraSettings()
    }
    
    fun setManualISO(iso: Int) {
        if (!manualMode) {
            Log.w(TAG, "Cannot set manual ISO in auto mode")
            return
        }
        
        manualISO = iso
        Log.d(TAG, "Manual ISO set to: $iso")
        applyCameraSettings()
    }
    
    fun setManualShutterSpeed(nanos: Long) {
        if (!manualMode) {
            Log.w(TAG, "Cannot set manual shutter speed in auto mode")
            return
        }
        
        manualShutter = nanos
        Log.d(TAG, "Manual shutter speed set to: ${nanos}ns")
        applyCameraSettings()
    }
    
    fun setManualFocusDistance(distance: Float) {
        if (!manualMode) {
            Log.w(TAG, "Cannot set manual focus in auto mode")
            return
        }
        
        manualFocusDistance = distance
        Log.d(TAG, "Manual focus distance set to: $distance")
        applyCameraSettings()
    }
    
    fun setWhiteBalance(mode: String, kelvin: Int) {
        val camera2Control = Camera2CameraControl.from(camera?.cameraControl ?: return)
        
        val wbMode = when (mode.lowercase()) {
            "auto" -> CaptureRequest.CONTROL_AWB_MODE_AUTO
            "daylight" -> CaptureRequest.CONTROL_AWB_MODE_DAYLIGHT
            "cloudy" -> CaptureRequest.CONTROL_AWB_MODE_CLOUDY_DAYLIGHT
            "tungsten" -> CaptureRequest.CONTROL_AWB_MODE_INCANDESCENT
            "fluorescent" -> CaptureRequest.CONTROL_AWB_MODE_FLUORESCENT
            else -> CaptureRequest.CONTROL_AWB_MODE_AUTO
        }
        
        val captureOptions = CaptureRequestOptions.Builder()
            .setCaptureRequestOption(CaptureRequest.CONTROL_AWB_MODE, wbMode)
            .build()
        camera2Control.captureRequestOptions = captureOptions
        Log.d(TAG, "White balance set to: $mode")
    }
    
    // Camera Info Getters
    fun getZoomRange(): Pair<Float, Float> {
        val zoomState = camera?.cameraInfo?.zoomState?.value
        return Pair(zoomState?.minZoomRatio ?: 1.0f, zoomState?.maxZoomRatio ?: 1.0f)
    }
    
    fun getExposureRange(): Pair<Int, Int> {
        val exposureState = camera?.cameraInfo?.exposureState
        val range = exposureState?.exposureCompensationRange
        return Pair(range?.lower ?: -2, range?.upper ?: 2)
    }
    
    fun getSupportedISOs(): IntRange {
        // This is device-specific, typical range
        return IntRange(100, 3200)
    }
    
    fun getSupportedShutterSpeeds(): LongRange {
        // Typical range: 1/8000s to 30s in nanoseconds
        return LongRange(125000, 30000000000)
    }
    
    fun getCameraCapabilities(): Map<String, Any> {
        val zoom = getZoomRange()
        val exposure = getExposureRange()
        val iso = getSupportedISOs()
        val shutter = getSupportedShutterSpeeds()
        
        return mapOf(
            "zoom_min" to zoom.first,
            "zoom_max" to zoom.second,
            "exposure_min" to exposure.first,
            "exposure_max" to exposure.second,
            "iso_min" to iso.first,
            "iso_max" to iso.last,
            "shutter_min_ns" to shutter.first,
            "shutter_max_ns" to shutter.last
        )
    }
    
    fun switchCamera(lifecycleOwner: LifecycleOwner, previewView: PreviewView) {
        lensFacing = if (lensFacing == CameraSelector.LENS_FACING_BACK) {
            CameraSelector.LENS_FACING_FRONT
        } else {
            CameraSelector.LENS_FACING_BACK
        }
        startCamera(lifecycleOwner, previewView)
    }
    
    fun setResolution(width: Int, height: Int, lifecycleOwner: LifecycleOwner, previewView: PreviewView) {
        currentResolution = Size(width, height)
        startCamera(lifecycleOwner, previewView)
    }
    
    fun release() {
        cameraExecutor.shutdown()
        cameraProvider?.unbindAll()
    }
}
