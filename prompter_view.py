"""
High-Performance 60 FPS Prompter Render Widget
Zero-Lag Hybrid Voice Pacing + Karaoke Active Highlighting + Unlimited Text Support
"""

import time
from typing import List, Optional, Tuple
from PyQt6.QtCore import Qt, QTimer, QRectF, QPointF, pyqtSignal
from PyQt6.QtWidgets import QWidget
from PyQt6.QtGui import (
    QPainter, QFont, QFontMetrics, QColor,
    QLinearGradient, QPen, QBrush, QMouseEvent, QWheelEvent
)
from word_matcher import WordMatcher, ScriptToken


class PrompterCanvas(QWidget):
    word_clicked = pyqtSignal(int)          # Emits token index when clicked
    progress_changed = pyqtSignal(int, int)  # current, total

    def __init__(self, matcher: WordMatcher, parent=None):
        super().__init__(parent)
        self.matcher = matcher
        
        # Display settings
        self.font_family = "Segoe UI"
        self.font_size = 32
        self.line_spacing = 1.45
        self.mirror_h = False
        self.mirror_v = False
        self.show_eyeline = True
        self.eyeline_ratio = 0.35  # Göz hizası %35 yükseklikte
        
        # Color Theme (Default: Neon Cyan)
        self.bg_color = QColor(11, 14, 20, 240)
        self.color_read = QColor(135, 145, 160, 95)
        self.color_active = QColor(0, 240, 255, 255)
        self.color_active_bg = QColor(0, 240, 255, 45)
        self.color_unread = QColor(245, 248, 255, 245)
        self.color_eyeline = QColor(0, 240, 255, 120)
        
        # Smooth Voice Pacing Engine ("Tak Tak Tak" Akıcılığı)
        self.is_voice_mode = True
        self.is_voice_speaking = False
        self.is_playing = True
        self.words_per_minute = 140.0         # Okuma hızı (WPM)
        self.last_voice_step_time = time.time()
        
        # Manual Mode Settings
        self.is_manual_mode = False
        self.manual_speed = 3.2
        
        # Scrolling interpolation
        self.current_scroll_y = 0.0
        self.target_scroll_y = 0.0
        
        # Layout cache: List of (token_index, QRectF)
        self.token_rects: List[Tuple[int, QRectF]] = []
        self.total_content_height = 0.0
        
        # 60 FPS animation timer
        self.anim_timer = QTimer(self)
        self.anim_timer.timeout.connect(self._on_animation_frame)
        self.anim_timer.start(16)  # ~60 FPS
        
        self.setMouseTracking(True)
        self.recompute_layout()

    def set_theme(self, theme_name: str):
        if theme_name == "Cyan":
            self.color_active = QColor(0, 240, 255, 255)
            self.color_active_bg = QColor(0, 240, 255, 45)
            self.color_eyeline = QColor(0, 240, 255, 120)
        elif theme_name == "Gold":
            self.color_active = QColor(255, 215, 0, 255)
            self.color_active_bg = QColor(255, 215, 0, 45)
            self.color_eyeline = QColor(255, 215, 0, 120)
        elif theme_name == "Emerald":
            self.color_active = QColor(0, 255, 163, 255)
            self.color_active_bg = QColor(0, 255, 163, 45)
            self.color_eyeline = QColor(0, 255, 163, 120)
        elif theme_name == "Classic White":
            self.color_active = QColor(255, 255, 255, 255)
            self.color_active_bg = QColor(255, 255, 255, 50)
            self.color_eyeline = QColor(255, 255, 255, 100)
        self.update()

    def set_font_size(self, size: int):
        self.font_size = max(16, min(72, size))
        self.recompute_layout()
        self.update()

    def set_bg_opacity(self, alpha_percent: int):
        alpha = int(255 * (alpha_percent / 100.0))
        self.bg_color.setAlpha(alpha)
        self.update()

    def toggle_mirror_h(self):
        self.mirror_h = not self.mirror_h
        self.update()

    def set_speaking_active(self, active: bool):
        """Called by VoiceEngine VAD."""
        self.is_voice_speaking = active
        if active:
            self.last_voice_step_time = time.time()

    def recompute_layout(self):
        """Calculates exact x, y, width, height for all tokens without length limits."""
        self.token_rects.clear()
        if not self.matcher or not self.matcher.tokens:
            self.total_content_height = 0
            return

        font = QFont(self.font_family, self.font_size, QFont.Weight.Bold)
        fm = QFontMetrics(font)
        
        margin_x = 36.0
        margin_y = 50.0
        usable_width = max(200.0, float(self.width()) - (margin_x * 2))
        
        line_height = fm.height() * self.line_spacing
        space_width = fm.horizontalAdvance(" ")
        
        current_x = margin_x
        current_y = margin_y
        
        for token in self.matcher.tokens:
            word_w = float(fm.horizontalAdvance(token.original_text))
            word_h = float(fm.height())
            
            if current_x + word_w > margin_x + usable_width and current_x > margin_x:
                current_x = margin_x
                current_y += line_height
                
            rect = QRectF(current_x, current_y, word_w, word_h)
            self.token_rects.append((token.index, rect))
            
            current_x += word_w + space_width
            
            if token.is_newline:
                current_x = margin_x
                current_y += line_height

        self.total_content_height = current_y + line_height + 250.0
        self._update_target_scroll()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.recompute_layout()

    def update_active_word(self, index: int):
        """Dispatched when voice recognizer matches a word."""
        self.matcher.set_index(index)
        self.progress_changed.emit(self.matcher.current_index, self.matcher.total_words)
        self._update_target_scroll()
        self.last_voice_step_time = time.time()
        self.update()

    def _update_target_scroll(self):
        if not self.token_rects:
            return
            
        cur_idx = self.matcher.current_index
        if 0 <= cur_idx < len(self.token_rects):
            _, active_rect = self.token_rects[cur_idx]
            eyeline_px = self.height() * self.eyeline_ratio
            self.target_scroll_y = max(0.0, active_rect.top() - eyeline_px)
        elif cur_idx >= len(self.token_rects):
            self.target_scroll_y = max(0.0, self.total_content_height - self.height())

    def _on_animation_frame(self):
        """60 FPS interpolation and live continuous pacing."""
        now = time.time()
        
        # 1. Voice-Activated Continuous Pacer ("Tak Tak Tak" Akışı)
        if not self.is_manual_mode and self.is_playing and self.is_voice_speaking:
            step_interval = 60.0 / max(60.0, self.words_per_minute)  # Saniye başına kelime adımı
            if now - self.last_voice_step_time >= step_interval:
                self.last_voice_step_time = now
                if self.matcher.current_index < self.matcher.total_words - 1:
                    self.matcher.advance_by(1)
                    self.progress_changed.emit(self.matcher.current_index, self.matcher.total_words)
                    self._update_target_scroll()

        # 2. Manual constant-speed mode
        elif self.is_manual_mode and self.is_playing:
            self.target_scroll_y += self.manual_speed

        # 3. Smooth Camera Easing (60 FPS)
        diff = self.target_scroll_y - self.current_scroll_y
        if abs(diff) > 0.25:
            self.current_scroll_y += diff * 0.14
            self.update()
        elif diff != 0:
            self.current_scroll_y = self.target_scroll_y
            self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setRenderHint(QPainter.RenderHint.TextAntialiasing)

        # 1. Arka Plan
        painter.fillRect(self.rect(), self.bg_color)

        if self.mirror_h or self.mirror_v:
            painter.save()
            sx = -1.0 if self.mirror_h else 1.0
            sy = -1.0 if self.mirror_v else 1.0
            tx = self.width() if self.mirror_h else 0
            ty = self.height() if self.mirror_v else 0
            painter.translate(tx, ty)
            painter.scale(sx, sy)

        # 2. Göz Hizası Kılavuz Çizgisi
        eyeline_y = self.height() * self.eyeline_ratio
        if self.show_eyeline:
            grad = QLinearGradient(0, eyeline_y, self.width(), eyeline_y)
            grad.setColorAt(0.0, QColor(0, 0, 0, 0))
            grad.setColorAt(0.12, self.color_eyeline)
            grad.setColorAt(0.5, self.color_eyeline)
            grad.setColorAt(0.88, self.color_eyeline)
            grad.setColorAt(1.0, QColor(0, 0, 0, 0))
            
            pen = QPen(QBrush(grad), 1.5, Qt.PenStyle.DashLine)
            painter.setPen(pen)
            painter.drawLine(QPointF(15, eyeline_y), QPointF(self.width() - 15, eyeline_y))

        # 3. Kelimeleri Çiz (Sınırsız Metin & Hızlı Viewport Filtreleme)
        font = QFont(self.font_family, self.font_size, QFont.Weight.DemiBold)
        painter.setFont(font)
        
        cur_idx = self.matcher.current_index
        view_top = self.current_scroll_y - 80
        view_bottom = self.current_scroll_y + self.height() + 80

        for token_idx, rect in self.token_rects:
            if rect.bottom() < view_top or rect.top() > view_bottom:
                continue
                
            token = self.matcher.tokens[token_idx]
            draw_rect = QRectF(rect.x(), rect.y() - self.current_scroll_y, rect.width(), rect.height())
            
            if token_idx < cur_idx:
                painter.setPen(self.color_read)
                painter.drawText(draw_rect, Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter, token.original_text)
            elif token_idx == cur_idx:
                # Aktif Kelime - Parlayan Neon Pill
                glow_pad_x = 6.0
                glow_pad_y = 3.0
                pill_rect = QRectF(
                    draw_rect.x() - glow_pad_x,
                    draw_rect.y() - glow_pad_y,
                    draw_rect.width() + (glow_pad_x * 2),
                    draw_rect.height() + (glow_pad_y * 2)
                )
                painter.setPen(QPen(self.color_active, 1.5))
                painter.setBrush(self.color_active_bg)
                painter.drawRoundedRect(pill_rect, 6.0, 6.0)
                
                painter.setPen(self.color_active)
                painter.drawText(draw_rect, Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter, token.original_text)
            else:
                painter.setPen(self.color_unread)
                painter.drawText(draw_rect, Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter, token.original_text)

        if self.mirror_h or self.mirror_v:
            painter.restore()

    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton:
            click_pos = event.position()
            doc_x = click_pos.x()
            doc_y = click_pos.y() + self.current_scroll_y
            
            for token_idx, rect in self.token_rects:
                if rect.contains(doc_x, doc_y):
                    self.update_active_word(token_idx)
                    self.word_clicked.emit(token_idx)
                    break
        super().mousePressEvent(event)

    def wheelEvent(self, event: QWheelEvent):
        delta = event.angleDelta().y()
        self.target_scroll_y = max(0.0, min(self.target_scroll_y - (delta * 0.8), self.total_content_height - self.height()))
        self.update()
        event.accept()
