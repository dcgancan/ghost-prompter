"""
Script Editor and Prompter Settings Window
Ulusoy Digital - Muzaffer Ulusoy Branding
Allows typing/pasting text, loading/saving .txt files, selecting microphone,
choosing speech recognition language, theme styling, and calculating estimated speaking time.
"""

import os
import webbrowser
from typing import List, Optional
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QColor, QIcon, QDesktopServices, QCursor
from PyQt6.QtCore import QUrl
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTextEdit,
    QPushButton, QLabel, QComboBox, QFileDialog,
    QGroupBox, QTabWidget, QSpinBox, QMessageBox, QFrame,
    QSlider
)
from voice_engine import VoiceEngine


SAMPLE_SCRIPTS = {
    "🎬 Ulusoy Digital - YouTube & Video Açılışı": (
        "Herkese merhaba arkadaşlar! Ben Muzaffer Ulusoy. Yeni bir videoya hepiniz hoş geldiniz.\n"
        "Bugün Ulusoy Digital stüdyolarında geliştirdiğimiz yeni nesil ses takipli teleprompter yazılımını inceliyoruz.\n"
        "Bu uygulamanın en büyük gücü, ben konuştukça sesimi kelime kelime takip edip metni tam konuşma hızımda otomatik kaydırması.\n"
        "Üstelik şu anda ekran kaydı alırken bu prompter penceresi video kaydında kesinlikle görünmüyor!\n"
        "Daha fazla dijital içerik ve yazılım çözümleri için ulusoydigital.com adresini ziyaret etmeyi ve kanalımıza abone olmayı unutmayın.\n"
        "Şimdi hep birlikte detaylara geçelim!"
    ),
    "💼 Dijital Pazarlama ve Marka Sunumu": (
        "Sayın konuklar ve değerli iş ortaklarımız, sunumumuza hoş geldiniz. Ben Muzaffer Ulusoy.\n"
        "Ulusoy Digital olarak, markanızı dijital dünyada en üst seviyeye taşıyacak yenilikçi stratejilerimizi sizlerle paylaşmaktan mutluluk duyuyorum.\n"
        "Günümüz dijital çağında etkileyici video prodüksiyonları ve akıcı konuşma deneyimi, izleyiciyle güven bağı kurmanın temel anahtarıdır.\n"
        "Gelişmiş teknolojilerimiz sayesinde kamera karşısında her zaman özgüvenli ve profesyonel bir duruş sergileyebilirsiniz.\n"
        "Detaylı bilgi ve projelerimiz için ulusoydigital.com üzerinden bize dilediğiniz zaman ulaşabilirsiniz. Teşekkürler."
    ),
    "🎓 Eğitim & Profesyonel İçerik Üretimi": (
        "Merhaba değerli takipçilerim,\n"
        "Bugünkü dersimizde dijital içerik üretiminde kamera karşısında akıcı ve kusursuz konuşma tekniklerini ele alıyoruz.\n"
        "Prompter kullanırken en önemli kural, metni okuyormuş gibi değil, izleyiciyle samimi bir sohbet ediyormuş hissi vermektir.\n"
        "Ulusoy Digital ses takipli prompter sistemi tam olarak bu doğallığı yakalamanızı sağlar."
    )
}


class EditorWindow(QWidget):
    script_applied = pyqtSignal(str)   # Emits script text to prompter
    settings_changed = pyqtSignal(dict) # Emits theme, mic, lang settings

    def __init__(self, voice_engine: VoiceEngine, parent=None):
        super().__init__(parent)
        self.voice_engine = voice_engine
        
        self.setWindowTitle("Ulusoy Digital Prompter - Metin Düzenleyici & Ayarlar")
        self.resize(720, 640)
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
        self._load_default_script()

    def _init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(18, 14, 18, 16)
        main_layout.setSpacing(12)

        # --- Brand Banner (Ulusoy Digital & Muzaffer Ulusoy) ---
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

        lbl_brand = QLabel("🚀 <b>ULUSOY DIGITAL</b> <span style='color:#8B949E;'>| Muzaffer Ulusoy</span>", brand_frame)
        lbl_brand.setStyleSheet("font-size: 14px; color: #00F0FF;")

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

        brand_layout.addWidget(lbl_brand)
        brand_layout.addStretch()
        brand_layout.addWidget(btn_website)
        main_layout.addWidget(brand_frame)

        # Tabs: 1. Konuşma Metni, 2. Ayarlar
        self.tabs = QTabWidget(self)
        
        # --- TAB 1: SCRIPT EDITOR ---
        self.tab_editor = QWidget()
        editor_layout = QVBoxLayout(self.tab_editor)
        editor_layout.setContentsMargins(14, 14, 14, 14)
        editor_layout.setSpacing(10)

        # Toolbar above editor
        toolbar = QHBoxLayout()
        toolbar.setSpacing(8)

        self.btn_load_file = QPushButton("📂 Metin Dosyası Aç (.txt)", self.tab_editor)
        self.btn_load_file.clicked.connect(self._load_file)

        self.btn_save_file = QPushButton("💾 Metni Kaydet", self.tab_editor)
        self.btn_save_file.clicked.connect(self._save_file)

        self.sample_combo = QComboBox(self.tab_editor)
        self.sample_combo.addItem("✨ Hazır Örnek Konuşma Metinleri...")
        for name in SAMPLE_SCRIPTS.keys():
            self.sample_combo.addItem(name)
        self.sample_combo.currentIndexChanged.connect(self._on_sample_selected)

        toolbar.addWidget(self.btn_load_file)
        toolbar.addWidget(self.btn_save_file)
        toolbar.addWidget(self.sample_combo)
        toolbar.addStretch()

        # Text Area
        self.text_edit = QTextEdit(self.tab_editor)
        self.text_edit.setPlaceholderText("Konuşma metninizi buraya yazın veya yapıştırın...")
        self.text_edit.textChanged.connect(self._update_stats)

        # Stats Bar (Words, characters, estimated duration)
        stats_bar = QHBoxLayout()
        self.lbl_word_count = QLabel("Toplam Kelime: 0", self.tab_editor)
        self.lbl_word_count.setStyleSheet("color: #C9D1D9; font-weight: 500;")
        
        self.lbl_char_count = QLabel("Karakter: 0", self.tab_editor)
        self.lbl_char_count.setStyleSheet("color: #8B949E;")

        self.lbl_est_time = QLabel("⏱️ Tahmini Okuma Süresi: 00:00", self.tab_editor)
        self.lbl_est_time.setStyleSheet("color: #00F0FF; font-weight: bold; font-size: 13px;")

        stats_bar.addWidget(self.lbl_word_count)
        stats_bar.addWidget(QLabel("•"))
        stats_bar.addWidget(self.lbl_char_count)
        stats_bar.addStretch()
        stats_bar.addWidget(self.lbl_est_time)

        editor_layout.addLayout(toolbar)
        editor_layout.addWidget(self.text_edit, 1)
        editor_layout.addLayout(stats_bar)
        self.tabs.addTab(self.tab_editor, "📝 Konuşma Metni")

        # --- TAB 2: SETTINGS (Tamamen Türkçeleştirilmiş) ---
        self.tab_settings = QWidget()
        settings_layout = QVBoxLayout(self.tab_settings)
        settings_layout.setContentsMargins(18, 18, 18, 18)
        settings_layout.setSpacing(18)

        # 1. Ses ve Mikrofon Ayarları
        group_voice = QGroupBox("🎙️ Ses Tanıma ve Mikrofon Ayarları", self.tab_settings)
        group_voice.setStyleSheet("QGroupBox { font-weight: bold; color: #00F0FF; font-size: 13px; }")
        gv_layout = QVBoxLayout(group_voice)
        gv_layout.setContentsMargins(14, 18, 14, 14)
        gv_layout.setSpacing(12)

        # Ses Tanıma Dili
        row_lang = QHBoxLayout()
        lbl_lang = QLabel("Ses Tanıma Dili:", group_voice)
        lbl_lang.setStyleSheet("color: #E6EDF3; font-weight: 500;")
        self.combo_lang = QComboBox(group_voice)
        self.combo_lang.addItem("🇹🇷 Türkçe (tr-TR)", "tr-TR")
        self.combo_lang.addItem("🇺🇸 İngilizce (en-US)", "en-US")
        self.combo_lang.addItem("🇩🇪 Almanca (de-DE)", "de-DE")
        self.combo_lang.addItem("🇪🇸 İspanyolca (es-ES)", "es-ES")
        self.combo_lang.currentIndexChanged.connect(self._on_lang_changed)
        row_lang.addWidget(lbl_lang)
        row_lang.addWidget(self.combo_lang, 1)
        gv_layout.addLayout(row_lang)

        # Mikrofon Aygıtı (Düzeltilmiş Türkçe İsimler)
        row_mic = QHBoxLayout()
        lbl_mic = QLabel("Kullanılacak Mikrofon:", group_voice)
        lbl_mic.setStyleSheet("color: #E6EDF3; font-weight: 500;")
        self.combo_mic = QComboBox(group_voice)
        self._populate_microphones()
        self.combo_mic.currentIndexChanged.connect(self._on_mic_changed)
        row_mic.addWidget(lbl_mic)
        row_mic.addWidget(self.combo_mic, 1)
        gv_layout.addLayout(row_mic)

        # Mikrofon Yenile Butonu
        btn_refresh_mic = QPushButton("🔄 Mikrofon Listesini Yenile", group_voice)
        btn_refresh_mic.clicked.connect(self._populate_microphones)
        gv_layout.addWidget(btn_refresh_mic)

        settings_layout.addWidget(group_voice)

        # 2. Görünüm ve Vurgulama Ayarları
        group_theme = QGroupBox("🎨 Görünüm ve Vurgu Teması", self.tab_settings)
        group_theme.setStyleSheet("QGroupBox { font-weight: bold; color: #00F0FF; font-size: 13px; }")
        gt_layout = QVBoxLayout(group_theme)
        gt_layout.setContentsMargins(14, 18, 14, 14)
        gt_layout.setSpacing(12)

        # Renk Teması
        row_theme = QHBoxLayout()
        lbl_theme = QLabel("Aktif Kelime Vurgu Rengi:", group_theme)
        lbl_theme.setStyleSheet("color: #E6EDF3; font-weight: 500;")
        self.combo_theme = QComboBox(group_theme)
        self.combo_theme.addItem("💎 Neon Turkuaz (Cyan)", "Cyan")
        self.combo_theme.addItem("🌟 Altın Sarısı (Gold)", "Gold")
        self.combo_theme.addItem("🌿 Zümrüt Yeşili (Emerald)", "Emerald")
        self.combo_theme.addItem("⚪ Klasik Beyaz", "Classic White")
        row_theme.addWidget(lbl_theme)
        row_theme.addWidget(self.combo_theme, 1)
        gt_layout.addLayout(row_theme)

        settings_layout.addWidget(group_theme)
        settings_layout.addStretch()

        self.tabs.addTab(self.tab_settings, "⚙️ Ayarlar")

        # Bottom Action Bar
        btn_layout = QHBoxLayout()
        
        lbl_footer = QLabel("Geliştirici: <b>Muzaffer Ulusoy</b> | Ulusoy Digital", self)
        lbl_footer.setStyleSheet("color: #6E7681; font-size: 11px;")

        self.btn_apply = QPushButton("🚀 Prompter'a Yükle ve Başlat", self)
        self.btn_apply.setObjectName("btnApply")
        self.btn_apply.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_apply.clicked.connect(self._apply_script)

        btn_layout.addWidget(lbl_footer)
        btn_layout.addStretch()
        btn_layout.addWidget(self.btn_apply)

        main_layout.addWidget(self.tabs, 1)
        main_layout.addLayout(btn_layout)

    def _load_default_script(self):
        self.text_edit.setPlainText(SAMPLE_SCRIPTS["🎬 Ulusoy Digital - YouTube & Video Açılışı"])
        self._update_stats()

    def _populate_microphones(self):
        self.combo_mic.clear()
        self.combo_mic.addItem("🎤 Varsayılan Sistem Mikrofonu", None)
        mics = VoiceEngine.get_microphone_list()
        for idx, clean_name in mics:
            self.combo_mic.addItem(f"{idx}: {clean_name}", idx)

    def _update_stats(self):
        text = self.text_edit.toPlainText().strip()
        words = text.split()
        word_count = len(words)
        char_count = len(text)
        
        # Ortalama konuşma hızı: Dakikada 130 kelime
        seconds_total = int((word_count / 130.0) * 60)
        minutes = seconds_total // 60
        seconds = seconds_total % 60
        
        self.lbl_word_count.setText(f"Toplam Kelime: {word_count}")
        self.lbl_char_count.setText(f"Karakter: {char_count}")
        self.lbl_est_time.setText(f"⏱️ Tahmini Okuma Süresi: {minutes:02d}:{seconds:02d}")

    def _on_sample_selected(self, index: int):
        if index > 0:
            key = self.sample_combo.currentText()
            if key in SAMPLE_SCRIPTS:
                self.text_edit.setPlainText(SAMPLE_SCRIPTS[key])
                self._update_stats()

    def _load_file(self):
        path, _ = QFileDialog.getOpenFileName(self, "Metin Dosyası Aç", "", "Metin Dosyaları (*.txt);;Tüm Dosyalar (*.*)")
        if path:
            try:
                with open(path, "r", encoding="utf-8") as f:
                    self.text_edit.setPlainText(f.read())
                    self._update_stats()
            except Exception as e:
                QMessageBox.warning(self, "Hata", f"Dosya açılamadı: {e}")

    def _save_file(self):
        path, _ = QFileDialog.getSaveFileName(self, "Metni Kaydet", "ulusoy_prompter_metin.txt", "Metin Dosyaları (*.txt)")
        if path:
            try:
                with open(path, "w", encoding="utf-8") as f:
                    f.write(self.text_edit.toPlainText())
                QMessageBox.information(self, "Başarılı", "Konuşma metniniz başarıyla kaydedildi.")
            except Exception as e:
                QMessageBox.warning(self, "Hata", f"Dosya kaydedilemedi: {e}")

    def _on_lang_changed(self):
        lang_code = self.combo_lang.currentData()
        self.voice_engine.set_language(lang_code)

    def _on_mic_changed(self):
        mic_idx = self.combo_mic.currentData()
        self.voice_engine.set_mic_device(mic_idx)

    def _apply_script(self):
        text = self.text_edit.toPlainText().strip()
        if not text:
            QMessageBox.warning(self, "Uyarı", "Lütfen önce bir konuşma metni girin.")
            return

        selected_theme = self.combo_theme.currentData() or "Cyan"
        settings = {
            "theme": selected_theme
        }
        self.settings_changed.emit(settings)
        
        self.script_applied.emit(text)
        self.hide()
