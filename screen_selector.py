import tkinter as tk
from tkinter import ttk, messagebox
import pyautogui
from PIL import Image, ImageTk
import numpy as np
import cv2
import time
import json
import os
from mss import mss
from card_detector import CardDetector
from card_display import CardDisplay

class RoundedButton(tk.Canvas):
    """Rounded köşeli modern buton sınıfı"""
    def __init__(self, parent, text, command, bg_color="#4A90E2", fg_color="#222222", 
                 width=120, height=35, corner_radius=10, **kwargs):
        super().__init__(parent, width=width, height=height, background="#F4F4F9", 
                        highlightthickness=0, **kwargs)
        
        self.command = command
        self.bg_color = bg_color
        self.fg_color = fg_color
        self.corner_radius = corner_radius
        self.text = text  # Metni sakla
        
        # Rounded rectangle çiz
        self.draw_button()
        
        # Event'ler
        self.bind("<Button-1>", self._on_click)
        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)
        
    def draw_button(self, hover=False):
        """Rounded rectangle çiz"""
        self.delete("all")  # Tüm canvas'ı temizle
        
        # Hover durumunda renk değiştir
        color = self.bg_color
        if hover:
            if self.bg_color == "#4A90E2":
                color = "#357ABD"
            elif self.bg_color == "#E74C3C":
                color = "#C0392B"
            elif self.bg_color == "#27AE60":  # Yeşil hover
                color = "#229954"
        
        # Rounded rectangle çiz
        self.create_rounded_rectangle(0, 0, self.winfo_reqwidth(), self.winfo_reqheight(), 
                                    self.corner_radius, fill=color, tags="button_bg")
        
        # Metni yeniden çiz
        self.create_text(self.winfo_reqwidth()//2, self.winfo_reqheight()//2, 
                        text=self.text, fill=self.fg_color, 
                        font=("Segoe UI", 11, "bold"))
        
    def create_rounded_rectangle(self, x1, y1, x2, y2, radius, **kwargs):
        """Rounded rectangle oluştur"""
        # Köşe noktaları
        points = [
            x1 + radius, y1,
            x2 - radius, y1,
            x2, y1,
            x2, y1 + radius,
            x2, y2 - radius,
            x2, y2,
            x2 - radius, y2,
            x1 + radius, y2,
            x1, y2,
            x1, y2 - radius,
            x1, y1 + radius,
            x1, y1
        ]
        
        # Rounded rectangle çiz
        self.create_polygon(points, smooth=True, **kwargs)
        
    def _on_click(self, event):
        """Tıklama event'i"""
        if self.command:
            self.command()
            
    def _on_enter(self, event):
        """Mouse üzerine gelince"""
        self.draw_button(hover=True)
        
    def _on_leave(self, event):
        """Mouse ayrılınca"""
        self.draw_button(hover=False)
        
    def update_button(self, text=None, bg_color=None, fg_color=None):
        """Buton metnini ve rengini güncelle"""
        if text is not None:
            self.text = text
        if bg_color is not None:
            self.bg_color = bg_color
        if fg_color is not None:
            self.fg_color = fg_color
        self.draw_button()

class ScreenSelector:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("🎴 KART SAYICI")
        self.root.geometry("1000x400")  # Daha geniş pencere
        self.root.attributes('-topmost', True)  # Her zaman en üstte
        self.root.resizable(True, True)  # Boyut değiştirilebilir
        
        # Pencere ikonu ekle (varsa)
        try:
            self.root.iconbitmap("icon.ico")
        except:
            pass  # İkon yoksa devam et
        
        # Seçim değişkenleri
        self.start_x = None
        self.start_y = None
        self.end_x = None
        self.end_y = None
        self.selecting = False
        self.selection_window = None
        self.auto_capture_active = False
        self.auto_capture_job = None
        
        # Manuel mod değişkeni
        self.manual_mode = tk.BooleanVar(value=False)
        
        # Kart detektörü
        self.card_detector = CardDetector()
        
        # MSS instance'ı (hızlı ekran görüntüsü için)
        self.sct = mss()
        
        # Kayıt dosyası yolu
        self.settings_file = "selected_area.json"
        
        # FPS sayacı değişkenleri
        self.fps_start_time = None
        self.fps_frame_count = 0
        self.fps_last_print_time = None
        
        self.setup_ui()
        
        # Kayıtlı alan varsa sadece yükle, otomatik başlatma
        self.load_saved_area()
        
    def setup_ui(self):
        # Pencere kapatma event'i
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # Havalı stil tanımları
        self.setup_styles()
        
        # Ana frame
        main_frame = ttk.Frame(self.root, padding="20", style="Modern.TFrame")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Ana içerik frame - butonlar ve kartlar yan yana
        content_frame = ttk.Frame(main_frame, style="Modern.TFrame")
        content_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Sol tarafta butonlar için frame - sabit genişlik
        buttons_frame = ttk.Frame(content_frame, style="Modern.TFrame")
        buttons_frame.pack(side=tk.LEFT, padx=(0, 20), fill=tk.Y)
        buttons_frame.configure(width=180)  # Sabit genişlik
        buttons_frame.pack_propagate(False)  # Boyut sabit kalsın
        
        # Butonlar için ana container
        button_container = ttk.Frame(buttons_frame, style="Modern.TFrame")
        button_container.pack(expand=True, fill=tk.BOTH, padx=10, pady=10)
        
        # Üst kısım - Kontrol butonları
        top_frame = ttk.Frame(button_container, style="Modern.TFrame")
        top_frame.pack(side=tk.TOP, fill=tk.X, pady=(0, 15))
        
        # Alan seç butonu - sabit boyut
        self.select_button = RoundedButton(
            top_frame, 
            text="🎯 ALAN SEÇ", 
            command=self.start_selection,
            bg_color="#4A90E2",
            fg_color="#222222",
            width=160,
            height=45
        )
        self.select_button.pack(side=tk.TOP, fill=tk.X, pady=(0, 12))
        
        # Manuel checkbox - modern stil
        self.manual_checkbox = ttk.Checkbutton(
            top_frame, 
            text="🔒 MANUEL MOD", 
            variable=self.manual_mode,
            command=self.on_manual_mode_change,
            style="Modern.TCheckbutton"
        )
        self.manual_checkbox.pack(side=tk.TOP, fill=tk.X, pady=(0, 12))
        
        # Başlat/Durdur butonu - sabit boyut (başlangıçta yeşil)
        self.start_stop_button = RoundedButton(
            top_frame, 
            text="▶️ BAŞLAT", 
            command=self.toggle_auto_capture,
            bg_color="#27AE60",  # Başlangıçta yeşil
            fg_color="#222222",
            width=160,
            height=45
        )
        self.start_stop_button.pack(side=tk.TOP, fill=tk.X, pady=(0, 12))
        
        # Alt kısım - Reset butonu
        bottom_frame = ttk.Frame(button_container, style="Modern.TFrame")
        bottom_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=(15, 0))
        
        # Reset butonu - sabit boyut
        self.reset_button = RoundedButton(
            bottom_frame, 
            text="🔄 RESET", 
            command=self.reset_all_cards,
            bg_color="#E74C3C",
            fg_color="#222222",
            width=160,
            height=45
        )
        self.reset_button.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Seçim bilgileri kaldırıldı - sadece kart grid'i gösterilecek
        
        # Görüntü alanı kaldırıldı - performans için
        
        # Grid ağırlıkları
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(1, weight=1)
        
        # Kart görüntüleme sistemi
        try:
            self.card_display = CardDisplay(content_frame)
        except Exception as e:
            print(f"CardDisplay oluşturulurken hata: {str(e)}")
            self.card_display = None
            
    def setup_styles(self):
        """Modern stil tanımları"""
        style = ttk.Style()
        
        # Ana pencere arka planı
        self.root.configure(bg="#F4F4F9")
        
        # Modern buton stili
        style.configure("Modern.TButton",
                      background="#4A90E2",
                      foreground="#222222",  # Siyah metin
                      borderwidth=0,
                      relief="flat",
                      font=("Segoe UI", 10, "bold"),
                      padding=(15, 8))
        
        # Reset butonu stili (kırmızı)
        style.configure("Reset.TButton",
                      background="#E74C3C",
                      foreground="#222222",  # Siyah metin
                      borderwidth=0,
                      relief="flat",
                      font=("Segoe UI", 10, "bold"),
                      padding=(15, 8))
        
        # Modern checkbox stili
        style.configure("Modern.TCheckbutton",
                      background="#4A90E2",
                      foreground="#222222",  # Siyah metin
                      borderwidth=0,
                      font=("Segoe UI", 9, "bold"),
                      padding=(10, 5))
        
        # Hover efektleri
        style.map("Modern.TButton",
                 background=[("active", "#357ABD")],
                 relief=[("pressed", "flat")])
        
        style.map("Reset.TButton",
                 background=[("active", "#C0392B")],
                 relief=[("pressed", "flat")])
        
        style.map("Modern.TCheckbutton",
                 background=[("active", "#357ABD")])
        
        # Frame stilleri
        style.configure("Modern.TFrame",
                      background="#F4F4F9",
                      borderwidth=1,
                      relief="flat")
        
        # Label stilleri
        style.configure("Modern.TLabel",
                      background="#F4F4F9",
                      foreground="#222222",
                      font=("Segoe UI", 9))
        
        # LabelFrame stili
        style.configure("Modern.TLabelframe",
                      background="#F4F4F9",
                      foreground="#222222",
                      font=("Segoe UI", 10, "bold"))
        
        style.configure("Modern.TLabelframe.Label",
                      background="#F4F4F9",
                      foreground="#222222",
                      font=("Segoe UI", 10, "bold"))
        
    def start_selection(self):
        """Ekran seçimi başlat"""
        self.root.withdraw()  # Ana pencereyi gizle
        self.create_selection_window()
        
    def create_selection_window(self):
        """Seçim penceresi oluştur"""
        self.selection_window = tk.Toplevel()
        self.selection_window.attributes('-fullscreen', True)
        self.selection_window.attributes('-alpha', 0.3)
        self.selection_window.configure(bg='black')
        
        # Canvas oluştur
        self.canvas = tk.Canvas(self.selection_window, bg='black', highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        # Mouse event'leri
        self.canvas.bind('<Button-1>', self.on_mouse_down)
        self.canvas.bind('<B1-Motion>', self.on_mouse_drag)
        self.canvas.bind('<ButtonRelease-1>', self.on_mouse_up)
        self.canvas.bind('<Escape>', self.cancel_selection)
        
        # Talimatlar
        instruction_label = tk.Label(self.selection_window, 
                                   text="Mouse ile seçim yapın. ESC ile iptal edin.",
                                   bg='white', fg='black', font=('Arial', 12))
        instruction_label.place(x=10, y=10)
        
    def on_mouse_down(self, event):
        """Mouse basıldığında"""
        self.selecting = True
        self.start_x = event.x
        self.start_y = event.y
        self.rect = None
        
    def on_mouse_drag(self, event):
        """Mouse sürüklendiğinde"""
        if self.selecting:
            if self.rect:
                self.canvas.delete(self.rect)
            self.rect = self.canvas.create_rectangle(
                self.start_x, self.start_y, event.x, event.y,
                outline='red', width=2
            )
            
    def on_mouse_up(self, event):
        """Mouse bırakıldığında"""
        if self.selecting:
            self.end_x = event.x
            self.end_y = event.y
            self.selecting = False
            
            # Koordinatları düzenle
            x1, y1 = min(self.start_x, self.end_x), min(self.start_y, self.end_y)
            x2, y2 = max(self.start_x, self.end_x), max(self.start_y, self.end_y)
            
            # Seçim çok küçükse iptal et
            if abs(x2 - x1) < 10 or abs(y2 - y1) < 10:
                self.cancel_selection()
                return
                
            self.selection_window.destroy()
            self.root.deiconify()  # Ana pencereyi göster
            
            # Seçim bilgilerini güncelle
            self.update_selection_info(x1, y1, x2, y2)
            
    def cancel_selection(self, event=None):
        """Seçimi iptal et"""
        if self.selection_window:
            self.selection_window.destroy()
        self.root.deiconify()
        
    def update_selection_info(self, x1, y1, x2, y2):
        """Seçim bilgilerini güncelle"""
        # Seçim koordinatlarını sakla
        self.selection_coords = (x1, y1, x2, y2)
        
        # Seçilen alanı kaydet
        self.save_selected_area(x1, y1, x2, y2)
        
        # Otomatik yakalama başlatma - kullanıcı butona bassın
        # self.start_auto_capture()
        
    def capture_selected_area(self):
        """Seçili alanı yakala"""
        if not hasattr(self, 'selection_coords'):
            messagebox.showwarning("Uyarı", "Önce bir alan seçin!")
            return
            
        try:
            x1, y1, x2, y2 = self.selection_coords
            
            # MSS ile hızlı ekran görüntüsü al
            monitor = {"top": y1, "left": x1, "width": x2-x1, "height": y2-y1}
            screenshot = self.sct.grab(monitor)
            
            # MSS görüntüsünü PIL Image'e çevir
            screenshot_pil = Image.frombytes("RGB", screenshot.size, screenshot.rgb)
            
            # PIL Image'i Tkinter PhotoImage'e çevir
            photo = ImageTk.PhotoImage(screenshot_pil)
            
            # Görüntüyü göster
            self.image_label.config(image=photo, text="")
            self.image_label.image = photo  # Referansı sakla
            
            # Başarı mesajı
            messagebox.showinfo("Başarılı", "Seçili alan yakalandı!")
            
        except Exception as e:
            messagebox.showerror("Hata", f"Görüntü yakalama hatası: {str(e)}")
            
    def start_auto_capture(self):
        """Otomatik yakalama başlat"""
        if hasattr(self, 'selection_coords'):
            self.auto_capture_active = True
            self.auto_capture()
            # Buton metnini ve rengini güncelle (kırmızı)
            self.start_stop_button.update_button(
                text="⏸️ DURDUR",
                bg_color="#E74C3C"  # Kırmızı
            )
            
    def stop_auto_capture(self):
        """Otomatik yakalamayı durdur"""
        self.auto_capture_active = False
        if self.auto_capture_job:
            self.root.after_cancel(self.auto_capture_job)
            self.auto_capture_job = None
        # Buton metnini ve rengini güncelle (yeşil)
        self.start_stop_button.update_button(
            text="▶️ BAŞLAT",
            bg_color="#27AE60"  # Yeşil
        )
        
    def toggle_auto_capture(self):
        """Başlat/Durdur toggle"""
        if self.auto_capture_active:
            self.stop_auto_capture()
        else:
            self.start_auto_capture()
            
    def on_manual_mode_change(self):
        """Manuel mod değiştiğinde"""
        if self.manual_mode.get():
            print("🔒 Manuel mod aktif - otomatik tarama durduruldu")
            self.stop_auto_capture()
        else:
            print("🔓 Manuel mod deaktif - otomatik tarama başlatılabilir")
            
    def stop_auto_capture(self):
        """Otomatik yakalamayı durdur"""
        self.auto_capture_active = False
        if self.auto_capture_job:
            self.root.after_cancel(self.auto_capture_job)
            self.auto_capture_job = None
        # Buton metnini ve rengini güncelle (yeşil)
        self.start_stop_button.update_button(
            text="▶️ BAŞLAT",
            bg_color="#27AE60"  # Yeşil
        )
            
    def auto_capture(self):
        """Otomatik yakalama döngüsü"""
        if self.auto_capture_active and hasattr(self, 'selection_coords') and not self.manual_mode.get():
            try:
                # FPS hesaplama başlat
                if self.fps_start_time is None:
                    self.fps_start_time = time.time()
                    self.fps_frame_count = 0
                
                x1, y1, x2, y2 = self.selection_coords
                
                # MSS ile hızlı ekran görüntüsü al
                monitor = {"top": y1, "left": x1, "width": x2-x1, "height": y2-y1}
                screenshot = self.sct.grab(monitor)
                
                # MSS görüntüsünü PIL Image'e çevir
                screenshot_pil = Image.frombytes("RGB", screenshot.size, screenshot.rgb)
                
                # Kart tespiti yap
                detected_cards = self.card_detector.detect_cards(screenshot_pil)
                
                # Kart görüntüleme sistemini güncelle
                if self.card_display:
                    self.card_display.update_detected_cards(detected_cards)
                
                # FPS hesaplama
                self.fps_frame_count += 1
                current_time = time.time()
                
                # Her 1 saniyede bir FPS yazdır
                if self.fps_last_print_time is None or current_time - self.fps_last_print_time >= 1.0:
                    elapsed_time = current_time - self.fps_start_time
                    fps = self.fps_frame_count / elapsed_time if elapsed_time > 0 else 0
                    print(f"FPS: {fps:.1f} - Frame: {self.fps_frame_count} - Time: {elapsed_time:.1f}s")
                    
                    # FPS sayacını sıfırla
                    self.fps_start_time = current_time
                    self.fps_frame_count = 0
                    self.fps_last_print_time = current_time
                
            except Exception as e:
                print(f"Otomatik yakalama hatası: {str(e)}")
                
            # 0.1 saniye sonra tekrar çalıştır
            self.auto_capture_job = self.root.after(100, self.auto_capture)
            
    def reset_all_cards(self):
        """Tüm kartları reset et - tespit edilmemiş olarak işaretle"""
        try:
            if self.card_display:
                # Tüm kartları normal haline döndür
                for card_name in self.card_display.card_labels:
                    label = self.card_display.card_labels[card_name]
                    # Orijinal görüntüyü geri yükle
                    label.config(image=self.card_display.card_images[card_name])
                    label.image = self.card_display.card_images[card_name]
                
                # Tespit edilen kartları temizle
                self.card_display.detected_cards.clear()
                
                # Card detector'daki tespit edilen kartları da temizle
                self.card_detector.detected_cards.clear()  # Set'i temizle
                self.card_detector.previous_frame = None  # Önceki frame'i de temizle
                
                print("Tüm kartlar reset edildi!")
                
        except Exception as e:
            print(f"Reset hatası: {str(e)}")
    
    def load_saved_area(self):
        """Kayıtlı alanı sadece yükle, otomatik başlatma"""
        try:
            if os.path.exists(self.settings_file):
                with open(self.settings_file, 'r') as f:
                    saved_area = json.load(f)
                
                x1, y1, x2, y2 = saved_area['x1'], saved_area['y1'], saved_area['x2'], saved_area['y2']
                
                print(f"Kayıtlı alan yüklendi: ({x1}, {y1}) - ({x2}, {y2})")
                
                # Seçim bilgilerini güncelle
                self.update_selection_info(x1, y1, x2, y2)
                
            else:
                print("Kayıtlı alan bulunamadı, manuel seçim bekleniyor...")
                
        except Exception as e:
            print(f"Kayıtlı alan yüklenirken hata: {str(e)}")
            
    def load_and_start_saved_area(self):
        """Kayıtlı alanı yükle ve otomatik başlat (manuel başlatma için)"""
        try:
            if os.path.exists(self.settings_file):
                with open(self.settings_file, 'r') as f:
                    saved_area = json.load(f)
                
                x1, y1, x2, y2 = saved_area['x1'], saved_area['y1'], saved_area['x2'], saved_area['y2']
                
                print(f"Kayıtlı alan yüklendi: ({x1}, {y1}) - ({x2}, {y2})")
                
                # Seçim bilgilerini güncelle
                self.update_selection_info(x1, y1, x2, y2)
                
                # Manuel mod değilse otomatik başlat
                if not self.manual_mode.get():
                    self.start_auto_capture()
                
            else:
                print("Kayıtlı alan bulunamadı, manuel seçim bekleniyor...")
                
        except Exception as e:
            print(f"Kayıtlı alan yüklenirken hata: {str(e)}")
    
    def save_selected_area(self, x1, y1, x2, y2):
        """Seçilen alanı kaydet"""
        try:
            area_data = {
                'x1': x1,
                'y1': y1,
                'x2': x2,
                'y2': y2,
                'timestamp': time.time()
            }
            
            with open(self.settings_file, 'w') as f:
                json.dump(area_data, f, indent=2)
            
            print(f"Seçilen alan kaydedildi: ({x1}, {y1}) - ({x2}, {y2})")
            
        except Exception as e:
            print(f"Alan kaydedilirken hata: {str(e)}")
    
    def on_closing(self):
        """Pencere kapatılırken çağrılır"""
        self.stop_auto_capture()
        self.root.destroy()
            
    def run(self):
        """Uygulamayı çalıştır"""
        self.root.mainloop()

if __name__ == "__main__":
    app = ScreenSelector()
    app.run() 