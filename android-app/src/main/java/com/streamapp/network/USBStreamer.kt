package com.streamapp.network

import android.util.Log
import com.streamapp.protocol.Packet
import com.streamapp.protocol.PacketType
import kotlinx.coroutines.*
import java.io.InputStream
import java.io.OutputStream
import java.net.ServerSocket
import java.net.Socket

class USBStreamer(private val port: Int = 8889) {
    private var serverSocket: ServerSocket? = null
    private var clientSocket: Socket? = null
    private var outputStream: OutputStream? = null
    private var inputStream: InputStream? = null
    private var isRunning = false
    private val TAG = "USBStreamer"
    private val scope = CoroutineScope(Dispatchers.IO + SupervisorJob())
    
    var onClientConnected: (() -> Unit)? = null
    var onClientDisconnected: (() -> Unit)? = null
    var onControlCommand: ((String) -> Unit)? = null
    
    fun start() {
        if (isRunning) return
        
        scope.launch {
            try {
                serverSocket = ServerSocket(port)
                isRunning = true
                Log.d(TAG, "USB Server started on port $port (use adb reverse tcp:$port tcp:$port)")
                
                while (isRunning) {
                    try {
                        val client = serverSocket?.accept()
                        if (client != null) {
                            handleClient(client)
                        }
                    } catch (e: Exception) {
                        if (isRunning) {
                            Log.e(TAG, "Error accepting client", e)
                        }
                    }
                }
            } catch (e: Exception) {
                Log.e(TAG, "Error starting USB server", e)
            }
        }
    }
    
    private suspend fun handleClient(client: Socket) {
        withContext(Dispatchers.IO) {
            try {
                clientSocket?.close()
                clientSocket = client
                outputStream = client.getOutputStream()
                inputStream = client.getInputStream()
                
                Log.d(TAG, "USB Client connected")
                withContext(Dispatchers.Main) {
                    onClientConnected?.invoke()
                }
                
                receiveCommands()
                
            } catch (e: Exception) {
                Log.e(TAG, "Error handling USB client", e)
            } finally {
                withContext(Dispatchers.Main) {
                    onClientDisconnected?.invoke()
                }
            }
        }
    }
    
    private suspend fun receiveCommands() {
        val stream = inputStream ?: return
        
        while (isRunning && clientSocket?.isConnected == true) {
            try {
                val headerBuffer = ByteArray(21)
                var totalRead = 0
                
                while (totalRead < 21) {
                    val read = stream.read(headerBuffer, totalRead, 21 - totalRead)
                    if (read == -1) return
                    totalRead += read
                }
                
                val packet = Packet.fromBytes(headerBuffer + ByteArray(0))
                
                val payloadBuffer = ByteArray(packet.header.payloadSize)
                totalRead = 0
                while (totalRead < packet.header.payloadSize) {
                    val read = stream.read(payloadBuffer, totalRead, packet.header.payloadSize - totalRead)
                    if (read == -1) return
                    totalRead += read
                }
                
                if (packet.header.packetType == PacketType.CONTROL_COMMAND) {
                    val command = String(payloadBuffer, Charsets.UTF_8)
                    withContext(Dispatchers.Main) {
                        onControlCommand?.invoke(command)
                    }
                }
                
            } catch (e: Exception) {
                Log.e(TAG, "Error receiving command", e)
                break
            }
        }
    }
    
    fun sendVideoFrame(data: ByteArray, timestamp: Long, isKeyFrame: Boolean) {
        scope.launch {
            try {
                val packet = Packet(PacketType.VIDEO_FRAME, data, timestamp, 0)
                outputStream?.write(packet.toBytes())
                outputStream?.flush()
            } catch (e: Exception) {
                Log.e(TAG, "Error sending video frame", e)
            }
        }
    }
    
    fun sendAudioFrame(data: ByteArray, timestamp: Long) {
        scope.launch {
            try {
                val packet = Packet(PacketType.AUDIO_FRAME, data, timestamp, 0)
                outputStream?.write(packet.toBytes())
                outputStream?.flush()
            } catch (e: Exception) {
                Log.e(TAG, "Error sending audio frame", e)
            }
        }
    }
    
    fun stop() {
        isRunning = false
        
        try {
            outputStream?.close()
            inputStream?.close()
            clientSocket?.close()
            serverSocket?.close()
            scope.cancel()
            Log.d(TAG, "USB Server stopped")
        } catch (e: Exception) {
            Log.e(TAG, "Error stopping USB server", e)
        }
    }
    
    fun isClientConnected(): Boolean {
        return clientSocket?.isConnected == true
    }
}

