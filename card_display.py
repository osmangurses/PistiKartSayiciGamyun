import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import os

class CardDisplay:
    def __init__(self, parent_frame, cards_folder="CROPPEDCARDS"):
        self.parent_frame = parent_frame
        self.cards_folder = cards_folder
        self.card_labels = {}
        self.card_images = {}
        self.detected_cards = set()
        self.setup_card_grid()
        
    def setup_card_grid(self):
        """Kart grid'ini oluştur"""
        # Ana frame
        self.cards_frame = ttk.LabelFrame(self.parent_frame, text="Kart Şablonları", padding="10")
        self.cards_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(10, 0))
        
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
                    # Görüntüyü küçült (50x70 piksel)
                    original_image = Image.open(filepath)
                    resized_image = original_image.resize((50, 70), Image.Resampling.LANCZOS)
                    photo = ImageTk.PhotoImage(resized_image)
                    
                    # Label oluştur
                    card_name = os.path.splitext(filename)[0]
                    label = tk.Label(self.grid_frame, image=photo, relief=tk.RAISED, borderwidth=2)
                    label.image = photo  # Referansı sakla
                    label.grid(row=row, column=col, padx=2, pady=2)
                    
                    # Kart bilgilerini sakla
                    self.card_labels[card_name] = label
                    self.card_images[card_name] = photo
                    
                except Exception as e:
                    print(f"Kart yüklenemedi: {filename} - {str(e)}")
                    
                    
        except Exception as e:
            print(f"Kart grid'i oluşturulurken hata: {str(e)}")
            
    def update_detected_cards(self, detected_cards):
        """Tespit edilen kartları güncelle"""
        
        # Yeni tespitleri işaretle ve kaldır
        for card in detected_cards:
            card_name = card['name']
            if card_name in self.card_labels:
                label = self.card_labels[card_name]
                # Kartı gizle
                label.grid_remove()
                self.detected_cards.add(card_name) 