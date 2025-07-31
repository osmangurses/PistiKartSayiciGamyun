import cv2
import numpy as np
import os
from PIL import Image
import logging

class CardDetector:
    def __init__(self, cards_folder="CROPPEDCARDS"):
        self.cards_folder = cards_folder
        self.card_templates = {}
        self.detected_cards = set()  # Tespit edilen kartları sakla
        self.previous_frame = None  # Önceki frame'i sakla
        self.setup_logging()
        self.load_card_templates()
        
    def setup_logging(self):
        """Logging ayarları"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('card_detector.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        
    def load_card_templates(self):
        """CROPPEDCARDS klasöründeki kart şablonlarını yükle ve küçült"""
        try:
            if not os.path.exists(self.cards_folder):
                self.logger.error(f"{self.cards_folder} klasörü bulunamadı!")
                return
                
            # Küçültme oranı (0.5x = yarı boyut)
            scale_factor = 1
                
            for filename in os.listdir(self.cards_folder):
                if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
                    filepath = os.path.join(self.cards_folder, filename)
                    template = cv2.imread(filepath, cv2.IMREAD_COLOR)
                    
                    if template is not None:
                        # Şablonu küçült
                        height, width = template.shape[:2]
                        new_width = int(width * scale_factor)
                        new_height = int(height * scale_factor)
                        template_resized = cv2.resize(template, (new_width, new_height), interpolation=cv2.INTER_AREA)
                        
                        # Kart adını dosya adından çıkar (uzantısız)
                        card_name = os.path.splitext(filename)[0]
                        self.card_templates[card_name] = template_resized
                        self.logger.info(f"Kart şablonu yüklendi ve küçültüldü: {card_name} ({width}x{height} -> {new_width}x{new_height})")
                    else:
                        self.logger.warning(f"Görüntü yüklenemedi: {filename}")
                        
            self.logger.info(f"Toplam {len(self.card_templates)} kart şablonu yüklendi ve küçültüldü")
            
        except Exception as e:
            self.logger.error(f"Kart şablonları yüklenirken hata: {str(e)}")
            
    def detect_cards(self, screenshot):
        """Ekran görüntüsünde kartları tespit et - optimize edilmiş"""
        if not self.card_templates:
            self.logger.warning("Kart şablonları yüklenmemiş!")
            return []
            
        detected_cards = []
        
        try:
            # PIL Image'i OpenCV formatına çevir
            if isinstance(screenshot, Image.Image):
                screenshot_cv = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
            else:
                screenshot_cv = screenshot
            
            # Ekran görüntüsünü küçült (şablonlarla aynı oranda)
            scale_factor = 1
            height, width = screenshot_cv.shape[:2]
            new_width = int(width * scale_factor)
            new_height = int(height * scale_factor)
            screenshot_resized = cv2.resize(screenshot_cv, (new_width, new_height), interpolation=cv2.INTER_AREA)
            
            # Frame değişikliği kontrolü
            if self.previous_frame is not None:
                # Boyut kontrolü - aynı boyutta olmalı
                if screenshot_resized.shape == self.previous_frame.shape:
                    # Önceki frame ile karşılaştır
                    frame_diff = cv2.absdiff(screenshot_resized, self.previous_frame)
                    mean_diff = cv2.mean(frame_diff)[0]
                    
                    # Eğer frame değişikliği çok az ise, tarama yapma
                    if mean_diff < 5.0:  # Eşik değeri
                        self.logger.info("Frame değişikliği yok, tarama atlandı")
                        return []
                else:
                    # Boyut farklıysa önceki frame'i güncelle ve devam et
                    self.logger.info("Frame boyutu değişti, tarama devam ediyor")
            
            # Tarama başladığını logla
            self.logger.info("Kart taraması başladı...")
                
            # Her kart şablonu için kontrol et (sadece tespit edilmemiş olanlar)
            cards_checked = 0
            for card_name, template in self.card_templates.items():
                # Eğer kart zaten tespit edilmişse, atla
                if card_name in self.detected_cards:
                    continue
                    
                cards_checked += 1
                result = cv2.matchTemplate(screenshot_resized, template, cv2.TM_CCOEFF_NORMED)
                min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
                
                # Eşik değeri
                threshold = 0.99
                
                if max_val >= threshold:
                    detected_cards.append({
                        'name': card_name,
                        'confidence': max_val,
                        'location': max_loc
                    })
                    self.detected_cards.add(card_name)  # Tespit edilen kartı listeye ekle
                    self.logger.info(f"Kart tespit edildi: {card_name} (güven: {max_val:.2f}) - {cards_checked} kart tarandı")
                    
                    # İlk eşleşme bulunduğunda diğer kartları taramayı durdur
                    break
            
            # Eğer hiç eşleşme bulunmadıysa, bu frame'i previous frame olarak ata
            if not detected_cards:
                self.previous_frame = screenshot_resized.copy()
                self.logger.info(f"Hiç eşleşme bulunamadı - {cards_checked} kart tarandı, frame previous frame olarak atandı")
            else:
                self.logger.info(f"Eşleşme bulundu, frame previous frame olarak atanmadı")
                    
        except Exception as e:
            self.logger.error(f"Kart tespiti sırasında hata: {str(e)}")
            
        return detected_cards
        
    def get_detection_summary(self, detected_cards):
        """Tespit edilen kartların özetini döndür"""
        if not detected_cards:
            return "Kart tespit edilmedi"
            
        summary = f"{len(detected_cards)} kart tespit edildi:\n"
        for card in detected_cards:
            summary += f"- {card['name']} (güven: {card['confidence']:.2f})\n"
            
        return summary 