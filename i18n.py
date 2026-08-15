"""
Internationalization (i18n) Module
Supports full instant switching between Turkish (TR) and English (EN).
"""

from typing import Dict, Any

TRANSLATIONS: Dict[str, Dict[str, str]] = {
    "tr": {
        "app_title": "GhostPrompter - Muzaffer Ulusoy",
        "brand_name": "🚀 ULUSOY DIGITAL",
        "author_tag": "| Muzaffer Ulusoy",
        "stealth_hidden": "🛡️ Kayıtta Gizli",
        "stealth_visible": "👁️ Kayıtta Görünür",
        "stealth_tip": "OBS, Loom ve Ekran Kaydedicilerde bu pencere görünmez!\nTıklayarak gizlilik modunu açıp kapatabilirsiniz.",
        "click_through_off": "🖱️ Arkaya Tıkla (F8)",
        "click_through_on": "🔓 Arkaya Tıkla: AÇIK (F8)",
        "click_through_tip": "Tıklama Geçirgenliği (F8 Tuşu):\nAktif edildiğinde fareniz doğrudan arkadaki tarayıcıya/uygulamaya tıklar.\nPrompter üstte şeffaf kalır ve sesinizi takip eder!",
        "top_banner_btn": "📏 Kamera Çubuğu",
        "normal_size_btn": "📱 Normal Boyut",
        "top_banner_tip": "Prompterı kameranın tam altına ince yatay şerit yapar.\nBöylece ekranın altındaki tüm buton ve uygulamaları rahatça görürsünüz!",
        "status_waiting": "🎤 Konuşmanız bekleniyor...",
        "status_listening": "🎤 Konuşmanız canlı dinleniyor (Sıfır Gecikme)...",
        "status_paused": "⏸️ Ses takibi duraklatıldı",
        "status_stopped": "⏹️ Ses takibi kapalı",
        "status_click_through": "🔓 Fareniz arkadaki uygulamaya tıklar (Kapatmak için F8)",
        "status_manual": "⌨️ Manuel akış modu",
        "mode_voice": "🎤 Ses Takipli",
        "mode_manual": "⌨️ Manuel Hız",
        "mode_tip": "Konuşmanızla senkronize kayma modu (Sadece siz konuştuğunuzda kayar)",
        "btn_play_pause_tip": "Oynat / Duraklat (Boşluk Tuşu)",
        "btn_reset": "⏮️ Başa Sar",
        "btn_reset_tip": "Metni en başa sar (R Tuşu)",
        "btn_font_minus_tip": "Yazı Boyutunu Küçült (Aşağı Ok)",
        "btn_font_plus_tip": "Yazı Boyutunu Büyüt (Yukarı Ok)",
        "btn_mirror": "🪞 Ayna",
        "btn_mirror_tip": "Prompter camı için görüntüyü yatay ters çevir (M Tuşu)",
        "lbl_opacity": "Şeffaflık:",
        "opacity_tip": "Arka plan şeffaflığı (0% = Arkadaki ekran tamamen görünür)",
        "btn_editor_tip": "Metin Düzenleyici ve Ayarlar Paneli",
        "btn_restore_size_tip": "Rahat pencere boyutuna dön (Ctrl+0)",
        "btn_pin_tip": "Her Zaman Üstte Sabitle",
        "btn_min_tip": "Simge Durumuna Küçült / Aşağı İndir",
        "btn_max_tip": "Tam Ekran / Büyüt",
        "btn_restore_tip": "Normal Boyuta Dön",
        "btn_close_tip": "Kapat",
        "editor_title": "GhostPrompter - Metin Düzenleyici & Ayarlar",
        "tab_script": "📝 Konuşma Metni",
        "tab_settings": "⚙️ Ayarlar",
        "btn_open_file": "📂 Metin Dosyası Aç (.txt)",
        "btn_save_file": "💾 Metni Kaydet",
        "sample_placeholder": "✨ Hazır Örnek Konuşma Metinleri...",
        "text_placeholder": "Konuşma metninizi buraya yazın veya yapıştırın...",
        "lbl_word_count": "Toplam Kelime:",
        "lbl_char_count": "Karakter:",
        "lbl_est_time": "⏱️ Tahmini Okuma Süresi:",
        "group_voice": "🎙️ Ses Tanıma ve Mikrofon Ayarları",
        "lbl_lang": "Ses Tanıma Dili:",
        "lbl_mic": "Kullanılacak Mikrofon:",
        "btn_refresh_mic": "🔄 Mikrofon Listesini Yenile",
        "group_theme": "🎨 Görünüm ve Vurgu Teması",
        "lbl_theme": "Aktif Kelime Vurgu Rengi:",
        "btn_apply": "🚀 Prompter'a Yükle ve Başlat",
        "footer_text": "Geliştirici: <b>Muzaffer Ulusoy</b> | Ulusoy Digital",
        "default_mic": "🎤 Varsayılan Sistem Mikrofonu",
        "warn_empty": "Lütfen önce bir konuşma metni girin.",
        "save_success": "Konuşma metniniz başarıyla kaydedildi.",
        "lang_name_tr": "🇹🇷 Türkçe (Turkish)",
        "lang_name_en": "🇺🇸 İngilizce (English)",
        "theme_cyan": "💎 Neon Turkuaz (Cyan)",
        "theme_gold": "🌟 Altın Sarısı (Gold)",
        "theme_emerald": "🌿 Zümrüt Yeşili (Emerald)",
        "theme_white": "⚪ Klasik Beyaz (White)"
    },
    "en": {
        "app_title": "GhostPrompter - Muzaffer Ulusoy",
        "brand_name": "🚀 ULUSOY DIGITAL",
        "author_tag": "| Muzaffer Ulusoy",
        "stealth_hidden": "🛡️ Hidden on Recording",
        "stealth_visible": "👁️ Visible on Recording",
        "stealth_tip": "This window is invisible to OBS, Loom, Zoom & Screen Recorders!\nClick to toggle stealth mode.",
        "click_through_off": "🖱️ Click-Through (F8)",
        "click_through_on": "🔓 Click-Through: ON (F8)",
        "click_through_tip": "Click-Through Mode (F8 Key):\nWhen enabled, your mouse clicks pass straight through to background apps/browser.\nPrompter stays on top and tracks your voice seamlessly!",
        "top_banner_btn": "📏 Top Camera Bar",
        "normal_size_btn": "📱 Normal Size",
        "top_banner_tip": "Docks prompter as a slim banner right under your webcam.\nLeaves the entire screen below open for your browser & apps!",
        "status_waiting": "🎤 Waiting for speech...",
        "status_listening": "🎤 Listening live (Zero Latency)...",
        "status_paused": "⏸️ Voice tracking paused",
        "status_stopped": "⏹️ Voice tracking stopped",
        "status_click_through": "🔓 Mouse clicks through to background apps (Press F8 to toggle)",
        "status_manual": "⌨️ Manual scroll mode",
        "mode_voice": "🎤 Voice-Synced",
        "mode_manual": "⌨️ Manual Speed",
        "mode_tip": "Speech follow mode (Scrolls only when you speak)",
        "btn_play_pause_tip": "Play / Pause (Spacebar)",
        "btn_reset": "⏮️ Reset",
        "btn_reset_tip": "Rewind text to top (R Key)",
        "btn_font_minus_tip": "Decrease Font Size (Down Arrow)",
        "btn_font_plus_tip": "Increase Font Size (Up Arrow)",
        "btn_mirror": "🪞 Mirror",
        "btn_mirror_tip": "Flip horizontally for teleprompter glass (M Key)",
        "lbl_opacity": "Opacity:",
        "opacity_tip": "Background opacity (0% = 100% transparent glass)",
        "btn_editor_tip": "Script Editor & Settings Panel",
        "btn_restore_size_tip": "Restore Comfortable Size (Ctrl+0)",
        "btn_pin_tip": "Pin Always on Top",
        "btn_min_tip": "Minimize",
        "btn_max_tip": "Maximize Window",
        "btn_restore_tip": "Restore Down",
        "btn_close_tip": "Close",
        "editor_title": "GhostPrompter - Script Editor & Settings",
        "tab_script": "📝 Speech Script",
        "tab_settings": "⚙️ Settings",
        "btn_open_file": "📂 Open File (.txt)",
        "btn_save_file": "💾 Save Script",
        "sample_placeholder": "✨ Choose a Sample Script...",
        "text_placeholder": "Type or paste your presentation script here...",
        "lbl_word_count": "Total Words:",
        "lbl_char_count": "Characters:",
        "lbl_est_time": "⏱️ Estimated Reading Time:",
        "group_voice": "🎙️ Speech Recognition & Microphone",
        "lbl_lang": "Recognition Language:",
        "lbl_mic": "Microphone Device:",
        "btn_refresh_mic": "🔄 Refresh Microphones",
        "group_theme": "🎨 Visual Theme & Active Highlight",
        "lbl_theme": "Active Word Glow Color:",
        "btn_apply": "🚀 Load to Prompter & Start",
        "footer_text": "Developer: <b>Muzaffer Ulusoy</b> | Ulusoy Digital",
        "default_mic": "🎤 Default System Microphone",
        "warn_empty": "Please enter a speech script first.",
        "save_success": "Script successfully saved.",
        "lang_name_tr": "🇹🇷 Turkish (Türkçe)",
        "lang_name_en": "🇺🇸 English",
        "theme_cyan": "💎 Neon Cyan",
        "theme_gold": "🌟 Bright Gold",
        "theme_emerald": "🌿 Emerald Green",
        "theme_white": "⚪ Classic White"
    }
}


SAMPLE_SCRIPTS_I18N = {
    "tr": {
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
    },
    "en": {
        "🎬 Ulusoy Digital - YouTube & Video Intro": (
            "Hello everyone and welcome back to another video! I am Muzaffer Ulusoy.\n"
            "Today we are taking a deep dive into our next-generation voice-activated teleprompter software developed at Ulusoy Digital.\n"
            "The most powerful feature of this tool is how it follows my voice word by word in real time, automatically scrolling at my exact reading pace.\n"
            "Best of all, while I record my screen, this prompter window is completely invisible to screen recorders like OBS and Loom!\n"
            "Don't forget to subscribe to our channel and visit ulusoydigital.com for more innovative digital tools.\n"
            "Now let's jump right into the demo!"
        ),
        "💼 Professional Keynote & Product Pitch": (
            "Welcome distinguished guests and partners. My name is Muzaffer Ulusoy.\n"
            "On behalf of Ulusoy Digital, I am thrilled to present our innovative software solutions designed to elevate your content creation workflow.\n"
            "In today's digital landscape, delivering a seamless and confident presentation on camera is the key to engaging your audience.\n"
            "With our stealth teleprompter technology, you maintain natural eye contact while delivering your message flawlessly.\n"
            "Feel free to connect with us at ulusoydigital.com. Thank you for your time."
        ),
        "🎓 Masterclass & Tech Tutorial": (
            "Hello everyone and welcome to today's masterclass.\n"
            "In this session, we will explore high-performance audio processing and speech synchronization techniques.\n"
            "The secret to a great teleprompter experience is zero latency: matching words the exact millisecond they are spoken without jumping ahead.\n"
            "Let's get started step by step."
        )
    }
}


class I18nManager:
    _current_lang = "tr"

    @classmethod
    def set_language(cls, lang_code: str):
        if lang_code in ("tr", "en"):
            cls._current_lang = lang_code

    @classmethod
    def get_language(cls) -> str:
        return cls._current_lang

    @classmethod
    def t(cls, key: str) -> str:
        lang_dict = TRANSLATIONS.get(cls._current_lang, TRANSLATIONS["tr"])
        return lang_dict.get(key, key)

    @classmethod
    def get_samples(cls) -> Dict[str, str]:
        return SAMPLE_SCRIPTS_I18N.get(cls._current_lang, SAMPLE_SCRIPTS_I18N["tr"])
