"""
مثال استفاده از درایور میکروفون مجازی با Python
این اسکریپت از PyAudio/sounddevice برای ارسال صدا به میکروفون مجازی استفاده می‌کند
"""

import pyaudio
import numpy as np
import wave
import time
import struct

class VirtualMicrophone:
    def __init__(self):
        self.pa = pyaudio.PyAudio()
        self.render_device_index = None
        self.capture_device_index = None
        self._find_devices()
        
    def _find_devices(self):
        """پیدا کردن دستگاه‌های Virtual Microphone"""
        print("\n=== Available Audio Devices ===")
        for i in range(self.pa.get_device_count()):
            info = self.pa.get_device_info_by_index(i)
            print(f"{i}: {info['name']}")
            print(f"   Max Input Channels: {info['maxInputChannels']}")
            print(f"   Max Output Channels: {info['maxOutputChannels']}")
            
            if "Virtual Microphone Input" in info['name']:
                if info['maxOutputChannels'] > 0:
                    self.render_device_index = i
                    print("   *** Found Virtual Microphone Input (Render)")
            
            if "Virtual Microphone" in info['name'] and "Input" not in info['name']:
                if info['maxInputChannels'] > 0:
                    self.capture_device_index = i
                    print("   *** Found Virtual Microphone (Capture)")
        
        print("\n" + "=" * 50)
        
        if self.render_device_index is None:
            print("Warning: Virtual Microphone Input (render) not found")
        else:
            print(f"Using render device index: {self.render_device_index}")
            
        if self.capture_device_index is None:
            print("Warning: Virtual Microphone (capture) not found")
        else:
            print(f"Using capture device index: {self.capture_device_index}")
    
    def play_audio(self, audio_data, sample_rate=48000, channels=2):
        """
        پخش صدا به Virtual Microphone Input
        
        Args:
            audio_data: آرایه numpy شامل داده صوتی
            sample_rate: نرخ نمونه‌برداری
            channels: تعداد کانال‌ها
        """
        if self.render_device_index is None:
            raise Exception("Virtual Microphone Input device not found")
        
        stream = self.pa.open(
            format=pyaudio.paInt16,
            channels=channels,
            rate=sample_rate,
            output=True,
            output_device_index=self.render_device_index
        )
        
        try:
            stream.write(audio_data.tobytes())
        finally:
            stream.stop_stream()
            stream.close()
    
    def record_audio(self, duration=5, sample_rate=48000, channels=2):
        """
        ضبط صدا از Virtual Microphone
        
        Args:
            duration: مدت زمان ضبط (ثانیه)
            sample_rate: نرخ نمونه‌برداری
            channels: تعداد کانال‌ها
            
        Returns:
            آرایه numpy شامل داده ضبط شده
        """
        if self.capture_device_index is None:
            raise Exception("Virtual Microphone device not found")
        
        chunk = 1024
        frames = []
        
        stream = self.pa.open(
            format=pyaudio.paInt16,
            channels=channels,
            rate=sample_rate,
            input=True,
            input_device_index=self.capture_device_index,
            frames_per_buffer=chunk
        )
        
        try:
            print(f"Recording for {duration} seconds...")
            for i in range(0, int(sample_rate / chunk * duration)):
                data = stream.read(chunk)
                frames.append(data)
                if i % 10 == 0:
                    print(".", end="", flush=True)
            print("\nRecording finished")
        finally:
            stream.stop_stream()
            stream.close()
        
        # تبدیل به numpy array
        audio_data = b''.join(frames)
        audio_array = np.frombuffer(audio_data, dtype=np.int16)
        
        return audio_array
    
    def stream_continuous(self, callback, sample_rate=48000, channels=2, chunk=1024):
        """
        استریم مداوم با callback
        
        Args:
            callback: تابعی که داده صوتی تولید می‌کند
            sample_rate: نرخ نمونه‌برداری
            channels: تعداد کانال‌ها
            chunk: اندازه هر chunk
        """
        if self.render_device_index is None:
            raise Exception("Virtual Microphone Input device not found")
        
        stream = self.pa.open(
            format=pyaudio.paInt16,
            channels=channels,
            rate=sample_rate,
            output=True,
            output_device_index=self.render_device_index,
            frames_per_buffer=chunk,
            stream_callback=callback
        )
        
        return stream
    
    def close(self):
        """بستن PyAudio"""
        self.pa.terminate()


def example_sine_wave():
    """مثال ۱: تولید موج سینوسی ساده"""
    print("\n=== Example 1: Sine Wave ===")
    
    mic = VirtualMicrophone()
    
    try:
        # تنظیمات
        sample_rate = 48000
        duration = 3  # ثانیه
        frequency = 440  # Hz (نت A)
        
        # تولید موج سینوسی
        t = np.linspace(0, duration, int(sample_rate * duration))
        signal = np.sin(2 * np.pi * frequency * t)
        
        # تبدیل به stereo
        audio_data = np.column_stack([signal, signal])
        audio_data = (audio_data * 32767).astype(np.int16)
        
        print(f"Playing {frequency} Hz sine wave for {duration} seconds...")
        mic.play_audio(audio_data, sample_rate, 2)
        print("Done!")
        
    finally:
        mic.close()


def example_wave_file():
    """مثال ۲: پخش فایل WAV"""
    print("\n=== Example 2: Play WAV File ===")
    
    wave_file = input("Enter WAV file path: ")
    
    mic = VirtualMicrophone()
    
    try:
        # خواندن فایل WAV
        with wave.open(wave_file, 'rb') as wf:
            sample_rate = wf.getframerate()
            channels = wf.getnchannels()
            frames = wf.readframes(wf.getnframes())
        
        audio_data = np.frombuffer(frames, dtype=np.int16)
        
        print(f"Playing WAV file ({sample_rate} Hz, {channels} channels)...")
        mic.play_audio(audio_data, sample_rate, channels)
        print("Done!")
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        mic.close()


def example_loopback_test():
    """مثال ۳: تست Loopback"""
    print("\n=== Example 3: Loopback Test ===")
    
    mic = VirtualMicrophone()
    
    try:
        # تولید یک سیگنال تست
        sample_rate = 48000
        duration = 2
        frequency = 1000  # Hz
        
        t = np.linspace(0, duration, int(sample_rate * duration))
        signal = np.sin(2 * np.pi * frequency * t)
        audio_data = np.column_stack([signal, signal])
        audio_data = (audio_data * 32767).astype(np.int16)
        
        print("Step 1: Playing test signal to Virtual Microphone Input...")
        mic.play_audio(audio_data, sample_rate, 2)
        
        print("Step 2: Recording from Virtual Microphone...")
        time.sleep(0.5)  # کمی صبر کنید
        
        recorded = mic.record_audio(duration=2, sample_rate=sample_rate)
        
        # ذخیره صدای ضبط شده
        output_file = "loopback_test.wav"
        with wave.open(output_file, 'wb') as wf:
            wf.setnchannels(2)
            wf.setsampwidth(2)  # 16-bit
            wf.setframerate(sample_rate)
            wf.writeframes(recorded.tobytes())
        
        print(f"Recorded audio saved to {output_file}")
        
    finally:
        mic.close()


def example_live_stream():
    """مثال ۴: استریم زنده با صدای تولیدی"""
    print("\n=== Example 4: Live Streaming ===")
    
    mic = VirtualMicrophone()
    
    # متغیرهای global برای callback
    phase = [0]
    frequency = [440]
    
    def audio_callback(in_data, frame_count, time_info, status):
        # تولید موج سینوسی با فرکانس متغیر
        sample_rate = 48000
        t = np.arange(frame_count) / sample_rate
        
        # تغییر آهسته فرکانس
        frequency[0] += 0.5
        if frequency[0] > 880:
            frequency[0] = 440
        
        signal = np.sin(2 * np.pi * frequency[0] * (t + phase[0]))
        phase[0] += frame_count / sample_rate
        
        # Stereo
        audio_data = np.column_stack([signal, signal])
        audio_data = (audio_data * 32767).astype(np.int16)
        
        return (audio_data.tobytes(), pyaudio.paContinue)
    
    try:
        print("Streaming audio... Press Ctrl+C to stop")
        stream = mic.stream_continuous(audio_callback)
        stream.start_stream()
        
        while stream.is_active():
            time.sleep(0.1)
            
    except KeyboardInterrupt:
        print("\nStopped by user")
    finally:
        stream.stop_stream()
        stream.close()
        mic.close()


def example_mic_forward():
    """مثال ۵: فوروارد کردن میکروفون واقعی به میکروفون مجازی"""
    print("\n=== Example 5: Real Microphone Forward ===")
    
    mic = VirtualMicrophone()
    
    # پیدا کردن میکروفون واقعی
    real_mic_index = None
    for i in range(mic.pa.get_device_count()):
        info = mic.pa.get_device_info_by_index(i)
        if info['maxInputChannels'] > 0 and "Virtual" not in info['name']:
            real_mic_index = i
            print(f"Using real microphone: {info['name']}")
            break
    
    if real_mic_index is None:
        print("No real microphone found")
        mic.close()
        return
    
    try:
        chunk = 1024
        sample_rate = 48000
        
        # باز کردن stream ورودی (میکروفون واقعی)
        input_stream = mic.pa.open(
            format=pyaudio.paInt16,
            channels=2,
            rate=sample_rate,
            input=True,
            input_device_index=real_mic_index,
            frames_per_buffer=chunk
        )
        
        # باز کردن stream خروجی (میکروفون مجازی)
        output_stream = mic.pa.open(
            format=pyaudio.paInt16,
            channels=2,
            rate=sample_rate,
            output=True,
            output_device_index=mic.render_device_index,
            frames_per_buffer=chunk
        )
        
        print("Forwarding microphone... Press Ctrl+C to stop")
        while True:
            data = input_stream.read(chunk)
            output_stream.write(data)
            
    except KeyboardInterrupt:
        print("\nStopped by user")
    finally:
        input_stream.stop_stream()
        input_stream.close()
        output_stream.stop_stream()
        output_stream.close()
        mic.close()


def example_text_to_speech():
    """مثال ۶: تبدیل متن به گفتار (نیاز به pyttsx3)"""
    print("\n=== Example 6: Text-to-Speech ===")
    
    try:
        import pyttsx3
    except ImportError:
        print("Error: pyttsx3 not installed. Install with: pip install pyttsx3")
        return
    
    text = input("Enter text to speak: ")
    
    mic = VirtualMicrophone()
    
    try:
        engine = pyttsx3.init()
        
        # تنظیمات صدا
        engine.setProperty('rate', 150)  # سرعت
        engine.setProperty('volume', 1.0)  # حجم
        
        # ذخیره به فایل موقت
        temp_file = "temp_speech.wav"
        engine.save_to_file(text, temp_file)
        engine.runAndWait()
        
        # پخش فایل
        with wave.open(temp_file, 'rb') as wf:
            sample_rate = wf.getframerate()
            channels = wf.getnchannels()
            frames = wf.readframes(wf.getnframes())
        
        audio_data = np.frombuffer(frames, dtype=np.int16)
        
        print("Playing speech...")
        mic.play_audio(audio_data, sample_rate, channels)
        
        # حذف فایل موقت
        import os
        os.remove(temp_file)
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        mic.close()


def main():
    """منوی اصلی"""
    print("Virtual Microphone Examples")
    print("=" * 50)
    print("1. Play Sine Wave")
    print("2. Play WAV File")
    print("3. Loopback Test")
    print("4. Live Streaming")
    print("5. Real Microphone Forward")
    print("6. Text-to-Speech")
    print("0. Exit")
    
    choice = input("\nEnter your choice: ")
    
    if choice == "1":
        example_sine_wave()
    elif choice == "2":
        example_wave_file()
    elif choice == "3":
        example_loopback_test()
    elif choice == "4":
        example_live_stream()
    elif choice == "5":
        example_mic_forward()
    elif choice == "6":
        example_text_to_speech()
    elif choice == "0":
        print("Goodbye!")
    else:
        print("Invalid choice")


if __name__ == "__main__":
    main()

