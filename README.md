# 👻 GhostPrompter

<p align="center">
  <img src="https://img.shields.io/badge/Author-Muzaffer%20Ulusoy-00F0FF?style=for-the-badge" alt="Author">
  <img src="https://img.shields.io/badge/Brand-Ulusoy%20Digital-7928CA?style=for-the-badge" alt="Brand">
  <img src="https://img.shields.io/badge/Platform-Windows%2010%20%2F%2011-0078D6?style=for-the-badge&logo=windows" alt="Platform">
  <img src="https://img.shields.io/badge/Language-English%20%2F%20T%C3%BCrk%C3%A7e-success?style=for-the-badge" alt="Language">
  <img src="https://img.shields.io/badge/License-MIT-green?style=for-the-badge" alt="License">
</p>

<p align="center">
  <b>🎙️ Next-Gen Voice-Activated & Screen-Recorder-Invisible Teleprompter for Windows.</b><br>
  <i>Follows your speech word-by-word with zero latency (sub-30ms) while remaining 100% invisible in screen recordings (OBS, Loom, Zoom, Teams, Camtasia, Windows Game Bar).</i>
</p>

<p align="center">
  🌐 <b>Website:</b> <a href="https://ulusoydigital.com">ulusoydigital.com</a> &nbsp;|&nbsp; 
  👤 <b>Developer:</b> <a href="https://github.com/muqo16">Muzaffer Ulusoy (@muqo16)</a>
</p>

---

## 🌍 Language / Dil Seçimi
* [English (Global)](#-english-documentation)
* [Türkçe (Dokümantasyon)](#-türkçe-dokümantasyon)

---

# 🇺🇸 English Documentation

### ✨ Key Features

- **🛡️ 100% Stealth Mode (Invisible to Screen Recorders)**:
  - Powered by Windows Native `SetWindowDisplayAffinity(WDA_EXCLUDEFROMCAPTURE = 0x11)` API.
  - Visible and crystal-clear on your physical monitor, but **OBS Studio, Loom, Zoom screen share, MS Teams, and Windows Screen Recorder** completely ignore the window (capturing whatever is behind it).
- **⚡ Sub-30ms Zero-Latency Voice Tracking**:
  - Powered by local offline neural Vosk engine (supports English & Turkish).
  - Matches spoken words in real time as you pronounce them, highlighting active words karaoke-style.
- **🖱️ Click-Through Mode (F8 Key)**:
  - Toggle mouse transparency with a single key. Click links, buttons, and navigate websites/apps directly behind the prompter while it floats on top and tracks your voice!
- **📏 Slim Camera Bar Preset**:
  - Dock prompter horizontally right under your webcam to maintain direct camera eye contact while leaving 85% of your screen open for your browser or slide deck.
- **🪞 100% Transparent Glass & Mirror Mode**:
  - Adjustable 0% to 100% background transparency. Full support for beam-splitter physical prompter glass (`M` key).

### 🚀 Quick Start
1. Double-click **`run.bat`** to start GhostPrompter immediately.
2. Click the **`🇹🇷 TR / 🇺🇸 EN`** button on the top header to switch language.

---

# 🇹🇷 Türkçe Dokümantasyon

### ✨ Temel Özellikler

- **🛡️ %100 Hayalet Modu (Ekran Kaydedicilerde Görünmezlik)**:
  - Windows yerel `SetWindowDisplayAffinity(0x11)` API'si ile çalışır.
  - Siz monitörünüzde net görürken; **OBS Studio, Loom, Zoom, Teams ve Windows Ekran Kaydı** prompterı tamamen yok sayar.
- **⚡ Sıfır Gecikmeli Yerel Ses Takibi (Sub-30ms Vosk Engine)**:
  - Tamamen bilgisayarınızda yerel çalışan yapay zeka ile konuştuğunuz kelimeleri 30 milisaniyede yakalar ve parlatır.
- **🖱️ Arkaya Tıklama Modu (Click-Through - F8 Tuşu)**:
  - Prompter açıkken arkadaki web sayfalarına, butonlara veya uygulamalara doğrudan tıklayabilirsiniz.
- **📏 Kamera Çubuğu Modu**:
  - Prompterı kameranın tam altına ince şerit olarak yerleştirir, ekranın altını tamamen açık bırakır.
- **🌐 Çift Dil Desteği**:
  - Tek tıkla Türkçe ve İngilizce arasında anında geçiş yapabilirsiniz.

---

## ⌨️ Keyboard Shortcuts / Klavye Kısayolları

| Shortcut / Kısayol | Function (EN) | İşlev (TR) |
| :--- | :--- | :--- |
| **Space / Boşluk** | Play / Pause | Oynat / Duraklat |
| **F8** | Toggle Click-Through Mode | Arkaya Tıklama Modunu Aç/Kapat |
| **R** | Reset Script to Beginning | Metni Başa Sar |
| **G** | Toggle Stealth Mode | Kayıtta Gizlilik Modunu Aç/Kapat |
| **M** | Flip Horizontal (Mirror Glass) | Ayna Modu (Prompter Camı İçin) |
| **Up / Down Arrow** | Increase / Decrease Font Size | Font Boyutunu Büyüt / Küçült |
| **Left / Right Arrow** | Step 1 Word Back / Forward | 1 Kelime Geri / İleri Git |
| **Left Click (Word)** | Jump directly to clicked word | Tıklanan kelimeye anında zıpla |
| **Esc** | Minimize to taskbar | Simge durumuna küçült |

---

## 👨‍💻 Developer & Brand

* **Developer:** Muzaffer Ulusoy
* **GitHub Profile:** [@muqo16](https://github.com/muqo16)
* **Official Website:** [ulusoydigital.com](https://ulusoydigital.com)
* **License:** [MIT License](LICENSE) (2026 Muzaffer Ulusoy)
