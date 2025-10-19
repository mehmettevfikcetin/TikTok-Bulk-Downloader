# -*- coding: utf-8 -*-


import sys
import os
import time
import subprocess
import json
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTextEdit,
    QPushButton, QLineEdit, QFileDialog, QTableWidget, QTableWidgetItem,
    QProgressBar, QMessageBox, QHeaderView, QFrame, QScrollArea # QCheckBox kaldırıldı
)
from PyQt6.QtCore import QThread, pyqtSignal, Qt, QSettings, QCoreApplication, QSize # QSize eklendi
from PyQt6.QtGui import QIcon, QPalette, QColor, QFont, QPixmap # QPixmap eklendi
import yt_dlp

# --- YARDIMCI FONKSİYONLAR ---

def resource_path(relative_path):
    try: base_path = sys._MEIPASS
    except Exception: base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

YT_DLP_PATH = 'yt-dlp'
try:
    _yt_dlp_exe_internal = resource_path('yt-dlp.exe')
    if os.path.exists(_yt_dlp_exe_internal): YT_DLP_PATH = _yt_dlp_exe_internal
except Exception: pass

# --- Link Getirme Thread'i (yt-dlp ile) ---
class LinkFetcherThread(QThread):
    linksFetched = pyqtSignal(list)
    fetchStatus = pyqtSignal(str)
    fetchError = pyqtSignal(str)

    def __init__(self, cookies_path, target_url):
        super().__init__()
        self.cookies_path = cookies_path
        self.target_url = target_url
        self.running = True

    def run(self):
        try:
            self.fetchStatus.emit(f"yt-dlp ile {self.target_url} adresinden linkler alınıyor...")
            command = [
                YT_DLP_PATH, '--cookies', self.cookies_path, '--skip-download',
                '--flat-playlist', '-J', '--no-warnings', self.target_url
            ]
            process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                       text=True, encoding='utf-8', errors='ignore',
                                       creationflags=subprocess.CREATE_NO_WINDOW)
            stdout, stderr = process.communicate()

            if process.returncode != 0 or not stdout.strip():
                error_message = stderr.strip() or stdout.strip() or "yt-dlp bilinmeyen bir hata verdi."
                if len(error_message) > 300: error_message = error_message[:300] + "..."
                if "cookies" in error_message.lower(): self.fetchError.emit("Çerez dosyası hatalı/geçersiz. Yenileyin.")
                elif "403" in error_message or "private" in error_message.lower(): self.fetchError.emit("Giriş hatası veya hedef URL gizli/geçersiz. Çerez dosyasını ve URL'yi kontrol edin.")
                elif "unable to extract" in error_message.lower(): self.fetchError.emit(f"Linkler çıkarılamadı. URL doğru mu veya TikTok güncellendi mi?\nHata: {error_message}")
                else: self.fetchError.emit(f"yt-dlp hatası: {error_message}")
                return

            try:
                data = json.loads(stdout)
                urls = [entry.get('url') for entry in data.get('entries', []) if entry.get('url')]
            except json.JSONDecodeError:
                self.fetchError.emit("yt-dlp çıktısı anlaşılamadı (JSON hatası).")
                return

            if not urls:
                self.fetchError.emit("Bu URL'de hiç video linki bulunamadı.")
                return
            self.linksFetched.emit(urls)
        except FileNotFoundError:
            self.fetchError.emit(f"Hata: '{YT_DLP_PATH}' bulunamadı.")
        except Exception as e:
            self.fetchError.emit(f"Link alma sırasında beklenmedik hata: {str(e)}")

    def stop(self):
        self.running = False


# --- İndirme Thread'i ---
class DownloaderThread(QThread):
    videoFinished = pyqtSignal(int, str, str)
    progressUpdated = pyqtSignal(int, int)
    allFinished = pyqtSignal(int, int, int)

    def __init__(self, urls, target_dir):
        super().__init__()
        self.urls = urls
        self.target_dir = target_dir
        self.ffmpeg_path = resource_path("ffmpeg.exe")
        self.running = True
        self.stats = {'completed': 0, 'skipped': 0, 'errors': 0}

    def _hook(self, d):
        if not self.running: raise yt_dlp.utils.DownloadError("İptal edildi.")
        if d['status'] == 'downloading':
            p = d['_percent_str'].replace('%', '').strip()
            try: self.progressUpdated.emit(self.current_video_index, int(float(p)))
            except: pass

    def _post_hook(self, d): pass

    def run(self):
        for i, url in enumerate(self.urls):
            if not self.running: break
            self.current_video_index = i
            video_id = "Bilinmiyor"; title = "basliksiz"; status_message = "Hata"
            try:
                info_ydl_opts = {'quiet': True, 'skip_download': True, 'no_warnings': True}
                try:
                    with yt_dlp.YoutubeDL(info_ydl_opts) as ydl:
                        info = ydl.extract_info(url, download=False)
                        video_id = info.get('id', 'Bilinmiyor'); title = info.get('title', 'basliksiz')
                    if video_id == "Bilinmiyor": raise yt_dlp.utils.DownloadError("Video ID alınamadı.")
                except yt_dlp.utils.DownloadError as info_err:
                    status_message = f"HATA (Bilgi alınamadı: {str(info_err)[:50]}...)"; raise

                filename = f"{title[:30]}_{video_id}.mp4"
                filename = "".join(c for c in filename if c not in r'<>:"/\|?*')
                output_path = os.path.join(self.target_dir, filename)

                if os.path.exists(output_path):
                    status_message = "ATLANDI (Klasörde mevcut)"; self.stats['skipped'] += 1
                    self.videoFinished.emit(i, video_id, status_message)
                    if self.running: time.sleep(0.5); continue

                ydl_opts = {
                    'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
                    'outtmpl': output_path, 'ffmpeg_location': self.ffmpeg_path,
                    'progress_hooks': [self._hook], 'postprocessor_hooks': [self._post_hook],
                    'quiet': True, 'noprogress': True, 'no_warnings': True, 'no_overwrites': True
                }
                with yt_dlp.YoutubeDL(ydl_opts) as ydl: ydl.download([url])

                if not os.path.exists(output_path):
                    status_message = f"ATLANDI (yt-dlp tarafından?)"; self.stats['skipped'] += 1
                    self.videoFinished.emit(i, video_id, status_message)
                    if self.running: time.sleep(0.5); continue

                status_message = "TAMAMLANDI"; self.stats['completed'] += 1
                self.progressUpdated.emit(i, 100)
                self.videoFinished.emit(i, video_id, status_message)

                wait_time = 3
                for _ in range(wait_time * 2):
                    if not self.running: break; time.sleep(0.5)
                if not self.running: break

            except Exception as e:
                if isinstance(e, yt_dlp.utils.DownloadError): status_message = f"HATA (yt-dlp: {str(e)[:80]}...)"
                else: status_message = f"HATA (Genel: {str(e)[:80]}...)"; import traceback; traceback.print_exc()
                self.stats['errors'] += 1
                self.videoFinished.emit(i, video_id, status_message)
                if self.running: time.sleep(1)

        self.allFinished.emit(self.stats['completed'], self.stats['skipped'], self.stats['errors'])

    def stop(self): self.running = False


# --- Ana Arayüz (GUI) Sınıfı ---
class App(QWidget):
    def __init__(self):
        super().__init__()
        self.settings = QSettings("MyCompany", "KolayTikTokIndirici")
        self.downloader_thread = None
        self.fetcher_thread = None
        self.initUI()

    # --- TAM VE TEMİZLENMİŞ initUI (v7.3 - Yardım Butonlu) ---
    def initUI(self):
        self.setWindowTitle('TikTok Toplu Video İndirici')
        self.setGeometry(300, 300, 900, 800) # Biraz daha geniş ve yüksek
        self.setMinimumSize(800, 700) # Minimum boyut
        try:
            self.setWindowIcon(QIcon(resource_path("icon.ico")))
        except Exception as e:
            print(f"DEBUG: İkon yüklenemedi: {e}") # Hata varsa konsola yaz

        # --- MODERN KOYU TEMA ---
        palette = QPalette()
        palette.setColor(QPalette.ColorRole.Window, QColor(20, 20, 30)) # Koyu Mavi/Mor Arka Plan
        palette.setColor(QPalette.ColorRole.WindowText, QColor(240, 240, 245)) # Açık Gri Yazı
        palette.setColor(QPalette.ColorRole.Base, QColor(30, 30, 45)) # Input Alanı Arka Planı
        palette.setColor(QPalette.ColorRole.AlternateBase, QColor(45, 45, 65)) # Tablo Alternatif Satır
        palette.setColor(QPalette.ColorRole.Text, QColor(240, 240, 245)) # Input Alanı Yazı Rengi
        palette.setColor(QPalette.ColorRole.Button, QColor(35, 35, 55)) # Buton Arka Planı
        palette.setColor(QPalette.ColorRole.ButtonText, QColor(240, 240, 245)) # Buton Yazı Rengi
        palette.setColor(QPalette.ColorRole.Highlight, QColor(100, 181, 246)) # Seçim Rengi (Mavi)
        palette.setColor(QPalette.ColorRole.HighlightedText, QColor(255, 255, 255)) # Seçili Yazı Rengi
        self.setPalette(palette)
        # --- TEMA SONU ---

        main_layout = QVBoxLayout()
        main_layout.setSpacing(0) # Elemanlar arası boşluk sıfır, QFrame ile yöneteceğiz
        main_layout.setContentsMargins(0, 0, 0, 0) # Kenar boşlukları sıfır

        # --- BAŞLIK BÖLÜMÜ ---
        header = QFrame()
        # Gradient arka plan ve alt çizgi
        header.setStyleSheet("background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #1f1f3d, stop:1 #2d2d5f); border-bottom: 2px solid #00bfff;")
        header.setMinimumHeight(80)
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(30, 15, 30, 15)

        # --- YENİ YARDIM BUTONU ---
        self.help_button = QPushButton("❓ Yardım")
        self.help_button.setFixedSize(100, 40) # Sabit boyut
        self.help_button.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        self.help_button.setStyleSheet("""
            QPushButton {
                background-color: rgba(0, 191, 255, 0.2); /* Yarı saydam mavi */
                color: #00bfff;
                border: 1px solid #00bfff;
                border-radius: 20px; /* Yuvarlak köşeler */
                padding: 5px;
            }
            QPushButton:hover { background-color: rgba(0, 191, 255, 0.4); }
            QPushButton:pressed { background-color: rgba(0, 191, 255, 0.6); }
        """)
        self.help_button.clicked.connect(self.show_help_dialog)
        header_layout.addWidget(self.help_button, alignment=Qt.AlignmentFlag.AlignLeft)
        # --- YARDIM BUTONU SONU ---

        header_layout.addStretch(1) # Başlığı ortaya it

        title = QLabel('🎬 TikTok Toplu Video İndirici')
        title.setFont(QFont("Arial", 22, QFont.Weight.Bold))
        title.setStyleSheet("color: #00bfff; background: transparent; border: none;") # Arka planı şeffaf yap
        header_layout.addWidget(title)

        header_layout.addStretch(1) # Versiyonu sağa it

        version = QLabel(f'v{self.get_app_version()}') # Versiyonu dinamik al
        version.setFont(QFont("Arial", 9))
        version.setStyleSheet("color: #888; background: transparent; border: none;")
        header_layout.addWidget(version, alignment=Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignBottom)

        main_layout.addWidget(header)

        # --- SCROLL AREA İÇERİĞİ ---
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        # Scroll bar stilini de ayarlayalım
        scroll.setStyleSheet("""
            QScrollArea { border: none; background-color: #14141e; }
            QScrollBar:vertical {
                border: none;
                background: #252535;
                width: 12px;
                margin: 0px 0px 0px 0px;
            }
            QScrollBar::handle:vertical {
                background: #404060;
                min-height: 20px;
                border-radius: 6px;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                border: none; background: none; height: 0px;
            }
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
                background: none;
            }
        """)
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout(scroll_widget)
        scroll_layout.setSpacing(20) # Bölümler arası boşluk
        scroll_layout.setContentsMargins(30, 20, 30, 20) # İç kenar boşlukları

        # --- AŞAMA 1: AYARLAR ---
        settings_frame = QFrame()
        settings_frame.setStyleSheet(self.get_frame_style()) # Stil için yardımcı fonksiyon
        settings_content = QVBoxLayout(settings_frame)
        settings_content.setContentsMargins(20, 15, 20, 15); settings_content.setSpacing(10)

        settings_title = QLabel('⚙️ Adım 1: Ayarlar')
        settings_title.setFont(QFont("Arial", 12, QFont.Weight.Bold)); settings_title.setStyleSheet("color: #00bfff; border: none;")
        settings_content.addWidget(settings_title)

        cookie_layout = QHBoxLayout(); cookie_layout.setSpacing(10)
        cookie_label = QLabel("Çerez Dosyası:")
        cookie_label.setFont(QFont("Arial", 10))
        cookie_layout.addWidget(cookie_label)
        self.cookie_path_input = self.create_input_field()
        self.cookie_path_input.setReadOnly(True); self.cookie_path_input.setPlaceholderText("...")
        saved_cookie_path = self.settings.value("cookiePath", "")
        self.cookie_path_input.setText(saved_cookie_path)
        cookie_layout.addWidget(self.cookie_path_input, 1)
        self.browse_cookie_button = self.create_button('📁 Gözat', '#00bfff')
        self.browse_cookie_button.setMinimumWidth(80)
        self.browse_cookie_button.clicked.connect(self.browse_cookie_file)
        cookie_layout.addWidget(self.browse_cookie_button)
        settings_content.addLayout(cookie_layout)

        cookie_instructions = QLabel("💡 Tarayıcı eklentisi ('Get cookies.txt LOCALLY') ile TikTok çerez dosyasını seçin.")
        cookie_instructions.setStyleSheet("color: #888; font-size: 9px; border: none; background: transparent;")
        cookie_instructions.setWordWrap(True)
        settings_content.addWidget(cookie_instructions)

        target_url_layout = QHBoxLayout(); target_url_layout.setSpacing(10)
        target_url_label = QLabel("Hedef URL:")
        target_url_label.setFont(QFont("Arial", 10))
        target_url_layout.addWidget(target_url_label)
        self.target_url_input = self.create_input_field()
        self.target_url_input.setPlaceholderText("https://www.tiktok.com/@username/... URL yapıştırın")
        saved_target_url = self.settings.value("targetUrl", "")
        self.target_url_input.setText(saved_target_url)
        self.target_url_input.textChanged.connect(lambda: self.settings.setValue("targetUrl", self.target_url_input.text()))
        target_url_layout.addWidget(self.target_url_input, 1)
        settings_content.addLayout(target_url_layout)

        scroll_layout.addWidget(settings_frame)

        # --- AŞAMA 2: LİNKLERİ GETİR ---
        fetch_frame = QFrame()
        fetch_frame.setStyleSheet(self.get_frame_style())
        fetch_content = QVBoxLayout(fetch_frame)
        fetch_content.setContentsMargins(20, 15, 20, 15); fetch_content.setSpacing(10)

        fetch_title = QLabel('🔗 Adım 2: Linkleri Getir')
        fetch_title.setFont(QFont("Arial", 12, QFont.Weight.Bold)); fetch_title.setStyleSheet("color: #00bfff; border: none;")
        fetch_content.addWidget(fetch_title)

        self.fetch_links_button = self.create_button('Linkleri Getir', '#1abc9c')
        self.fetch_links_button.setMinimumHeight(45)
        self.fetch_links_button.setFont(QFont("Arial", 11, QFont.Weight.Bold))
        self.fetch_links_button.clicked.connect(self.start_link_fetch)
        fetch_content.addWidget(self.fetch_links_button)

        self.fetch_status_label = QLabel('Başlamak için ayarları yapıp butona basın.')
        self.fetch_status_label.setFont(QFont("Arial", 9)); self.fetch_status_label.setStyleSheet("color: #888; border: none; background: transparent;")
        self.fetch_status_label.setWordWrap(True)
        fetch_content.addWidget(self.fetch_status_label)

        self.url_input = QTextEdit()
        self.url_input.setPlaceholderText("Linkler buraya gelecek...")
        self.url_input.setMinimumHeight(100); self.url_input.setMaximumHeight(150) # Boyut ayarı
        self.url_input.setStyleSheet(self.get_text_edit_style()) # Stil için yardımcı fonksiyon
        
        # --- DEĞİŞİKLİK 1: textChanged sinyali eklendi ---
        self.url_input.textChanged.connect(self.update_download_button_state)
        # --- DEĞİŞİKLİK 1 SONU ---
        
        fetch_content.addWidget(self.url_input)

        scroll_layout.addWidget(fetch_frame)

        # --- AŞAMA 3: İNDİRME ---
        download_frame = QFrame()
        download_frame.setStyleSheet(self.get_frame_style())
        download_content = QVBoxLayout(download_frame)
        download_content.setContentsMargins(20, 15, 20, 15); download_content.setSpacing(10)

        download_title = QLabel('⬇️ Adım 3: İndir')
        download_title.setFont(QFont("Arial", 12, QFont.Weight.Bold)); download_title.setStyleSheet("color: #00bfff; border: none;")
        download_content.addWidget(download_title)

        folder_layout = QHBoxLayout(); folder_layout.setSpacing(10)
        folder_label = QLabel("İndirme Klasörü:")
        folder_label.setFont(QFont("Arial", 10))
        folder_layout.addWidget(folder_label)
        self.folder_path_input = self.create_input_field()
        self.folder_path_input.setReadOnly(True); self.folder_path_input.setPlaceholderText("...")
        saved_folder_path = self.settings.value("downloadPath", "")
        self.folder_path_input.setText(saved_folder_path)
        folder_layout.addWidget(self.folder_path_input, 1)
        self.browse_button = self.create_button('📁 Gözat', '#00bfff')
        self.browse_button.setMinimumWidth(80)
        self.browse_button.clicked.connect(self.browse_folder)
        folder_layout.addWidget(self.browse_button)
        download_content.addLayout(folder_layout)

        # Sıralama Checkbox'ı kaldırıldı

        self.download_button = self.create_button('İndirmeyi Başlat', '#e74c3c') # Kırmızı renk
        self.download_button.setMinimumHeight(50)
        self.download_button.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        self.download_button.clicked.connect(self.start_download)
        download_content.addWidget(self.download_button)

        # --- İlerleme Tablosu ---
        self.status_table = QTableWidget()
        self.status_table.setColumnCount(4)
        self.status_table.setHorizontalHeaderLabels(['URL', 'Video ID', 'Durum', 'İlerleme'])
        self.status_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.status_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        self.status_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        self.status_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.Fixed)
        self.status_table.horizontalHeader().resizeSection(3, 100)
        self.status_table.verticalHeader().setVisible(False)
        self.status_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.status_table.setMinimumHeight(200) # Biraz daha yüksek
        self.status_table.setStyleSheet(self.get_table_style()) # Stil için yardımcı fonksiyon
        download_content.addWidget(self.status_table)

        # Toplam İlerleme Çubuğu
        self.total_progress_bar = QProgressBar()
        self.total_progress_bar.setValue(0)
        self.total_progress_bar.setTextVisible(True)
        self.total_progress_bar.setFormat('Toplam İlerleme: %p%')
        self.total_progress_bar.setMinimumHeight(25)
        self.total_progress_bar.setStyleSheet(self.get_progress_bar_style()) # Stil için yardımcı fonksiyon
        download_content.addWidget(self.total_progress_bar)

        scroll_layout.addWidget(download_frame)
        scroll_layout.addStretch() # Elemanları yukarı iter

        scroll.setWidget(scroll_widget)
        main_layout.addWidget(scroll, 1) # Scroll area ana layout'a eklenir

        self.setLayout(main_layout)
        self.set_gui_state("idle")
        self.show()
    # --- initUI SONU ---

    # --- YARDIMCI STİL FONKSİYONLARI ---
    def get_app_version(self):
        return "7.3" # Versiyonu buradan yönetelim

    def get_frame_style(self):
        return """
            QFrame {
                background-color: #252535;
                border: 1px solid #404060; /* Daha ince border */
                border-radius: 10px;
                padding: 5px; /* İç boşluk eklendi */
            }
        """

    def create_input_field(self):
        input_field = QLineEdit()
        input_field.setStyleSheet("""
            QLineEdit {
                background-color: #2a2a3e;
                color: #e0e0e5;
                border: 1px solid #404060;
                border-radius: 6px;
                padding: 8px;
                font-size: 10px;
                min-height: 25px; /* Minimum yükseklik */
            }
            QLineEdit:focus {
                border: 1px solid #00bfff;
            }
            QLineEdit[readOnly="true"] { /* ReadOnly için farklı stil */
                background-color: #303045;
                color: #888;
            }
        """)
        return input_field

    def get_text_edit_style(self):
        return """
            QTextEdit {
                background-color: #2a2a3e;
                color: #c0c0c5; /* Biraz daha soluk */
                border: 1px solid #404060;
                border-radius: 8px;
                padding: 10px;
                font-size: 9px; /* Daha küçük font */
                font-family: Consolas, Courier, monospace; /* Monospace font */
            }
            QTextEdit:focus {
                border: 1px solid #00bfff;
            }
            QTextEdit[readOnly="true"] { /* ReadOnly için stil */
                background-color: #303045;
                color: #888;
            }
        """

    def create_button(self, text, base_color):
        button = QPushButton(text)
        hover_color = QColor(base_color).lighter(120).name()
        pressed_color = QColor(base_color).darker(120).name()
        button.setMinimumHeight(35) # Buton yüksekliği
        button.setCursor(Qt.CursorShape.PointingHandCursor) # El ikonu
        button.setStyleSheet(f"""
            QPushButton {{
                background-color: {base_color};
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px 12px;
                font-weight: bold;
                font-size: 10px;
            }}
            QPushButton:hover {{
                background-color: {hover_color};
            }}
            QPushButton:pressed {{
                background-color: {pressed_color};
            }}
            QPushButton:disabled {{ /* Devre dışı buton stili */
                background-color: #555;
                color: #999;
            }}
        """)
        return button

    def get_table_style(self):
        return """
            QTableWidget {
                background-color: #2a2a3e;
                color: #e0e0e5;
                gridline-color: #404060;
                border: 1px solid #404060;
                border-radius: 6px;
                font-size: 9px;
            }
            QHeaderView::section {
                background-color: #353555;
                color: #00bfff;
                border: none;
                padding: 6px; /* Biraz daha az padding */
                font-weight: bold;
                font-size: 10px;
            }
            QTableWidget::item {
                padding: 6px; /* Daha az padding */
                border-bottom: 1px solid #404060;
            }
            QTableWidget::item:selected { background-color: #404060; }
            /* Scroll bar stilleri (isteğe bağlı) */
            QScrollBar:vertical {
                border: none; background: #252535; width: 10px; margin: 0;
            }
            QScrollBar::handle:vertical { background: #404060; min-height: 20px; border-radius: 5px; }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0px; }
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical { background: none; }
            QScrollBar:horizontal { ... } /* Yatay için benzer stiller */
        """

    def get_progress_bar_style(self):
        return """
            QProgressBar {
                border: 1px solid #404060;
                border-radius: 8px;
                text-align: center;
                background-color: #2a2a3e;
                color: #FFFFFF;
                font-weight: bold;
                height: 20px; /* Biraz daha ince */
                font-size: 10px;
            }
            QProgressBar::chunk {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #00bfff, stop:1 #1abc9c);
                border-radius: 7px; /* İçerideki barın köşesi */
                margin: 1px; /* Kenardan hafif boşluk */
            }
        """
    # --- YARDIMCI STİL FONKSİYONLARI SONU ---

    # --- YENİ FONKSİYON: Yardım Penceresi ---
    def show_help_dialog(self):
        help_text = """
        <h2>❓ Nasıl Kullanılır?</h2>
        <p>Bu araç, TikTok'taki Kaydedilenlerde bulunan koleksiyonlarınızdaki videoları toplu indirmenizi sağlar.</p>
        <hr>
        <h4>Adım 1: Ayarlar (Çerez ve URL)</h4>
        <ol>
            <li><b>Çerez Dosyası:</b>
                <ul>
                    <li>Tarayıcınıza <b>"Get cookies.txt LOCALLY"</b> adlı eklentiyi kurun. (<i>Güvenilir ve açık kaynaklıdır</i>).</li>
                    <li>TikTok.com'a tarayıcınızdan giriş yapın.</li>
                    <li>İndirmek istediğiniz Koleksiyon sayfasındayken, tarayıcınızdaki eklenti simgesine tıklayın ve çerez dosyasını (<i>tiktok.com_cookies.txt</i> gibi) bilgisayarınıza indirin.</li>
                    <li>Uygulamadaki "Gözat..." butonu ile bu indirdiğiniz <code>.txt</code> dosyasını seçin. Bu dosya konumunu uygulama hatırlar.</li>
                    <li><b>Not:</b> Çerezler zamanla geçersiz olabilir. Hata alırsanız bu adımı tekrarlayın.</li>
                    <br>
                </ul>
            </li>
            <li><b>Hedef URL:</b>
                <ul>
                    <li>Tarayıcınızda, indirmek istediğiniz <b>Kaydedilenler</b> sayfasının tam URL'sini (adres çubuğundan) kopyalayın.</li>
                    <li>Uygulamadaki "Hedef URL" alanına yapıştırın. Bu URL de hatırlanır.</li>
                    <li>Örnek Koleksiyon URL: <code>https://www.tiktok.com/@username/collection/KoleksiyonAdi-123...</code></li>
                </ul>
            </li>
        </ol>
        <hr>
        <h4>Adım 2: Linkleri Getir</h4>
        <ul>
            <li>Ayarlar doğruysa, "Linkleri Getir" butonuna basın.</li>
            <li>Uygulama, yt-dlp kullanarak girdiğiniz URL'deki tüm video linklerini alttaki kutuya listeleyecektir. Bu işlem video sayısına göre biraz sürebilir.</li>
        </ul>
        <hr>
        <h4>Adım 3: İndir</h4>
        <ol>
            <li><b>İndirme Klasörü:</b> Videoların kaydedileceği klasörü "Gözat..." butonu ile seçin. Bu klasör de hatırlanır.</li>
            <li><b>İndirmeyi Başlat:</b> Butona basın ve videoların indirilmesini bekleyin.</li>
            <li>Alttaki tabloda her videonun durumunu (İndiriliyor, Tamamlandı, Atlandı, Hata) ve ilerlemesini görebilirsiniz.</li>
        </ol>
        """
        msgBox = QMessageBox(self)
        msgBox.setWindowTitle("Yardım ve Kullanım Kılavuzu")
        msgBox.setTextFormat(Qt.TextFormat.RichText) # HTML formatını etkinleştir
        msgBox.setText(help_text)
        # Daha büyük bir pencere için
        msgBox.setStyleSheet("QMessageBox { min-width: 500px; font-size: 11px; } QLabel { font-size: 11px; }")
        msgBox.exec()
    # --- YARDIM PENCERESİ SONU ---

    # --- DEĞİŞİKLİK 3: Yeni Fonksiyon Eklendi ---
    def update_download_button_state(self):
        """ Sadece indirme butonunun durumunu URL listesine göre günceller. """
        # Uygulamanın 'idle' olup olmadığını thread'leri kontrol ederek anlıyoruz.
        is_idle = not (self.downloader_thread and self.downloader_thread.isRunning()) and \
                  not (self.fetcher_thread and self.fetcher_thread.isRunning())
        
        self.download_button.setEnabled(is_idle and bool(self.url_input.toPlainText()))
    # --- DEĞİŞİKLİK 3 SONU ---


    # --- Diğer Metodlar ---
    def set_gui_state(self, state):
        is_idle = state == "idle"; is_fetching = state == "fetching"; is_downloading = state == "downloading"
        self.browse_cookie_button.setEnabled(is_idle); self.target_url_input.setEnabled(is_idle)
        self.fetch_links_button.setEnabled(is_idle and bool(self.cookie_path_input.text()) and bool(self.target_url_input.text()))
        self.browse_button.setEnabled(is_idle)
        self.download_button.setEnabled(is_idle and bool(self.url_input.toPlainText()))
        
        # --- DEĞİŞİKLİK 2: url_input kilidi eklendi ---
        self.url_input.setReadOnly(not is_idle) # Boşta değilken metin kutusunu kilitle
        # --- DEĞİŞİKLİK 2 SONU ---
        
        # self.reverse_order_checkbox.setEnabled(is_idle) # Kaldırıldı

        if is_fetching: self.fetch_links_button.setText("⏳ Linkler Getiriliyor...")
        else: self.fetch_links_button.setText("Linkleri Getir")
        if is_downloading: self.download_button.setText("⏳ İndiriliyor...")
        else: self.download_button.setText("İndirmeyi Başlat")

    def browse_cookie_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, 'Çerez Dosyasını Seç', self.settings.value("cookiePath", ""), 'Metin Dosyaları (*.txt);;Tüm Dosyalar (*)')
        if file_path: self.cookie_path_input.setText(file_path); self.settings.setValue("cookiePath", file_path); self.set_gui_state("idle")

    def browse_folder(self):
        start_path = self.settings.value("downloadPath", os.path.expanduser('~'))
        folder = QFileDialog.getExistingDirectory(self, 'İndirme Klasörünü Seç', start_path)
        if folder: self.folder_path_input.setText(folder); self.settings.setValue("downloadPath", folder)

    def start_link_fetch(self):
        cookie_file = self.cookie_path_input.text(); target_url = self.target_url_input.text().strip()
        if not cookie_file or not os.path.exists(cookie_file): QMessageBox.warning(self, 'Hata', 'Lütfen geçerli bir çerez dosyası seçin.'); return
        if not target_url or "tiktok.com" not in target_url: QMessageBox.warning(self, 'Hata', "Lütfen geçerli bir TikTok URL'si girin."); return
        self.settings.setValue("cookiePath", cookie_file); self.settings.setValue("targetUrl", target_url)
        self.set_gui_state("fetching"); self.url_input.clear()
        self.fetcher_thread = LinkFetcherThread(cookie_file, target_url)
        self.fetcher_thread.linksFetched.connect(self.on_links_fetched); self.fetcher_thread.fetchStatus.connect(self.on_fetch_status); self.fetcher_thread.fetchError.connect(self.on_fetch_error)
        self.fetcher_thread.start()

    def on_links_fetched(self, urls):
        self.url_input.setText("\n".join(urls)); self.set_gui_state("idle")
        self.fetch_status_label.setStyleSheet("color: #1abc9c;")
        self.fetch_status_label.setText(f"✓ {len(urls)} adet URL başarıyla bulundu. Adım 3'e geçebilirsiniz.")
        QMessageBox.information(self, 'Başarılı', f"✓ {len(urls)} adet video linki listeye eklendi.")

    def on_fetch_status(self, message):
        self.fetch_status_label.setStyleSheet("color: #f39c12;")
        self.fetch_status_label.setText(f"⏳ {message}")

    def on_fetch_error(self, error_message):
        self.set_gui_state("idle")
        self.fetch_status_label.setStyleSheet("color: #e74c3c;")
        self.fetch_status_label.setText(f"✗ Hata: {error_message}")
        QMessageBox.warning(self, 'Link Getirme Hatası', error_message)

    def start_download(self):
        urls = self.url_input.toPlainText().split('\n')
        urls = [url.strip() for url in urls if url.strip()]
        target_dir = self.folder_path_input.text()
        if not urls: QMessageBox.warning(self, 'Hata', 'İndirilecek URL bulunamadı.'); return
        if not target_dir: QMessageBox.warning(self, 'Hata', 'Lütfen bir indirme klasörü seçin.'); return
        self.settings.setValue("downloadPath", target_dir)
        # if self.reverse_order_checkbox.isChecked(): urls.reverse() # Kaldırıldı
        self.set_gui_state("downloading"); self.status_table.setRowCount(len(urls))
        self.total_progress_bar.setValue(0); self.completed_videos = 0; self.total_videos = len(urls)
        for i, url in enumerate(urls):
            progress_bar = QProgressBar(); progress_bar.setValue(0)
            progress_bar.setStyleSheet(self.get_progress_bar_style().replace("QProgressBar {", "QProgressBar { height: 16px;").replace("font-weight: bold;", "")) # Tablodaki progress bar stili
            self.status_table.setItem(i, 0, QTableWidgetItem(url.split('?')[0]))
            self.status_table.setItem(i, 1, QTableWidgetItem("-"))
            self.status_table.setItem(i, 2, QTableWidgetItem("⏳ Bekleniyor..."))
            self.status_table.setCellWidget(i, 3, progress_bar)
        self.downloader_thread = DownloaderThread(urls, target_dir)
        self.downloader_thread.videoFinished.connect(self.on_video_finished)
        self.downloader_thread.progressUpdated.connect(self.on_progress_updated)
        self.downloader_thread.allFinished.connect(self.on_all_finished)
        self.downloader_thread.start()

    def on_progress_updated(self, index, percentage):
        try:
            progress_bar = self.status_table.cellWidget(index, 3)
            if progress_bar: progress_bar.setValue(percentage)
        except Exception as e: print(f"DEBUG: on_progress_updated hatası (index={index}): {e}")

    def on_video_finished(self, index, video_id, status):
        try:
            if index < self.status_table.rowCount():
                self.status_table.setItem(index, 1, QTableWidgetItem(video_id))
                self.status_table.setItem(index, 2, QTableWidgetItem(status))
                status_item = self.status_table.item(index, 2)
                if status_item:
                    # Renkleri tema ile uyumlu hale getirelim
                    if "TAMAMLANDI" in status: status_item.setForeground(QColor(26, 188, 156)) # Yeşil/Turkuaz
                    elif "ATLANDI" in status: status_item.setForeground(QColor(243, 156, 18)) # Turuncu
                    elif "HATA" in status: status_item.setForeground(QColor(231, 76, 60)) # Kırmızı
            else: print(f"DEBUG: on_video_finished - Geçersiz satır index'i: {index}")
        except Exception as e: print(f"Tablo güncelleme hatası: {e}")
        try:
            progress_percent = int(((index + 1) / self.total_videos) * 100)
            self.total_progress_bar.setValue(progress_percent)
        except ZeroDivisionError: self.total_progress_bar.setValue(0)
        except Exception as e: print(f"DEBUG: total_progress_bar güncelleme hatası: {e}")

    def on_all_finished(self, completed, skipped, errors):
        self.set_gui_state("idle")
        self.download_button.setText('İndirmeyi Başlat')
        self.total_progress_bar.setValue(100)
        message = f"""
        <h3>✓ İndirme İşlemi Tamamlandı</h3>
        <hr>
        <p style='font-size:11px;'>
        Başarılı: <b style='color:#1abc9c;'>{completed}</b><br>
        Atlanan: <b style='color:#f39c12;'>{skipped}</b><br>
        Hatalı: <b style='color:#e74c3c;'>{errors}</b><br><br>
        Toplam İşlenen: <b>{completed + skipped + errors}</b>
        </p>
        """
        # Özel bir QMessageBox kullanalım
        msgBox = QMessageBox(self)
        msgBox.setWindowTitle("İşlem Tamamlandı")
        msgBox.setTextFormat(Qt.TextFormat.RichText)
        msgBox.setText(message)
        try:
            msgBox.setIconPixmap(QPixmap(resource_path("icon.ico")).scaled(64, 64, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)) # Pencere ikonunu kullan
        except Exception as e:
            print(f"DEBUG: Sonuç ikonunu yükleyemedi: {e}")
            msgBox.setIcon(QMessageBox.Icon.Information) # İkon yüklenemezse varsayılanı kullan
            
        msgBox.setStyleSheet("QMessageBox { background-color: #252535; font-size: 11px; } QLabel { color: #e0e0e5; font-size: 11px; }")
        msgBox.exec()


    def closeEvent(self, event):
        if self.downloader_thread and self.downloader_thread.isRunning():
            self.downloader_thread.stop(); self.downloader_thread.wait()
        if self.fetcher_thread and self.fetcher_thread.isRunning():
            self.fetcher_thread.stop(); self.fetcher_thread.wait()
        event.accept()

# --- Uygulamayı Başlat ---
if __name__ == '__main__':
    QCoreApplication.setOrganizationName("MyCompany")
    QCoreApplication.setApplicationName("KolayTikTokIndirici")

    app = QApplication(sys.argv)
    ex = App()
    sys.exit(app.exec())