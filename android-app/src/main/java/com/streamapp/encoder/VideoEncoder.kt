package com.streamapp.encoder

import android.media.MediaCodec
import android.media.MediaCodecInfo
import android.media.MediaFormat
import android.view.Surface
import android.util.Log
import java.util.concurrent.ExecutorService
import java.util.concurrent.Executors

class VideoEncoder(
    private val width: Int,
    private val height: Int,
    private val fps: Int = 30,
    private val bitrate: Int = 2000000
) {
    private var mediaCodec: MediaCodec? = null
    private var inputSurface: Surface? = null
    private var isRunning = false
    private val TAG = "VideoEncoder"
    private var configSent = false
    private var cachedConfigData: ByteArray? = null
    private val executor: ExecutorService = Executors.newSingleThreadExecutor()
    
    var onEncodedData: ((ByteArray, Long, Boolean) -> Unit)? = null
    var onConfigData: ((ByteArray) -> Unit)? = null
    
    fun start() {
        try {
            val format = MediaFormat.createVideoFormat(MediaFormat.MIMETYPE_VIDEO_AVC, width, height)
            format.setInteger(MediaFormat.KEY_COLOR_FORMAT, MediaCodecInfo.CodecCapabilities.COLOR_FormatSurface)
            format.setInteger(MediaFormat.KEY_BIT_RATE, bitrate)
            format.setInteger(MediaFormat.KEY_FRAME_RATE, fps)
            format.setInteger(MediaFormat.KEY_I_FRAME_INTERVAL, 1)
            
            mediaCodec = MediaCodec.createEncoderByType(MediaFormat.MIMETYPE_VIDEO_AVC)
            mediaCodec?.configure(format, null, null, MediaCodec.CONFIGURE_FLAG_ENCODE)
            
            // Create input Surface
            inputSurface = mediaCodec?.createInputSurface()
            
            mediaCodec?.start()
            isRunning = true
            
            // Start output processing thread
            startOutputProcessing()
            
            Log.d(TAG, "Video encoder started with Surface input: ${width}x${height} @ ${fps}fps")
        } catch (e: Exception) {
            Log.e(TAG, "Error starting encoder", e)
        }
    }
    
    fun getInputSurface(): Surface? {
        return inputSurface
    }
    
    private fun startOutputProcessing() {
        executor.execute {
            try {
                val codec = mediaCodec ?: return@execute
                val bufferInfo = MediaCodec.BufferInfo()
                
                while (isRunning) {
                    val outputBufferIndex = codec.dequeueOutputBuffer(bufferInfo, 10000)
                    
                    when (outputBufferIndex) {
                        MediaCodec.INFO_OUTPUT_FORMAT_CHANGED -> {
                            val outputFormat = codec.outputFormat
                            val csd0 = outputFormat.getByteBuffer("csd-0") // SPS
                            val csd1 = outputFormat.getByteBuffer("csd-1") // PPS
                            
                            if (csd0 != null && csd1 != null) {
                                val spsSize = csd0.remaining()
                                val ppsSize = csd1.remaining()
                                val configData = ByteArray(spsSize + ppsSize)
                                
                                csd0.get(configData, 0, spsSize)
                                csd1.get(configData, spsSize, ppsSize)
                                
                                cachedConfigData = configData
                                
                                if (!configSent) {
                                    onConfigData?.invoke(configData)
                                    configSent = true
                                    Log.d(TAG, "Video config data sent: SPS=${spsSize} bytes, PPS=${ppsSize} bytes")
                                }
                            }
                        }
                        MediaCodec.INFO_TRY_AGAIN_LATER -> {
                            // No output available
                        }
                        else -> {
                            if (outputBufferIndex >= 0) {
                                val outputBuffer = codec.getOutputBuffer(outputBufferIndex)
                                
                                if (outputBuffer != null && bufferInfo.size > 0) {
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
                        }
                    }
                }
            } catch (e: Exception) {
                Log.e(TAG, "Error in output processing loop", e)
            }
        }
    }
    
    fun resendConfig() {
        cachedConfigData?.let { config ->
            Log.d(TAG, "Resending video config: ${config.size} bytes")
            onConfigData?.invoke(config)
        }
    }
    
    fun stop() {
        if (!isRunning) return
        
        isRunning = false
        
        try {
            // Wait for output processing thread to finish
            executor.shutdown()
            try {
                if (!executor.awaitTermination(2, java.util.concurrent.TimeUnit.SECONDS)) {
                    Log.w(TAG, "Executor did not terminate in time, forcing shutdown")
                    executor.shutdownNow()
                }
            } catch (e: InterruptedException) {
                executor.shutdownNow()
                Thread.currentThread().interrupt()
            }
            
            // Now safely stop and release the codec
            mediaCodec?.stop()
            mediaCodec?.release()
            mediaCodec = null
            
            inputSurface?.release()
            inputSurface = null
            
            cachedConfigData = null
            configSent = false
            
            Log.d(TAG, "Video encoder stopped cleanly")
        } catch (e: Exception) {
            Log.e(TAG, "Error stopping encoder", e)
        }
    }
}
