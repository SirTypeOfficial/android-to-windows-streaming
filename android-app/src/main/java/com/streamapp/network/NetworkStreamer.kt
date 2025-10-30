package com.streamapp.network

import android.util.Log
import com.streamapp.protocol.MAGIC_NUMBER
import com.streamapp.protocol.Packet
import com.streamapp.protocol.PacketHeader
import com.streamapp.protocol.PacketType
import kotlinx.coroutines.*
import java.io.InputStream
import java.io.OutputStream
import java.net.ServerSocket
import java.net.Socket

class NetworkStreamer(private val port: Int = 8888) {
    private var serverSocket: ServerSocket? = null
    private var clientSocket: Socket? = null
    private var outputStream: OutputStream? = null
    private var inputStream: InputStream? = null
    private var isRunning = false
    private val TAG = "NetworkStreamer"
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
                Log.d(TAG, "Server started on port $port")
                
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
                Log.e(TAG, "Error starting server", e)
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
                
                Log.d(TAG, "Client connected: ${client.inetAddress.hostAddress}")
                withContext(Dispatchers.Main) {
                    onClientConnected?.invoke()
                }
                
                receiveCommands()
                
            } catch (e: Exception) {
                Log.e(TAG, "Error handling client", e)
            } finally {
                withContext(Dispatchers.Main) {
                    onClientDisconnected?.invoke()
                }
            }
        }
    }
    
    private suspend fun receiveCommands() {
        val stream = inputStream ?: return
        var consecutiveErrors = 0
        val maxConsecutiveErrors = 5
        
        while (isRunning && clientSocket?.isConnected == true) {
            try {
                val headerBuffer = ByteArray(PacketHeader.HEADER_SIZE)
                var totalRead = 0
                
                while (totalRead < PacketHeader.HEADER_SIZE) {
                    val read = stream.read(headerBuffer, totalRead, PacketHeader.HEADER_SIZE - totalRead)
                    if (read == -1) return
                    totalRead += read
                }
                
                val header = PacketHeader.fromBytes(headerBuffer)
                
                if (header.magic != MAGIC_NUMBER) {
                    Log.e(TAG, "Invalid magic number: 0x${header.magic.toString(16).uppercase()}")
                    consecutiveErrors++
                    if (consecutiveErrors >= maxConsecutiveErrors) {
                        Log.e(TAG, "Too many consecutive errors, stopping command receiver")
                        break
                    }
                    continue
                }
                
                if (header.payloadSize < 0 || header.payloadSize > 1024 * 1024) {
                    Log.e(TAG, "Invalid payload size: ${header.payloadSize}")
                    consecutiveErrors++
                    if (consecutiveErrors >= maxConsecutiveErrors) {
                        Log.e(TAG, "Too many consecutive errors, stopping command receiver")
                        break
                    }
                    continue
                }
                
                val payloadBuffer = ByteArray(header.payloadSize)
                totalRead = 0
                while (totalRead < header.payloadSize) {
                    val read = stream.read(payloadBuffer, totalRead, header.payloadSize - totalRead)
                    if (read == -1) return
                    totalRead += read
                }
                
                val fullPacket = headerBuffer + payloadBuffer
                val packet = Packet.fromBytes(fullPacket)
                
                consecutiveErrors = 0
                
                if (packet.packetType == PacketType.CONTROL_COMMAND) {
                    val command = String(packet.payload, Charsets.UTF_8)
                    withContext(Dispatchers.Main) {
                        onControlCommand?.invoke(command)
                    }
                }
                
            } catch (e: Exception) {
                if (e is java.net.SocketException && 
                    (e.message?.contains("Connection reset") == true || 
                     e.message?.contains("Socket closed") == true)) {
                    Log.d(TAG, "Client disconnected")
                    break
                }
                Log.e(TAG, "Error receiving command", e)
                consecutiveErrors++
                if (consecutiveErrors >= maxConsecutiveErrors) {
                    Log.e(TAG, "Too many consecutive errors, stopping command receiver")
                    break
                }
            }
        }
    }
    
    fun sendVideoConfig(configData: ByteArray) {
        scope.launch {
            try {
                // Check if client is connected
                if (clientSocket?.isConnected != true) {
                    return@launch
                }
                
                val packet = Packet(PacketType.VIDEO_CONFIG, configData, 0, 0)
                outputStream?.write(packet.toBytes())
                outputStream?.flush()
                Log.d(TAG, "Video config sent: ${configData.size} bytes")
            } catch (e: Exception) {
                Log.e(TAG, "Error sending video config", e)
            }
        }
    }
    
    fun sendVideoFrame(data: ByteArray, timestamp: Long, isKeyFrame: Boolean) {
        scope.launch {
            try {
                // Check if client is connected
                if (clientSocket?.isConnected != true) {
                    return@launch
                }
                
                val packet = Packet(PacketType.VIDEO_FRAME, data, timestamp, 0)
                outputStream?.write(packet.toBytes())
                outputStream?.flush()
            } catch (e: Exception) {
                // Don't log "Broken pipe" errors when socket is disconnected
                if (e is java.net.SocketException && e.message?.contains("Broken pipe") == true) {
                    return@launch
                }
                Log.e(TAG, "Error sending video frame", e)
            }
        }
    }
    
    fun sendAudioFrame(data: ByteArray, timestamp: Long) {
        scope.launch {
            try {
                // Check if client is connected
                if (clientSocket?.isConnected != true) {
                    return@launch
                }
                
                val packet = Packet(PacketType.AUDIO_FRAME, data, timestamp, 0)
                outputStream?.write(packet.toBytes())
                outputStream?.flush()
            } catch (e: Exception) {
                // Don't log "Broken pipe" errors when socket is disconnected
                if (e is java.net.SocketException && e.message?.contains("Broken pipe") == true) {
                    return@launch
                }
                Log.e(TAG, "Error sending audio frame", e)
            }
        }
    }
    
    fun sendAudioConfig(configData: ByteArray) {
        scope.launch {
            try {
                // Check if client is connected
                if (clientSocket?.isConnected != true) {
                    return@launch
                }
                
                val packet = Packet(PacketType.AUDIO_CONFIG, configData, 0, 0)
                outputStream?.write(packet.toBytes())
                outputStream?.flush()
                Log.d(TAG, "Audio config sent: ${configData.size} bytes")
            } catch (e: Exception) {
                Log.e(TAG, "Error sending audio config", e)
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
            Log.d(TAG, "Server stopped")
        } catch (e: Exception) {
            Log.e(TAG, "Error stopping server", e)
        }
    }
    
    fun isClientConnected(): Boolean {
        return clientSocket?.isConnected == true
    }
}

