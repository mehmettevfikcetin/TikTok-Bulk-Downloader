# -*- coding: utf-8 -*-


import sys
import os
import time
import subprocess
import json
import re # URL ve Dosya adından ID ayıklamak için gerekli
import requests # YENİ EKLENDI (İnternetten veri çekmek için)

from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTextEdit,
    QPushButton, QLineEdit, QFileDialog, QTableWidget, QTableWidgetItem,
    QProgressBar, QMessageBox, QHeaderView, QFrame, QScrollArea,
    QAbstractItemView, QDialog, QTextBrowser
)
from PyQt6.QtCore import QThread, pyqtSignal, Qt, QSettings, QCoreApplication, QSize, QTimer, QUrl # QTimer eklendi
from PyQt6.QtGui import QDesktopServices, QIcon, QPalette, QColor, QFont, QPixmap # QPixmap eklendi

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

# FFmpeg konumu (ses/görüntü birleştirme ve senkronizasyon için)
FFMPEG_DIR = '.'
try:
    _ffmpeg_exe_internal = resource_path('ffmpeg.exe')
    if os.path.exists(_ffmpeg_exe_internal): FFMPEG_DIR = os.path.dirname(_ffmpeg_exe_internal)
except Exception: pass

# Ortak User-Agent (Çerezlerle uyumlu güncel masaüstü kimliği)
COMMON_USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36'

# --- STİL KONSTANTLARı (Modern Pro Paleti) ---
class StyleConstants:
    # Modern Pro Renk Paleti (Catppuccin Mocha bazlı)
    BG_PRIMARY = "#1e1e2e"      # Çok koyu lacivert (Ana zemin)
    BG_SURFACE = "#313244"      # Panel/Kutu arka planı
    BG_INPUT = "#3b3d52"        # Input alanları (AÇILDI - okunurluk için)
    BORDER = "#585b70"          # Kenarlıklar
    TEXT_PRIMARY = "#cdd6f4"    # Ana metin (Kırık beyaz)
    TEXT_SECONDARY = "#bac2de"  # İkincil metin (AÇILDI - okunurluk için)
    TEXT_MUTED = "#7f849c"      # Çok soluk metin (footerlar vs)
    ACCENT = "#89b4fa"          # Vurgu rengi (Yumuşak Mavi)
    ACCENT_HOVER = "#b4befe"    # Buton Hover
    ERROR = "#f38ba8"           # Hata Rengi
    SUCCESS = "#a6e3a1"         # Başarı Rengi
    WARNING = "#fab387"         # Uyarı/Turuncu Rengi
    
    # Font
    FONT_FAMILY = "Segoe UI"
    FONT_SIZE_BASE = 14
    BORDER_RADIUS = 8  # Sayısal tut, px eklemesini stylesheet'te yap
    
    @staticmethod
    def get_stylesheet():
        S = StyleConstants
        return f"""
            * {{
                font-family: {S.FONT_FAMILY}, Roboto, Arial, sans-serif;
                font-size: 14px;
            }}
            
            QWidget {{
                background-color: {S.BG_PRIMARY};
                color: {S.TEXT_PRIMARY};
            }}
            
            QDialog {{
                background-color: {S.BG_PRIMARY};
                color: {S.TEXT_PRIMARY};
            }}
            
            QLabel {{
                color: {S.TEXT_PRIMARY};
                background: transparent;
                border: none;
            }}
            
            QLineEdit {{
                background-color: {S.BG_INPUT};
                color: {S.TEXT_PRIMARY};
                border: 1px solid {S.BORDER};
                border-radius: {S.BORDER_RADIUS}px;
                padding: 8px 12px;
                min-height: 38px;
                font-size: 14px;
            }}
            
            QLineEdit:focus {{
                border: 2px solid {S.ACCENT};
            }}
            
            QPushButton {{
                background-color: {S.ACCENT};
                color: white;
                border: none;
                border-radius: {S.BORDER_RADIUS}px;
                padding: 8px 18px;
                font-weight: bold;
                min-height: 36px;
                font-size: 13px;
            }}
            
            QPushButton:hover {{
                background-color: {S.ACCENT_HOVER};
            }}
            
            QPushButton:pressed {{
                background-color: #6ba5f5;
            }}
            
            QPushButton:disabled {{
                background-color: {S.BORDER};
                color: {S.TEXT_MUTED};
            }}
            
            QTableWidget {{
                background-color: {S.BG_INPUT};
                color: {S.TEXT_PRIMARY};
                gridline-color: {S.BORDER};
                border: 1px solid {S.BORDER};
                border-radius: {S.BORDER_RADIUS}px;
                font-size: 12px;
            }}
            
            QHeaderView::section {{
                background-color: {S.BG_SURFACE};
                color: {S.ACCENT};
                border: none;
                padding: 8px;
                font-weight: bold;
                font-size: 13px;
            }}
            
            QTableWidget::item {{
                padding: 6px;
                border-bottom: 1px solid {S.BORDER};
            }}
            
            QTableWidget::item:selected {{
                background-color: {S.ACCENT};
                color: {S.BG_PRIMARY};
            }}
            
            QFrame {{
                background-color: {S.BG_SURFACE};
                border: 1px solid {S.BORDER};
                border-radius: {S.BORDER_RADIUS}px;
            }}
            
            QTextBrowser {{
                background-color: {S.BG_INPUT};
                color: {S.TEXT_PRIMARY};
                border: 1px solid {S.BORDER};
                border-radius: {S.BORDER_RADIUS}px;
                padding: 12px;
                font-size: 14px;
            }}
            
            QScrollBar:vertical {{
                border: none;
                background: {S.BG_PRIMARY};
                width: 10px;
                margin: 0;
            }}
            
            QScrollBar::handle:vertical {{
                background: {S.BORDER};
                min-height: 20px;
                border-radius: 5px;
            }}
            
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
                height: 0;
                border: none;
                background: none;
            }}
            
            QProgressBar {{
                border: 1px solid {S.BORDER};
                border-radius: {S.BORDER_RADIUS}px;
                text-align: center;
                background-color: {S.BG_INPUT};
                color: {S.TEXT_PRIMARY};
                height: 24px;
                font-weight: bold;
            }}
            
            QProgressBar::chunk {{
                background: {S.ACCENT};
                border-radius: 6px;
                margin: 1px;
            }}
            
            QTextEdit {{
                background-color: {S.BG_INPUT};
                color: {S.TEXT_PRIMARY};
                border: 1px solid {S.BORDER};
                border-radius: {S.BORDER_RADIUS}px;
                padding: 10px;
            }}
            
            QTextEdit:focus {{
                border: 2px solid {S.ACCENT};
            }}
            
            QMessageBox {{
                background-color: {S.BG_PRIMARY};
            }}
            QMessageBox QLabel {{
                color: {S.TEXT_PRIMARY};
                font-size: 13px;
                background: transparent;
            }}
            QMessageBox QPushButton {{
                min-width: 90px;
                min-height: 32px;
                padding: 6px 16px;
                border-radius: {S.BORDER_RADIUS}px;
                font-weight: bold;
            }}
        """

# --- YENİ CLASS: Hata Detay Penceresi ---
class ErrorDialog(QDialog):
    def __init__(self, error_list, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Hatalı Videolar Listesi")
        self.setMinimumSize(750, 420)
        self.resize(900, 520)
        
        # Stil uygula (layout'tan ÖNCE)
        self.setStyleSheet(StyleConstants.get_stylesheet())
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(16)
        
        # Başlık
        info_label = QLabel(f"   Hata Detayları — Toplam {len(error_list)} video indirilemedi")
        info_label.setFont(QFont(StyleConstants.FONT_FAMILY, 14, QFont.Weight.Bold))
        info_label.setStyleSheet(f"color: {StyleConstants.ERROR}; border: none; background: transparent;")
        layout.addWidget(info_label)
        
        # Hata Tablosu
        self.table = QTableWidget()
        self.table.setColumnCount(2)
        self.table.setHorizontalHeaderLabels(["Video URL", "Hata Nedeni"])
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Interactive)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.table.horizontalHeader().resizeSection(0, 350)
        self.table.verticalHeader().setVisible(False)
        self.table.setRowCount(len(error_list))
        self.table.setWordWrap(True)
        self.table.setAlternatingRowColors(False)
        self.table.setStyleSheet(f"""
            QTableWidget {{
                background-color: {StyleConstants.BG_INPUT};
                color: {StyleConstants.TEXT_PRIMARY};
                gridline-color: {StyleConstants.BORDER};
                border: 1px solid {StyleConstants.BORDER};
                border-radius: {StyleConstants.BORDER_RADIUS}px;
                font-size: 11px;
            }}
            QHeaderView::section {{
                background-color: {StyleConstants.BG_SURFACE};
                color: {StyleConstants.ACCENT};
                border: none;
                padding: 8px 12px;
                font-weight: bold;
                font-size: 12px;
                border-bottom: 2px solid {StyleConstants.ACCENT};
            }}
            QTableWidget::item {{
                padding: 8px;
                border-bottom: 1px solid {StyleConstants.BORDER};
            }}
            QTableWidget::item:selected {{
                background-color: {StyleConstants.ACCENT};
                color: {StyleConstants.BG_PRIMARY};
            }}
        """)
        
        for i, item in enumerate(error_list):
            url_text = item['url'][:80] + "..." if len(item['url']) > 80 else item['url']
            url_item = QTableWidgetItem(url_text)
            error_item = QTableWidgetItem(item['error'])
            error_item.setForeground(QColor(StyleConstants.ERROR))
            
            self.table.setItem(i, 0, url_item)
            self.table.setItem(i, 1, error_item)
            self.table.resizeRowToContents(i)
            
        layout.addWidget(self.table)
        
        # Buton Layout
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(12)
        
        copy_btn = QPushButton("   Kopyala")
        copy_btn.setFixedHeight(40)
        copy_btn.setMinimumWidth(140)
        copy_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        copy_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {StyleConstants.ACCENT};
                color: white; border: none; border-radius: {StyleConstants.BORDER_RADIUS}px;
                font-weight: bold; font-size: 13px; padding: 8px 20px;
            }}
            QPushButton:hover {{ background-color: {StyleConstants.ACCENT_HOVER}; }}
        """)
        copy_btn.clicked.connect(self.copy_all_urls)
        btn_layout.addWidget(copy_btn)
        
        btn_layout.addStretch()
        
        close_btn = QPushButton("   Kapat")
        close_btn.setFixedHeight(40)
        close_btn.setMinimumWidth(140)
        close_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        close_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {StyleConstants.BG_INPUT};
                color: {StyleConstants.TEXT_PRIMARY}; border: 1px solid {StyleConstants.BORDER};
                border-radius: {StyleConstants.BORDER_RADIUS}px;
                font-weight: bold; font-size: 13px; padding: 8px 20px;
            }}
            QPushButton:hover {{ background-color: {StyleConstants.BORDER}; }}
        """)
        close_btn.clicked.connect(self.close)
        btn_layout.addWidget(close_btn)
        
        layout.addLayout(btn_layout)

    def copy_all_urls(self):
        urls = []
        for row in range(self.table.rowCount()):
            item = self.table.item(row, 0)
            if item: urls.append(item.text())
        
        QApplication.clipboard().setText("\n".join(urls))
        QMessageBox.information(self, "Başarılı", "Hatalı URL'ler panoya kopyalandı.")

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
            self.fetchStatus.emit(f"yt-dlp ile {self.target_url} adresinden linkler derinlemesine taranıyor (Mobil Modu)...")
            
            # --- LinkFetcherThread GÜNCELLEMESİ ---
            command = [
                YT_DLP_PATH,
                '--cookies', self.cookies_path,
                '--skip-download',
                '--flat-playlist',
                '-J', # JSON çıktısı al
                '--no-warnings',
                '--ignore-errors',       # Hatalı videoları atla, durma
                '--no-cache-dir',        # Eski önbelleği kullanma, taze veri çek
                '--retries', '10',       # Hata alırsan 10 kere tekrar dene
                '--fragment-retries', '10',
                '--extractor-retries', '5',  # Sayfa kazıma hatalarında tekrar dene
                '--socket-timeout', '30',    # Bağlantı zaman aşımı (saniye)
                '--sleep-requests', '1.5',   # Her istek arası bekleme
                '--sleep-interval', '1',     # İstekler arası minimum bekleme
                # MASAÜSTÜ KİMLİĞİ (Çerezlerle eşleşmesi için)
                '--user-agent', COMMON_USER_AGENT,
                '--referer', 'https://www.tiktok.com/',
                self.target_url
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
            
            # Bulunan sayı ile ilgili bilgilendirme
            print(f"DEBUG: Bulunan link sayısı: {len(urls)}")
            self.linksFetched.emit(urls)
            
        except FileNotFoundError:
             self.fetchError.emit(f"Hata: '{YT_DLP_PATH}' bulunamadı.")
        except Exception as e:
            self.fetchError.emit(f"Link alma sırasında beklenmedik hata: {str(e)}")

    def stop(self):
        self.running = False


# --- İndirme Thread'i (Hızlı Yerel Kontrol + Hata Raporlama Özellikli) ---
# --- GÜNCELLENMİŞ İndirme Thread'i (subprocess kullanan kararlı versiyon) ---
class DownloaderThread(QThread):
    videoFinished = pyqtSignal(int, str, str)
    progressUpdated = pyqtSignal(int, int)
    allFinished = pyqtSignal(int, int, int, list)

    def __init__(self, urls, target_dir, cookies_path):
        super().__init__()
        self.urls = urls
        self.target_dir = target_dir
        self.cookies_path = cookies_path
        self.running = True
        self.stats = {'completed': 0, 'skipped': 0, 'errors': 0}
        self.failed_list = []

    def get_existing_video_ids(self):
        existing_ids = set()
        if not os.path.exists(self.target_dir): return existing_ids
        try:
            files = os.listdir(self.target_dir)
            for f in files:
                if f.endswith(".mp4"):
                    match = re.search(r'_(\d+)\.mp4$', f)
                    if match: existing_ids.add(match.group(1))
        except Exception: pass
        return existing_ids

    def extract_id_from_url(self, url):
        match = re.search(r'/video/(\d+)', url)
        if match: return match.group(1)
        return None

    def run(self):
        existing_ids = self.get_existing_video_ids()

        for i, url in enumerate(self.urls):
            if not self.running: break
            
            video_id = self.extract_id_from_url(url) or "Bilinmiyor"
            
            # 1. HIZLI KONTROL (Var mı?)
            if video_id in existing_ids:
                self.stats['skipped'] += 1
                self.videoFinished.emit(i, video_id, "ATLANDI (Mevcut)")
                self.progressUpdated.emit(i, 100)
                time.sleep(0.05)
                continue

            # 2. İNDİRME (subprocess ile yt-dlp.exe çağırarak)
            try:
                # Dosya adı formatı: Baslik_ID.mp4
                output_template = os.path.join(self.target_dir, "%(title).30s_%(id)s.%(ext)s")
                
                command = [
                    YT_DLP_PATH,
                    '--cookies', self.cookies_path,
                    '--output', output_template,
                    '--no-overwrites',
                    '--no-warnings',
                    '--ignore-errors',
                    '--newline',  # İlerleme çubuğu için gerekli
                    # --- SES/GÖRÜNTÜ SENKRONİZASYONU ---
                    '--format', 'b[ext=mp4]/bv*+ba/b',       # Önce hazır mp4, yoksa birleştir
                    '--merge-output-format', 'mp4',            # Çıktı her zaman mp4 olsun
                    '--ffmpeg-location', FFMPEG_DIR,            # FFmpeg konumunu göster
                    '--fixup', 'force',                        # Bozuk zaman damgalarını onar
                    '--postprocessor-args', 'ffmpeg:-avoid_negative_ts make_zero',  # Negatif zaman damgası düzelt
                    # --- KARARLILIK / HATA YÖNETİMİ ---
                    '--retries', '5',
                    '--fragment-retries', '5',
                    '--extractor-retries', '3',
                    '--socket-timeout', '30',
                    '--no-cache-dir',
                    # --- MASAÜSTÜ KİMLİĞİ ---
                    '--user-agent', COMMON_USER_AGENT,
                    '--referer', 'https://www.tiktok.com/',
                    url
                ]

                process = subprocess.Popen(
                    command,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    encoding='utf-8',
                    errors='ignore',
                    creationflags=subprocess.CREATE_NO_WINDOW
                )

                status_message = "İndiriliyor..."
                
                # Çıktıyı satır satır oku (İlerleme çubuğu için)
                while True:
                    line = process.stdout.readline()
                    if not line and process.poll() is not None:
                        break
                    if line:
                        # yt-dlp çıktısından yüzdeyi yakala: "[download]  45.0% of 10.00MiB..."
                        if "[download]" in line and "%" in line:
                            try:
                                parts = line.split()
                                for part in parts:
                                    if "%" in part:
                                        percent = float(part.replace("%", ""))
                                        self.progressUpdated.emit(i, int(percent))
                                        break
                            except: pass

                if process.returncode == 0:
                    self.stats['completed'] += 1
                    self.videoFinished.emit(i, video_id, "TAMAMLANDI")
                    self.progressUpdated.emit(i, 100)
                else:
                    # Hata varsa stderr oku
                    err_out = process.stderr.read()
                    self.stats['errors'] += 1
                    clean_err = err_out.strip() or "Bilinmeyen Hata"
                    self.failed_list.append({'url': url, 'error': clean_err})
                    self.videoFinished.emit(i, video_id, "HATA")

            except Exception as e:
                self.stats['errors'] += 1
                self.failed_list.append({'url': url, 'error': str(e)})
                self.videoFinished.emit(i, video_id, f"HATA: {str(e)[:20]}")

            # TikTok'un engellememesi için bekleme süresi
            if self.running: time.sleep(2)

        self.allFinished.emit(self.stats['completed'], self.stats['skipped'], self.stats['errors'], self.failed_list)

    def stop(self):
        self.running = False


# --- YENİ CLASS: Ayarlar ve Hakkında Penceresi ---
class SettingsDialog(QDialog):
    def __init__(self, current_version, parent=None):
        super().__init__(parent)
        self.parent_app = parent
        self.setWindowTitle("Ayarlar & Hakkında")
        self.setFixedSize(480, 380)
        
        # Stil uygula (layout'tan ÖNCE)
        self.setStyleSheet(StyleConstants.get_stylesheet())
        
        layout = QVBoxLayout(self)
        layout.setSpacing(16)
        layout.setContentsMargins(24, 24, 24, 24)

        # --- Üst Kısım: Versiyon ve Güncelleme ---
        version_frame = QFrame()
        version_frame.setStyleSheet(f"""
            QFrame {{
                background-color: {StyleConstants.BG_SURFACE};
                border: 1px solid {StyleConstants.BORDER};
                border-radius: {StyleConstants.BORDER_RADIUS}px;
            }}
        """)
        v_layout = QVBoxLayout(version_frame)
        v_layout.setSpacing(14)
        v_layout.setContentsMargins(20, 18, 20, 18)
        
        self.version_label = QLabel(f"Mevcut Sürüm: v{current_version}")
        self.version_label.setFont(QFont(StyleConstants.FONT_FAMILY, 14, QFont.Weight.Bold))
        self.version_label.setStyleSheet(f"color: {StyleConstants.ACCENT}; border: none; background: transparent;")
        v_layout.addWidget(self.version_label)
        
        self.update_btn = QPushButton("Güncellemeleri Kontrol Et")
        self.update_btn.setFixedHeight(42)
        self.update_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.update_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {StyleConstants.ACCENT}; color: white;
                border: none; border-radius: {StyleConstants.BORDER_RADIUS}px;
                font-weight: bold; font-size: 13px; padding: 8px 20px;
            }}
            QPushButton:hover {{ background-color: {StyleConstants.ACCENT_HOVER}; }}
            QPushButton:disabled {{ background-color: {StyleConstants.BORDER}; color: {StyleConstants.TEXT_MUTED}; }}
        """)
        self.update_btn.clicked.connect(self.check_update_click)
        v_layout.addWidget(self.update_btn)
        
        layout.addWidget(version_frame)

        # --- Alt Kısım: Geliştirici ve GitHub ---
        dev_frame = QFrame()
        dev_frame.setStyleSheet(f"""
            QFrame {{
                background-color: {StyleConstants.BG_SURFACE};
                border: 1px solid {StyleConstants.BORDER};
                border-radius: {StyleConstants.BORDER_RADIUS}px;
            }}
        """)
        d_layout = QVBoxLayout(dev_frame)
        d_layout.setSpacing(10)
        d_layout.setContentsMargins(20, 18, 20, 18)
        
        dev_title = QLabel("Geliştirici")
        dev_title.setFont(QFont(StyleConstants.FONT_FAMILY, 13, QFont.Weight.Bold))
        dev_title.setStyleSheet(f"color: {StyleConstants.TEXT_PRIMARY}; border: none; background: transparent;")
        d_layout.addWidget(dev_title)
        
        github_info = QLabel('GitHub Profilini Ziyaret Et  →')
        github_info.setFont(QFont(StyleConstants.FONT_FAMILY, 12))
        github_info.setStyleSheet(f"color: {StyleConstants.ACCENT}; border: none; background: transparent;")
        github_info.setCursor(Qt.CursorShape.PointingHandCursor)
        github_info.mousePressEvent = self.open_github
        d_layout.addWidget(github_info)
        
        layout.addWidget(dev_frame)
        layout.addStretch()
        
        # Kapat Butonu
        close_btn = QPushButton("Kapat")
        close_btn.setFixedHeight(42)
        close_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        close_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {StyleConstants.BG_INPUT};
                color: {StyleConstants.TEXT_PRIMARY}; border: 1px solid {StyleConstants.BORDER};
                border-radius: {StyleConstants.BORDER_RADIUS}px;
                font-weight: bold; font-size: 13px; padding: 8px 20px;
            }}
            QPushButton:hover {{ background-color: {StyleConstants.BORDER}; }}
        """)
        close_btn.clicked.connect(self.close)
        layout.addWidget(close_btn)

    def open_github(self, event):
        # Kendi GitHub linkini buraya yaz
        QDesktopServices.openUrl(QUrl("https://github.com/mehmettevfikcetin"))

    def check_update_click(self):
        self.update_btn.setText("⏳ Kontrol Ediliyor...")
        self.update_btn.setEnabled(False)
        self.parent_app.check_for_updates(manual=True)
        QTimer.singleShot(2000, lambda: (
            self.update_btn.setText("🔄 Güncellemeleri Kontrol Et"),
            self.update_btn.setEnabled(True)
        ))


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
        self.setGeometry(200, 200, 1000, 900)
        self.setMinimumSize(900, 750)
        try:
            self.setWindowIcon(QIcon(resource_path("icon.ico")))
        except Exception:
            pass

        # Global Stil Uygula
        self.setStyleSheet(StyleConstants.get_stylesheet())

        main_layout = QVBoxLayout()
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0, 0, 0, 0)

        # --- BAŞLIK BÖLÜMÜ ---
        header = QFrame()
        header.setStyleSheet(f"""
            QFrame {{
                background-color: {StyleConstants.BG_SURFACE};
                border: none;
                border-bottom: 2px solid {StyleConstants.ACCENT};
                border-radius: 0px;
            }}
        """)
        header.setMinimumHeight(90)
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(30, 20, 30, 20)
        header_layout.setSpacing(15)

        # Yardım Butonu
        self.help_button = QPushButton("Yardım")
        self.help_button.setMinimumWidth(100)
        self.help_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.help_button.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                color: {StyleConstants.ACCENT};
                border: 2px solid {StyleConstants.ACCENT};
                border-radius: 8px;
                padding: 8px 16px;
                font-weight: bold;
            }}
            QPushButton:hover {{ background-color: {StyleConstants.ACCENT}; color: white; }}
        """)
        self.help_button.clicked.connect(self.show_help_dialog)
        header_layout.addWidget(self.help_button)

        header_layout.addStretch(1)

        # Ana Başlık
        title = QLabel('TikTok Toplu Video İndirici')
        title_font = QFont(StyleConstants.FONT_FAMILY, 24, QFont.Weight.Bold)
        title.setFont(title_font)
        title.setStyleSheet(f"color: {StyleConstants.ACCENT}; background-color: transparent; border: none;")
        header_layout.addWidget(title)

        header_layout.addStretch(1)

        # Ayarlar Butonu
        self.settings_button = QPushButton("Ayarlar")
        self.settings_button.setMinimumWidth(100)
        self.settings_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.settings_button.setStyleSheet(f"""
            QPushButton {{
                background-color: {StyleConstants.ACCENT};
                color: white;
                border: none;
                border-radius: 8px;
                padding: 10px 20px;
                font-weight: bold;
            }}
            QPushButton:hover {{ background-color: {StyleConstants.ACCENT_HOVER}; }}
        """)
        self.settings_button.clicked.connect(self.open_settings_dialog)
        header_layout.addWidget(self.settings_button)

        main_layout.addWidget(header)

        # --- SCROLL AREA ---
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet(f"""
            QScrollArea {{ border: none; background-color: {StyleConstants.BG_PRIMARY}; }}
        """)
        
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout(scroll_widget)
        scroll_layout.setSpacing(20)
        scroll_layout.setContentsMargins(30, 20, 30, 20)

        # --- AŞAMA 1: AYARLAR ---
        settings_frame = QFrame()
        settings_frame.setStyleSheet(f"background-color: {StyleConstants.BG_SURFACE}; border: 1px solid {StyleConstants.BORDER}; border-radius: {StyleConstants.BORDER_RADIUS}px;")
        settings_content = QVBoxLayout(settings_frame)
        settings_content.setContentsMargins(20, 20, 20, 20)
        settings_content.setSpacing(15)

        settings_title = QLabel('Adım 1: Ayarlamalar')
        settings_title.setFont(QFont(StyleConstants.FONT_FAMILY, 14, QFont.Weight.Bold))
        settings_title.setStyleSheet(f"color: {StyleConstants.ACCENT}; border: none; background: transparent;")
        settings_content.addWidget(settings_title)

        # Çerez Dosyası
        cookie_layout = QHBoxLayout()
        cookie_layout.setSpacing(10)
        cookie_label = QLabel("Çerez Dosyası:")
        cookie_label.setFont(QFont(StyleConstants.FONT_FAMILY, 11))
        cookie_layout.addWidget(cookie_label)
        
        self.cookie_path_input = QLineEdit()
        self.cookie_path_input.setReadOnly(True)
        self.cookie_path_input.setPlaceholderText("Çerez dosyasını seçin...")
        self.cookie_path_input.setMinimumHeight(40)
        self.cookie_path_input.setStyleSheet(f"""
            QLineEdit {{
                background-color: {StyleConstants.BG_INPUT};
                color: {StyleConstants.TEXT_PRIMARY};
                border: 1px solid {StyleConstants.BORDER};
                border-radius: {StyleConstants.BORDER_RADIUS}px;
                padding: 8px 12px;
                font-size: 11px;
            }}
        """)
        saved_cookie_path = self.settings.value("cookiePath", "")
        self.cookie_path_input.setText(saved_cookie_path)
        cookie_layout.addWidget(self.cookie_path_input, 1)
        
        self.browse_cookie_button = self.create_button('📂 Seç', StyleConstants.ACCENT)
        self.browse_cookie_button.setMinimumHeight(40)
        self.browse_cookie_button.setMinimumWidth(90)
        self.browse_cookie_button.clicked.connect(self.browse_cookie_file)
        cookie_layout.addWidget(self.browse_cookie_button)
        settings_content.addLayout(cookie_layout)

        cookie_instructions = QLabel("Tarayıcı eklentisi ('Get cookies.txt LOCALLY') ile TikTok çerez dosyasını seçin.")
        cookie_instructions.setStyleSheet(f"color: {StyleConstants.TEXT_MUTED}; font-size: 11px; border: none; background: transparent;")
        cookie_instructions.setWordWrap(True)
        settings_content.addWidget(cookie_instructions)

        target_url_layout = QHBoxLayout()
        target_url_layout.setSpacing(15)
        target_url_label = QLabel("Hedef URL:")
        target_url_label.setFont(QFont(StyleConstants.FONT_FAMILY, 11, QFont.Weight.Bold))
        target_url_label.setStyleSheet(f"color: {StyleConstants.TEXT_PRIMARY}; border: none;")
        target_url_layout.addWidget(target_url_label)
        self.target_url_input = self.create_input_field()
        self.target_url_input.setMinimumHeight(40)
        self.target_url_input.setPlaceholderText("https://www.tiktok.com/@username/... URL yapıştırın")
        saved_target_url = self.settings.value("targetUrl", "")
        self.target_url_input.setText(saved_target_url)
        self.target_url_input.textChanged.connect(lambda: self.settings.setValue("targetUrl", self.target_url_input.text()))
        target_url_layout.addWidget(self.target_url_input, 1)
        settings_content.addLayout(target_url_layout)

        scroll_layout.addWidget(settings_frame)

        # --- AŞAMA 2: LİNKLERİ GETİR ---
        fetch_frame = QFrame()
        fetch_frame.setStyleSheet(f"""
            QFrame {{
                background-color: {StyleConstants.BG_SURFACE};
                border: 1px solid {StyleConstants.BORDER};
                border-radius: {StyleConstants.BORDER_RADIUS}px;
            }}
        """)
        fetch_content = QVBoxLayout(fetch_frame)
        fetch_content.setContentsMargins(25, 20, 25, 20)
        fetch_content.setSpacing(15)

        fetch_title = QLabel('Adım 2: Bağlantıları Al')
        fetch_title.setFont(QFont(StyleConstants.FONT_FAMILY, 14, QFont.Weight.Bold))
        fetch_title.setStyleSheet(f"color: {StyleConstants.ACCENT}; border: none; background: transparent;")
        fetch_content.addWidget(fetch_title)

        self.fetch_links_button = self.create_button('🎯 Bağlantıları Getir', StyleConstants.SUCCESS)
        self.fetch_links_button.setMinimumHeight(50)
        self.fetch_links_button.setFont(QFont(StyleConstants.FONT_FAMILY, 12, QFont.Weight.Bold))
        self.fetch_links_button.clicked.connect(self.start_link_fetch)
        fetch_content.addWidget(self.fetch_links_button)

        self.fetch_status_label = QLabel('Başlamak için ayarları yapıp butona basın.')
        self.fetch_status_label.setFont(QFont(StyleConstants.FONT_FAMILY, 10))
        self.fetch_status_label.setStyleSheet(f"color: {StyleConstants.TEXT_SECONDARY}; border: none; background: transparent;")
        self.fetch_status_label.setWordWrap(True)
        fetch_content.addWidget(self.fetch_status_label)

        self.url_input = QTextEdit()
        self.url_input.setPlaceholderText("Linkler buraya gelecek...")
        self.url_input.setMinimumHeight(120)
        self.url_input.setMaximumHeight(180)
        self.url_input.setStyleSheet(f"""
            QTextEdit {{
                background-color: {StyleConstants.BG_INPUT};
                color: {StyleConstants.TEXT_PRIMARY};
                border: 1px solid {StyleConstants.BORDER};
                border-radius: {StyleConstants.BORDER_RADIUS}px;
                padding: 10px;
                font-size: 11px;
                font-family: 'Consolas', 'Courier New', monospace;
            }}
            QTextEdit:focus {{
                border: 2px solid {StyleConstants.ACCENT};
            }}
        """)
        self.url_input.textChanged.connect(self.update_download_button_state)
        fetch_content.addWidget(self.url_input)

        scroll_layout.addWidget(fetch_frame)

        # --- AŞAMA 3: İNDİRME ---
        download_frame = QFrame()
        download_frame.setStyleSheet(f"""
            QFrame {{
                background-color: {StyleConstants.BG_SURFACE};
                border: 1px solid {StyleConstants.BORDER};
                border-radius: {StyleConstants.BORDER_RADIUS}px;
            }}
        """)
        download_content = QVBoxLayout(download_frame)
        download_content.setContentsMargins(25, 20, 25, 20)
        download_content.setSpacing(15)

        download_title = QLabel('Adım 3: İndir')
        download_title.setFont(QFont(StyleConstants.FONT_FAMILY, 14, QFont.Weight.Bold))
        download_title.setStyleSheet(f"color: {StyleConstants.ACCENT}; border: none; background: transparent;")
        download_content.addWidget(download_title)

        folder_layout = QHBoxLayout()
        folder_layout.setSpacing(12)
        folder_label = QLabel("İndirme Klasörü:")
        folder_label.setFont(QFont(StyleConstants.FONT_FAMILY, 11, QFont.Weight.Bold))
        folder_label.setStyleSheet(f"color: {StyleConstants.TEXT_PRIMARY}; border: none;")
        folder_layout.addWidget(folder_label)
        self.folder_path_input = self.create_input_field()
        self.folder_path_input.setReadOnly(True)
        self.folder_path_input.setPlaceholderText("Klasör seçin...")
        self.folder_path_input.setMinimumHeight(40)
        saved_folder_path = self.settings.value("downloadPath", "")
        self.folder_path_input.setText(saved_folder_path)
        folder_layout.addWidget(self.folder_path_input, 1)
        self.browse_button = self.create_button('📁 Gözat', StyleConstants.ACCENT)
        self.browse_button.setMinimumHeight(40)
        self.browse_button.setMinimumWidth(100)
        self.browse_button.clicked.connect(self.browse_folder)
        folder_layout.addWidget(self.browse_button)
        download_content.addLayout(folder_layout)

        # İndirme Butonları Satırı
        download_btn_layout = QHBoxLayout()
        download_btn_layout.setSpacing(12)

        self.download_button = self.create_button('⚡ İndirmeyi Başlat', StyleConstants.ERROR)
        self.download_button.setMinimumHeight(55)
        self.download_button.setMaximumWidth(16777215)
        self.download_button.setFont(QFont(StyleConstants.FONT_FAMILY, 13, QFont.Weight.Bold))
        self.download_button.clicked.connect(self.start_download)
        download_btn_layout.addWidget(self.download_button, stretch=3)

        self.open_folder_button = self.create_button('Klasörü Aç', StyleConstants.ACCENT)
        self.open_folder_button.setMinimumHeight(55)
        self.open_folder_button.setMaximumWidth(16777215)
        self.open_folder_button.setFont(QFont(StyleConstants.FONT_FAMILY, 12, QFont.Weight.Bold))
        self.open_folder_button.setStyleSheet(f"""
            QPushButton {{
                background-color: {StyleConstants.BG_INPUT};
                color: {StyleConstants.TEXT_PRIMARY}; border: 1px solid {StyleConstants.BORDER};
                border-radius: {StyleConstants.BORDER_RADIUS}px;
                font-weight: bold; font-size: 12px; padding: 10px 16px;
            }}
            QPushButton:hover {{ background-color: {StyleConstants.BORDER}; }}
            QPushButton:disabled {{ background-color: {StyleConstants.BG_INPUT}; color: {StyleConstants.TEXT_MUTED}; border: 1px solid {StyleConstants.BORDER}; }}
        """)
        self.open_folder_button.clicked.connect(self.open_download_folder)
        self.open_folder_button.setEnabled(False)
        download_btn_layout.addWidget(self.open_folder_button, stretch=1)

        download_content.addLayout(download_btn_layout)

        # --- İlerleme Tablosu ---
        self.status_table = QTableWidget()
        self.status_table.setColumnCount(4)
        self.status_table.setHorizontalHeaderLabels(['URL', 'ID', 'Durum', 'İlerleme'])
        self.status_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.status_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        self.status_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        self.status_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.Fixed)
        self.status_table.horizontalHeader().resizeSection(3, 110)
        self.status_table.verticalHeader().setVisible(False)
        self.status_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.status_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.status_table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.status_table.setMinimumHeight(220)
        self.status_table.setStyleSheet(f"""
            QTableWidget {{
                background-color: {StyleConstants.BG_INPUT};
                color: {StyleConstants.TEXT_PRIMARY};
                gridline-color: {StyleConstants.BORDER};
                border: 1px solid {StyleConstants.BORDER};
                border-radius: {StyleConstants.BORDER_RADIUS}px;
                font-size: 11px;
            }}
            QHeaderView::section {{
                background-color: {StyleConstants.BG_SURFACE};
                color: {StyleConstants.ACCENT};
                border: none;
                padding: 8px 12px;
                font-weight: bold;
                font-size: 12px;
                border-bottom: 2px solid {StyleConstants.ACCENT};
            }}
            QTableWidget::item {{
                padding: 8px;
                border-bottom: 1px solid {StyleConstants.BORDER};
            }}
            QTableWidget::item:selected {{
                background-color: {StyleConstants.ACCENT};
                color: {StyleConstants.BG_PRIMARY};
            }}
        """)
        download_content.addWidget(self.status_table)

        # Toplam İlerleme Çubuğu
        self.total_progress_bar = QProgressBar()
        self.total_progress_bar.setValue(0)
        self.total_progress_bar.setTextVisible(True)
        self.total_progress_bar.setFormat('⚙ Toplam: %p%')
        self.total_progress_bar.setMinimumHeight(32)
        self.total_progress_bar.setStyleSheet(f"""
            QProgressBar {{
                border: 1px solid {StyleConstants.BORDER};
                border-radius: {StyleConstants.BORDER_RADIUS}px;
                text-align: center;
                background-color: {StyleConstants.BG_INPUT};
                color: {StyleConstants.TEXT_PRIMARY};
                font-weight: bold;
                font-size: 11px;
            }}
            QProgressBar::chunk {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, 
                    stop:0 {StyleConstants.ACCENT}, 
                    stop:1 {StyleConstants.SUCCESS});
                border-radius: 7px;
                margin: 1px;
            }}
        """)
        download_content.addWidget(self.total_progress_bar)

        scroll_layout.addWidget(download_frame)
        scroll_layout.addStretch() # Elemanları yukarı iter

        scroll.setWidget(scroll_widget)
        main_layout.addWidget(scroll, 1) # Scroll area ana layout'a eklenir

        # --- FOOTER BAR ---
        footer = QFrame()
        footer.setFixedHeight(36)
        footer.setStyleSheet(f"""
            QFrame {{
                background-color: {StyleConstants.BG_SURFACE};
                border-top: 1px solid {StyleConstants.BORDER};
                border-radius: 0px;
                border-left: none;
                border-right: none;
                border-bottom: none;
            }}
        """)
        footer_layout = QHBoxLayout(footer)
        footer_layout.setContentsMargins(20, 0, 20, 0)

        footer_version = QLabel(f"v{self.get_app_version()}")
        footer_version.setStyleSheet(f"color: {StyleConstants.TEXT_MUTED}; font-size: 11px; border: none;")
        footer_layout.addWidget(footer_version)

        footer_layout.addStretch()

        footer_credit = QLabel("TikTok Bulk Downloader")
        footer_credit.setStyleSheet(f"color: {StyleConstants.TEXT_MUTED}; font-size: 11px; border: none;")
        footer_layout.addWidget(footer_credit)

        main_layout.addWidget(footer)

        self.setLayout(main_layout)
        self.set_gui_state("idle")
        self.show()
        
        # --- GÜNCELLEME KONTROLÜNÜ BAŞLAT ---
        # Uygulama açıldıktan 2 saniye sonra kontrol et
        QTimer.singleShot(2000, self.check_for_updates)
    # --- initUI SONU ---

    # --- YARDIMCI STİL FONKSİYONLARI ---
    def get_app_version(self):
        return "1.8.8" # Versiyonu buradan yönetelim

    def get_frame_style(self):
        S = StyleConstants
        return f"""
            QFrame {{
                background-color: {S.BG_SURFACE};
                border: 1px solid {S.BORDER};
                border-radius: {S.BORDER_RADIUS}px;
            }}
        """

    def create_input_field(self):
        input_field = QLineEdit()
        input_field.setStyleSheet(f"""
            QLineEdit {{
                background-color: {StyleConstants.BG_INPUT};
                color: {StyleConstants.TEXT_PRIMARY};
                border: 1px solid {StyleConstants.BORDER};
                border-radius: {StyleConstants.BORDER_RADIUS}px;
                padding: 8px 12px;
                font-size: 12px;
                min-height: 35px;
            }}
            QLineEdit:focus {{
                border: 2px solid {StyleConstants.ACCENT};
            }}
            QLineEdit[readOnly="true"] {{
                background-color: {StyleConstants.BG_SURFACE};
                color: {StyleConstants.TEXT_SECONDARY};
            }}
        """)
        return input_field

    def get_text_edit_style(self):
        S = StyleConstants
        return f"""
            QTextEdit {{
                background-color: {S.BG_INPUT};
                color: {S.TEXT_PRIMARY};
                border: 1px solid {S.BORDER};
                border-radius: {S.BORDER_RADIUS}px;
                padding: 10px;
                font-size: 11px;
                font-family: Consolas, Courier, monospace;
            }}
            QTextEdit:focus {{
                border: 2px solid {S.ACCENT};
            }}
            QTextEdit[readOnly="true"] {{
                background-color: {S.BG_SURFACE};
                color: {S.TEXT_SECONDARY};
            }}
        """

    def create_button(self, text, base_color):
        button = QPushButton(text)
        hover_color = QColor(base_color).lighter(115).name()
        pressed_color = QColor(base_color).darker(115).name()
        button.setMinimumHeight(45)
        button.setCursor(Qt.CursorShape.PointingHandCursor)
        button.setStyleSheet(f"""
            QPushButton {{
                background-color: {base_color};
                color: white;
                border: none;
                border-radius: {StyleConstants.BORDER_RADIUS}px;
                padding: 10px 16px;
                font-weight: bold;
                font-size: 13px;
                font-family: {StyleConstants.FONT_FAMILY};
            }}
            QPushButton:hover {{
                background-color: {hover_color};
            }}
            QPushButton:pressed {{
                background-color: {pressed_color};
            }}
            QPushButton:disabled {{
                background-color: {StyleConstants.BORDER};
                color: {StyleConstants.TEXT_MUTED};
            }}
        """)
        return button

    def get_table_style(self):
        S = StyleConstants
        return f"""
            QTableWidget {{
                background-color: {S.BG_INPUT};
                color: {S.TEXT_PRIMARY};
                gridline-color: {S.BORDER};
                border: 1px solid {S.BORDER};
                border-radius: {S.BORDER_RADIUS}px;
                font-size: 11px;
            }}
            QHeaderView::section {{
                background-color: {S.BG_SURFACE};
                color: {S.ACCENT};
                border: none;
                padding: 6px;
                font-weight: bold;
                font-size: 11px;
            }}
            QTableWidget::item {{
                padding: 6px;
                border-bottom: 1px solid {S.BORDER};
            }}
            QTableWidget::item:selected {{ background-color: {S.ACCENT}; color: {S.BG_PRIMARY}; }}
            QScrollBar:vertical {{
                border: none; background: {S.BG_PRIMARY}; width: 10px; margin: 0;
            }}
            QScrollBar::handle:vertical {{ background: {S.BORDER}; min-height: 20px; border-radius: 5px; }}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height: 0px; }}
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{ background: none; }}
        """

    def get_progress_bar_style(self):
        S = StyleConstants
        return f"""
            QProgressBar {{
                border: 1px solid {S.BORDER};
                border-radius: {S.BORDER_RADIUS}px;
                text-align: center;
                background-color: {S.BG_INPUT};
                color: {S.TEXT_PRIMARY};
                font-weight: bold;
                height: 20px;
                font-size: 10px;
            }}
            QProgressBar::chunk {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 {S.ACCENT}, stop:1 {S.SUCCESS});
                border-radius: 7px;
                margin: 1px;
            }}
        """
    # --- YARDIMCI STİL FONKSİYONLARI SONU ---

    # --- YENİ FONKSİYON: Yardım Penceresi ---
    def show_help_dialog(self):
        S = StyleConstants
        
        dialog = QDialog(self)
        dialog.setWindowTitle("Kullanım Rehberi")
        dialog.setMinimumSize(580, 520)
        dialog.resize(620, 580)
        dialog.setStyleSheet(f"""
            QDialog {{ background-color: {S.BG_PRIMARY}; }}
            QLabel {{ background: transparent; border: none; }}
            QFrame {{ border: none; }}
        """)
        
        main_layout = QVBoxLayout(dialog)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Scroll Area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet(f"QScrollArea {{ border: none; background: {S.BG_PRIMARY}; }}")
        
        content = QWidget()
        layout = QVBoxLayout(content)
        layout.setContentsMargins(28, 24, 28, 20)
        layout.setSpacing(20)
        
        # --- Başlık ---
        title = QLabel("Nasıl Kullanılır?")
        title.setFont(QFont(S.FONT_FAMILY, 18, QFont.Weight.Bold))
        title.setStyleSheet(f"color: {S.ACCENT};")
        layout.addWidget(title)
        
        subtitle = QLabel("TikTok koleksiyonlarınızdaki videoları 3 adımda indirin.")
        subtitle.setFont(QFont(S.FONT_FAMILY, 11))
        subtitle.setStyleSheet(f"color: {S.TEXT_SECONDARY};")
        subtitle.setWordWrap(True)
        layout.addWidget(subtitle)
        
        # --- Adım kartları ---
        def make_step_card(number, title_text, steps_list):
            card = QFrame()
            card.setStyleSheet(f"""
                QFrame {{ background-color: {S.BG_SURFACE}; border-radius: {S.BORDER_RADIUS}px; }}
            """)
            card_layout = QVBoxLayout(card)
            card_layout.setContentsMargins(18, 14, 18, 14)
            card_layout.setSpacing(8)
            
            # Adım başlığı
            header = QHBoxLayout()
            badge = QLabel(f"  {number}  ")
            badge.setFixedSize(28, 28)
            badge.setAlignment(Qt.AlignmentFlag.AlignCenter)
            badge.setFont(QFont(S.FONT_FAMILY, 11, QFont.Weight.Bold))
            badge.setStyleSheet(f"""
                background-color: {S.ACCENT}; color: white; border-radius: 14px;
            """)
            header.addWidget(badge)
            
            step_title = QLabel(title_text)
            step_title.setFont(QFont(S.FONT_FAMILY, 13, QFont.Weight.Bold))
            step_title.setStyleSheet(f"color: {S.TEXT_PRIMARY}; margin-left: 4px;")
            header.addWidget(step_title)
            header.addStretch()
            card_layout.addLayout(header)
            
            # Adım açıklamaları
            for step in steps_list:
                step_label = QLabel(f"  {step}")
                step_label.setFont(QFont(S.FONT_FAMILY, 10))
                step_label.setStyleSheet(f"color: {S.TEXT_SECONDARY}; padding-left: 4px;")
                step_label.setWordWrap(True)
                card_layout.addWidget(step_label)
            
            return card
        
        card1 = make_step_card("1", "Çerez Dosyası Hazırlayın", [
            "Chrome/Edge'e 'Get cookies.txt LOCALLY' eklentisini kurun",
            "TikTok.com'a giriş yapıp koleksiyon sayfasına gidin",
            "Eklenti simgesine tıklayın → Export All Cookies",
            "İndirilen .txt dosyasını uygulamada 📂 Seç ile seçin",
            "Hedef URL alanına koleksiyon linkini yapıştırın"
        ])
        layout.addWidget(card1)
        
        card2 = make_step_card("2", "Linkleri Getirin", [
            "🎯 Bağlantıları Getir butonuna tıklayın",
            "Uygulama tüm video linklerini otomatik bulacaktır",
            "Linkler metin kutusuna listelenecektir"
        ])
        layout.addWidget(card2)
        
        card3 = make_step_card("3", "İndirin", [
            "📁 Gözat ile indirme klasörünü seçin",
            "⚡ İndirmeyi Başlat butonuna tıklayın",
            "İlerlemeyi tablodaki durum çubuklarından takip edin",
            "Daha önce indirilen videolar otomatik atlanır"
        ])
        layout.addWidget(card3)
        
        # --- SSS ---
        faq_title = QLabel("Sık Sorulan Sorular")
        faq_title.setFont(QFont(S.FONT_FAMILY, 14, QFont.Weight.Bold))
        faq_title.setStyleSheet(f"color: {S.ACCENT}; margin-top: 4px;")
        layout.addWidget(faq_title)
        
        def make_faq(question, answer):
            faq = QFrame()
            faq.setStyleSheet(f"QFrame {{ background-color: {S.BG_SURFACE}; border-radius: {S.BORDER_RADIUS}px; }}")
            faq_layout = QVBoxLayout(faq)
            faq_layout.setContentsMargins(16, 12, 16, 12)
            faq_layout.setSpacing(4)
            q = QLabel(question)
            q.setFont(QFont(S.FONT_FAMILY, 11, QFont.Weight.Bold))
            q.setStyleSheet(f"color: {S.TEXT_PRIMARY};")
            q.setWordWrap(True)
            faq_layout.addWidget(q)
            a = QLabel(answer)
            a.setFont(QFont(S.FONT_FAMILY, 10))
            a.setStyleSheet(f"color: {S.TEXT_SECONDARY};")
            a.setWordWrap(True)
            faq_layout.addWidget(a)
            return faq
        
        layout.addWidget(make_faq(
            "Çerez dosyam neden çalışmıyor?",
            "Çerezlerin süresi dolmuş olabilir. TikTok'a tekrar giriş yapıp yeni bir çerez dosyası indirin."
        ))
        layout.addWidget(make_faq(
            "Bazı videolar neden indirilemedi?",
            "Video silinmiş, gizlenmiş veya bölgenizde engellenmiş olabilir. İndirme sonunda 'Hataları Gör' butonuyla detaylara bakabilirsiniz."
        ))
        layout.addWidget(make_faq(
            "Aynı koleksiyonu tekrar indirirsem ne olur?",
            "Uygulama daha önce indirilen videoları otomatik olarak algılar ve atlar. Sadece yeni eklenen videolar indirilir."
        ))
        
        layout.addStretch()
        scroll.setWidget(content)
        main_layout.addWidget(scroll, 1)
        
        # Alt buton çubuğu
        bottom_bar = QFrame()
        bottom_bar.setFixedHeight(56)
        bottom_bar.setStyleSheet(f"QFrame {{ background-color: {S.BG_SURFACE}; border-top: 1px solid {S.BORDER}; }}")
        bottom_layout = QHBoxLayout(bottom_bar)
        bottom_layout.setContentsMargins(20, 0, 20, 0)
        
        ver_label = QLabel(f"v{self.get_app_version()}")
        ver_label.setFont(QFont(S.FONT_FAMILY, 10))
        ver_label.setStyleSheet(f"color: {S.TEXT_MUTED};")
        bottom_layout.addWidget(ver_label)
        
        bottom_layout.addStretch()
        
        close_btn = QPushButton("Kapat")
        close_btn.setFixedSize(90, 34)
        close_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        close_btn.setStyleSheet(f"""
            QPushButton {{ background-color: {S.ACCENT}; color: white; border: none;
            border-radius: {S.BORDER_RADIUS}px; font-weight: bold; font-size: 12px; }}
            QPushButton:hover {{ background-color: {S.ACCENT_HOVER}; }}
        """)
        close_btn.clicked.connect(dialog.close)
        bottom_layout.addWidget(close_btn)
        
        main_layout.addWidget(bottom_bar)
        dialog.exec()

    # --- YARDIM PENCERESİ SONU ---

    # --- GÜNCELLEME FONKSİYONLARI ---
    def check_for_updates(self, manual=False):
        """GitHub'dan son sürümü kontrol eder."""
        try:
            repo_url = "https://api.github.com/repos/mehmettevfikcetin/TikTok-Bulk-Downloader/releases/latest"
            response = requests.get(repo_url, timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                latest_version = data['tag_name']
                current_version = f"v{self.get_app_version()}"
                
                print(f"DEBUG: Mevcut: {current_version}, Son Sürüm: {latest_version}")

                if latest_version != current_version:
                    download_url = ""
                    for asset in data['assets']:
                        if asset['name'].endswith(".exe"):
                            download_url = asset['browser_download_url']
                            break
                    
                    if download_url:
                        # Türkçe butonlarla custom dialog oluştur
                        msg_box = QMessageBox(self)
                        msg_box.setWindowTitle("🔄 Güncelleme Mevcut")
                        msg_box.setText(f"Yeni bir sürüm bulundu! İndirip güncellemek ister misiniz?\n\nMevcut: {current_version}\nYeni Sürüm: {latest_version}")
                        msg_box.setIcon(QMessageBox.Icon.Information)
                        
                        yes_btn = msg_box.addButton("✅ Evet", QMessageBox.ButtonRole.YesRole)
                        no_btn = msg_box.addButton("❌ Hayır", QMessageBox.ButtonRole.NoRole)
                        
                        msg_box.setStyleSheet(StyleConstants.get_stylesheet())
                        msg_box.exec()
                        
                        if msg_box.clickedButton() == yes_btn:
                            self.perform_auto_update(download_url)
                
                else:
                    if manual:
                        QMessageBox.information(self, "✅ Durum", f"Zaten en güncel sürümü kullanıyorsunuz.\n\nSürüm: {current_version}")

        except Exception as e:
            print(f"Güncelleme kontrol hatası: {e}")
            if manual:
                QMessageBox.warning(self, "⚠️ Hata", f"Güncelleme kontrolü yapılamadı:\n{e}")

    def perform_auto_update(self, url):
        """Yeni sürümü indirir ve eskiyle değiştirir (v4 - Agresif kill, self-cleanup)."""
        try:
            self.download_button.setText("📥 Güncelleme İndiriliyor...")
            self.download_button.setEnabled(False)
            if hasattr(self, 'fetch_links_button'):
                self.fetch_links_button.setEnabled(False)
            QCoreApplication.processEvents()
            
            # Mevcut executable yolu (MUTLAK yol)
            if getattr(sys, 'frozen', False):
                current_exe = os.path.abspath(sys.executable)
            else:
                current_exe = os.path.abspath(sys.argv[0])
            
            if not current_exe.endswith(".exe"):
                QMessageBox.warning(self, "⚠️ Uyarı", "Bu özellik sadece .exe formatında çalışır.")
                self._reset_update_buttons()
                return

            exe_dir = os.path.dirname(current_exe)
            exe_name_no_ext = os.path.splitext(os.path.basename(current_exe))[0]
            new_exe_path = os.path.join(exe_dir, "tiktok_update_new.exe")
            
            print(f"📦 Mevcut exe: {current_exe}")
            print(f"📁 Exe dizini: {exe_dir}")
            
            # 1. Yeni sürümü indir
            response = requests.get(url, stream=True, timeout=300)
            if response.status_code != 200:
                raise Exception(f"İndirme hatası: HTTP {response.status_code}")
            
            total_size = int(response.headers.get('content-length', 0))
            downloaded = 0
            
            with open(new_exe_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=65536):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        if total_size:
                            percent = (downloaded / total_size) * 100
                            self.download_button.setText(f"📥 İndiriliyor: {percent:.0f}%")
                            QCoreApplication.processEvents()
            
            if not os.path.exists(new_exe_path):
                raise Exception(f"İndirilen dosya bulunamadı: {new_exe_path}")
            
            new_size = os.path.getsize(new_exe_path)
            if new_size < 50000:
                os.remove(new_exe_path)
                raise Exception(f"İndirilen dosya çok küçük ({new_size} bytes), bozuk olabilir!")
            
            print(f"✅ İndirme tamamlandı: {new_exe_path} ({new_size:,} bytes)")
            self.download_button.setText("🔧 Güncelleme hazırlanıyor...")
            QCoreApplication.processEvents()
            
            # 2. PowerShell update scripti
            pid = os.getpid()
            ps_script_path = os.path.join(exe_dir, "updater.ps1")
            
            ps_script = f"""# TikTok Indirici - Otomatik Guncelleyici v4
$ErrorActionPreference = 'SilentlyContinue'
$oldExe = '{current_exe}'
$newExe = '{new_exe_path}'
$targetPid = {pid}
$exeProcessName = '{exe_name_no_ext}'
$scriptPath = $MyInvocation.MyCommand.Path

Write-Host ''
Write-Host '  Guncelleme baslatildi...' -ForegroundColor Cyan
Write-Host ''

# === ADIM 1: Uygulamayi tamamen kapat ===
# Once PID ile, sonra isimle - tum prosesleri oldir
Write-Host '  [1/4] Uygulama kapatiliyor...' -ForegroundColor Yellow

# PID ile oldir
try {{ Stop-Process -Id $targetPid -Force -ErrorAction SilentlyContinue }} catch {{}}

# Isim ile oldir (PyInstaller bootloader dahil)
Start-Sleep -Milliseconds 500
Get-Process -Name $exeProcessName -ErrorAction SilentlyContinue | ForEach-Object {{
    try {{ $_ | Stop-Process -Force }} catch {{}}
}}

# Dosya kilidinin acilmasini bekle (max 20 saniye)
$unlocked = $false
for ($i = 0; $i -lt 20; $i++) {{
    Start-Sleep -Seconds 1
    try {{
        if (Test-Path $oldExe) {{
            $stream = [System.IO.File]::Open($oldExe, 'Open', 'ReadWrite', 'None')
            $stream.Close()
            $stream.Dispose()
            $unlocked = $true
            break
        }} else {{
            $unlocked = $true
            break
        }}
    }} catch {{
        Write-Host "    Dosya kilitli, bekleniyor... ($($i+1)/20)" -ForegroundColor DarkGray
    }}
}}

if (-not $unlocked) {{
    Write-Host '  HATA: Dosya kilidi acilamadi!' -ForegroundColor Red
    Write-Host '  Lutfen uygulamayi manuel kapatin.' -ForegroundColor Red
    Start-Sleep -Seconds 5
    # Temizlik: scriptini sil
    Start-Process cmd -ArgumentList "/c timeout /t 2 /nobreak >NUL & del `"$scriptPath`"" -WindowStyle Hidden
    exit 1
}}

# === ADIM 2: Eski exe'yi sil ===
Write-Host '  [2/4] Eski surum kaldiriliyor...' -ForegroundColor Yellow
if (Test-Path $oldExe) {{
    Remove-Item -Path $oldExe -Force -ErrorAction SilentlyContinue
    Start-Sleep -Milliseconds 500
    if (Test-Path $oldExe) {{
        # Son care: rename et
        $backupName = $oldExe + '.old'
        Rename-Item -Path $oldExe -NewName $backupName -Force -ErrorAction SilentlyContinue
    }}
}}

# === ADIM 3: Yeni dosyayi tasi ===
Write-Host '  [3/4] Yeni surum hazirlaniyor...' -ForegroundColor Yellow
if (Test-Path $oldExe) {{
    # Eski hala varsa (rename edilmis bile olabilir), kopyala
    Copy-Item -Path $newExe -Destination $oldExe -Force
    Remove-Item -Path $newExe -Force -ErrorAction SilentlyContinue
}} else {{
    Move-Item -Path $newExe -Destination $oldExe -Force
}}

# Dogrulama
if (-not (Test-Path $oldExe)) {{
    # Son fallback: yeni exe'yi eski isimle kopyala
    if (Test-Path $newExe) {{
        Copy-Item -Path $newExe -Destination $oldExe -Force
    }}
}}

# === ADIM 4: Yeni surumu baslat + temizlik ===
if (Test-Path $oldExe) {{
    Write-Host ''
    Write-Host '  Guncelleme basarili!' -ForegroundColor Green
    Write-Host '  Yeni surum baslatiliyor...' -ForegroundColor Cyan
    Write-Host ''
    
    Start-Sleep -Milliseconds 500
    Start-Process -FilePath $oldExe
    
    # .old backup dosyasini ve scriptini temizle (cmd ile - ps1 kendini silemez)
    $oldBackup = $oldExe + '.old'
    Start-Process cmd -ArgumentList "/c timeout /t 3 /nobreak >NUL & del /F /Q `"$oldBackup`" >NUL 2>&1 & del /F /Q `"$newExe`" >NUL 2>&1 & del /F /Q `"$scriptPath`" >NUL 2>&1" -WindowStyle Hidden
}} else {{
    Write-Host '  HATA: Guncelleme dogrulanamadi!' -ForegroundColor Red
    Start-Sleep -Seconds 5
    Start-Process cmd -ArgumentList "/c timeout /t 2 /nobreak >NUL & del `"$scriptPath`"" -WindowStyle Hidden
}}
"""
            
            with open(ps_script_path, "w", encoding='utf-8-sig') as f:
                f.write(ps_script)
            
            print(f"🚀 Güncelleyici başlatılıyor: {ps_script_path}")
            self.download_button.setText("🚀 Güncelleme Başlatılıyor...")
            QCoreApplication.processEvents()
            
            subprocess.Popen(
                [
                    'powershell.exe',
                    '-ExecutionPolicy', 'Bypass',
                    '-NoProfile',
                    '-File', ps_script_path
                ],
                cwd=exe_dir,
                creationflags=subprocess.CREATE_NEW_CONSOLE
            )
            
            print("⏹️ Uygulama kapanıyor...")
            os._exit(0)
            
        except Exception as e:
            print(f"❌ Güncelleme hatası: {e}")
            error_msg = f"Otomatik güncelleme yapılamadı:\n{e}\n\nTarayıcıda indirme sayfası açılsın mı?"
            reply = QMessageBox.question(
                self, "Güncelleme Hatası", error_msg,
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if reply == QMessageBox.StandardButton.Yes:
                QDesktopServices.openUrl(QUrl("https://github.com/mehmettevfikcetin/TikTok-Bulk-Downloader/releases/latest"))
            
            try:
                if 'new_exe_path' in locals() and os.path.exists(new_exe_path):
                    os.remove(new_exe_path)
            except: pass
            
            self._reset_update_buttons()
    
    def _reset_update_buttons(self):
        """Güncelleme sonrası butonları eski haline döndürür."""
        self.download_button.setText("⚡ İndirmeyi Başlat")
        self.download_button.setEnabled(True)
        if hasattr(self, 'fetch_links_button'):
            self.fetch_links_button.setEnabled(True)
    # --- GÜNCELLEME FONKSİYONLARI BİTİŞ ---

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
        
        # Klasörü Aç butonunu güncelle
        if hasattr(self, 'open_folder_button'):
            self.open_folder_button.setEnabled(is_idle and bool(self.folder_path_input.text()))
        
        self.url_input.setReadOnly(not is_idle) # Boşta değilken metin kutusunu kilitle

        if is_fetching: self.fetch_links_button.setText("⏳ Linkler Getiriliyor...")
        else: self.fetch_links_button.setText("🎯 Bağlantıları Getir")
        if is_downloading: self.download_button.setText("⏳ İndiriliyor...")
        else: self.download_button.setText("⚡ İndirmeyi Başlat")

    def browse_cookie_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, 'Çerez Dosyasını Seç', self.settings.value("cookiePath", ""), 'Metin Dosyaları (*.txt);;Tüm Dosyalar (*)')
        if file_path: self.cookie_path_input.setText(file_path); self.settings.setValue("cookiePath", file_path); self.set_gui_state("idle")

    def browse_folder(self):
        start_path = self.settings.value("downloadPath", os.path.expanduser('~'))
        folder = QFileDialog.getExistingDirectory(self, 'İndirme Klasörünü Seç', start_path)
        if folder:
            self.folder_path_input.setText(folder)
            self.settings.setValue("downloadPath", folder)
            if hasattr(self, 'open_folder_button'):
                self.open_folder_button.setEnabled(True)

    def open_download_folder(self):
        """Seçili indirme klasörünü dosya gezgininde açar."""
        folder = self.folder_path_input.text()
        if folder and os.path.exists(folder):
            QDesktopServices.openUrl(QUrl.fromLocalFile(folder))
        else:
            QMessageBox.warning(self, 'Hata', 'Klasör bulunamadı. Lütfen geçerli bir klasör seçin.')

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
        self.fetch_status_label.setStyleSheet(f"color: {StyleConstants.SUCCESS}; border: none; background: transparent;")
        self.fetch_status_label.setText(f"✓ {len(urls)} adet URL başarıyla bulundu. Adım 3'e geçebilirsiniz.")
        QMessageBox.information(self, 'Başarılı', f"✓ {len(urls)} adet video linki listeye eklendi.")

    def on_fetch_status(self, message):
        self.fetch_status_label.setStyleSheet(f"color: {StyleConstants.WARNING}; border: none; background: transparent;")
        self.fetch_status_label.setText(f"⏳ {message}")

    def on_fetch_error(self, error_message):
        self.set_gui_state("idle")
        self.fetch_status_label.setStyleSheet(f"color: {StyleConstants.ERROR}; border: none; background: transparent;")
        self.fetch_status_label.setText(f"✗ Hata: {error_message}")
        QMessageBox.warning(self, 'Link Getirme Hatası', error_message)

    def start_download(self):
        urls = self.url_input.toPlainText().split('\n')
        urls = [url.strip() for url in urls if url.strip()]
        target_dir = self.folder_path_input.text()
        cookie_file = self.cookie_path_input.text()  # Çerez yolunu al

        if not urls: QMessageBox.warning(self, 'Hata', 'İndirilecek URL bulunamadı.'); return
        if not target_dir: QMessageBox.warning(self, 'Hata', 'Lütfen bir indirme klasörü seçin.'); return
        
        # Eğer çerez dosyası yoksa uyar
        if not cookie_file or not os.path.exists(cookie_file):
             QMessageBox.warning(self, 'Hata', 'Çerez dosyası bulunamadı! İndirme için çerez şarttır.'); return

        self.settings.setValue("downloadPath", target_dir)
        self.download_start_time = time.time()  # Süre takibi başlat
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
            
        # Burası değişti: cookie_file parametresini ekledik
        self.downloader_thread = DownloaderThread(urls, target_dir, cookie_file)
        
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

    def on_all_finished(self, completed, skipped, errors, failed_list):
        self.set_gui_state("idle")
        self.download_button.setText('⚡ İndirmeyi Başlat')
        self.total_progress_bar.setValue(100)
        
        # Geçen süreyi hesapla
        elapsed = time.time() - getattr(self, 'download_start_time', time.time())
        minutes = int(elapsed // 60)
        seconds = int(elapsed % 60)
        elapsed_str = f"{minutes}dk {seconds}sn" if minutes > 0 else f"{seconds}sn"
        total = completed + skipped + errors
        
        # --- Minimalist Tamamlanma Dialogu (QDialog) ---
        dialog = QDialog(self)
        dialog.setWindowTitle("Tamamlandı")
        dialog.setFixedSize(340, 300)
        dialog.setStyleSheet(f"""
            QDialog {{ background-color: {StyleConstants.BG_PRIMARY}; }}
            QLabel {{ background: transparent; border: none; }}
        """)
        
        layout = QVBoxLayout(dialog)
        layout.setContentsMargins(30, 25, 30, 20)
        layout.setSpacing(0)
        
        # Başarı ikonu + başlık
        header = QLabel("✓  Tamamlandı")
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header.setFont(QFont(StyleConstants.FONT_FAMILY, 16, QFont.Weight.Bold))
        header.setStyleSheet(f"color: {StyleConstants.SUCCESS}; margin-bottom: 16px;")
        layout.addWidget(header)
        
        # İstatistik satırları
        stats_widget = QWidget()
        stats_widget.setStyleSheet(f"""
            QWidget {{ background-color: {StyleConstants.BG_SURFACE}; border-radius: {StyleConstants.BORDER_RADIUS}px; }}
        """)
        stats_layout = QVBoxLayout(stats_widget)
        stats_layout.setContentsMargins(20, 16, 20, 16)
        stats_layout.setSpacing(8)
        
        def add_stat_row(label_text, value, color):
            row = QHBoxLayout()
            lbl = QLabel(label_text)
            lbl.setFont(QFont(StyleConstants.FONT_FAMILY, 11))
            lbl.setStyleSheet(f"color: {StyleConstants.TEXT_SECONDARY};")
            val = QLabel(str(value))
            val.setFont(QFont(StyleConstants.FONT_FAMILY, 12, QFont.Weight.Bold))
            val.setStyleSheet(f"color: {color};")
            val.setAlignment(Qt.AlignmentFlag.AlignRight)
            row.addWidget(lbl)
            row.addWidget(val)
            stats_layout.addLayout(row)
        
        add_stat_row("Başarılı", completed, StyleConstants.SUCCESS)
        add_stat_row("Atlanan", skipped, StyleConstants.WARNING)
        add_stat_row("Hatalı", errors, StyleConstants.ERROR)
        
        # Ayırıcı çizgi
        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setFixedHeight(1)
        sep.setStyleSheet(f"background-color: {StyleConstants.BORDER}; border: none;")
        stats_layout.addWidget(sep)
        
        add_stat_row("Toplam", total, StyleConstants.TEXT_PRIMARY)
        add_stat_row("Süre", elapsed_str, StyleConstants.ACCENT)
        
        layout.addWidget(stats_widget)
        layout.addSpacing(16)
        
        # Butonlar
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(8)
        
        # Hatalıları Göster (sadece hata varsa)
        show_errors_btn = None
        if errors > 0:
            show_errors_btn = QPushButton("Hataları Gör")
            show_errors_btn.setCursor(Qt.CursorShape.PointingHandCursor)
            show_errors_btn.setFixedHeight(36)
            show_errors_btn.setStyleSheet(f"""
                QPushButton {{ background-color: transparent; color: {StyleConstants.ERROR};
                border: 1px solid {StyleConstants.ERROR}; border-radius: {StyleConstants.BORDER_RADIUS}px;
                font-weight: bold; font-size: 11px; padding: 0 12px; }}
                QPushButton:hover {{ background-color: {StyleConstants.ERROR}; color: white; }}
            """)
            btn_layout.addWidget(show_errors_btn)
        
        btn_layout.addStretch()
        
        ok_btn = QPushButton("Tamam")
        ok_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        ok_btn.setFixedHeight(36)
        ok_btn.setStyleSheet(f"""
            QPushButton {{ background-color: {StyleConstants.BG_INPUT}; color: {StyleConstants.TEXT_PRIMARY};
            border: 1px solid {StyleConstants.BORDER}; border-radius: {StyleConstants.BORDER_RADIUS}px;
            font-weight: bold; font-size: 11px; padding: 0 16px; }}
            QPushButton:hover {{ background-color: {StyleConstants.BORDER}; }}
        """)
        ok_btn.clicked.connect(dialog.accept)
        btn_layout.addWidget(ok_btn)
        
        folder_btn = QPushButton("Klasörü Aç")
        folder_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        folder_btn.setFixedHeight(36)
        folder_btn.setStyleSheet(f"""
            QPushButton {{ background-color: {StyleConstants.ACCENT}; color: white;
            border: none; border-radius: {StyleConstants.BORDER_RADIUS}px;
            font-weight: bold; font-size: 11px; padding: 0 16px; }}
            QPushButton:hover {{ background-color: {StyleConstants.ACCENT_HOVER}; }}
        """)
        btn_layout.addWidget(folder_btn)
        
        layout.addLayout(btn_layout)
        
        # Buton bağlantıları
        folder_btn.clicked.connect(lambda: (dialog.accept(), self.open_download_folder()))
        if show_errors_btn:
            show_errors_btn.clicked.connect(lambda: (dialog.accept(), ErrorDialog(failed_list, self).exec()))
        
        dialog.exec()

    def open_settings_dialog(self):
        """Ayarlar ve Hakkında penceresini aç."""
        dialog = SettingsDialog(self.get_app_version(), self)
        dialog.exec()

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