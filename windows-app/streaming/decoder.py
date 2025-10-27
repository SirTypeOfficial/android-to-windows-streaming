import av
import numpy as np
import logging
from typing import Optional, Callable
import pyaudio

logger = logging.getLogger(__name__)

class VideoDecoder:
    def __init__(self):
        self.codec = av.CodecContext.create('h264', 'r')
        self.on_frame_decoded: Optional[Callable[[np.ndarray], None]] = None
        self.frame_count = 0
        logger.info("Video decoder initialized")
    
    def decode(self, data: bytes, timestamp: int, is_keyframe: bool):
        try:
            logger.debug(f"Decoding frame: size={len(data)}, keyframe={is_keyframe}")
            packet = av.Packet(data)
            frames = self.codec.decode(packet)
            
            for frame in frames:
                img = frame.to_ndarray(format='bgr24')
                self.frame_count += 1
                logger.debug(f"Frame decoded successfully: {frame.width}x{frame.height}, total frames={self.frame_count}")
                if self.on_frame_decoded:
                    self.on_frame_decoded(img)
                else:
                    logger.warning("on_frame_decoded callback is not set")
        except Exception as e:
            logger.error(f"Error decoding video frame: {e}", exc_info=True)
    
    def close(self):
        try:
            self.codec.close()
        except:
            pass

class AudioDecoder:
    def __init__(self):
        self.codec = av.CodecContext.create('aac', 'r')
        
        self.audio = pyaudio.PyAudio()
        self.stream: Optional[pyaudio.Stream] = None
        self.sample_rate = 44100
        self.channels = 2
        
        try:
            self.stream = self.audio.open(
                format=pyaudio.paInt16,
                channels=self.channels,
                rate=self.sample_rate,
                output=True,
                frames_per_buffer=1024
            )
            logger.info("Audio decoder initialized")
        except Exception as e:
            logger.error(f"Failed to initialize audio output: {e}")
    
    def decode(self, data: bytes, timestamp: int):
        if not self.stream:
            return
        
        try:
            packet = av.Packet(data)
            frames = self.codec.decode(packet)
            
            for frame in frames:
                audio_array = frame.to_ndarray()
                audio_bytes = audio_array.tobytes()
                self.stream.write(audio_bytes)
        except Exception as e:
            logger.error(f"Error decoding audio frame: {e}")
    
    def close(self):
        if self.stream:
            self.stream.stop_stream()
            self.stream.close()
        self.audio.terminate()
        try:
            self.codec.close()
        except:
            pass

