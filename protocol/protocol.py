import struct
import json
from enum import IntEnum
from dataclasses import dataclass
from typing import Optional

MAGIC_NUMBER = 0x4157534D

class PacketType(IntEnum):
    HANDSHAKE_REQUEST = 0x01
    HANDSHAKE_RESPONSE = 0x02
    VIDEO_FRAME = 0x10
    AUDIO_FRAME = 0x11
    CONTROL_COMMAND = 0x20
    CONTROL_RESPONSE = 0x21
    KEEPALIVE = 0x30
    ERROR = 0xFF

@dataclass
class PacketHeader:
    magic: int
    packet_type: PacketType
    payload_size: int
    timestamp: int
    sequence_number: int
    
    HEADER_SIZE = 21
    
    def to_bytes(self) -> bytes:
        return struct.pack(
            '>IBIQI',
            self.magic,
            self.packet_type,
            self.payload_size,
            self.timestamp,
            self.sequence_number
        )
    
    @staticmethod
    def from_bytes(data: bytes) -> 'PacketHeader':
        magic, packet_type, payload_size, timestamp, seq_num = struct.unpack('>IBIQI', data)
        return PacketHeader(
            magic=magic,
            packet_type=PacketType(packet_type),
            payload_size=payload_size,
            timestamp=timestamp,
            sequence_number=seq_num
        )

class Packet:
    def __init__(self, packet_type: PacketType, payload: bytes, timestamp: int = 0, seq_num: int = 0):
        self.header = PacketHeader(
            magic=MAGIC_NUMBER,
            packet_type=packet_type,
            payload_size=len(payload),
            timestamp=timestamp,
            sequence_number=seq_num
        )
        self.payload = payload
    
    def to_bytes(self) -> bytes:
        return self.header.to_bytes() + self.payload
    
    @staticmethod
    def from_bytes(data: bytes) -> 'Packet':
        header = PacketHeader.from_bytes(data[:PacketHeader.HEADER_SIZE])
        payload = data[PacketHeader.HEADER_SIZE:PacketHeader.HEADER_SIZE + header.payload_size]
        packet = Packet(header.packet_type, payload)
        packet.header = header
        return packet

class ControlCommand:
    @staticmethod
    def create_command(command: str, parameters: dict) -> str:
        return json.dumps({
            "command": command,
            "parameters": parameters
        })
    
    @staticmethod
    def parse_command(json_str: str) -> tuple:
        data = json.loads(json_str)
        return data["command"], data["parameters"]
    
    @staticmethod
    def set_resolution(width: int, height: int) -> str:
        return ControlCommand.create_command("set_resolution", {"width": width, "height": height})
    
    @staticmethod
    def set_fps(fps: int) -> str:
        return ControlCommand.create_command("set_fps", {"fps": fps})
    
    @staticmethod
    def switch_camera(camera: str) -> str:
        return ControlCommand.create_command("switch_camera", {"camera": camera})
    
    @staticmethod
    def set_flash(enabled: bool) -> str:
        return ControlCommand.create_command("set_flash", {"enabled": enabled})
    
    @staticmethod
    def set_focus(mode: str, distance: float = 0.0) -> str:
        return ControlCommand.create_command("set_focus", {"mode": mode, "distance": distance})
    
    @staticmethod
    def set_brightness(value: float) -> str:
        return ControlCommand.create_command("set_brightness", {"value": value})

