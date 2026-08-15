"""
Voice Recognition Engine for Real-Time Prompter Following
Listens to the microphone in a non-blocking background thread,
performs fast speech-to-text, and emits recognized phrases for word tracking.
"""

import time
import queue
import threading
from typing import Optional, List
import speech_recognition as sr
from PyQt6.QtCore import QObject, pyqtSignal


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
    speech_detected = pyqtSignal(str)     # Emits recognized phrase
    mic_level = pyqtSignal(float)          # Emits 0.0 - 1.0 audio volume level
    status_changed = pyqtSignal(str)       # "Dinleniyor...", "Bağlandı", etc.
    error_occurred = pyqtSignal(str)       # Error message


class VoiceEngine:
    def __init__(self, language: str = "tr-TR", mic_device_index: Optional[int] = None):
        self.language = language
        self.mic_device_index = mic_device_index
        self.signals = VoiceEngineSignals()
        self.is_running = False
        self.is_paused = False
        self._thread: Optional[threading.Thread] = None
        self._stop_event = threading.Event()
        
        self.recognizer = sr.Recognizer()
        # Optimize for low latency speech tracking
        self.recognizer.energy_threshold = 300
        self.recognizer.dynamic_energy_threshold = True
        self.recognizer.pause_threshold = 0.5        # Pause time before phrase is sent
        self.recognizer.phrase_threshold = 0.2
        self.recognizer.non_speaking_duration = 0.3

    @staticmethod
    def get_microphone_list() -> List[tuple]:
        """Returns list of (index, cleaned_device_name)."""
        try:
            mics = sr.Microphone.list_microphone_names()
            result = []
            for i, raw_name in enumerate(mics):
                clean_name = clean_device_name(raw_name)
                result.append((i, clean_name))
            return result
        except Exception as e:
            print(f"[VoiceEngine] Mikrofon listesi hatası: {e}")
            return []

    def set_language(self, language: str):
        self.language = language

    def set_mic_device(self, device_index: Optional[int]):
        self.mic_device_index = device_index
        if self.is_running:
            self.stop()
            self.start()

    def start(self):
        """Starts background microphone listener."""
        if self.is_running:
            return
        self.is_running = True
        self.is_paused = False
        self._stop_event.clear()
        self._thread = threading.Thread(target=self._listen_loop, daemon=True)
        self._thread.start()
        self.signals.status_changed.emit("🎤 Mikrofon dinleniyor...")

    def pause(self):
        self.is_paused = True
        self.signals.status_changed.emit("⏸️ Ses takibi duraklatıldı")

    def resume(self):
        self.is_paused = False
        self.signals.status_changed.emit("🎤 Mikrofon dinleniyor...")

    def stop(self):
        """Stops background thread."""
        self.is_running = False
        self._stop_event.set()
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=1.0)
        self._thread = None
        self.signals.status_changed.emit("⏹️ Ses takibi kapalı")

    def _listen_loop(self):
        """Continuous background listening loop."""
        try:
            with sr.Microphone(device_index=self.mic_device_index) as source:
                # Quick ambient noise calibration
                try:
                    self.signals.status_changed.emit("⚙️ Ortam sesi ayarlanıyor...")
                    self.recognizer.adjust_for_ambient_noise(source, duration=0.8)
                except Exception:
                    pass

                self.signals.status_changed.emit("🎤 Konuşmanız dinleniyor...")

                while self.is_running and not self._stop_event.is_set():
                    if self.is_paused:
                        time.sleep(0.1)
                        continue

                    try:
                        # Listen for short spoken phrase
                        audio = self.recognizer.listen(
                            source,
                            timeout=2.0,
                            phrase_time_limit=4.0
                        )
                        
                        if self.is_paused or not self.is_running:
                            continue

                        # Recognize speech via Google's free streaming speech API (fast & multilingual)
                        try:
                            text = self.recognizer.recognize_google(
                                audio,
                                language=self.language
                            )
                            if text and text.strip():
                                self.signals.speech_detected.emit(text.strip())
                        except sr.UnknownValueError:
                            # Audio not understood / background silence
                            pass
                        except sr.RequestError as req_err:
                            self.signals.error_occurred.emit(f"Bağlantı hatası: {req_err}")
                            time.sleep(1.0)

                    except sr.WaitTimeoutError:
                        # Normal timeout when user is silent
                        pass
                    except Exception as e:
                        if self.is_running:
                            print(f"[VoiceEngine] Dinleme hatası: {e}")
                            time.sleep(0.2)

        except Exception as e:
            err_msg = f"Mikrofon başlatılamadı: {e}"
            print(f"[VoiceEngine] {err_msg}")
            self.signals.error_occurred.emit(err_msg)
            self.signals.status_changed.emit("❌ Mikrofon hatası")
            self.is_running = False
