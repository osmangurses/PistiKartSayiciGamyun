import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import os

class CardDisplay:
    def __init__(self, parent_frame, cards_folder="CARDS"):
        self.parent_frame = parent_frame
        self.cards_folder = cards_folder
        self.card_labels = {}
        self.card_images = {}
        self.card_pil_images = {}  # Orijinal PIL görüntüleri sakla
        self.detected_cards = set()
        self.setup_card_grid()
        
    def setup_card_grid(self):
        """Kart grid'ini oluştur"""
        # Ana frame - parent_frame artık content_frame
        self.cards_frame = ttk.LabelFrame(self.parent_frame, text="KALAN KARTLAR", padding="10")
        self.cards_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # Grid frame
        self.grid_frame = ttk.Frame(self.cards_frame)
        self.grid_frame.pack(expand=True, fill=tk.BOTH)
        
        # Kartları yükle ve göster
        self.load_and_display_cards()
        
    def load_and_display_cards(self):
        """Kartları yükle ve grid'de göster"""
        try:
            if not os.path.exists(self.cards_folder):
                print(f"{self.cards_folder} klasörü bulunamadı!")
                return
                
            # Kartları sırala (suit ve rank'e göre)
            card_files = []
            for filename in os.listdir(self.cards_folder):
                if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
                    card_files.append(filename)
            
            # Kartları sırala: Hearts, Diamonds, Clubs, Spades
            suits_order = ['Hearts', 'Diamonds', 'Clubs', 'Spades']
            ranks_order = ['Ace', 'Two', 'Three', 'Four', 'Five', 'Six', 'Seven', 'Eight', 'Nine', 'Ten', 'Jack', 'Queen', 'King']
            
            sorted_cards = []
            for suit in suits_order:
                for rank in ranks_order:
                    for filename in card_files:
                        if filename.startswith(f"{suit} {rank}"):
                            sorted_cards.append(filename)
                            break
            
            # Grid oluştur (4 suit x 13 rank)
            for i, filename in enumerate(sorted_cards):
                row = i // 13  # 13 kart per satır
                col = i % 13   # 13 sütun
                
                # Kart görüntüsünü yükle
                filepath = os.path.join(self.cards_folder, filename)
                try:
                    # Görüntüyü büyüt (50x70 piksel - %100 oranında büyütme)
                    original_image = Image.open(filepath)
                    resized_image = original_image.resize((50, 70), Image.Resampling.LANCZOS)
                    photo = ImageTk.PhotoImage(resized_image)
                    
                    # Label oluştur
                    card_name = os.path.splitext(filename)[0]
                    label = tk.Label(self.grid_frame, image=photo, relief=tk.RAISED, borderwidth=2, cursor="hand2")
                    label.image = photo  # Referansı sakla
                    label.grid(row=row, column=col, padx=2, pady=2)
                    
                    # Tıklama event'i ekle
                    label.bind('<Button-1>', lambda e, name=card_name: self.on_card_click(name))
                    
                    # Kart bilgilerini sakla
                    self.card_labels[card_name] = label
                    self.card_images[card_name] = photo
                    self.card_pil_images[card_name] = resized_image  # Orijinal PIL görüntüsünü sakla
                    
                except Exception as e:
                    print(f"Kart yüklenemedi: {filename} - {str(e)}")
                    
                    
        except Exception as e:
            print(f"Kart grid'i oluşturulurken hata: {str(e)}")
            
    def update_detected_cards(self, detected_cards):
        """Tespit edilen kartları güncelle"""
        
        # Yeni tespit edilen kartları mevcut listeye ekle
        for card in detected_cards:
            card_name = card['name']
            if card_name in self.card_labels and card_name not in self.detected_cards:
                label = self.card_labels[card_name]
                # Siyah filtre uygula
                self.apply_black_filter(label, card_name)
                self.detected_cards.add(card_name)
                print(f"Yeni kart tespit edildi: {card_name}")
    
    def apply_black_filter(self, label, card_name):
        """Kartın üzerine siyah filtre uygula"""
        try:
            # Orijinal PIL görüntüsünü al
            original_pil = self.card_pil_images[card_name]
            
            # Yarı şeffaf siyah filtre oluştur
            black_filter = Image.new('RGBA', (50, 70), (0, 0, 0, 128))  # Alpha 128 = yarı şeffaf
            
            # Orijinal görüntüyü RGBA'ya çevir
            original_rgba = original_pil.convert('RGBA')
            
            # İki görüntüyü birleştir
            combined_image = Image.alpha_composite(original_rgba, black_filter)
            
            # Tkinter PhotoImage'e çevir
            filtered_image = ImageTk.PhotoImage(combined_image)
            
            # Label'a uygula
            label.config(image=filtered_image)
            label.image = filtered_image
            
        except Exception as e:
            print(f"Siyah filtre uygulanırken hata: {str(e)}")
    
    def on_card_click(self, card_name):
        """Kart tıklandığında çağrılır"""
        try:
            if card_name in self.card_labels:
                label = self.card_labels[card_name]
                
                # Kart zaten tespit edilmiş mi kontrol et
                if card_name in self.detected_cards:
                    # Tespit edilmişse, normal haline döndür
                    label.config(image=self.card_images[card_name])
                    label.image = self.card_images[card_name]
                    self.detected_cards.remove(card_name)
                    print(f"Kart normal haline döndürüldü: {card_name}")
                else:
                    # Tespit edilmemişse, siyah filtre uygula
                    self.apply_black_filter(label, card_name)
                    self.detected_cards.add(card_name)
                    print(f"Kart tespit edildi: {card_name}")
                    
        except Exception as e:
            print(f"Kart tıklama hatası: {str(e)}") 