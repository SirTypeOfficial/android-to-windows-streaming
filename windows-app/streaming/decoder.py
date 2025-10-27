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
        self.codec_opened = False
        logger.info("Video decoder initialized")
    
    def set_config(self, config_data: bytes):
        """Set codec configuration data (SPS/PPS) from Android encoder"""
        try:
            # Set extradata (SPS/PPS) and open the codec
            self.codec.extradata = config_data
            self.codec.open()
            self.codec_opened = True
            
            logger.info(f"Video codec configured with SPS/PPS: {len(config_data)} bytes")
            logger.info(f"Codec parameters: {self.codec.width}x{self.codec.height}, format={self.codec.pix_fmt}")
        except Exception as e:
            logger.error(f"Failed to set video codec config: {e}", exc_info=True)
    
    def decode(self, data: bytes, timestamp: int, is_keyframe: bool):
        if not self.codec_opened:
            logger.warning("Video codec not yet configured, skipping frame")
            return
        
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
        
        # Audio parameters - will be confirmed from extradata
        self.sample_rate = 44100
        self.channels = 2
        
        self.audio = pyaudio.PyAudio()
        self.stream: Optional[pyaudio.Stream] = None
        self.codec_opened = False
        
        try:
            self.stream = self.audio.open(
                format=pyaudio.paInt16,
                channels=self.channels,
                rate=self.sample_rate,
                output=True,
                frames_per_buffer=1024
            )
            logger.info(f"Audio decoder initialized: {self.sample_rate}Hz, {self.channels} channels")
        except Exception as e:
            logger.error(f"Failed to initialize audio output: {e}")
    
    def set_config(self, config_data: bytes):
        """Set codec configuration data (extradata) from Android encoder"""
        try:
            # Set extradata and open the codec
            # The codec will parse the extradata and configure itself
            self.codec.extradata = config_data
            self.codec.open()
            self.codec_opened = True
            
            # Log the actual codec parameters after opening
            logger.info(f"Audio codec configured with extradata: {len(config_data)} bytes")
            logger.info(f"Codec parameters: {self.codec.sample_rate}Hz, {self.codec.channels} channels, layout={self.codec.layout.name}")
            
            # If codec parameters differ from our PyAudio stream, recreate the stream
            if self.codec.sample_rate != self.sample_rate or self.codec.channels != self.channels:
                logger.warning(f"Audio parameters mismatch - recreating audio stream")
                if self.stream:
                    self.stream.stop_stream()
                    self.stream.close()
                
                self.sample_rate = self.codec.sample_rate
                self.channels = self.codec.channels
                
                self.stream = self.audio.open(
                    format=pyaudio.paInt16,
                    channels=self.channels,
                    rate=self.sample_rate,
                    output=True,
                    frames_per_buffer=1024
                )
                logger.info(f"Audio stream recreated: {self.sample_rate}Hz, {self.channels} channels")
        except Exception as e:
            logger.error(f"Failed to set audio codec config: {e}", exc_info=True)
    
    def decode(self, data: bytes, timestamp: int):
        if not self.stream:
            return
        
        if not self.codec_opened:
            logger.warning("Audio codec not yet configured, skipping frame")
            return
        
        try:
            packet = av.Packet(data)
            frames = self.codec.decode(packet)
            
            for frame in frames:
                # Convert audio to the format expected by PyAudio (int16)
                # AAC decoder typically outputs float or s16 format
                audio_array = frame.to_ndarray(format='s16')
                
                # Ensure the shape is correct (channels, samples) -> (samples * channels,)
                if len(audio_array.shape) > 1:
                    audio_array = audio_array.reshape(-1)
                
                audio_bytes = audio_array.astype(np.int16).tobytes()
                self.stream.write(audio_bytes)
                logger.debug(f"Played audio frame: {len(audio_bytes)} bytes")
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

