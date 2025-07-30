import cv2
import numpy as np
import os
from PIL import Image
import logging

class CardDetector:
    def __init__(self, cards_folder="CROPPEDCARDS"):
        self.cards_folder = cards_folder
        self.card_templates = {}
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
        """CROPPEDCARDS klasöründeki kart şablonlarını yükle"""
        try:
            if not os.path.exists(self.cards_folder):
                self.logger.error(f"{self.cards_folder} klasörü bulunamadı!")
                return
                
            for filename in os.listdir(self.cards_folder):
                if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
                    filepath = os.path.join(self.cards_folder, filename)
                    template = cv2.imread(filepath, cv2.IMREAD_COLOR)
                    
                    if template is not None:
                        # Kart adını dosya adından çıkar (uzantısız)
                        card_name = os.path.splitext(filename)[0]
                        self.card_templates[card_name] = template
                        self.logger.info(f"Kart şablonu yüklendi: {card_name}")
                    else:
                        self.logger.warning(f"Görüntü yüklenemedi: {filename}")
                        
            self.logger.info(f"Toplam {len(self.card_templates)} kart şablonu yüklendi")
            
        except Exception as e:
            self.logger.error(f"Kart şablonları yüklenirken hata: {str(e)}")
            
    def detect_cards(self, screenshot):
        """Ekran görüntüsünde kartları tespit et"""
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
                
            # Her kart şablonu için kontrol et
            for card_name, template in self.card_templates.items():
                result = cv2.matchTemplate(screenshot_cv, template, cv2.TM_CCOEFF_NORMED)
                min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
                
                # Eşik değeri (0.8 = %80 benzerlik)
                threshold = 0.99
                
                if max_val >= threshold:
                    detected_cards.append({
                        'name': card_name,
                        'confidence': max_val,
                        'location': max_loc
                    })
                    self.logger.info(f"Kart tespit edildi: {card_name} (güven: {max_val:.2f})")
                    
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