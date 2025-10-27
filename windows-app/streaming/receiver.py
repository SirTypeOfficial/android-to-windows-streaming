import logging
from typing import Optional, Callable
from threading import Thread
from protocol import Packet, PacketType, PacketHeader

logger = logging.getLogger(__name__)

class StreamReceiver:
    def __init__(self, connection_manager):
        self.connection_manager = connection_manager
        self.is_receiving = False
        self.receive_thread: Optional[Thread] = None
        
        self.on_video_frame: Optional[Callable[[bytes, int, bool], None]] = None
        self.on_audio_frame: Optional[Callable[[bytes, int], None]] = None
        self.on_control_response: Optional[Callable[[str], None]] = None
        
    def start(self):
        if self.is_receiving:
            return
        
        self.is_receiving = True
        self.receive_thread = Thread(target=self._receive_loop, daemon=True)
        self.receive_thread.start()
        logger.info("Stream receiver started")
    
    def stop(self):
        self.is_receiving = False
        if self.receive_thread:
            self.receive_thread.join(timeout=2.0)
        logger.info("Stream receiver stopped")
    
    def _receive_loop(self):
        logger.info("Receive loop started")
        while self.is_receiving:
            try:
                header_data = self.connection_manager.receive_data(PacketHeader.HEADER_SIZE)
                if not header_data:
                    logger.warning("No header data received, breaking loop")
                    break
                
                header = PacketHeader.from_bytes(header_data)
                logger.debug(f"Received packet: type={header.packet_type}, size={header.payload_size}")
                
                payload_data = self.connection_manager.receive_data(header.payload_size)
                if not payload_data:
                    logger.warning("No payload data received, breaking loop")
                    break
                
                self._handle_packet(header, payload_data)
                
            except Exception as e:
                logger.error(f"Error in receive loop: {e}", exc_info=True)
                break
        
        self.is_receiving = False
        logger.info("Receive loop stopped")
    
    def _handle_packet(self, header: PacketHeader, payload: bytes):
        try:
            if header.packet_type == PacketType.VIDEO_FRAME:
                logger.debug(f"Handling video frame: size={len(payload)}")
                if self.on_video_frame:
                    is_keyframe = len(payload) > 4 and payload[4] == 0x67
                    self.on_video_frame(payload, header.timestamp, is_keyframe)
                else:
                    logger.warning("on_video_frame callback is not set")
            
            elif header.packet_type == PacketType.AUDIO_FRAME:
                logger.debug(f"Handling audio frame: size={len(payload)}")
                if self.on_audio_frame:
                    self.on_audio_frame(payload, header.timestamp)
            
            elif header.packet_type == PacketType.CONTROL_RESPONSE:
                if self.on_control_response:
                    response = payload.decode('utf-8')
                    self.on_control_response(response)
            
            elif header.packet_type == PacketType.KEEPALIVE:
                logger.debug("Received keepalive packet")
            
        except Exception as e:
            logger.error(f"Error handling packet: {e}", exc_info=True)

