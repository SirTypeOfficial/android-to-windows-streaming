package com.streamapp.protocol

import org.json.JSONObject
import java.nio.ByteBuffer
import java.nio.ByteOrder

const val MAGIC_NUMBER = 0x4157534D

enum class PacketType(val value: Byte) {
    HANDSHAKE_REQUEST(0x01),
    HANDSHAKE_RESPONSE(0x02),
    VIDEO_CONFIG(0x03),
    AUDIO_CONFIG(0x04),
    VIDEO_FRAME(0x10),
    AUDIO_FRAME(0x11),
    CONTROL_COMMAND(0x20),
    CONTROL_RESPONSE(0x21),
    KEEPALIVE(0x30),
    ERROR(0xFF.toByte());
    
    companion object {
        fun fromByte(byte: Byte): PacketType {
            return values().find { it.value == byte } ?: ERROR
        }
    }
}

data class PacketHeader(
    val magic: Int,
    val packetType: PacketType,
    val payloadSize: Int,
    val timestamp: Long,
    val sequenceNumber: Int
) {
    companion object {
        const val HEADER_SIZE = 21
        
        fun fromBytes(data: ByteArray): PacketHeader {
            val buffer = ByteBuffer.wrap(data).order(ByteOrder.BIG_ENDIAN)
            return PacketHeader(
                magic = buffer.int,
                packetType = PacketType.fromByte(buffer.get()),
                payloadSize = buffer.int,
                timestamp = buffer.long,
                sequenceNumber = buffer.int
            )
        }
    }
    
    fun toBytes(): ByteArray {
        val buffer = ByteBuffer.allocate(HEADER_SIZE).order(ByteOrder.BIG_ENDIAN)
        buffer.putInt(magic)
        buffer.put(packetType.value)
        buffer.putInt(payloadSize)
        buffer.putLong(timestamp)
        buffer.putInt(sequenceNumber)
        return buffer.array()
    }
}

class Packet(
    val packetType: PacketType,
    val payload: ByteArray,
    timestamp: Long = System.currentTimeMillis(),
    sequenceNumber: Int = 0
) {
    val header = PacketHeader(
        magic = MAGIC_NUMBER,
        packetType = packetType,
        payloadSize = payload.size,
        timestamp = timestamp,
        sequenceNumber = sequenceNumber
    )
    
    fun toBytes(): ByteArray {
        return header.toBytes() + payload
    }
    
    companion object {
        fun fromBytes(data: ByteArray): Packet {
            val header = PacketHeader.fromBytes(data.sliceArray(0 until PacketHeader.HEADER_SIZE))
            val payload = data.sliceArray(PacketHeader.HEADER_SIZE until PacketHeader.HEADER_SIZE + header.payloadSize)
            return Packet(header.packetType, payload, header.timestamp, header.sequenceNumber)
        }
    }
}

object ControlCommand {
    fun createCommand(command: String, parameters: Map<String, Any>): String {
        val json = JSONObject()
        json.put("command", command)
        json.put("parameters", JSONObject(parameters))
        return json.toString()
    }
    
    fun parseCommand(jsonStr: String): Pair<String, Map<String, Any>> {
        val json = JSONObject(jsonStr)
        val command = json.getString("command")
        val params = json.getJSONObject("parameters")
        val paramsMap = mutableMapOf<String, Any>()
        params.keys().forEach { key ->
            paramsMap[key] = params.get(key)
        }
        return Pair(command, paramsMap)
    }
    
    fun setResolution(width: Int, height: Int): String {
        return createCommand("set_resolution", mapOf("width" to width, "height" to height))
    }
    
    fun setFps(fps: Int): String {
        return createCommand("set_fps", mapOf("fps" to fps))
    }
    
    fun switchCamera(camera: String): String {
        return createCommand("switch_camera", mapOf("camera" to camera))
    }
    
    fun setFlash(enabled: Boolean): String {
        return createCommand("set_flash", mapOf("enabled" to enabled))
    }
    
    fun setFocus(mode: String, distance: Float = 0f): String {
        return createCommand("set_focus", mapOf("mode" to mode, "distance" to distance))
    }
    
    fun setBrightness(value: Float): String {
        return createCommand("set_brightness", mapOf("value" to value))
    }
    
    fun setZoom(ratio: Float): String {
        return createCommand("set_zoom", mapOf("ratio" to ratio))
    }
    
    fun setManualMode(enabled: Boolean): String {
        return createCommand("set_manual_mode", mapOf("enabled" to enabled))
    }
    
    fun setManualISO(iso: Int): String {
        return createCommand("set_manual_iso", mapOf("iso" to iso))
    }
    
    fun setManualShutter(nanos: Long): String {
        return createCommand("set_manual_shutter", mapOf("nanos" to nanos))
    }
    
    fun setManualFocus(distance: Float): String {
        return createCommand("set_manual_focus", mapOf("distance" to distance))
    }
    
    fun setWhiteBalance(mode: String, kelvin: Int): String {
        return createCommand("set_white_balance", mapOf("mode" to mode, "kelvin" to kelvin))
    }
    
    fun setTapFocus(x: Float, y: Float, screenWidth: Int, screenHeight: Int): String {
        return createCommand("set_tap_focus", mapOf(
            "x" to x,
            "y" to y,
            "screenWidth" to screenWidth,
            "screenHeight" to screenHeight
        ))
    }
    
    fun getCameraCapabilities(): String {
        return createCommand("get_camera_capabilities", emptyMap())
    }
}

