import os
import subprocess
import threading
import customtkinter as ctk
from tkinter import filedialog, messagebox, scrolledtext
import tkinter as tk

# Modern tema ayarları
ctk.set_appearance_mode("dark")  # "dark" veya "light"
ctk.set_default_color_theme("green")  # "blue", "green", "dark-blue"

class InstagramDownloader:
    def __init__(self):
        self.root = ctk.CTk()
        self.root.title("Instagram Video Downloader")
        self.root.geometry("700x500")
        self.root.resizable(True, True)
        
        # Progress değişkeni
        self.progress_var = tk.DoubleVar()
        
        self.create_widgets()
        
    def create_widgets(self):
        # Ana başlık
        title_label = ctk.CTkLabel(
            self.root, 
            text="Instagram Video Downloader", 
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title_label.pack(pady=(20, 10))
        
        # URL girişi frame'i
        url_frame = ctk.CTkFrame(self.root)
        url_frame.pack(pady=10, padx=20, fill="x")
        
        url_label = ctk.CTkLabel(
            url_frame, 
            text="Instagram Video/Reels Linki:",
            font=ctk.CTkFont(size=14)
        )
        url_label.pack(pady=(15, 5))
        
        self.url_entry = ctk.CTkEntry(
            url_frame, 
            width=500, 
            height=40,
            placeholder_text="Instagram linkini buraya yapıştırın...",
            font=ctk.CTkFont(size=12)
        )
        self.url_entry.pack(pady=(5, 15))
        
        # İndir butonu
        self.download_btn = ctk.CTkButton(
            self.root,
            text="📥 İndir",
            width=200,
            height=50,
            command=self.download_video,
            font=ctk.CTkFont(size=16, weight="bold"),
            corner_radius=25
        )
        self.download_btn.pack(pady=15)
        
        # Progress bar frame'i
        progress_frame = ctk.CTkFrame(self.root)
        progress_frame.pack(pady=10, padx=20, fill="x")
        
        progress_label = ctk.CTkLabel(
            progress_frame,
            text="İndirme İlerlemesi:",
            font=ctk.CTkFont(size=12)
        )
        progress_label.pack(pady=(10, 5))
        
        self.progress_bar = ctk.CTkProgressBar(
            progress_frame,
            width=500,
            height=20,
            corner_radius=10
        )
        self.progress_bar.pack(pady=(5, 15))
        self.progress_bar.set(0)
        
        # Log alanı
        log_frame = ctk.CTkFrame(self.root)
        log_frame.pack(pady=10, padx=20, fill="both", expand=True)
        
        log_label = ctk.CTkLabel(
            log_frame,
            text="İşlem Logları:",
            font=ctk.CTkFont(size=12)
        )
        log_label.pack(pady=(10, 5))
        
        # ScrolledText için tkinter kullanıyoruz çünkü CTk'da yok
        self.log_box = scrolledtext.ScrolledText(
            log_frame,
            width=70,
            height=12,
            state='disabled',
            bg="#212121",
            fg="#ffffff",
            insertbackground="#ffffff",
            font=("Consolas", 10)
        )
        self.log_box.pack(pady=(5, 15), padx=15, fill="both", expand=True)
        
        # Alt bilgi
        info_label = ctk.CTkLabel(
            self.root,
            text="yt-dlp kullanılarak geliştirilmiştir",
            font=ctk.CTkFont(size=10),
            text_color="gray"
        )
        info_label.pack(pady=(0, 10))
        
    def log(self, message):
        """Log mesajlarını ekler"""
        self.log_box.config(state='normal')
        self.log_box.insert(tk.END, message + "\n")
        self.log_box.yview(tk.END)
        self.log_box.config(state='disabled')
        
    def download_video(self):
        """Video indirme işlemini başlatır"""
        url = self.url_entry.get().strip()
        if not url:
            messagebox.showerror("Hata", "Lütfen bir Instagram linki girin!")
            return

        save_path = filedialog.askdirectory(title="Videoyu kaydetmek istediğiniz klasörü seçin")
        if not save_path:
            self.log("İşlem iptal edildi.")
            return

        # Butonu devre dışı bırak
        self.download_btn.configure(state="disabled", text="İndiriliyor...")
        self.progress_bar.set(0)
        
        threading.Thread(target=self.run_download, args=(url, save_path), daemon=True).start()
        
    def run_download(self, url, save_path):
        """Arka planda video indirme işlemini çalıştırır"""
        self.log(f"İndiriliyor: {url}")
        self.log(f"Kayıt yeri: {save_path}")

        cmd = [
            "yt-dlp",
            "-f", "bestvideo+bestaudio",
            "-o", os.path.join(save_path, "%(title)s.%(ext)s"),
            "--newline",
            url
        ]

        try:
            process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
            for line in process.stdout:
                line = line.strip()
                self.log(line)

                # Progress yüzdesi parse et
                if "%" in line:
                    try:
                        percent_str = line.split("%")[0].split()[-1]
                        percent = float(percent_str)
                        self.progress_bar.set(percent / 100)
                    except:
                        pass
                        
            process.wait()

            if process.returncode == 0:
                self.progress_bar.set(1.0)
                self.log("✅ İndirme tamamlandı!")
                messagebox.showinfo("Başarılı", f"Video kaydedildi:\n{save_path}")
            else:
                self.log("❌ Hata: Video indirilemedi.")
                messagebox.showerror("Hata", "Video indirilemedi. Linki kontrol edin veya yt-dlp kurulu mu bakın.")
                
        except Exception as e:
            self.log(f"❌ Hata: {e}")
            messagebox.showerror("Hata", f"Bir hata oluştu:\n{e}")
        finally:
            # Butonu tekrar etkinleştir
            self.download_btn.configure(state="normal", text="📥 İndir")
            
    def run(self):
        """Uygulamayı başlatır"""
        self.root.mainloop()

# Uygulamayı başlat
if __name__ == "__main__":
    app = InstagramDownloader()
    app.run()