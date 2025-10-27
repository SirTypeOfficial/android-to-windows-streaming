package com.streamapp

import android.app.Notification
import android.app.NotificationChannel
import android.app.NotificationManager
import android.app.Service
import android.content.Intent
import android.os.Binder
import android.os.IBinder
import android.util.Log
import androidx.core.app.NotificationCompat
import com.streamapp.encoder.AudioEncoder
import com.streamapp.encoder.VideoEncoder
import com.streamapp.network.NetworkStreamer
import com.streamapp.network.USBStreamer

class StreamingService : Service() {
    private val binder = LocalBinder()
    private val TAG = "StreamingService"
    
    private var videoEncoder: VideoEncoder? = null
    private var audioEncoder: AudioEncoder? = null
    var networkStreamer: NetworkStreamer? = null
        private set
    var usbStreamer: USBStreamer? = null
        private set
    
    private var isStreaming = false
    
    // Allow external code to register callbacks
    var onClientConnectedCallback: (() -> Unit)? = null
    var onClientDisconnectedCallback: (() -> Unit)? = null
    
    inner class LocalBinder : Binder() {
        fun getService(): StreamingService = this@StreamingService
    }
    
    override fun onBind(intent: Intent?): IBinder {
        return binder
    }
    
    override fun onCreate() {
        super.onCreate()
        createNotificationChannel()
        startForeground(NOTIFICATION_ID, createNotification())
    }
    
    fun startStreaming(width: Int, height: Int, fps: Int, useWifi: Boolean) {
        if (isStreaming) return
        
        Log.d(TAG, "Starting streaming: ${width}x${height} @ ${fps}fps via ${if (useWifi) "WiFi" else "USB"}")
        
        videoEncoder = VideoEncoder(width, height, fps)
        audioEncoder = AudioEncoder()
        
        if (useWifi) {
            networkStreamer = NetworkStreamer()
            videoEncoder?.onConfigData = { configData ->
                networkStreamer?.sendVideoConfig(configData)
            }
            videoEncoder?.onEncodedData = { data, timestamp, isKeyFrame ->
                networkStreamer?.sendVideoFrame(data, timestamp, isKeyFrame)
            }
            audioEncoder?.onConfigData = { configData ->
                networkStreamer?.sendAudioConfig(configData)
            }
            audioEncoder?.onEncodedData = { data, timestamp ->
                networkStreamer?.sendAudioFrame(data, timestamp)
            }
            
            // Resend config when client connects
            networkStreamer?.onClientConnected = {
                Log.d(TAG, "Client connected via WiFi, resending configs")
                videoEncoder?.resendConfig()
                audioEncoder?.resendConfig()
                onClientConnectedCallback?.invoke()
            }
            
            networkStreamer?.onClientDisconnected = {
                onClientDisconnectedCallback?.invoke()
            }
            
            networkStreamer?.start()
        } else {
            usbStreamer = USBStreamer()
            videoEncoder?.onConfigData = { configData ->
                usbStreamer?.sendVideoConfig(configData)
            }
            videoEncoder?.onEncodedData = { data, timestamp, isKeyFrame ->
                usbStreamer?.sendVideoFrame(data, timestamp, isKeyFrame)
            }
            audioEncoder?.onConfigData = { configData ->
                usbStreamer?.sendAudioConfig(configData)
            }
            audioEncoder?.onEncodedData = { data, timestamp ->
                usbStreamer?.sendAudioFrame(data, timestamp)
            }
            
            // Resend config when client connects
            usbStreamer?.onClientConnected = {
                Log.d(TAG, "Client connected via USB, resending configs")
                videoEncoder?.resendConfig()
                audioEncoder?.resendConfig()
                onClientConnectedCallback?.invoke()
            }
            
            usbStreamer?.onClientDisconnected = {
                onClientDisconnectedCallback?.invoke()
            }
            
            usbStreamer?.start()
        }
        
        videoEncoder?.start()
        audioEncoder?.start()
        
        isStreaming = true
    }
    
    fun stopStreaming() {
        if (!isStreaming) return
        
        Log.d(TAG, "Stopping streaming")
        
        videoEncoder?.stop()
        audioEncoder?.stop()
        networkStreamer?.stop()
        usbStreamer?.stop()
        
        videoEncoder = null
        audioEncoder = null
        networkStreamer = null
        usbStreamer = null
        
        isStreaming = false
    }
    
    fun getVideoEncoder(): VideoEncoder? = videoEncoder
    
    fun getAudioEncoder(): AudioEncoder? = audioEncoder
    
    fun isStreamingActive(): Boolean = isStreaming
    
    override fun onDestroy() {
        stopStreaming()
        super.onDestroy()
    }
    
    private fun createNotificationChannel() {
        val channel = NotificationChannel(
            CHANNEL_ID,
            "Streaming Service",
            NotificationManager.IMPORTANCE_LOW
        )
        val manager = getSystemService(NotificationManager::class.java)
        manager.createNotificationChannel(channel)
    }
    
    private fun createNotification(): Notification {
        return NotificationCompat.Builder(this, CHANNEL_ID)
            .setContentTitle("Android Stream")
            .setContentText("در حال استریم...")
            .setSmallIcon(android.R.drawable.ic_menu_camera)
            .build()
    }
    
    companion object {
        private const val CHANNEL_ID = "StreamingServiceChannel"
        private const val NOTIFICATION_ID = 1
    }
}

