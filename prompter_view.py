"""
High-Performance 60 FPS Prompter Render Widget
Custom QPainter canvas with karaoke-style active word highlighting,
smooth eye-line scrolling, eyeline guide marker, and mirror (flip) support.
"""

from typing import List, Optional, Tuple
from PyQt6.QtCore import Qt, QTimer, QRectF, QPointF, pyqtSignal
from PyQt6.QtWidgets import QWidget
from PyQt6.QtGui import (
    QPainter, QFont, QFontMetrics, QColor,
    QLinearGradient, QPen, QBrush, QMouseEvent, QWheelEvent
)
from word_matcher import WordMatcher, ScriptToken


class PrompterCanvas(QWidget):
    word_clicked = pyqtSignal(int)      # Emits token index when clicked
    progress_changed = pyqtSignal(int, int)  # current, total

    def __init__(self, matcher: WordMatcher, parent=None):
        super().__init__(parent)
        self.matcher = matcher
        
        # Display settings
        self.font_family = "Segoe UI"
        self.font_size = 32
        self.line_spacing = 1.4
        self.mirror_h = False
        self.mirror_v = False
        self.show_eyeline = True
        self.eyeline_ratio = 0.35  # Eye level at 35% from the top
        
        # Color Theme (Default: Modern Cyber Dark)
        self.bg_color = QColor(15, 17, 23, 235)           # Deep transparent dark
        self.color_read = QColor(140, 150, 165, 90)       # Dimmed past words
        self.color_active = QColor(0, 240, 255, 255)      # Glowing Neon Cyan active word
        self.color_active_bg = QColor(0, 240, 255, 45)   # Active word pill glow
        self.color_unread = QColor(245, 248, 255, 240)    # Crisp upcoming words
        self.color_eyeline = QColor(0, 240, 255, 120)     # Eyeline laser guide
        
        # Scrolling interpolation
        self.current_scroll_y = 0.0
        self.target_scroll_y = 0.0
        self.manual_scroll_offset = 0.0
        self.is_manual_mode = False
        self.manual_speed = 3.0  # Pixels per frame in manual mode
        self.is_playing = True
        
        # Layout cache: List of (token_index, QRectF)
        self.token_rects: List[Tuple[int, QRectF]] = []
        self.total_content_height = 0.0
        
        # 60 FPS animation timer for smooth scrolling
        self.anim_timer = QTimer(self)
        self.anim_timer.timeout.connect(self._on_animation_frame)
        self.anim_timer.start(16)  # ~60 FPS
        
        self.setMouseTracking(True)
        self.recompute_layout()

    def set_theme(self, theme_name: str):
        """Predefined color themes."""
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

    def toggle_mirror_v(self):
        self.mirror_v = not self.mirror_v
        self.update()

    def recompute_layout(self):
        """Calculates exact x, y, width, height for each word token."""
        self.token_rects.clear()
        if not self.matcher or not self.matcher.tokens:
            self.total_content_height = 0
            return

        font = QFont(self.font_family, self.font_size, QFont.Weight.Bold)
        fm = QFontMetrics(font)
        
        margin_x = 40.0
        margin_y = 60.0
        usable_width = max(200.0, float(self.width()) - (margin_x * 2))
        
        line_height = fm.height() * self.line_spacing
        space_width = fm.horizontalAdvance(" ")
        
        current_x = margin_x
        current_y = margin_y
        
        for token in self.matcher.tokens:
            word_w = float(fm.horizontalAdvance(token.original_text))
            word_h = float(fm.height())
            
            # Wrap line if exceeding usable width
            if current_x + word_w > margin_x + usable_width and current_x > margin_x:
                current_x = margin_x
                current_y += line_height
                
            rect = QRectF(current_x, current_y, word_w, word_h)
            self.token_rects.append((token.index, rect))
            
            current_x += word_w + space_width
            
            if token.is_newline:
                current_x = margin_x
                current_y += line_height

        self.total_content_height = current_y + line_height + 200.0
        self._update_target_scroll()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.recompute_layout()

    def update_active_word(self, index: int):
        """Called when a new word is matched via speech."""
        self.matcher.set_index(index)
        self.progress_changed.emit(self.matcher.current_index, self.matcher.total_words)
        self._update_target_scroll()
        self.update()

    def _update_target_scroll(self):
        """Calculates where the camera should scroll so active word hits the eye-line."""
        if not self.token_rects:
            return
            
        cur_idx = self.matcher.current_index
        if 0 <= cur_idx < len(self.token_rects):
            _, active_rect = self.token_rects[cur_idx]
            eyeline_px = self.height() * self.eyeline_ratio
            # Active word aligned to eye-line
            self.target_scroll_y = max(0.0, active_rect.top() - eyeline_px)
        elif cur_idx >= len(self.token_rects):
            self.target_scroll_y = max(0.0, self.total_content_height - self.height())

    def _on_animation_frame(self):
        """Interpolates smooth scrolling towards target position."""
        if self.is_manual_mode and self.is_playing:
            # Constant speed scrolling in manual mode
            self.target_scroll_y += self.manual_speed
            
        # Smooth spring/ease interpolation
        diff = self.target_scroll_y - self.current_scroll_y
        if abs(diff) > 0.3:
            self.current_scroll_y += diff * 0.12  # Easing factor
            self.update()
        elif diff != 0:
            self.current_scroll_y = self.target_scroll_y
            self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setRenderHint(QPainter.RenderHint.TextAntialiasing)

        # 1. Fill Background
        painter.fillRect(self.rect(), self.bg_color)

        # Apply mirroring transformations if enabled
        if self.mirror_h or self.mirror_v:
            painter.save()
            sx = -1.0 if self.mirror_h else 1.0
            sy = -1.0 if self.mirror_v else 1.0
            tx = self.width() if self.mirror_h else 0
            ty = self.height() if self.mirror_v else 0
            painter.translate(tx, ty)
            painter.scale(sx, sy)

        # 2. Draw Eyeline Guide Marker
        eyeline_y = self.height() * self.eyeline_ratio
        if self.show_eyeline:
            # Gradient laser line
            grad = QLinearGradient(0, eyeline_y, self.width(), eyeline_y)
            grad.setColorAt(0.0, QColor(0, 0, 0, 0))
            grad.setColorAt(0.15, self.color_eyeline)
            grad.setColorAt(0.5, self.color_eyeline)
            grad.setColorAt(0.85, self.color_eyeline)
            grad.setColorAt(1.0, QColor(0, 0, 0, 0))
            
            pen = QPen(QBrush(grad), 1.5, Qt.PenStyle.DashLine)
            painter.setPen(pen)
            painter.drawLine(QPointF(20, eyeline_y), QPointF(self.width() - 20, eyeline_y))
            
            # Subtle side arrow indicators
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(self.color_eyeline)
            arrow_size = 6.0
            # Left arrow
            painter.drawPolygon([
                QPointF(15, eyeline_y),
                QPointF(15 - arrow_size, eyeline_y - arrow_size),
                QPointF(15 - arrow_size, eyeline_y + arrow_size)
            ])
            # Right arrow
            painter.drawPolygon([
                QPointF(self.width() - 15, eyeline_y),
                QPointF(self.width() - 15 + arrow_size, eyeline_y - arrow_size),
                QPointF(self.width() - 15 + arrow_size, eyeline_y + arrow_size)
            ])

        # 3. Draw Words
        font = QFont(self.font_family, self.font_size, QFont.Weight.DemiBold)
        painter.setFont(font)
        fm = QFontMetrics(font)
        
        cur_idx = self.matcher.current_index
        view_top = self.current_scroll_y - 100
        view_bottom = self.current_scroll_y + self.height() + 100

        for token_idx, rect in self.token_rects:
            # Viewport culling
            if rect.bottom() < view_top or rect.top() > view_bottom:
                continue
                
            token = self.matcher.tokens[token_idx]
            draw_rect = QRectF(rect.x(), rect.y() - self.current_scroll_y, rect.width(), rect.height())
            
            if token_idx < cur_idx:
                # Past read words
                painter.setPen(self.color_read)
                painter.drawText(draw_rect, Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter, token.original_text)
            elif token_idx == cur_idx:
                # Active word - Glowing Background Pill
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
                
                # Active word text (bold and glowing color)
                painter.setPen(self.color_active)
                painter.drawText(draw_rect, Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter, token.original_text)
            else:
                # Upcoming words
                painter.setPen(self.color_unread)
                painter.drawText(draw_rect, Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter, token.original_text)

        if self.mirror_h or self.mirror_v:
            painter.restore()

    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton:
            # Check if clicked on a word
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
        # Mouse wheel manual scroll
        delta = event.angleDelta().y()
        self.target_scroll_y = max(0.0, min(self.target_scroll_y - (delta * 0.8), self.total_content_height - self.height()))
        self.update()
        event.accept()
