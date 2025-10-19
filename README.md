# 🎬 TikTok Bulk Video Downloader (TikTok Toplu Video İndirici)

![App Icon](https://raw.githubusercontent.com/mehmettevfikcetin/TikTok-Bulk-Downloader/main/icon.ico)

[**🇬🇧 English Version**](#-english-version) | [**🇹🇷 Türkçe Versiyon**](#-türkçe-versiyon)

---

## 🇬🇧 English Version

This is a Windows (x64) desktop application developed to bulk download video collections from your "Saved" (Collections) on TikTok.

### 🚀 Download & Run (No Installation)

The easiest method is to use the compiled `.exe` file.

1.  Go to the [**Releases**](https://github.com/mehmettevfikcetin/TikTok-Bulk-Downloader/releases) section of this repository.
2.  Download the `.exe` file from the "Assets" section of the latest release (e.g., `v1.0`).
3.  Run the downloaded file directly. No installation is required.

### ✨ Features

* **Bulk Link Fetching:** Scrapes all video links from a TikTok collection URL.
* **Bulk Downloading:** Downloads all fetched links sequentially.
* **Modern UI:** A modern and easy-to-use interface built with PyQt6.
* **Status Tracking:** Tracks the status for each video (Waiting, Downloading, Skipped, Error, Completed).
* **Progress Bars:** Individual progress for each video and total progress for the entire batch.
* **Memory:** Remembers your selected cookie file and download folder paths.
* **Help Menu:** Access to a "How to Use?" guide from within the app.
* **Tools Included:** Comes bundled with `yt-dlp.exe` and `ffmpeg.exe`.

### ❓ How to Use?

You can also access these steps by clicking the "❓ Help" button in the app's interface.

**Step 1: Settings**
* **Cookie File:** Install the **"Get cookies.txt LOCALLY"** browser extension. While logged into TikTok.com, click the extension, download the `tiktok.com_cookies.txt` file, and select it in the app using "Browse".
* **Target URL:** Copy and paste the full URL of the TikTok collection you want to download (from your browser's address bar).

**Step 2: Fetch Links**
* Press the button and wait for all video links from the collection to populate the text box below.

**Step 3: Download**
* **Download Folder:** Choose the folder where the videos will be saved.
* **Start Download:** Press the button and monitor the download process in the table.

### 🐍 For Developers

If you want to run or contribute to this project from the source code:

**1. Clone the Repo**
git clone [https://github.com/mehmettevfikcetin/TikTok-Bulk-Downloader.git](https://github.com/mehmettevfikcetin/TikTok-Bulk-Downloader.git)
cd TikTok-Bulk-Downloader

2. Install Requirements
   
pip install -r requirements.txt
(Required packages: PyQt6 and yt-dlp)

4. Run Ensure ffmpeg.exe and yt-dlp.exe are in the same directory as the main Python script (tiktok_downloader.py).

python tiktok_downloader.py
4. Compile .exe (Optional) If you wish to compile the app yourself, you can use PyInstaller:

pyinstaller --onefile --windowed --icon="icon.ico" --add-data="icon.ico;." --add-data="ffmpeg.exe;." --add-data="yt-dlp.exe;." tiktok_downloader.py

📜 License
This project is licensed under the MIT License.

##🇹🇷 Türkçe Versiyon
Bu araç, TikTok'taki "Kaydedilenler" (Collections) altında bulunan video koleksiyonlarını toplu olarak indirmek için geliştirilmiş bir Windows (x64) masaüstü uygulamasıdır.

🚀 İndir ve Kullan (Kurulumsuz)
En kolay yöntem, derlenmiş .exe dosyasını kullanmaktır.

Bu deponun Releases (Sürümler) bölümüne gidin.

En son sürümün (Örn: v1.0) altındaki "Assets" bölümünden .exe uzantılı dosyayı indirin.

İndirdiğiniz dosyayı direkt çalıştırın. Kurulum gerektirmez.

✨ Özellikler
Toplu Link Getirme: TikTok koleksiyon URL'si üzerinden tüm video linklerini çeker.

Toplu İndirme: Getirilen tüm linkleri sırayla indirir.

Gelişmiş Arayüz: PyQt6 ile modern ve kullanımı kolay bir arayüz.

Durum Takibi: Her video için (Bekleniyor, İndiriliyor, Atlandı, Hata, Tamamlandı) durum takibi.

İlerleme Çubukları: Her video için ayrı ve tüm işlem için genel ilerleme durumu.

Hafıza: Seçtiğiniz çerez dosyası ve indirme klasörü yollarını hatırlar.

Yardım Menüsü: Uygulama içinden "Nasıl Kullanılır?" rehberine erişim.

Yardımcı Araçlar Dahil: yt-dlp.exe ve ffmpeg.exe programla birlikte paketlenmiştir.

❓ Nasıl Kullanılır?
Uygulamayı açtıktan sonra, arayüzdeki "❓ Yardım" butonuna tıklayarak da bu adımlara ulaşabilirsiniz.

1. Adım: Ayarlar

Çerez Dosyası: Tarayıcınıza "Get cookies.txt LOCALLY" eklentisini kurun. TikTok.com'da giriş yapmışken eklentiye tıklayıp tiktok.com_cookies.txt dosyasını indirin ve "Gözat" ile uygulamada seçin.

Hedef URL: İndirmek istediğiniz TikTok koleksiyonunun tam URL'sini (adres çubuğundan) kopyalayıp yapıştırın.

2. Adım: Linkleri Getir

Butona basarak koleksiyondaki tüm video linklerinin alt kutuya dolmasını bekleyin.

3. Adım: İndir

İndirme Klasörü: Videoların kaydedileceği klasörü seçin.

İndirmeyi Başlat: Butona basın ve tablodan indirme sürecini takip edin.

🐍 Geliştiriciler İçin
Bu projeyi kaynaktan çalıştırmak veya geliştirmek isterseniz:

1. Depoyu Klonlayın

git clone [https://github.com/mehmettevfikcetin/TikTok-Bulk-Downloader.git](https://github.com/mehmettevfikcetin/TikTok-Bulk-Downloader.git)
cd DEPO_ADIN
2. Gerekli Kütüphaneleri Kurun


pip install -r requirements.txt
(Gerekli kütüphaneler: PyQt6 ve yt-dlp)

3. Çalıştırın ffmpeg.exe ve yt-dlp.exe dosyalarının ana Python script'i (tiktok_downloader.py) ile aynı klasörde olduğundan emin olun.

python tiktok_downloader.py
4. .exe Derleme (İsteğe bağlı) Uygulamayı kendiniz derlemek isterseniz PyInstaller kullanabilirsiniz:

pyinstaller --onefile --windowed --icon="icon.ico" --add-data="icon.ico;." --add-data="ffmpeg.exe;." --add-data="yt-dlp.exe;." tiktok_downloader.py
📜 Lisans
  Bu proje MIT Lisansı altında lisanslanmıştır.
