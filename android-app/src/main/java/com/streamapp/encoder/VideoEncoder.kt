package com.streamapp.encoder

import android.media.MediaCodec
import android.media.MediaCodecInfo
import android.media.MediaFormat
import android.util.Log
import androidx.camera.core.ImageProxy
import java.nio.ByteBuffer

class VideoEncoder(
    private val width: Int,
    private val height: Int,
    private val fps: Int = 30,
    private val bitrate: Int = 2000000
) {
    private var mediaCodec: MediaCodec? = null
    private var isRunning = false
    private val TAG = "VideoEncoder"
    private var configSent = false
    private var cachedConfigData: ByteArray? = null
    
    var onEncodedData: ((ByteArray, Long, Boolean) -> Unit)? = null
    var onConfigData: ((ByteArray) -> Unit)? = null
    
    fun start() {
        try {
            val format = MediaFormat.createVideoFormat(MediaFormat.MIMETYPE_VIDEO_AVC, width, height)
            format.setInteger(MediaFormat.KEY_COLOR_FORMAT, MediaCodecInfo.CodecCapabilities.COLOR_FormatYUV420Flexible)
            format.setInteger(MediaFormat.KEY_BIT_RATE, bitrate)
            format.setInteger(MediaFormat.KEY_FRAME_RATE, fps)
            format.setInteger(MediaFormat.KEY_I_FRAME_INTERVAL, 1)
            
            mediaCodec = MediaCodec.createEncoderByType(MediaFormat.MIMETYPE_VIDEO_AVC)
            mediaCodec?.configure(format, null, null, MediaCodec.CONFIGURE_FLAG_ENCODE)
            mediaCodec?.start()
            isRunning = true
            
            Log.d(TAG, "Video encoder started: ${width}x${height} @ ${fps}fps")
        } catch (e: Exception) {
            Log.e(TAG, "Error starting encoder", e)
        }
    }
    
    fun encodeFrame(imageProxy: ImageProxy) {
        if (!isRunning) return
        
        try {
            val codec = mediaCodec ?: return
            val inputBufferIndex = codec.dequeueInputBuffer(10000)
            
            if (inputBufferIndex >= 0) {
                val inputBuffer = codec.getInputBuffer(inputBufferIndex)
                inputBuffer?.clear()
                
                val yuvImage = imageProxyToNV21(imageProxy)
                inputBuffer?.put(yuvImage)
                
                val presentationTimeUs = System.nanoTime() / 1000
                codec.queueInputBuffer(inputBufferIndex, 0, yuvImage.size, presentationTimeUs, 0)
            }
            
            val bufferInfo = MediaCodec.BufferInfo()
            var outputBufferIndex = codec.dequeueOutputBuffer(bufferInfo, 0)
            
            while (outputBufferIndex >= 0) {
                if (outputBufferIndex == MediaCodec.INFO_OUTPUT_FORMAT_CHANGED) {
                    // Send SPS/PPS when format changes
                    val outputFormat = codec.outputFormat
                    val csd0 = outputFormat.getByteBuffer("csd-0") // SPS
                    val csd1 = outputFormat.getByteBuffer("csd-1") // PPS
                    
                    if (csd0 != null && csd1 != null) {
                        // Combine SPS and PPS with start codes
                        val spsSize = csd0.remaining()
                        val ppsSize = csd1.remaining()
                        val configData = ByteArray(spsSize + ppsSize)
                        
                        csd0.get(configData, 0, spsSize)
                        csd1.get(configData, spsSize, ppsSize)
                        
                        // Cache the config data
                        cachedConfigData = configData
                        
                        // Send config if callback is set
                        if (!configSent) {
                            onConfigData?.invoke(configData)
                            configSent = true
                            Log.d(TAG, "Video config data sent: SPS=${spsSize} bytes, PPS=${ppsSize} bytes")
                        }
                    }
                } else {
                    val outputBuffer = codec.getOutputBuffer(outputBufferIndex)
                    
                    if (outputBuffer != null && bufferInfo.size > 0) {
                        // Skip codec config buffers (they're sent separately)
                        if ((bufferInfo.flags and MediaCodec.BUFFER_FLAG_CODEC_CONFIG) == 0) {
                            val data = ByteArray(bufferInfo.size)
                            outputBuffer.position(bufferInfo.offset)
                            outputBuffer.get(data, 0, bufferInfo.size)
                            
                            val isKeyFrame = (bufferInfo.flags and MediaCodec.BUFFER_FLAG_KEY_FRAME) != 0
                            onEncodedData?.invoke(data, bufferInfo.presentationTimeUs, isKeyFrame)
                        }
                    }
                    
                    codec.releaseOutputBuffer(outputBufferIndex, false)
                }
                
                outputBufferIndex = codec.dequeueOutputBuffer(bufferInfo, 0)
            }
        } catch (e: Exception) {
            Log.e(TAG, "Error encoding frame", e)
        } finally {
            imageProxy.close()
        }
    }
    
    private fun imageProxyToNV21(image: ImageProxy): ByteArray {
        val ySize = image.width * image.height
        val uvSize = ySize / 2
        val nv21 = ByteArray(ySize + uvSize)
        
        val yBuffer = image.planes[0].buffer
        val uBuffer = image.planes[1].buffer
        val vBuffer = image.planes[2].buffer
        
        yBuffer.get(nv21, 0, ySize)
        
        val uvWidth = image.width / 2
        val uvHeight = image.height / 2
        var uvIndex = ySize
        
        for (row in 0 until uvHeight) {
            for (col in 0 until uvWidth) {
                val vPos = row * vBuffer.capacity() / uvHeight + col * 2
                val uPos = row * uBuffer.capacity() / uvHeight + col * 2
                
                if (vPos < vBuffer.capacity() && uPos < uBuffer.capacity()) {
                    nv21[uvIndex++] = vBuffer.get(vPos)
                    nv21[uvIndex++] = uBuffer.get(uPos)
                }
            }
        }
        
        return nv21
    }
    
    fun resendConfig() {
        cachedConfigData?.let { config ->
            Log.d(TAG, "Resending video config: ${config.size} bytes")
            onConfigData?.invoke(config)
        }
    }
    
    fun stop() {
        isRunning = false
        try {
            mediaCodec?.stop()
            mediaCodec?.release()
            mediaCodec = null
            cachedConfigData = null
            Log.d(TAG, "Video encoder stopped")
        } catch (e: Exception) {
            Log.e(TAG, "Error stopping encoder", e)
        }
    }
}

