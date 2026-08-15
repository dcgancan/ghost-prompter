"""
Script Editor and Prompter Settings Window
Full Multi-Language Support (Turkish 🇹🇷 & English 🇺🇸)
Ulusoy Digital - Muzaffer Ulusoy Branding
"""

import os
import webbrowser
from typing import List, Optional
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QColor, QIcon, QDesktopServices, QCursor
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTextEdit,
    QPushButton, QLabel, QComboBox, QFileDialog,
    QGroupBox, QTabWidget, QMessageBox, QFrame, QSlider
)
from voice_engine import VoiceEngine
from i18n import I18nManager


class EditorWindow(QWidget):
    script_applied = pyqtSignal(str)          # Emits script text to prompter
    settings_changed = pyqtSignal(dict)        # Emits theme, mic, lang settings
    ui_language_changed = pyqtSignal(str)      # "tr" or "en"

    def __init__(self, voice_engine: VoiceEngine, parent=None):
        super().__init__(parent)
        self.voice_engine = voice_engine
        self.resize(740, 660)
        
        self.setStyleSheet("""
            QWidget {
                background-color: #0B0E14;
                color: #E6EDF3;
                font-family: 'Segoe UI', sans-serif;
            }
            QTabWidget::pane {
                border: 1px solid rgba(0, 240, 255, 0.2);
                background-color: #121722;
                border-radius: 10px;
            }
            QTabBar::tab {
                background-color: #0B0E14;
                color: #8B949E;
                padding: 10px 22px;
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
                font-weight: bold;
                font-size: 13px;
            }
            QTabBar::tab:selected {
                background-color: #121722;
                color: #00F0FF;
                border-bottom: 3px solid #00F0FF;
            }
            QTextEdit {
                background-color: #0B0E14;
                border: 1px solid rgba(255, 255, 255, 0.15);
                border-radius: 8px;
                padding: 14px;
                font-size: 15px;
                color: #F0F6FC;
                line-height: 1.6;
            }
            QTextEdit:focus {
                border-color: #00F0FF;
            }
            QPushButton {
                background-color: #1C2333;
                color: #E6EDF3;
                border: 1px solid rgba(255, 255, 255, 0.14);
                border-radius: 8px;
                padding: 8px 16px;
                font-size: 13px;
                font-weight: 500;
            }
            QPushButton:hover {
                background-color: #273147;
                border-color: rgba(0, 240, 255, 0.4);
            }
            QPushButton#btnApply {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #00F0FF, stop:1 #0099FF);
                color: #0B0E14;
                font-weight: bold;
                font-size: 14px;
                padding: 11px 24px;
                border-radius: 8px;
                border: none;
            }
            QPushButton#btnApply:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #33F3FF, stop:1 #33ADFF);
            }
            QComboBox {
                background-color: #0B0E14;
                border: 1px solid rgba(255, 255, 255, 0.18);
                border-radius: 6px;
                padding: 8px 14px;
                color: #E6EDF3;
                font-size: 13px;
            }
            QComboBox::drop-down {
                border: none;
            }
            QComboBox QAbstractItemView {
                background-color: #121722;
                color: #E6EDF3;
                selection-background-color: #00F0FF;
                selection-color: #0B0E14;
                border: 1px solid rgba(0, 240, 255, 0.3);
                padding: 4px;
            }
            QLabel {
                color: #8B949E;
            }
        """)

        self._init_ui()
        self.retranslate_ui()
        self._load_default_script()

    def _init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(18, 14, 18, 16)
        main_layout.setSpacing(12)

        # Brand Banner
        brand_frame = QFrame(self)
        brand_frame.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #121722, stop:1 #1A2234);
                border: 1px solid rgba(0, 240, 255, 0.25);
                border-radius: 10px;
                padding: 4px;
            }
        """)
        brand_layout = QHBoxLayout(brand_frame)
        brand_layout.setContentsMargins(14, 8, 14, 8)

        self.lbl_brand = QLabel(brand_frame)
        self.lbl_brand.setStyleSheet("font-size: 14px; color: #00F0FF;")

        # Language Selector Button in Banner
        self.combo_ui_lang = QComboBox(brand_frame)
        self.combo_ui_lang.addItem("🇹🇷 Türkçe", "tr")
        self.combo_ui_lang.addItem("🇺🇸 English", "en")
        self.combo_ui_lang.currentIndexChanged.connect(self._on_ui_lang_changed)
        self.combo_ui_lang.setFixedWidth(130)

        btn_website = QPushButton("🌐 ulusoydigital.com", brand_frame)
        btn_website.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_website.setStyleSheet("""
            QPushButton {
                background: rgba(0, 240, 255, 0.1);
                color: #00F0FF;
                border: 1px solid rgba(0, 240, 255, 0.3);
                border-radius: 6px;
                padding: 4px 12px;
                font-size: 12px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: rgba(0, 240, 255, 0.25);
            }
        """)
        btn_website.clicked.connect(lambda: webbrowser.open("https://ulusoydigital.com"))

        brand_layout.addWidget(self.lbl_brand)
        brand_layout.addStretch()
        brand_layout.addWidget(self.combo_ui_lang)
        brand_layout.addWidget(btn_website)
        main_layout.addWidget(brand_frame)

        # Tabs
        self.tabs = QTabWidget(self)
        
        # --- TAB 1: SCRIPT EDITOR ---
        self.tab_editor = QWidget()
        editor_layout = QVBoxLayout(self.tab_editor)
        editor_layout.setContentsMargins(14, 14, 14, 14)
        editor_layout.setSpacing(10)

        toolbar = QHBoxLayout()
        toolbar.setSpacing(8)

        self.btn_load_file = QPushButton(self.tab_editor)
        self.btn_load_file.clicked.connect(self._load_file)

        self.btn_save_file = QPushButton(self.tab_editor)
        self.btn_save_file.clicked.connect(self._save_file)

        self.sample_combo = QComboBox(self.tab_editor)
        self.sample_combo.currentIndexChanged.connect(self._on_sample_selected)

        toolbar.addWidget(self.btn_load_file)
        toolbar.addWidget(self.btn_save_file)
        toolbar.addWidget(self.sample_combo)
        toolbar.addStretch()

        self.text_edit = QTextEdit(self.tab_editor)
        self.text_edit.textChanged.connect(self._update_stats)

        stats_bar = QHBoxLayout()
        self.lbl_word_count = QLabel(self.tab_editor)
        self.lbl_word_count.setStyleSheet("color: #C9D1D9; font-weight: 500;")
        
        self.lbl_char_count = QLabel(self.tab_editor)
        self.lbl_char_count.setStyleSheet("color: #8B949E;")

        self.lbl_est_time = QLabel(self.tab_editor)
        self.lbl_est_time.setStyleSheet("color: #00F0FF; font-weight: bold; font-size: 13px;")

        stats_bar.addWidget(self.lbl_word_count)
        stats_bar.addWidget(QLabel("•"))
        stats_bar.addWidget(self.lbl_char_count)
        stats_bar.addStretch()
        stats_bar.addWidget(self.lbl_est_time)

        editor_layout.addLayout(toolbar)
        editor_layout.addWidget(self.text_edit, 1)
        editor_layout.addLayout(stats_bar)
        self.tabs.addTab(self.tab_editor, "")

        # --- TAB 2: SETTINGS ---
        self.tab_settings = QWidget()
        settings_layout = QVBoxLayout(self.tab_settings)
        settings_layout.setContentsMargins(18, 18, 18, 18)
        settings_layout.setSpacing(18)

        self.group_voice = QGroupBox(self.tab_settings)
        self.group_voice.setStyleSheet("QGroupBox { font-weight: bold; color: #00F0FF; font-size: 13px; }")
        gv_layout = QVBoxLayout(self.group_voice)
        gv_layout.setContentsMargins(14, 18, 14, 14)
        gv_layout.setSpacing(12)

        row_lang = QHBoxLayout()
        self.lbl_lang = QLabel(self.group_voice)
        self.lbl_lang.setStyleSheet("color: #E6EDF3; font-weight: 500;")
        self.combo_lang = QComboBox(self.group_voice)
        self.combo_lang.addItem("🇹🇷 Türkçe (Turkish - tr)", "tr-TR")
        self.combo_lang.addItem("🇺🇸 English (en-us)", "en-US")
        self.combo_lang.currentIndexChanged.connect(self._on_lang_changed)
        row_lang.addWidget(self.lbl_lang)
        row_lang.addWidget(self.combo_lang, 1)
        gv_layout.addLayout(row_lang)

        row_mic = QHBoxLayout()
        self.lbl_mic = QLabel(self.group_voice)
        self.lbl_mic.setStyleSheet("color: #E6EDF3; font-weight: 500;")
        self.combo_mic = QComboBox(self.group_voice)
        self._populate_microphones()
        self.combo_mic.currentIndexChanged.connect(self._on_mic_changed)
        row_mic.addWidget(self.lbl_mic)
        row_mic.addWidget(self.combo_mic, 1)
        gv_layout.addLayout(row_mic)

        self.btn_refresh_mic = QPushButton(self.group_voice)
        self.btn_refresh_mic.clicked.connect(self._populate_microphones)
        gv_layout.addWidget(self.btn_refresh_mic)

        settings_layout.addWidget(self.group_voice)

        self.group_theme = QGroupBox(self.tab_settings)
        self.group_theme.setStyleSheet("QGroupBox { font-weight: bold; color: #00F0FF; font-size: 13px; }")
        gt_layout = QVBoxLayout(self.group_theme)
        gt_layout.setContentsMargins(14, 18, 14, 14)
        gt_layout.setSpacing(12)

        row_theme = QHBoxLayout()
        self.lbl_theme = QLabel(self.group_theme)
        self.lbl_theme.setStyleSheet("color: #E6EDF3; font-weight: 500;")
        self.combo_theme = QComboBox(self.group_theme)
        row_theme.addWidget(self.lbl_theme)
        row_theme.addWidget(self.combo_theme, 1)
        gt_layout.addLayout(row_theme)

        settings_layout.addWidget(self.group_theme)
        settings_layout.addStretch()

        self.tabs.addTab(self.tab_settings, "")

        btn_layout = QHBoxLayout()
        self.lbl_footer = QLabel(self)
        self.lbl_footer.setStyleSheet("color: #6E7681; font-size: 11px;")

        self.btn_apply = QPushButton(self)
        self.btn_apply.setObjectName("btnApply")
        self.btn_apply.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_apply.clicked.connect(self._apply_script)

        btn_layout.addWidget(self.lbl_footer)
        btn_layout.addStretch()
        btn_layout.addWidget(self.btn_apply)

        main_layout.addWidget(self.tabs, 1)
        main_layout.addLayout(btn_layout)

    def retranslate_ui(self):
        """Refreshes all text strings to current language."""
        t = I18nManager.t
        self.setWindowTitle(t("editor_title"))
        self.lbl_brand.setText(f"{t('brand_name')} <span style='color:#8B949E;'>{t('author_tag')}</span>")
        
        self.tabs.setTabText(0, t("tab_script"))
        self.tabs.setTabText(1, t("tab_settings"))
        
        self.btn_load_file.setText(t("btn_open_file"))
        self.btn_save_file.setText(t("btn_save_file"))
        self.text_edit.setPlaceholderText(t("text_placeholder"))
        
        self.group_voice.setTitle(t("group_voice"))
        self.lbl_lang.setText(t("lbl_lang"))
        self.lbl_mic.setText(t("lbl_mic"))
        self.btn_refresh_mic.setText(t("btn_refresh_mic"))
        
        self.group_theme.setTitle(t("group_theme"))
        self.lbl_theme.setText(t("lbl_theme"))
        
        self.lbl_footer.setText(t("footer_text"))
        self.btn_apply.setText(t("btn_apply"))
        
        # Repopulate Themes
        cur_theme_idx = max(0, self.combo_theme.currentIndex())
        self.combo_theme.clear()
        self.combo_theme.addItem(t("theme_cyan"), "Cyan")
        self.combo_theme.addItem(t("theme_gold"), "Gold")
        self.combo_theme.addItem(t("theme_emerald"), "Emerald")
        self.combo_theme.addItem(t("theme_white"), "Classic White")
        self.combo_theme.setCurrentIndex(cur_theme_idx)
        
        # Repopulate Sample Scripts
        self._populate_sample_scripts()
        self._update_stats()

    def _populate_sample_scripts(self):
        samples = I18nManager.get_samples()
        self.sample_combo.clear()
        self.sample_combo.addItem(I18nManager.t("sample_placeholder"))
        for title in samples.keys():
            self.sample_combo.addItem(title)

    def _load_default_script(self):
        samples = I18nManager.get_samples()
        first_key = list(samples.keys())[0]
        self.text_edit.setPlainText(samples[first_key])
        self._update_stats()

    def _on_ui_lang_changed(self, index: int):
        lang = self.combo_ui_lang.currentData()
        I18nManager.set_language(lang)
        
        # Automatically update voice engine language
        if lang == "en":
            self.combo_lang.setCurrentIndex(1)  # en-US
        else:
            self.combo_lang.setCurrentIndex(0)  # tr-TR
            
        self.retranslate_ui()
        self.ui_language_changed.emit(lang)

    def set_active_language(self, lang_code: str):
        if lang_code == "en":
            self.combo_ui_lang.setCurrentIndex(1)
        else:
            self.combo_ui_lang.setCurrentIndex(0)

    def _populate_microphones(self):
        self.combo_mic.clear()
        self.combo_mic.addItem(I18nManager.t("default_mic"), None)
        mics = VoiceEngine.get_microphone_list()
        for idx, clean_name in mics:
            self.combo_mic.addItem(f"{idx}: {clean_name}", idx)

    def _update_stats(self):
        text = self.text_edit.toPlainText().strip()
        words = text.split()
        word_count = len(words)
        char_count = len(text)
        
        seconds_total = int((word_count / 135.0) * 60)
        minutes = seconds_total // 60
        seconds = seconds_total % 60
        
        t = I18nManager.t
        self.lbl_word_count.setText(f"{t('lbl_word_count')} {word_count}")
        self.lbl_char_count.setText(f"{t('lbl_char_count')} {char_count}")
        self.lbl_est_time.setText(f"{t('lbl_est_time')} {minutes:02d}:{seconds:02d}")

    def _on_sample_selected(self, index: int):
        if index > 0:
            key = self.sample_combo.currentText()
            samples = I18nManager.get_samples()
            if key in samples:
                self.text_edit.setPlainText(samples[key])
                self._update_stats()

    def _load_file(self):
        t = I18nManager.t
        path, _ = QFileDialog.getOpenFileName(self, t("btn_open_file"), "", "Text Files (*.txt);;All Files (*.*)")
        if path:
            try:
                with open(path, "r", encoding="utf-8") as f:
                    self.text_edit.setPlainText(f.read())
                    self._update_stats()
            except Exception as e:
                QMessageBox.warning(self, "Error", f"Could not open file: {e}")

    def _save_file(self):
        t = I18nManager.t
        path, _ = QFileDialog.getSaveFileName(self, t("btn_save_file"), "ghostprompter_script.txt", "Text Files (*.txt)")
        if path:
            try:
                with open(path, "w", encoding="utf-8") as f:
                    f.write(self.text_edit.toPlainText())
                QMessageBox.information(self, "OK", t("save_success"))
            except Exception as e:
                QMessageBox.warning(self, "Error", f"Could not save: {e}")

    def _on_lang_changed(self):
        lang_code = self.combo_lang.currentData()
        self.voice_engine.set_language(lang_code)

    def _on_mic_changed(self):
        mic_idx = self.combo_mic.currentData()
        self.voice_engine.set_mic_device(mic_idx)

    def _apply_script(self):
        text = self.text_edit.toPlainText().strip()
        if not text:
            QMessageBox.warning(self, "Warning", I18nManager.t("warn_empty"))
            return

        selected_theme = self.combo_theme.currentData() or "Cyan"
        settings = {
            "theme": selected_theme
        }
        self.settings_changed.emit(settings)
        self.script_applied.emit(text)
        self.hide()
