import tkinter as tk
from tkinter import ttk, messagebox
import pyautogui
from PIL import Image, ImageTk
import numpy as np
import cv2
from card_detector import CardDetector
from card_display import CardDisplay

class ScreenSelector:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Ekran Seçici")
        self.root.geometry("800x600")
        self.root.attributes('-topmost', True)  # Her zaman en üstte
        
        # Seçim değişkenleri
        self.start_x = None
        self.start_y = None
        self.end_x = None
        self.end_y = None
        self.selecting = False
        self.selection_window = None
        self.auto_capture_active = False
        self.auto_capture_job = None
        
        # Kart detektörü
        self.card_detector = CardDetector()
        
        self.setup_ui()
        
    def setup_ui(self):
        # Pencere kapatma event'i
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # Ana frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Başlık
        title_label = ttk.Label(main_frame, text="Ekran Seçici", font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))
        
        # Butonlar
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=1, column=0, columnspan=2, pady=(0, 20))
        
        self.select_button = ttk.Button(button_frame, text="Ekran Seç", command=self.start_selection)
        self.select_button.pack()
        
        # Seçim bilgileri kaldırıldı - sadece kart grid'i gösterilecek
        
        # Görüntü alanı kaldırıldı - performans için
        
        # Grid ağırlıkları
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(2, weight=1)
        
        # Kart görüntüleme sistemi
        try:
            self.card_display = CardDisplay(main_frame)
        except Exception as e:
            print(f"CardDisplay oluşturulurken hata: {str(e)}")
            self.card_display = None
        
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
        
        # Otomatik yakalama başlat
        self.start_auto_capture()
        
    def capture_selected_area(self):
        """Seçili alanı yakala"""
        if not hasattr(self, 'selection_coords'):
            messagebox.showwarning("Uyarı", "Önce bir alan seçin!")
            return
            
        try:
            x1, y1, x2, y2 = self.selection_coords
            
            # Ekran görüntüsü al
            screenshot = pyautogui.screenshot(region=(x1, y1, x2-x1, y2-y1))
            
            # PIL Image'i Tkinter PhotoImage'e çevir
            photo = ImageTk.PhotoImage(screenshot)
            
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
            
    def stop_auto_capture(self):
        """Otomatik yakalamayı durdur"""
        self.auto_capture_active = False
        if self.auto_capture_job:
            self.root.after_cancel(self.auto_capture_job)
            self.auto_capture_job = None
            
    def auto_capture(self):
        """Otomatik yakalama döngüsü"""
        if self.auto_capture_active and hasattr(self, 'selection_coords'):
            try:
                x1, y1, x2, y2 = self.selection_coords
                
                # Ekran görüntüsü al
                screenshot = pyautogui.screenshot(region=(x1, y1, x2-x1, y2-y1))
                
                # Kart tespiti yap
                detected_cards = self.card_detector.detect_cards(screenshot)
                
                # Kart görüntüleme sistemini güncelle
                if self.card_display:
                    self.card_display.update_detected_cards(detected_cards)
                
            except Exception as e:
                print(f"Otomatik yakalama hatası: {str(e)}")
                
            # 0.1 saniye sonra tekrar çalıştır
            self.auto_capture_job = self.root.after(100, self.auto_capture)
            
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