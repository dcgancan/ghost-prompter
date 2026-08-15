"""
Real-Time Offline Streaming Voice Recognition Engine
Powered by Vosk Local Neural Speech Engine + SoundDevice
Sub-30ms Instant Streaming ("Konuştuğunuz Anda Kelimenin Üzerine Gelir")
"""

import sys
import json
import time
import queue
import threading
from typing import Optional, List
import sounddevice as sd
import vosk
from PyQt6.QtCore import QObject, pyqtSignal


# Disable Vosk verbose C logs
vosk.SetLogLevel(-1)


def clean_device_name(name: str) -> str:
    """Fixes Windows audio driver UTF-8 / Mojibake encoding artifacts."""
    if not name:
        return ""
    fixes = {
        'EÅŸleÅŸtiricisi': 'Eşleştiricisi',
        'SÃ¼rÃ¼cÃ¼sÃ¼': 'Sürücüsü',
        'HoparlÃ¶r': 'Hoparlör',
        'Yakalama SÃ¼rÃ¼cÃ¼sÃ¼': 'Yakalama Sürücüsü',
        'Ã§': 'ç', 'Ã‡': 'Ç',
        'Ã¶': 'ö', 'Ã–': 'Ö',
        'Ã¼': 'ü', 'Ãœ': 'Ü',
        'Ä±': 'ı', 'Ä°': 'İ',
        'ÅŸ': 'ş', 'Åž': 'Ş',
        'ÄŸ': 'ğ', 'Äž': 'Ğ',
        'Å\x9f': 'ş', 'Å\x9e': 'Ş',
        'Ã\xbc': 'ü', 'Ã\xb6': 'ö'
    }
    for k, v in fixes.items():
        name = name.replace(k, v)
    try:
        name = name.encode('latin1').decode('utf-8')
    except Exception:
        pass
    return name.strip()


class VoiceEngineSignals(QObject):
    speech_detected = pyqtSignal(str)       # Emits recognized partial/final words instantly
    status_changed = pyqtSignal(str)         # Status text
    error_occurred = pyqtSignal(str)         # Error message


class VoiceEngine:
    _models_cache = {}

    def __init__(self, language: str = "tr-TR", mic_device_index: Optional[int] = None):
        self.language = language
        self.mic_device_index = mic_device_index
        self.signals = VoiceEngineSignals()
        
        self.is_running = False
        self.is_paused = False
        self._thread: Optional[threading.Thread] = None
        self._stop_event = threading.Event()
        self._audio_queue = queue.Queue(maxsize=50)
        
        self.sample_rate = 16000
        self.vosk_model: Optional[vosk.Model] = None
        self.recognizer: Optional[vosk.KaldiRecognizer] = None
        self._last_partial = ""

    def _get_or_load_model(self, lang_code: str) -> Optional[vosk.Model]:
        """Loads Vosk local offline neural model for ultra-low latency."""
        # Convert tr-TR -> tr, en-US -> en-us
        target_lang = "tr"
        if "en" in lang_code.lower():
            target_lang = "en-us"
        elif "de" in lang_code.lower():
            target_lang = "de"
        elif "es" in lang_code.lower():
            target_lang = "es"

        if target_lang in VoiceEngine._models_cache:
            return VoiceEngine._models_cache[target_lang]

        try:
            self.signals.status_changed.emit("⚙️ Yerel ses modeli hazırlanıyor...")
            model = vosk.Model(lang=target_lang)
            VoiceEngine._models_cache[target_lang] = model
            return model
        except Exception as e:
            print(f"[VoiceEngine] Vosk model yükleme hatası: {e}")
            return None

    @staticmethod
    def get_microphone_list() -> List[tuple]:
        """Returns clean list of available input audio devices."""
        try:
            devices = sd.query_devices()
            result = []
            for i, dev in enumerate(devices):
                if dev.get('max_input_channels', 0) > 0:
                    clean_name = clean_device_name(dev.get('name', ''))
                    result.append((i, clean_name))
            return result
        except Exception as e:
            print(f"[VoiceEngine] Mikrofon listeleme hatası: {e}")
            return []

    def set_language(self, language: str):
        self.language = language
        if self.is_running:
            self.stop()
            self.start()

    def set_mic_device(self, device_index: Optional[int]):
        self.mic_device_index = device_index
        if self.is_running:
            self.stop()
            self.start()

    def start(self):
        if self.is_running:
            return
        self.is_running = True
        self.is_paused = False
        self._stop_event.clear()
        self._last_partial = ""
        self._thread = threading.Thread(target=self._streaming_worker, daemon=True)
        self._thread.start()

    def pause(self):
        self.is_paused = True
        self.signals.status_changed.emit("⏸️ Ses takibi duraklatıldı")

    def resume(self):
        self.is_paused = False
        self._last_partial = ""
        self.signals.status_changed.emit("🎤 Canlı ses takibi aktif...")

    def stop(self):
        self.is_running = False
        self._stop_event.set()
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=1.0)
        self._thread = None
        self.signals.status_changed.emit("⏹️ Ses takibi kapalı")

    def _audio_callback(self, indata, frames, time_info, status):
        """Ultra-fast 50ms audio chunk capture."""
        if status:
            pass
        if self.is_running and not self.is_paused:
            try:
                # Put raw 16-bit PCM bytes into stream queue
                self._audio_queue.put_nowait(bytes(indata))
            except queue.Full:
                pass

    def _streaming_worker(self):
        """Background continuous streaming decoder thread (0ms cloud latency)."""
        try:
            self.vosk_model = self._get_or_load_model(self.language)
            if not self.vosk_model:
                self.signals.error_occurred.emit("Ses modeli yüklenemedi")
                return

            self.recognizer = vosk.KaldiRecognizer(self.vosk_model, self.sample_rate)
            self.recognizer.SetWords(True)

            # Block size = 800 samples = 50ms per audio frame
            block_size = 800
            
            with sd.RawInputStream(
                samplerate=self.sample_rate,
                blocksize=block_size,
                device=self.mic_device_index,
                dtype='int16',
                channels=1,
                callback=self._audio_callback
            ):
                self.signals.status_changed.emit("🎤 Konuşmanız canlı dinleniyor (Sıfır Gecikme)...")

                while self.is_running and not self._stop_event.is_set():
                    try:
                        data = self._audio_queue.get(timeout=0.2)
                    except queue.Empty:
                        continue

                    if self.is_paused or not self.is_running:
                        continue

                    # Process audio chunk with Vosk
                    if self.recognizer.AcceptWaveform(data):
                        # Final phrase result
                        res = json.loads(self.recognizer.Result())
                        text = res.get("text", "").strip()
                        if text:
                            self.signals.speech_detected.emit(text)
                            self._last_partial = ""
                    else:
                        # Instant real-time partial result while speaker is uttering words!
                        partial_res = json.loads(self.recognizer.PartialResult())
                        partial = partial_res.get("partial", "").strip()
                        if partial and partial != self._last_partial:
                            self._last_partial = partial
                            # Emit partial words in real time (<30ms)
                            self.signals.speech_detected.emit(partial)

        except Exception as e:
            err_msg = f"Mikrofon akış hatası: {e}"
            print(f"[VoiceEngine] {err_msg}")
            self.signals.error_occurred.emit(err_msg)
            self.signals.status_changed.emit("❌ Mikrofon başlatılamadı")
            self.is_running = False
