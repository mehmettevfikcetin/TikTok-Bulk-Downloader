EN
🎬 TikTok Bulk Downloader (v1.5)
Advanced bulk video downloader for TikTok Collections and Saved Lists. Built with Python, PyQt6, and yt-dlp.

This application allows users to backup their saved TikTok collections locally. It features a unique "Hybrid Mode" to bypass common scraping limitations and a "Fast Check" system to skip existing files instantly.

🔥 Key Features
🛡️ Hybrid Scraping Strategy:

Mobile Mode (Link Fetching): Mimics an iPhone (iOS 16) to fetch links without pagination limits.

Desktop Mode (Downloading): Mimics a Desktop Chrome browser with cookies to bypass age restrictions and authentication checks.

⚡ Fast Smart Check (Local Cache):

Checks for existing files locally before making any network requests.

Skips already downloaded videos in milliseconds without triggering TikTok's API limits.

📝 Error Reporting System:

Generates a detailed report of failed downloads at the end of the process.

Includes a "Copy All Failed URLs" button for easy retry or manual inspection.

🎨 Modern Dark GUI:

Clean, user-friendly interface built with PyQt6.

Real-time progress bars for each video and total batch progress.

🔒 Anti-Detection Mechanisms:

Implements randomized sleep intervals and human-like behavior to prevent IP bans.

🛠️ Installation & Requirements
Clone the repository:

Bash

git clone https://github.com/mehmettevfikcetin/TikTok-Bulk-Downloader.git
cd TikTok-Bulk-Downloader
Install dependencies:

Bash

pip install -r requirements.txt
(Dependencies: PyQt6, yt-dlp)

FFmpeg:

Ensure ffmpeg.exe and ffprobe.exe are in the same directory as the script or added to your system PATH.

🚀 How to Use
Get Cookies (Essential):

Install the "Get cookies.txt LOCALLY" extension for Chrome/Edge.

Log in to TikTok.com and download your cookies as a .txt file.

Run the App:

Bash

python tiktok_downloader.py
Select Cookie File: Click "Browse" and select the .txt file you downloaded.

Enter URL: Paste the link to your TikTok Collection or Saved Videos page.

Fetch Links: Click "Linkleri Getir". The app will find all videos using the Mobile strategy.

Download: Select a folder and click "İndirmeyi Başlat".

⚠️ Disclaimer
This tool is for educational purposes and personal archiving only. Please respect the copyright of the content creators and TikTok's Terms of Service.

🇹🇷 TikTok Toplu Video İndirici (v7.6)
TikTok Koleksiyonları ve Kaydedilenler listesi için gelişmiş toplu video indirme aracı. Python, PyQt6 ve yt-dlp ile geliştirilmiştir.

TR
--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

Bu uygulama, TikTok koleksiyonlarınızı yerel olarak yedeklemenizi sağlar. Yaygın engellemeleri aşmak için benzersiz bir "Hibrit Mod" ve var olan dosyaları anında geçen "Hızlı Kontrol" sistemine sahiptir.

🔥 Temel Özellikler
🛡️ Hibrit Tarama Stratejisi:

Mobil Mod (Link Bulma): Sayfalama sınırlarına takılmadan tüm linkleri bulmak için kendini iPhone (iOS 16) olarak tanıtır.

Masaüstü Modu (İndirme): Yaş kısıtlamalarını ve giriş engellerini aşmak için çerezleri kullanarak kendini Masaüstü Chrome tarayıcısı olarak tanıtır.

⚡ Hızlı Akıllı Kontrol (Yerel Önbellek):

İndirme yapmadan önce klasördeki dosyaları kontrol eder.

Daha önce indirilmiş videoları, sunucuya hiç istek atmadan milisaniyeler içinde atlar.

📝 Hata Raporlama Sistemi:

İşlem sonunda indirilemeyen videoların detaylı bir listesini sunar.

Hatalı linkleri tek tıkla kopyalama özelliği mevcuttur.

🎨 Modern Karanlık Arayüz:

PyQt6 ile hazırlanmış şık ve kullanıcı dostu arayüz.

Her video için ayrı, toplam işlem için genel ilerleme çubukları.

🔒 Bot Algılama Koruması:

IP banlanmasını önlemek için insani bekleme süreleri ve rastgele gecikmeler kullanır.

🛠️ Kurulum ve Gereksinimler
Projeyi indirin:

Bash

git clone https://github.com/mehmettevfikcetin/TikTok-Bulk-Downloader.git
cd TikTok-Bulk-Downloader
Kütüphaneleri yükleyin:

Bash

pip install -r requirements.txt
(Gerekli kütüphaneler: PyQt6, yt-dlp)

FFmpeg:

ffmpeg.exe ve ffprobe.exe dosyalarının script ile aynı klasörde olduğundan emin olun.

🚀 Nasıl Kullanılır?
Çerezleri Alın (Önemli):

Chrome/Edge için "Get cookies.txt LOCALLY" eklentisini kurun.

TikTok.com'a giriş yapın ve eklentiye tıklayarak çerezleri .txt olarak indirin.

Uygulamayı Başlatın:

Bash

python tiktok_downloader.py
Çerez Dosyasını Seçin: "Gözat" butonuna basıp indirdiğiniz .txt dosyasını seçin.

URL Girin: İndirmek istediğiniz Koleksiyon veya Kaydedilenler sayfasının linkini yapıştırın.

Linkleri Getir: Butona basın. Uygulama Mobil stratejisi ile tüm linkleri bulacaktır.

İndir: Klasör seçin ve "İndirmeyi Başlat" butonuna basın.

⚠️ Yasal Uyarı
Bu araç sadece eğitim amaçlı ve kişisel arşivleme içindir. Lütfen içerik üreticilerinin telif haklarına ve TikTok'un Hizmet Koşullarına saygı gösterin.
