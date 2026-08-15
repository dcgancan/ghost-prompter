# 👻 GhostPrompter

<p align="center">
  <img src="https://img.shields.io/badge/Yazar-Muzaffer%20Ulusoy-00F0FF?style=for-the-badge" alt="Yazar">
  <img src="https://img.shields.io/badge/Marka-Ulusoy%20Digital-7928CA?style=for-the-badge" alt="Marka">
  <img src="https://img.shields.io/badge/Platform-Windows%2010%20%2F%2011-0078D6?style=for-the-badge&logo=windows" alt="Platform">
  <img src="https://img.shields.io/badge/Python-3.10%2B-3776AB?style=for-the-badge&logo=python" alt="Python">
  <img src="https://img.shields.io/badge/Lisans-MIT-success?style=for-the-badge" alt="Lisans">
</p>

<p align="center">
  <b>🎙️ Ekran kaydı alırken mikrofondan sesinizi kelime kelime takip eden ve video kaydında (OBS, Loom, Zoom, Game Bar vb.) %100 görünmez olan profesyonel yeni nesil Teleprompter.</b>
</p>

<p align="center">
  🌐 <b>Web Sitesi:</b> <a href="https://ulusoydigital.com">ulusoydigital.com</a> &nbsp;|&nbsp; 
  👤 <b>Geliştirici:</b> <a href="https://github.com/muqo16">Muzaffer Ulusoy (@muqo16)</a>
</p>

---

## 🌟 Neden GhostPrompter?

Bir video, eğitim veya canlı sunum kaydederken prompter kullanmak istersiniz ancak prompter penceresinin videoda veya ekran paylaşımında görünmesini istemezsiniz. **GhostPrompter**, Windows işletim sisteminin doğrudan grafik katmanına entegre olarak bu sorunu çözer.

* 🛡️ **Kayıtta %100 Görünmezlik (Stealth Mode)**: Monitörünüzde prompterı rahatça okursunuz; ancak **OBS Studio, Loom, Camtasia, Zoom, Discord, Teams veya Windows Ekran Alıntısı Aracı** prompterı tamamen yok sayarak arkasındaki masaüstünü/uygulamayı kaydeder.
* 🎤 **Akıllı Ses Takibi (Voice-Follow & Karaoke Sync)**: Siz mikrofona konuştukça sesinizi gerçek zamanlı dinler, okuduğunuz kelimeleri neon ışıkla parlatır ve metni konuşma temponuza göre 60 FPS akıcılıkla otomatik kaydırır.
* 🎯 **Göz Hizası Lazer Kılavuzu**: Tam kamera lensine bakarak doğal konuşabilmeniz için okuma çizgisi.
* 🌓 **Şeffaflık & Ayna Modu**: Şeffaf arka plan desteği ve fiziksel yansıtmalı prompter camları için tek tuşla (`M`) yatay ters çevirme.

---

## 🚀 Hızlı Başlangıç

### 1. Yöntem: Tek Tıkla Başlatma (Tavsiye Edilen)
Projeyi indirdikten sonra klasördeki **`run.bat`** dosyasına çift tıklayarak GhostPrompter'ı anında başlatabilirsiniz.

### 2. Yöntem: Terminal ile Çalıştırma
```bash
# 1. Depoyu klonlayın
git clone https://github.com/muqo16/ghost-prompter.git
cd ghost-prompter

# 2. Bağımlılıkları yükleyin
pip install -r requirements.txt

# 3. Başlatın
python main.py
```

---

## ⌨️ Klavye Kısayolları

| Kısayol | İşlev |
| :--- | :--- |
| **Boşluk (Space)** | Oynat / Duraklat |
| **R** | Metni en başa sar (Reset) |
| **G** | Hayalet Modunu Aç / Kapat (Kayıtta Gizle) |
| **M** | Ayna Modu (Prompter camı için yatay çevir) |
| **Yukarı / Aşağı Ok** | Font Boyutunu Büyüt / Küçült |
| **Sol / Sağ Ok** | 1 Kelime Geri / İleri Git |
| **Sol Tık (Kelime)** | Tıklanan kelimeye anında odaklan |
| **Fare Tekerleği** | Manuel serbest kaydırma |
| **Esc** | Simge durumuna küçült |

---

## 🛠️ Proje Mimarisi

```
├── main.py              # Uygulama ana başlatıcısı
├── prompter_window.py   # Şeffaf ana GhostPrompter penceresi ve kontrol çubuğu
├── prompter_view.py     # 60 FPS donanım hızlandırmalı metin çizim & karaoke motoru
├── voice_engine.py      # Gerçek zamanlı mikrofon dinleme & konuşma tanıma iş parçacığı
├── word_matcher.py      # Türkçe fonetik normalizasyon & kayan pencere eşleme algoritması
├── stealth.py           # Windows Win32 SetWindowDisplayAffinity görünmezlik modülü
├── editor_window.py     # Metin düzenleyici, istatistikler ve Türkçe ayarlar paneli
├── run.bat              # Windows tek tıkla başlatıcı
├── requirements.txt     # Python bağımlılıkları (PyQt6, SpeechRecognition, PyAudio, RapidFuzz)
└── LICENSE              # MIT Lisansı (Muzaffer Ulusoy / Ulusoy Digital)
```

---

## 📄 Lisans

Bu proje [MIT Lisansı](LICENSE) altında lisanslanmıştır.

---

## 👨‍💻 Geliştirici & İletişim

* **Geliştirici:** Muzaffer Ulusoy
* **GitHub:** [@muqo16](https://github.com/muqo16)
* **Marka / Web Sitesi:** [ulusoydigital.com](https://ulusoydigital.com)
