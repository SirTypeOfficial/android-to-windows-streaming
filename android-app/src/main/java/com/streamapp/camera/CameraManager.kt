package com.streamapp.camera

import android.content.Context
import android.util.Size
import androidx.camera.core.*
import androidx.camera.lifecycle.ProcessCameraProvider
import androidx.camera.view.PreviewView
import androidx.core.content.ContextCompat
import androidx.lifecycle.LifecycleOwner
import java.util.concurrent.ExecutorService
import java.util.concurrent.Executors

class CameraManager(private val context: Context) {
    private var cameraProvider: ProcessCameraProvider? = null
    private var camera: Camera? = null
    private var preview: Preview? = null
    private var imageAnalysis: ImageAnalysis? = null
    private var lensFacing = CameraSelector.LENS_FACING_BACK
    private val cameraExecutor: ExecutorService = Executors.newSingleThreadExecutor()
    
    var currentResolution = Size(1280, 720)
        private set
    
    var onFrameAvailable: ((ImageProxy) -> Unit)? = null
    
    fun initialize(lifecycleOwner: LifecycleOwner, previewView: PreviewView, callback: (Boolean) -> Unit) {
        val cameraProviderFuture = ProcessCameraProvider.getInstance(context)
        
        cameraProviderFuture.addListener({
            try {
                cameraProvider = cameraProviderFuture.get()
                startCamera(lifecycleOwner, previewView)
                callback(true)
            } catch (e: Exception) {
                e.printStackTrace()
                callback(false)
            }
        }, ContextCompat.getMainExecutor(context))
    }
    
    private fun startCamera(lifecycleOwner: LifecycleOwner, previewView: PreviewView) {
        val cameraProvider = cameraProvider ?: return
        
        cameraProvider.unbindAll()
        
        preview = Preview.Builder()
            .build()
            .also {
                it.setSurfaceProvider(previewView.surfaceProvider)
            }
        
        imageAnalysis = ImageAnalysis.Builder()
            .setTargetResolution(currentResolution)
            .setBackpressureStrategy(ImageAnalysis.STRATEGY_KEEP_ONLY_LATEST)
            .build()
            .also { analysis ->
                analysis.setAnalyzer(cameraExecutor) { imageProxy ->
                    onFrameAvailable?.invoke(imageProxy)
                }
            }
        
        val cameraSelector = CameraSelector.Builder()
            .requireLensFacing(lensFacing)
            .build()
        
        try {
            camera = cameraProvider.bindToLifecycle(
                lifecycleOwner,
                cameraSelector,
                preview,
                imageAnalysis
            )
        } catch (e: Exception) {
            e.printStackTrace()
        }
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
    
    fun setFlashMode(enabled: Boolean) {
        camera?.cameraControl?.enableTorch(enabled)
    }
    
    fun setFocus(x: Float, y: Float) {
        val factory = previewView?.meteringPointFactory ?: return
        val point = factory.createPoint(x, y)
        val action = FocusMeteringAction.Builder(point).build()
        camera?.cameraControl?.startFocusAndMetering(action)
    }
    
    fun setExposure(value: Int) {
        camera?.cameraControl?.setExposureCompensationIndex(value)
    }
    
    private var previewView: PreviewView? = null
    
    fun release() {
        cameraExecutor.shutdown()
        cameraProvider?.unbindAll()
    }
}

