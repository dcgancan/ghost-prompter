"""
Main Prompter Overlay Window
Ulusoy Digital - GhostPrompter
100% Transparent Canvas + Click-Through (F8) + High-Contrast Floating Text
"""

import sys
import webbrowser
from PyQt6.QtCore import Qt, QPoint, pyqtSignal, QSize
from PyQt6.QtGui import QIcon, QFont, QColor, QCursor, QGuiApplication
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QSlider, QFrame, QGraphicsDropShadowEffect,
    QSizeGrip, QToolTip
)

from prompter_view import PrompterCanvas
from word_matcher import WordMatcher
from voice_engine import VoiceEngine
import stealth


class PrompterWindow(QMainWindow):
    open_editor_requested = pyqtSignal()

    def __init__(self, matcher: WordMatcher, voice_engine: VoiceEngine):
        super().__init__()
        self.matcher = matcher
        self.voice_engine = voice_engine
        
        # Window Configuration
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.SubWindow
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setMinimumSize(380, 160)
        self.resize(860, 480)

        # State flags
        self.is_stealth_active = True
        self.is_click_through = False
        self.is_always_on_top = True
        self.is_top_banner_mode = False
        
        self.saved_normal_geo = None
        self.drag_position = QPoint()
        self.is_dragging = False

        # Setup UI
        self._init_ui()
        self._connect_signals()

    def _init_ui(self):
        self.central_widget = QWidget(self)
        self.central_layout = QVBoxLayout(self.central_widget)
        self.central_layout.setContentsMargins(6, 6, 6, 6)
        self.central_layout.setSpacing(0)
        self.setCentralWidget(self.central_widget)

        # Outer Glass Card with Border
        # Varsayılan olarak tamamen şeffaf arka plan
        self.card_frame = QFrame(self.central_widget)
        self.card_frame.setObjectName("cardFrame")
        self.card_frame.setStyleSheet("""
            QFrame#cardFrame {
                background-color: rgba(10, 14, 22, 0.25);
                border: 1px solid rgba(0, 240, 255, 0.35);
                border-radius: 12px;
            }
        """)

        self.card_layout = QVBoxLayout(self.card_frame)
        self.card_layout.setContentsMargins(0, 0, 0, 0)
        self.card_layout.setSpacing(0)

        # 1. Top Header Bar (Hafif Yarı Saydam Kontroller)
        self.header_bar = QWidget(self.card_frame)
        self.header_bar.setFixedHeight(42)
        self.header_bar.setStyleSheet("""
            QWidget {
                background-color: rgba(15, 20, 30, 0.75);
                border-top-left-radius: 12px;
                border-top-right-radius: 12px;
                border-bottom: 1px solid rgba(0, 240, 255, 0.2);
            }
        """)
        self.header_layout = QHBoxLayout(self.header_bar)
        self.header_layout.setContentsMargins(12, 0, 8, 0)
        self.header_layout.setSpacing(8)

        # Brand Button
        self.brand_btn = QPushButton("🚀 ULUSOY DIGITAL", self.header_bar)
        self.brand_btn.setToolTip("ulusoydigital.com - Muzaffer Ulusoy\nWeb sitesini açmak için tıklayın")
        self.brand_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.brand_btn.setStyleSheet("""
            QPushButton {
                background: transparent;
                color: #00F0FF;
                font-weight: 800;
                font-size: 12px;
                border: none;
            }
            QPushButton:hover {
                color: #55F7FF;
            }
        """)
        self.brand_btn.clicked.connect(lambda: webbrowser.open("https://ulusoydigital.com"))

        # Ghost Mode Badge
        self.stealth_badge = QPushButton("🛡️ Kayıtta Gizli", self.header_bar)
        self.stealth_badge.setToolTip("OBS, Loom ve Ekran Kaydedicilerde bu pencere görünmez!")
        self.stealth_badge.setCursor(Qt.CursorShape.PointingHandCursor)
        self.stealth_badge.setStyleSheet("""
            QPushButton {
                background-color: rgba(0, 240, 255, 0.2);
                color: #00F0FF;
                border: 1px solid rgba(0, 240, 255, 0.45);
                border-radius: 6px;
                padding: 3px 8px;
                font-size: 11px;
                font-weight: bold;
            }
        """)
        self.stealth_badge.clicked.connect(self.toggle_stealth_mode)

        # Click-Through Mode Toggle Badge (F8)
        self.click_through_badge = QPushButton("🖱️ Arkaya Tıkla (F8)", self.header_bar)
        self.click_through_badge.setToolTip("Tıklama Geçirgenliği (F8 Tuşu):\nAktif edildiğinde fareniz doğrudan arkadaki tarayıcıya/uygulamaya tıklar.\nPrompter üstte şeffaf kalır ve sesinizi takip eder!")
        self.click_through_badge.setCursor(Qt.CursorShape.PointingHandCursor)
        self.click_through_badge.setStyleSheet("""
            QPushButton {
                background-color: rgba(255, 255, 255, 0.1);
                color: #E6EDF3;
                border: 1px solid rgba(255, 255, 255, 0.25);
                border-radius: 6px;
                padding: 3px 8px;
                font-size: 11px;
                font-weight: bold;
            }
        """)
        self.click_through_badge.clicked.connect(self.toggle_click_through)

        # Slim Top Banner Preset Button
        self.btn_top_banner = QPushButton("📏 Kamera Çubuğu", self.header_bar)
        self.btn_top_banner.setToolTip("Prompterı kameranın tam altına ince yatay şerit yapar.\nBöylece ekranın altındaki tüm buton ve uygulamaları rahatça görürsünüz!")
        self.btn_top_banner.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_top_banner.setStyleSheet("""
            QPushButton {
                background-color: rgba(163, 113, 247, 0.2);
                color: #D2A8FF;
                border: 1px solid rgba(163, 113, 247, 0.45);
                border-radius: 6px;
                padding: 3px 8px;
                font-size: 11px;
                font-weight: bold;
            }
        """)
        self.btn_top_banner.clicked.connect(self.toggle_top_banner_mode)

        # Live Status Label
        self.status_lbl = QLabel("🎤 Konuşmanız bekleniyor...", self.header_bar)
        self.status_lbl.setStyleSheet("color: #8B949E; font-size: 11px;")

        # Controls
        self.btn_editor = self._create_icon_btn("📝", "Metin Düzenleyici ve Ayarlar Paneli", self._open_editor)
        self.btn_pin = self._create_icon_btn("📌", "Her Zaman Üstte Sabitle", self.toggle_always_on_top)
        self.btn_min = self._create_icon_btn("🗕", "Simge Durumuna Küçült", self.showMinimized)
        self.btn_close = self._create_icon_btn("✕", "Kapat", self.close, is_close=True)

        self.header_layout.addWidget(self.brand_btn)
        self.header_layout.addWidget(self.stealth_badge)
        self.header_layout.addWidget(self.click_through_badge)
        self.header_layout.addWidget(self.btn_top_banner)
        self.header_layout.addWidget(self.status_lbl)
        self.header_layout.addStretch()
        self.header_layout.addWidget(self.btn_editor)
        self.header_layout.addWidget(self.btn_pin)
        self.header_layout.addWidget(self.btn_min)
        self.header_layout.addWidget(self.btn_close)

        # 2. Prompter Canvas (%100 Şeffaf Arka Plan)
        self.canvas = PrompterCanvas(self.matcher, self.card_frame)

        # 3. Bottom Controls Bar
        self.bottom_bar = QWidget(self.card_frame)
        self.bottom_bar.setFixedHeight(44)
        self.bottom_bar.setStyleSheet("""
            QWidget {
                background-color: rgba(15, 20, 30, 0.75);
                border-bottom-left-radius: 12px;
                border-bottom-right-radius: 12px;
                border-top: 1px solid rgba(255, 255, 255, 0.08);
            }
            QPushButton {
                background-color: rgba(255, 255, 255, 0.08);
                color: #E6EDF3;
                border: 1px solid rgba(255, 255, 255, 0.15);
                border-radius: 6px;
                padding: 4px 10px;
                font-size: 11px;
                font-weight: 500;
            }
            QPushButton:hover {
                background-color: rgba(255, 255, 255, 0.18);
                border-color: rgba(0, 240, 255, 0.4);
            }
            QLabel {
                color: #8B949E;
                font-size: 11px;
            }
        """)
        self.bottom_layout = QHBoxLayout(self.bottom_bar)
        self.bottom_layout.setContentsMargins(12, 0, 12, 0)
        self.bottom_layout.setSpacing(8)

        # Mode Toggle
        self.btn_mode = QPushButton("🎤 Ses Takipli", self.bottom_bar)
        self.btn_mode.setToolTip("Konuşmanızla senkronize kayma modu (Sadece siz konuştuğunuzda kayar)")
        self.btn_mode.setStyleSheet("background-color: #00F0FF; color: #0B0E14; font-weight: bold;")
        self.btn_mode.clicked.connect(self.toggle_voice_manual_mode)

        # Play/Pause
        self.btn_play_pause = QPushButton("⏸️", self.bottom_bar)
        self.btn_play_pause.setToolTip("Oynat / Duraklat (Boşluk Tuşu)")
        self.btn_play_pause.setFixedWidth(34)
        self.btn_play_pause.clicked.connect(self.toggle_play_pause)

        # Reset
        self.btn_reset = QPushButton("⏮️ Başa Sar", self.bottom_bar)
        self.btn_reset.setToolTip("Metni en başa sar (R Tuşu)")
        self.btn_reset.clicked.connect(self.reset_prompter)

        # Font +/-
        self.btn_font_minus = QPushButton("A-", self.bottom_bar)
        self.btn_font_minus.setFixedWidth(30)
        self.btn_font_minus.clicked.connect(lambda: self.adjust_font_size(-3))
        
        self.btn_font_plus = QPushButton("A+", self.bottom_bar)
        self.btn_font_plus.setFixedWidth(30)
        self.btn_font_plus.clicked.connect(lambda: self.adjust_font_size(3))

        # Mirror
        self.btn_mirror = QPushButton("🪞 Ayna", self.bottom_bar)
        self.btn_mirror.clicked.connect(self.canvas.toggle_mirror_h)

        # Opacity slider (0% - 100%) -> Varsayılan %15 (Cam gibi şeffaf)
        self.opacity_lbl = QLabel("Şeffaflık:", self.bottom_bar)
        self.opacity_slider = QSlider(Qt.Orientation.Horizontal, self.bottom_bar)
        self.opacity_slider.setRange(0, 100)
        self.opacity_slider.setValue(15)
        self.opacity_slider.setFixedWidth(70)
        self.opacity_slider.setToolTip("Arka plan şeffaflığı (0% = Arkadaki ekran tamamen görünür)")
        self.opacity_slider.valueChanged.connect(self._on_opacity_change)

        # Progress Counter
        self.progress_lbl = QLabel("0 / 0", self.bottom_bar)
        self.progress_lbl.setStyleSheet("color: #00F0FF; font-weight: bold;")

        # Size grip
        self.size_grip = QSizeGrip(self.bottom_bar)
        self.size_grip.setFixedSize(14, 14)

        self.bottom_layout.addWidget(self.btn_mode)
        self.bottom_layout.addWidget(self.btn_play_pause)
        self.bottom_layout.addWidget(self.btn_reset)
        self.bottom_layout.addWidget(self.btn_font_minus)
        self.bottom_layout.addWidget(self.btn_font_plus)
        self.bottom_layout.addWidget(self.btn_mirror)
        self.bottom_layout.addWidget(self.opacity_lbl)
        self.bottom_layout.addWidget(self.opacity_slider)
        self.bottom_layout.addStretch()
        self.bottom_layout.addWidget(self.progress_lbl)
        self.bottom_layout.addWidget(self.size_grip)

        # Assemble layout
        self.card_layout.addWidget(self.header_bar)
        self.card_layout.addWidget(self.canvas, 1)
        self.card_layout.addWidget(self.bottom_bar)
        self.central_layout.addWidget(self.card_frame)

    def _create_icon_btn(self, text: str, tooltip: str, callback, is_close: bool = False) -> QPushButton:
        btn = QPushButton(text, self.header_bar)
        btn.setToolTip(tooltip)
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        btn.setFixedSize(28, 28)
        if is_close:
            btn.setStyleSheet("""
                QPushButton {
                    background: transparent;
                    color: #8B949E;
                    border: none;
                    border-radius: 6px;
                    font-size: 12px;
                }
                QPushButton:hover {
                    background-color: #DA3633;
                    color: #FFFFFF;
                }
            """)
        else:
            btn.setStyleSheet("""
                QPushButton {
                    background: transparent;
                    color: #C9D1D9;
                    border: none;
                    border-radius: 6px;
                    font-size: 12px;
                }
                QPushButton:hover {
                    background-color: rgba(255, 255, 255, 0.15);
                    color: #00F0FF;
                }
            """)
        btn.clicked.connect(callback)
        return btn

    def _connect_signals(self):
        self.voice_engine.signals.speech_detected.connect(self._on_speech_recognized)
        self.voice_engine.signals.status_changed.connect(self._on_voice_status_changed)
        self.voice_engine.signals.error_occurred.connect(self._on_voice_error)
        self.canvas.progress_changed.connect(self._on_progress_update)

    def showEvent(self, event):
        super().showEvent(event)
        self.apply_stealth_mode(True)

    def apply_stealth_mode(self, enable: bool):
        hwnd = int(self.winId())
        success = stealth.set_stealth_mode(hwnd, enable)
        self.is_stealth_active = enable and success
        if self.is_stealth_active:
            self.stealth_badge.setText("🛡️ Kayıtta Gizli")
            self.stealth_badge.setStyleSheet("""
                QPushButton {
                    background-color: rgba(0, 240, 255, 0.2);
                    color: #00F0FF;
                    border: 1px solid rgba(0, 240, 255, 0.45);
                    border-radius: 6px;
                    padding: 3px 8px;
                    font-size: 11px;
                    font-weight: bold;
                }
            """)
        else:
            self.stealth_badge.setText("👁️ Kayıtta Görünür")
            self.stealth_badge.setStyleSheet("""
                QPushButton {
                    background-color: rgba(255, 165, 0, 0.2);
                    color: #FFA500;
                    border: 1px solid rgba(255, 165, 0, 0.45);
                    border-radius: 6px;
                    padding: 3px 8px;
                    font-size: 11px;
                    font-weight: bold;
                }
            """)

    def toggle_stealth_mode(self):
        self.apply_stealth_mode(not self.is_stealth_active)

    def toggle_click_through(self):
        """Toggles mouse click-through so mouse clicks directly into the browser/app behind."""
        self.is_click_through = not self.is_click_through
        hwnd = int(self.winId())
        stealth.set_click_through(hwnd, self.is_click_through)
        
        if self.is_click_through:
            self.click_through_badge.setText("🔓 Arkaya Tıkla: AÇIK (F8)")
            self.click_through_badge.setStyleSheet("""
                QPushButton {
                    background-color: rgba(0, 255, 163, 0.25);
                    color: #00FFA3;
                    border: 1px solid rgba(0, 255, 163, 0.6);
                    border-radius: 6px;
                    padding: 3px 8px;
                    font-size: 11px;
                    font-weight: bold;
                }
            """)
            self.status_lbl.setText("🔓 Fareniz arkadaki uygulamaya tıklar (Kapatmak için F8)")
        else:
            self.click_through_badge.setText("🖱️ Arkaya Tıkla (F8)")
            self.click_through_badge.setStyleSheet("""
                QPushButton {
                    background-color: rgba(255, 255, 255, 0.1);
                    color: #E6EDF3;
                    border: 1px solid rgba(255, 255, 255, 0.25);
                    border-radius: 6px;
                    padding: 3px 8px;
                    font-size: 11px;
                    font-weight: bold;
                }
            """)
            self.status_lbl.setText("🎤 Konuşmanız bekleniyor...")

    def toggle_top_banner_mode(self):
        """Positions prompter as a slim banner right under webcam at top of screen."""
        self.is_top_banner_mode = not self.is_top_banner_mode
        screen = QGuiApplication.primaryScreen().availableGeometry()
        
        if self.is_top_banner_mode:
            self.saved_normal_geo = self.geometry()
            banner_w = int(screen.width() * 0.94)
            banner_h = 180
            banner_x = int((screen.width() - banner_w) / 2)
            banner_y = screen.top() + 6
            self.setGeometry(banner_x, banner_y, banner_w, banner_h)
            self.btn_top_banner.setText("📱 Normal Boyut")
        else:
            if self.saved_normal_geo:
                self.setGeometry(self.saved_normal_geo)
            else:
                self.resize(860, 480)
            self.btn_top_banner.setText("📏 Kamera Çubuğu")

    def toggle_always_on_top(self):
        self.is_always_on_top = not self.is_always_on_top
        flags = self.windowFlags()
        if self.is_always_on_top:
            flags |= Qt.WindowType.WindowStaysOnTopHint
            self.btn_pin.setStyleSheet("color: #00F0FF; background-color: rgba(0, 240, 255, 0.2);")
        else:
            flags &= ~Qt.WindowType.WindowStaysOnTopHint
            self.btn_pin.setStyleSheet("color: #C9D1D9; background: transparent;")
        self.setWindowFlags(flags)
        self.show()
        self.apply_stealth_mode(self.is_stealth_active)

    def toggle_voice_manual_mode(self):
        self.canvas.is_manual_mode = not self.canvas.is_manual_mode
        if self.canvas.is_manual_mode:
            self.btn_mode.setText("⌨️ Manuel Hız")
            self.btn_mode.setStyleSheet("background-color: #A371F7; color: #FFFFFF; font-weight: bold;")
            self.voice_engine.pause()
            self.status_lbl.setText("⌨️ Manuel akış modu")
        else:
            self.btn_mode.setText("🎤 Ses Takipli")
            self.btn_mode.setStyleSheet("background-color: #00F0FF; color: #0B0E14; font-weight: bold;")
            self.voice_engine.resume()
            self.status_lbl.setText("🎤 Konuşmanız bekleniyor...")

    def toggle_play_pause(self):
        self.canvas.is_playing = not self.canvas.is_playing
        if self.canvas.is_playing:
            self.btn_play_pause.setText("⏸️")
            if not self.canvas.is_manual_mode:
                self.voice_engine.resume()
        else:
            self.btn_play_pause.setText("▶️")
            self.voice_engine.pause()

    def reset_prompter(self):
        self.matcher.reset_progress()
        self.canvas.update_active_word(0)
        self.canvas.current_scroll_y = 0
        self.canvas.target_scroll_y = 0

    def adjust_font_size(self, delta: int):
        new_size = self.canvas.font_size + delta
        self.canvas.set_font_size(new_size)

    def _on_opacity_change(self, value: int):
        self.canvas.set_bg_opacity(value)
        alpha = (value / 100.0) * 0.85
        self.card_frame.setStyleSheet(f"""
            QFrame#cardFrame {{
                background-color: rgba(10, 14, 22, {alpha:.2f});
                border: 1px solid rgba(0, 240, 255, 0.35);
                border-radius: 12px;
            }}
        """)

    def _on_speech_recognized(self, phrase: str):
        """Advances prompter ONLY when words are actually recognized."""
        if not self.canvas.is_playing or self.canvas.is_manual_mode:
            return

        self.status_lbl.setText(f"🗣️ \"{phrase[:24]}...\"" if len(phrase) > 24 else f"🗣️ \"{phrase}\"")
        matched_idx = self.matcher.match_spoken_phrase(phrase)
        if matched_idx is not None:
            self.canvas.update_active_word(matched_idx)

    def _on_voice_status_changed(self, status: str):
        self.status_lbl.setText(status)

    def _on_voice_error(self, err: str):
        self.status_lbl.setText(f"⚠️ {err[:25]}")

    def _on_progress_update(self, current: int, total: int):
        self.progress_lbl.setText(f"{current + 1} / {total}")

    def _open_editor(self):
        self.open_editor_requested.emit()

    def load_new_script(self, text: str):
        self.matcher.load_script(text)
        self.canvas.recompute_layout()
        self.reset_prompter()

    # Window Drag Mechanics
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            if self.header_bar.geometry().contains(event.position().toPoint()):
                self.is_dragging = True
                self.drag_position = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
                event.accept()
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self.is_dragging and event.buttons() & Qt.MouseButton.LeftButton:
            self.move(event.globalPosition().toPoint() - self.drag_position)
            event.accept()
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        self.is_dragging = False
        super().mouseReleaseEvent(event)

    # Keyboard Shortcuts
    def keyPressEvent(self, event):
        key = event.key()
        if key == Qt.Key.Key_F8:
            self.toggle_click_through()
        elif key == Qt.Key.Key_Space:
            self.toggle_play_pause()
        elif key == Qt.Key.Key_R:
            self.reset_prompter()
        elif key == Qt.Key.Key_G:
            self.toggle_stealth_mode()
        elif key == Qt.Key.Key_M:
            self.canvas.toggle_mirror_h()
        elif key == Qt.Key.Key_Right:
            self.canvas.update_active_word(self.matcher.current_index + 1)
        elif key == Qt.Key.Key_Left:
            self.canvas.update_active_word(max(0, self.matcher.current_index - 1))
        elif key == Qt.Key.Key_Up:
            self.adjust_font_size(2)
        elif key == Qt.Key.Key_Down:
            self.adjust_font_size(-2)
        elif key == Qt.Key.Key_Escape:
            self.showMinimized()
        else:
            super().keyPressEvent(event)
