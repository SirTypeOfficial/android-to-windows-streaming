package com.streamapp.encoder

import android.media.*
import android.util.Log
import java.nio.ByteBuffer

class AudioEncoder(
    private val sampleRate: Int = 44100,
    private val channelCount: Int = 2,
    private val bitrate: Int = 128000
) {
    private var mediaCodec: MediaCodec? = null
    private var audioRecord: AudioRecord? = null
    private var isRunning = false
    private val TAG = "AudioEncoder"
    private var recordingThread: Thread? = null
    private var configSent = false
    private var cachedConfigData: ByteArray? = null
    
    var onEncodedData: ((ByteArray, Long) -> Unit)? = null
    var onConfigData: ((ByteArray) -> Unit)? = null
    
    fun start() {
        try {
            val channelConfig = if (channelCount == 2) {
                AudioFormat.CHANNEL_IN_STEREO
            } else {
                AudioFormat.CHANNEL_IN_MONO
            }
            
            val minBufferSize = AudioRecord.getMinBufferSize(
                sampleRate,
                channelConfig,
                AudioFormat.ENCODING_PCM_16BIT
            )
            
            audioRecord = AudioRecord(
                MediaRecorder.AudioSource.MIC,
                sampleRate,
                channelConfig,
                AudioFormat.ENCODING_PCM_16BIT,
                minBufferSize * 2
            )
            
            val format = MediaFormat.createAudioFormat(MediaFormat.MIMETYPE_AUDIO_AAC, sampleRate, channelCount)
            format.setInteger(MediaFormat.KEY_AAC_PROFILE, MediaCodecInfo.CodecProfileLevel.AACObjectLC)
            format.setInteger(MediaFormat.KEY_BIT_RATE, bitrate)
            format.setInteger(MediaFormat.KEY_MAX_INPUT_SIZE, 16384)
            
            mediaCodec = MediaCodec.createEncoderByType(MediaFormat.MIMETYPE_AUDIO_AAC)
            mediaCodec?.configure(format, null, null, MediaCodec.CONFIGURE_FLAG_ENCODE)
            mediaCodec?.start()
            
            audioRecord?.startRecording()
            isRunning = true
            
            recordingThread = Thread { recordAudio() }
            recordingThread?.start()
            
            Log.d(TAG, "Audio encoder started: ${sampleRate}Hz, ${channelCount} channels")
        } catch (e: Exception) {
            Log.e(TAG, "Error starting audio encoder", e)
        }
    }
    
    private fun recordAudio() {
        val codec = mediaCodec ?: return
        val recorder = audioRecord ?: return
        
        val bufferSize = 4096
        val audioData = ByteArray(bufferSize)
        
        while (isRunning) {
            try {
                val readBytes = recorder.read(audioData, 0, bufferSize)
                
                if (readBytes > 0) {
                    val inputBufferIndex = codec.dequeueInputBuffer(10000)
                    
                    if (inputBufferIndex >= 0) {
                        val inputBuffer = codec.getInputBuffer(inputBufferIndex)
                        inputBuffer?.clear()
                        inputBuffer?.put(audioData, 0, readBytes)
                        
                        val presentationTimeUs = System.nanoTime() / 1000
                        codec.queueInputBuffer(inputBufferIndex, 0, readBytes, presentationTimeUs, 0)
                    }
                }
                
                val bufferInfo = MediaCodec.BufferInfo()
                var outputBufferIndex = codec.dequeueOutputBuffer(bufferInfo, 0)
                
                while (outputBufferIndex >= 0) {
                    if (outputBufferIndex == MediaCodec.INFO_OUTPUT_FORMAT_CHANGED) {
                        // Send codec configuration data when format changes
                        val outputFormat = codec.outputFormat
                        val csd0 = outputFormat.getByteBuffer("csd-0")
                        if (csd0 != null) {
                            val configData = ByteArray(csd0.remaining())
                            csd0.get(configData)
                            
                            // Cache the config data
                            cachedConfigData = configData
                            
                            // Send config if callback is set
                            if (!configSent) {
                                onConfigData?.invoke(configData)
                                configSent = true
                                Log.d(TAG, "Audio config data sent: ${configData.size} bytes")
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
                                
                                onEncodedData?.invoke(data, bufferInfo.presentationTimeUs)
                            }
                        }
                        
                        codec.releaseOutputBuffer(outputBufferIndex, false)
                    }
                    outputBufferIndex = codec.dequeueOutputBuffer(bufferInfo, 0)
                }
            } catch (e: Exception) {
                Log.e(TAG, "Error recording audio", e)
            }
        }
    }
    
    fun resendConfig() {
        cachedConfigData?.let { config ->
            Log.d(TAG, "Resending audio config: ${config.size} bytes")
            onConfigData?.invoke(config)
        }
    }
    
    fun stop() {
        isRunning = false
        
        try {
            recordingThread?.join(1000)
            
            audioRecord?.stop()
            audioRecord?.release()
            audioRecord = null
            
            mediaCodec?.stop()
            mediaCodec?.release()
            mediaCodec = null
            
            cachedConfigData = null
            
            Log.d(TAG, "Audio encoder stopped")
        } catch (e: Exception) {
            Log.e(TAG, "Error stopping audio encoder", e)
        }
    }
}

