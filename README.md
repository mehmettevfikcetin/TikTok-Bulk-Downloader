<div align="center">

# 🎬 TikTok Bulk Downloader

### TikTok Toplu Video İndirici

<br>

[![Version](https://img.shields.io/badge/version-1.8.9-blue?style=for-the-badge&logo=semver)](https://github.com/mehmettevfikcetin/TikTok-Bulk-Downloader/releases/latest)
[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![PyQt6](https://img.shields.io/badge/PyQt6-GUI-41CD52?style=for-the-badge&logo=qt&logoColor=white)](https://www.riverbankcomputing.com/software/pyqt/)
[![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)](LICENSE)
[![Stars](https://img.shields.io/github/stars/mehmettevfikcetin/TikTok-Bulk-Downloader?style=for-the-badge&logo=github)](https://github.com/mehmettevfikcetin/TikTok-Bulk-Downloader/stargazers)

<br>

**[🇹🇷 Türkçe](#-türkçe)** · **[🇬🇧 English](#-english)**

<br>

<img src="https://raw.githubusercontent.com/mehmettevfikcetin/TikTok-Bulk-Downloader/main/icon.ico" width="120" alt="TikTok Bulk Downloader Logo">

<br>

> TikTok koleksiyonlarınızdaki videoları toplu olarak indirin.<br>
> Bulk download videos from your TikTok collections.

</div>

<br>

---

<br>

# 🇹🇷 Türkçe

## 📋 Nedir?

**TikTok Toplu Video İndirici**, TikTok'ta kaydettiğiniz koleksiyonlardaki videoları toplu olarak bilgisayarınıza indirmenizi sağlayan masaüstü uygulamasıdır. Modern koyu tema arayüzü, otomatik güncelleme sistemi ve akıllı atlama mekanizması ile kolay ve hızlı kullanım sunar.

## ✨ Özellikler

| Özellik | Açıklama |
|---------|----------|
| 📦 **Toplu İndirme** | Koleksiyondaki tüm videoları tek seferde indirir |
| ⚡ **Akıllı Atlama** | Daha önce indirilen videoları otomatik algılar ve atlar |
| 🎯 **Otomatik Link Bulma** | yt-dlp ile koleksiyon sayfasındaki tüm linkleri otomatik çeker |
| 🎨 **Modern Arayüz** | Catppuccin Mocha temalı şık koyu tema tasarımı |
| 📊 **Detaylı İlerleme** | Her video için ayrı + toplam ilerleme çubuğu |
| 📝 **Hata Raporlama** | İndirilemeyen videoların detaylı listesi ve kopyalama imkanı |
| 🔄 **Otomatik Güncelleme** | Yeni sürüm çıktığında otomatik bildirim ve tek tıkla güncelleme |
| 🔒 **Anti-Bot Koruma** | TikTok engellemelerini önlemek için akıllı bekleme süreleri |
| 🎬 **FFmpeg Entegrasyonu** | Ses/görüntü senkronizasyonu ve format dönüşümü |
| 📂 **Klasör Yönetimi** | İndirme klasörünü seçme ve hızlı açma |

## 🛠️ Kurulum

### Hazır .exe ile (Önerilen)

1. [**Releases**](https://github.com/mehmettevfikcetin/TikTok-Bulk-Downloader/releases/latest) sayfasından en son `.exe` dosyasını indirin
2. Çalıştırın — kurulum gerekmez!

### Kaynak Koddan

```bash
# Projeyi indirin
git clone https://github.com/mehmettevfikcetin/TikTok-Bulk-Downloader.git
cd TikTok-Bulk-Downloader

# Kütüphaneleri yükleyin
pip install PyQt6 requests

# Ek gereksinimler (aynı klasöre koyun)
# - yt-dlp.exe  → https://github.com/yt-dlp/yt-dlp/releases
# - ffmpeg.exe  → https://ffmpeg.org/download.html

# Uygulamayı başlatın
python tiktok_downloader.py
```

## 🚀 Kullanım Rehberi

### Adım 1 — Çerez Dosyasını Hazırlayın

1. Chrome veya Edge tarayıcınıza **"Get cookies.txt LOCALLY"** eklentisini kurun
2. [TikTok.com](https://www.tiktok.com)'a giriş yapın
3. İndirmek istediğiniz koleksiyon sayfasına gidin
4. Eklenti simgesine tıklayın → **"Export All Cookies"** ile `.txt` dosyasını kaydedin

### Adım 2 — Linkleri Getirin

1. Uygulamada **"📂 Seç"** butonuyla çerez dosyasını seçin
2. **Hedef URL** alanına koleksiyon sayfasının linkini yapıştırın
3. **"🎯 Bağlantıları Getir"** butonuna tıklayın
4. Tüm video linkleri otomatik olarak listelenecektir

### Adım 3 — İndirin

1. **"📁 Gözat"** ile indirme klasörünü seçin
2. **"⚡ İndirmeyi Başlat"** butonuna tıklayın
3. İlerlemeyi tablodaki durum çubuklarından takip edin

> 💡 **İpucu:** Daha önce indirdiğiniz videolar otomatik olarak atlanır, böylece aynı koleksiyonu tekrar indirmeye çalışsanız bile zaman kaybetmezsiniz.

## ⚙️ Gereksinimler

| Bileşen | Minimum |
|---------|---------|
| İşletim Sistemi | Windows 10/11 |
| Python | 3.10+ (kaynak koddan çalıştırma için) |
| PyQt6 | 6.x |
| yt-dlp | Güncel sürüm |
| FFmpeg | Güncel sürüm |

<br>

---

<br>

# 🇬🇧 English

## 📋 What Is It?

**TikTok Bulk Downloader** is a desktop application that lets you bulk download videos from your saved TikTok collections to your computer. It features a modern dark theme UI, automatic updates, and smart skip mechanisms for a smooth experience.

## ✨ Features

| Feature | Description |
|---------|-------------|
| 📦 **Bulk Download** | Downloads all videos in a collection at once |
| ⚡ **Smart Skip** | Automatically detects and skips previously downloaded videos |
| 🎯 **Auto Link Fetching** | Extracts all video links from a collection page via yt-dlp |
| 🎨 **Modern UI** | Sleek dark theme inspired by Catppuccin Mocha |
| 📊 **Detailed Progress** | Individual + total progress bars for every video |
| 📝 **Error Reporting** | Detailed list of failed downloads with copy functionality |
| 🔄 **Auto Update** | Notifies and updates with one click when a new version is released |
| 🔒 **Anti-Bot Protection** | Smart delays to avoid TikTok rate-limiting |
| 🎬 **FFmpeg Integration** | Audio/video sync and format conversion |
| 📂 **Folder Management** | Download folder selection and quick open |

## 🛠️ Installation

### Pre-built .exe (Recommended)

1. Download the latest `.exe` from [**Releases**](https://github.com/mehmettevfikcetin/TikTok-Bulk-Downloader/releases/latest)
2. Run it — no installation required!

### From Source

```bash
# Clone the repository
git clone https://github.com/mehmettevfikcetin/TikTok-Bulk-Downloader.git
cd TikTok-Bulk-Downloader

# Install dependencies
pip install PyQt6 requests

# Additional requirements (place in the same folder)
# - yt-dlp.exe  → https://github.com/yt-dlp/yt-dlp/releases
# - ffmpeg.exe  → https://ffmpeg.org/download.html

# Run the application
python tiktok_downloader.py
```

## 🚀 Usage Guide

### Step 1 — Prepare Cookie File

1. Install the **"Get cookies.txt LOCALLY"** extension on Chrome or Edge
2. Log in to [TikTok.com](https://www.tiktok.com)
3. Navigate to the collection page you want to download
4. Click the extension icon → **"Export All Cookies"** to save the `.txt` file

### Step 2 — Fetch Links

1. In the app, click **"📂 Select"** to choose your cookie file
2. Paste the collection page URL into the **Target URL** field
3. Click **"🎯 Fetch Links"**
4. All video links will be automatically listed

### Step 3 — Download

1. Click **"📁 Browse"** to choose a download folder
2. Click **"⚡ Start Download"**
3. Track progress via the status bars in the table

> 💡 **Tip:** Previously downloaded videos are automatically skipped, so re-running on the same collection won't waste time.

## ⚙️ Requirements

| Component | Minimum |
|-----------|---------|
| OS | Windows 10/11 |
| Python | 3.10+ (for running from source) |
| PyQt6 | 6.x |
| yt-dlp | Latest |
| FFmpeg | Latest |

<br>

---

<br>

<div align="center">

## ⚠️ Yasal Uyarı / Disclaimer

Bu araç sadece **kişisel arşivleme** ve **eğitim amaçlıdır**.<br>
İçerik üreticilerinin telif haklarına ve TikTok Hizmet Koşullarına saygı gösterin.

This tool is for **personal archiving** and **educational purposes** only.<br>
Please respect content creators' copyrights and TikTok's Terms of Service.

<br>

---

<br>

**Geliştirici / Developer:** [mehmettevfikcetin](https://github.com/mehmettevfikcetin)

⭐ Projeyi beğendiyseniz yıldız vermeyi unutmayın! / If you like this project, don't forget to star it!

</div>
