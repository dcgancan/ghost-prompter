"""
High-Performance Prompter Render Widget
100% Transparent Background Support + High-Contrast Glowing Text + Zero Ghost Scrolling
"""

from typing import List, Optional, Tuple
from PyQt6.QtCore import Qt, QTimer, QRectF, QPointF, pyqtSignal
from PyQt6.QtWidgets import QWidget
from PyQt6.QtGui import (
    QPainter, QFont, QFontMetrics, QColor,
    QLinearGradient, QPen, QBrush, QMouseEvent, QWheelEvent,
    QPainterPath
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
        self.eyeline_ratio = 0.35
        
        # Color Theme (Default: High-Contrast Neon Cyan on Transparent Canvas)
        # Default: 0 Alpha (Tamamen Şeffaf / Arkası %100 Görünür)
        self.bg_color = QColor(0, 0, 0, 0)
        self.color_read = QColor(160, 175, 195, 120)        # Okunan kelimeler
        self.color_active = QColor(0, 245, 255, 255)        # Aktif parlayan kelime
        self.color_active_bg = QColor(0, 240, 255, 60)     # Aktif kelime arkası neon glow
        self.color_unread = QColor(255, 255, 255, 255)      # Yaklaşan okunacak kelimeler (Tam beyaz)
        self.color_shadow = QColor(0, 0, 0, 230)            # Yazı okunurluğu için koyu gölge
        self.color_eyeline = QColor(0, 240, 255, 140)       # Göz hizası lazer çizgisi
        
        # State
        self.is_manual_mode = False
        self.is_playing = True
        self.manual_speed = 3.0
        
        # Scrolling interpolation
        self.current_scroll_y = 0.0
        self.target_scroll_y = 0.0
        
        # Layout cache: List of (token_index, QRectF)
        self.token_rects: List[Tuple[int, QRectF]] = []
        self.total_content_height = 0.0
        
        # 60 FPS animation timer for camera easing
        self.anim_timer = QTimer(self)
        self.anim_timer.timeout.connect(self._on_animation_frame)
        self.anim_timer.start(16)
        
        self.setMouseTracking(True)
        self.recompute_layout()

    def set_theme(self, theme_name: str):
        if theme_name == "Cyan":
            self.color_active = QColor(0, 245, 255, 255)
            self.color_active_bg = QColor(0, 240, 255, 60)
            self.color_eyeline = QColor(0, 240, 255, 140)
        elif theme_name == "Gold":
            self.color_active = QColor(255, 215, 0, 255)
            self.color_active_bg = QColor(255, 215, 0, 60)
            self.color_eyeline = QColor(255, 215, 0, 140)
        elif theme_name == "Emerald":
            self.color_active = QColor(0, 255, 163, 255)
            self.color_active_bg = QColor(0, 255, 163, 60)
            self.color_eyeline = QColor(0, 255, 163, 140)
        elif theme_name == "Classic White":
            self.color_active = QColor(255, 255, 255, 255)
            self.color_active_bg = QColor(255, 255, 255, 70)
            self.color_eyeline = QColor(255, 255, 255, 120)
        self.update()

    def set_font_size(self, size: int):
        self.font_size = max(18, min(76, size))
        self.recompute_layout()
        self.update()

    def set_bg_opacity(self, alpha_percent: int):
        """0% = Tamamen şeffaf (arkası kristal netliğinde), 100% = Katı siyah."""
        alpha = int(255 * (alpha_percent / 100.0))
        self.bg_color = QColor(10, 13, 18, alpha)
        self.update()

    def toggle_mirror_h(self):
        self.mirror_h = not self.mirror_h
        self.update()

    def recompute_layout(self):
        """Calculates exact positions for all tokens."""
        self.token_rects.clear()
        if not self.matcher or not self.matcher.tokens:
            self.total_content_height = 0
            return

        font = QFont(self.font_family, self.font_size, QFont.Weight.Bold)
        fm = QFontMetrics(font)
        
        margin_x = 30.0
        margin_y = 45.0
        usable_width = max(180.0, float(self.width()) - (margin_x * 2))
        
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
        """Advances active word ONLY when speech is recognized or word clicked."""
        self.matcher.set_index(index)
        self.progress_changed.emit(self.matcher.current_index, self.matcher.total_words)
        self._update_target_scroll()
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
        """Only scrolls if in manual mode or interpolating to matched word."""
        if self.is_manual_mode and self.is_playing:
            self.target_scroll_y += self.manual_speed

        diff = self.target_scroll_y - self.current_scroll_y
        if abs(diff) > 0.3:
            self.current_scroll_y += diff * 0.16
            self.update()
        elif diff != 0:
            self.current_scroll_y = self.target_scroll_y
            self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setRenderHint(QPainter.RenderHint.TextAntialiasing)

        # 1. Arka Plan (Şeffaf veya Opak)
        if self.bg_color.alpha() > 0:
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
            grad.setColorAt(0.1, self.color_eyeline)
            grad.setColorAt(0.5, self.color_eyeline)
            grad.setColorAt(0.9, self.color_eyeline)
            grad.setColorAt(1.0, QColor(0, 0, 0, 0))
            
            pen = QPen(QBrush(grad), 2.0, Qt.PenStyle.DashLine)
            painter.setPen(pen)
            painter.drawLine(QPointF(10, eyeline_y), QPointF(self.width() - 10, eyeline_y))

        # 3. Metin Çizimi (Yüksek Kontrast & Gölgelendirme)
        font = QFont(self.font_family, self.font_size, QFont.Weight.Bold)
        painter.setFont(font)
        
        cur_idx = self.matcher.current_index
        view_top = self.current_scroll_y - 80
        view_bottom = self.current_scroll_y + self.height() + 80

        for token_idx, rect in self.token_rects:
            if rect.bottom() < view_top or rect.top() > view_bottom:
                continue
                
            token = self.matcher.tokens[token_idx]
            draw_rect = QRectF(rect.x(), rect.y() - self.current_scroll_y, rect.width(), rect.height())
            
            # Yazı arkasında kontrast gölgesi (Arkadaki açık renkli web sayfalarında bile net okunabilmesi için)
            shadow_rect = QRectF(draw_rect.x() + 2, draw_rect.y() + 2, draw_rect.width(), draw_rect.height())
            painter.setPen(self.color_shadow)
            painter.drawText(shadow_rect, Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter, token.original_text)

            if token_idx < cur_idx:
                painter.setPen(self.color_read)
                painter.drawText(draw_rect, Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter, token.original_text)
            elif token_idx == cur_idx:
                # Aktif Kelime - Parlayan Neon Pill
                glow_pad_x = 7.0
                glow_pad_y = 4.0
                pill_rect = QRectF(
                    draw_rect.x() - glow_pad_x,
                    draw_rect.y() - glow_pad_y,
                    draw_rect.width() + (glow_pad_x * 2),
                    draw_rect.height() + (glow_pad_y * 2)
                )
                painter.setPen(QPen(self.color_active, 1.8))
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
