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
            # If codec is already open, close and recreate it
            if self.codec_opened:
                logger.info("Video codec already opened, recreating...")
                try:
                    self.codec.close()
                except:
                    pass
                self.codec = av.CodecContext.create('h264', 'r')
                self.codec_opened = False
            
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
    def __init__(self, virtual_microphone=None):
        self.codec = av.CodecContext.create('aac', 'r')
        
        # Audio parameters
        self.sample_rate = 48000
        self.channels = 2
        self.codec_opened = False
        
        # Virtual Microphone
        self.virtual_microphone = virtual_microphone
        self.use_virtual_mic = False
        
        # Fallback: PyAudio stream
        self.audio = None
        self.stream: Optional[pyaudio.Stream] = None
        
        if self.virtual_microphone:
            try:
                if self.virtual_microphone.open():
                    self.use_virtual_mic = True
                    logger.info("✓ Audio decoder متصل به VirtuCore Microphone")
                else:
                    logger.warning("استفاده از PyAudio به عنوان fallback")
                    self._init_pyaudio()
            except Exception as e:
                logger.error(f"خطا در اتصال به VirtuCore Microphone: {e}")
                self._init_pyaudio()
        else:
            self._init_pyaudio()
    
    def _init_pyaudio(self):
        """راه‌اندازی PyAudio به عنوان fallback"""
        try:
            self.audio = pyaudio.PyAudio()
            self.stream = self.audio.open(
                format=pyaudio.paInt16,
                channels=self.channels,
                rate=self.sample_rate,
                output=True,
                frames_per_buffer=1024
            )
            logger.info(f"Audio decoder با PyAudio: {self.sample_rate}Hz, {self.channels} channels")
        except Exception as e:
            logger.error(f"Failed to initialize audio output: {e}")
    
    def set_config(self, config_data: bytes):
        """Set codec configuration data (extradata) from Android encoder"""
        try:
            # Parse config packet: [sample_rate (4 bytes)][channels (4 bytes)][extradata]
            if len(config_data) < 8:
                logger.error(f"Audio config data too short: {len(config_data)} bytes")
                return
            
            import struct
            sample_rate, channels = struct.unpack('>II', config_data[:8])
            extradata = config_data[8:]
            
            logger.info(f"Audio config received: {sample_rate}Hz, {channels} channels, extradata={len(extradata)} bytes")
            
            # If codec is already open, close and recreate it
            if self.codec_opened:
                logger.info("Audio codec already opened, recreating...")
                try:
                    self.codec.close()
                except:
                    pass
                self.codec = av.CodecContext.create('aac', 'r')
                self.codec_opened = False
            
            # Set extradata and open the codec
            self.codec.extradata = extradata if len(extradata) > 0 else None
            self.codec.open()
            self.codec_opened = True
            
            # Update our parameters
            self.sample_rate = sample_rate
            self.channels = channels
            
            # Recreate the audio stream if using PyAudio
            if not self.use_virtual_mic and self.audio:
                if self.stream:
                    self.stream.stop_stream()
                    self.stream.close()
                
                self.stream = self.audio.open(
                    format=pyaudio.paInt16,
                    channels=self.channels,
                    rate=self.sample_rate,
                    output=True,
                    frames_per_buffer=1024
                )
            
            logger.info(f"Audio codec configured: {self.sample_rate}Hz, {self.channels} channels")
        except Exception as e:
            logger.error(f"Failed to set audio codec config: {e}", exc_info=True)
    
    def decode(self, data: bytes, timestamp: int):
        if not self.codec_opened:
            logger.warning("Audio codec not yet configured, skipping frame")
            return
        
        # بررسی اینکه آیا output در دسترس است
        if not self.use_virtual_mic and not self.stream:
            return
        
        try:
            packet = av.Packet(data)
            frames = self.codec.decode(packet)
            
            for frame in frames:
                # Convert audio to numpy array
                audio_array = frame.to_ndarray()
                
                # Ensure the shape is correct (channels, samples) -> (samples * channels,)
                if len(audio_array.shape) > 1:
                    audio_array = audio_array.reshape(-1)
                
                # Convert to int16 if not already
                if audio_array.dtype != np.int16:
                    if audio_array.dtype in [np.float32, np.float64]:
                        audio_array = (audio_array * 32767).astype(np.int16)
                    else:
                        audio_array = audio_array.astype(np.int16)
                
                # ارسال به virtual microphone یا PyAudio
                if self.use_virtual_mic:
                    self.virtual_microphone.send_audio(audio_array)
                    logger.debug(f"Sent audio to VirtuCore Mic: {len(audio_array)} samples")
                elif self.stream:
                    audio_bytes = audio_array.tobytes()
                    self.stream.write(audio_bytes)
                    logger.debug(f"Played audio frame: {len(audio_bytes)} bytes")
                    
        except Exception as e:
            logger.error(f"Error decoding audio frame: {e}", exc_info=True)
    
    def close(self):
        if self.virtual_microphone:
            try:
                self.virtual_microphone.close()
            except:
                pass
        
        if self.stream:
            try:
                self.stream.stop_stream()
                self.stream.close()
            except:
                pass
        
        if self.audio:
            try:
                self.audio.terminate()
            except:
                pass
        
        try:
            self.codec.close()
        except:
            pass

