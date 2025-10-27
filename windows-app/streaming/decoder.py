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
        logger.info("Video decoder initialized")
    
    def decode(self, data: bytes, timestamp: int, is_keyframe: bool):
        try:
            packet = av.Packet(data)
            frames = self.codec.decode(packet)
            
            for frame in frames:
                img = frame.to_ndarray(format='bgr24')
                if self.on_frame_decoded:
                    self.on_frame_decoded(img)
        except Exception as e:
            logger.error(f"Error decoding video frame: {e}")
    
    def close(self):
        try:
            self.codec.close()
        except:
            pass

class AudioDecoder:
    def __init__(self):
        self.codec = av.CodecContext.create('aac', 'r')
        self.codec.sample_rate = 44100
        self.codec.channels = 2
        
        self.audio = pyaudio.PyAudio()
        self.stream: Optional[pyaudio.Stream] = None
        
        try:
            self.stream = self.audio.open(
                format=pyaudio.paInt16,
                channels=2,
                rate=44100,
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

