package com.streamapp

import android.Manifest
import android.content.ComponentName
import android.content.Context
import android.content.Intent
import android.content.ServiceConnection
import android.content.pm.PackageManager
import android.os.Bundle
import android.os.IBinder
import android.util.Log
import android.view.View
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity
import androidx.camera.core.ImageProxy
import androidx.core.app.ActivityCompat
import androidx.core.content.ContextCompat
import com.google.android.material.button.MaterialButton
import com.google.android.material.chip.Chip
import com.streamapp.camera.CameraManager
import com.streamapp.control.ControlHandler
import android.widget.TextView
import androidx.camera.view.PreviewView
import kotlin.random.Random

class MainActivity : AppCompatActivity() {
    private val TAG = "MainActivity"
    private val PERMISSIONS_REQUEST_CODE = 100
    private val REQUIRED_PERMISSIONS = arrayOf(
        Manifest.permission.CAMERA,
        Manifest.permission.RECORD_AUDIO,
        Manifest.permission.POST_NOTIFICATIONS
    )
    
    private lateinit var previewView: PreviewView
    private lateinit var btnStartStop: MaterialButton
    private lateinit var btnSwitchCamera: MaterialButton
    private lateinit var btnFlash: MaterialButton
    private lateinit var chipWifi: Chip
    private lateinit var chipUsb: Chip
    private lateinit var tvStatus: TextView
    private lateinit var tvPairingCode: TextView
    
    private var cameraManager: CameraManager? = null
    private var controlHandler: ControlHandler? = null
    private var streamingService: StreamingService? = null
    private var isStreaming = false
    private var pairingCode: String = ""
    private var useWifi = true
    
    private val serviceConnection = object : ServiceConnection {
        override fun onServiceConnected(name: ComponentName?, service: IBinder?) {
            val binder = service as StreamingService.LocalBinder
            streamingService = binder.getService()
            Log.d(TAG, "Service connected")
        }
        
        override fun onServiceDisconnected(name: ComponentName?) {
            streamingService = null
            Log.d(TAG, "Service disconnected")
        }
    }
    
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)
        
        initViews()
        
        if (allPermissionsGranted()) {
            initCamera()
        } else {
            ActivityCompat.requestPermissions(this, REQUIRED_PERMISSIONS, PERMISSIONS_REQUEST_CODE)
        }
        
        bindService(Intent(this, StreamingService::class.java), serviceConnection, Context.BIND_AUTO_CREATE)
    }
    
    private fun initViews() {
        previewView = findViewById(R.id.previewView)
        btnStartStop = findViewById(R.id.btnStartStop)
        btnSwitchCamera = findViewById(R.id.btnSwitchCamera)
        btnFlash = findViewById(R.id.btnFlash)
        chipWifi = findViewById(R.id.chipWifi)
        chipUsb = findViewById(R.id.chipUsb)
        tvStatus = findViewById(R.id.tvStatus)
        tvPairingCode = findViewById(R.id.tvPairingCode)
        
        btnStartStop.setOnClickListener {
            toggleStreaming()
        }
        
        btnSwitchCamera.setOnClickListener {
            cameraManager?.switchCamera(this, previewView)
        }
        
        btnFlash.setOnClickListener {
            cameraManager?.setFlashMode(!btnFlash.isChecked)
            btnFlash.isChecked = !btnFlash.isChecked
        }
        
        chipWifi.setOnCheckedChangeListener { _, isChecked ->
            if (isChecked) {
                useWifi = true
                chipUsb.isChecked = false
            }
        }
        
        chipUsb.setOnCheckedChangeListener { _, isChecked ->
            if (isChecked) {
                useWifi = false
                chipWifi.isChecked = false
            }
        }
    }
    
    private fun initCamera() {
        cameraManager = CameraManager(this)
        cameraManager?.initialize(this, previewView) { success ->
            if (success) {
                Log.d(TAG, "Camera initialized successfully")
                controlHandler = ControlHandler(cameraManager!!, this, previewView)
                setupControlHandler()
            } else {
                Toast.makeText(this, "خطا در راه‌اندازی دوربین", Toast.LENGTH_SHORT).show()
            }
        }
    }
    
    private fun setupControlHandler() {
        controlHandler?.onResolutionChanged = { width, height ->
            if (isStreaming) {
                stopStreaming()
                startStreaming(width, height)
            }
        }
        
        controlHandler?.onFpsChanged = { fps ->
            if (isStreaming) {
                stopStreaming()
                startStreaming(fps = fps)
            }
        }
    }
    
    private fun toggleStreaming() {
        if (isStreaming) {
            stopStreaming()
        } else {
            startStreaming()
        }
    }
    
    private fun startStreaming(width: Int = 1280, height: Int = 720, fps: Int = 30) {
        val service = streamingService ?: return
        
        service.startStreaming(width, height, fps, useWifi)
        
        cameraManager?.onFrameAvailable = { imageProxy ->
            service.getVideoEncoder()?.encodeFrame(imageProxy)
        }
        
        val streamer = if (useWifi) service.networkStreamer else service.usbStreamer
        
        streamer?.onClientConnected = {
            runOnUiThread {
                tvStatus.text = getString(R.string.connected)
                tvPairingCode.visibility = View.GONE
            }
        }
        
        streamer?.onClientDisconnected = {
            runOnUiThread {
                tvStatus.text = getString(R.string.waiting_for_connection)
                generatePairingCode()
            }
        }
        
        streamer?.onControlCommand = { command ->
            controlHandler?.handleCommand(command)
        }
        
        isStreaming = true
        btnStartStop.text = getString(R.string.stop_streaming)
        tvStatus.text = getString(R.string.waiting_for_connection)
        generatePairingCode()
        
        Log.d(TAG, "Streaming started")
    }
    
    private fun stopStreaming() {
        streamingService?.stopStreaming()
        cameraManager?.onFrameAvailable = null
        
        isStreaming = false
        btnStartStop.text = getString(R.string.start_streaming)
        tvStatus.text = getString(R.string.disconnected)
        tvPairingCode.visibility = View.GONE
        
        Log.d(TAG, "Streaming stopped")
    }
    
    private fun generatePairingCode() {
        pairingCode = String.format("%06d", Random.nextInt(0, 1000000))
        tvPairingCode.text = getString(R.string.pairing_code, pairingCode)
        tvPairingCode.visibility = View.VISIBLE
    }
    
    private fun allPermissionsGranted() = REQUIRED_PERMISSIONS.all {
        ContextCompat.checkSelfPermission(baseContext, it) == PackageManager.PERMISSION_GRANTED
    }
    
    override fun onRequestPermissionsResult(
        requestCode: Int,
        permissions: Array<String>,
        grantResults: IntArray
    ) {
        super.onRequestPermissionsResult(requestCode, permissions, grantResults)
        if (requestCode == PERMISSIONS_REQUEST_CODE) {
            if (allPermissionsGranted()) {
                initCamera()
            } else {
                Toast.makeText(this, "دسترسی‌های لازم داده نشده", Toast.LENGTH_SHORT).show()
                finish()
            }
        }
    }
    
    override fun onDestroy() {
        super.onDestroy()
        unbindService(serviceConnection)
        cameraManager?.release()
    }
}

