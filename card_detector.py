import cv2
import numpy as np
import os
from PIL import Image
import logging
import threading
import time
import psutil
import multiprocessing

class CardDetector:
    def __init__(self, cards_folder="CROPPEDCARDS"):
        self.cards_folder = cards_folder
        self.card_templates = {}
        self.detected_cards = set()  # Tespit edilen kartları sakla
        self.previous_frame = None  # Önceki frame'i sakla
        self.setup_logging()
        self.load_card_templates()
        
        # Thread'ler için lock
        self.detection_lock = threading.Lock()
        self.detected_cards = set()  # Normal set
        
        # Adaptif thread sistemi
        self.cpu_count = multiprocessing.cpu_count()
        self.optimal_thread_count = self.get_optimal_thread_count()
        self.logger.info(f"CPU Çekirdek Sayısı: {self.cpu_count}, Optimal Thread Sayısı: {self.optimal_thread_count}")
        
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
    
    def get_optimal_thread_count(self):
        """CPU kullanımına göre optimal thread sayısını hesapla"""
        try:
            # CPU kullanımını al
            cpu_usage = psutil.cpu_percent(interval=0.1)
            
            # CPU çekirdek sayısına göre temel thread sayısı
            if self.cpu_count >= 8:
                base_threads = 13  # Maksimum paralellik
            elif self.cpu_count >= 4:
                base_threads = 8   # Yüksek paralellik
            else:
                base_threads = 4   # Temel paralellik
            
            # CPU kullanımına göre adaptif ayarlama
            if cpu_usage < 30:
                # Düşük CPU kullanımı - daha fazla thread
                adaptive_threads = min(base_threads + 2, 13)
                self.logger.info(f"CPU kullanımı düşük ({cpu_usage:.1f}%), thread sayısı artırıldı: {adaptive_threads}")
            elif cpu_usage < 60:
                # Orta CPU kullanımı - optimal thread
                adaptive_threads = base_threads
                self.logger.info(f"CPU kullanımı orta ({cpu_usage:.1f}%), optimal thread sayısı: {adaptive_threads}")
            else:
                # Yüksek CPU kullanımı - daha az thread
                adaptive_threads = max(base_threads - 2, 2)
                self.logger.info(f"CPU kullanımı yüksek ({cpu_usage:.1f}%), thread sayısı azaltıldı: {adaptive_threads}")
            
            return adaptive_threads
            
        except Exception as e:
            self.logger.error(f"Thread sayısı hesaplanırken hata: {str(e)}")
            return 4  # Varsayılan değer
    
    def detect_cards_in_range(self, screenshot_resized, card_names, thread_id):
        """Belirli bir kart aralığını tara (thread için)"""
        detected_cards = []
        cards_checked = 0
        
        for card_name in card_names:
            # Eğer kart zaten tespit edilmişse, atla
            with self.detection_lock:
                if card_name in self.detected_cards:
                    continue
            
            cards_checked += 1
            template = self.card_templates[card_name]
            
            result = cv2.matchTemplate(screenshot_resized, template, cv2.TM_CCOEFF_NORMED)
            min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
            
            # Eşik değeri
            threshold = 0.99
            
            if max_val >= threshold:
                detected_cards.append({
                    'name': card_name,
                    'confidence': max_val,
                    'location': max_loc,
                    'thread_id': thread_id
                })
                
                with self.detection_lock:
                    self.detected_cards.add(card_name)
                
                self.logger.info(f"Thread {thread_id}: Kart tespit edildi: {card_name} (güven: {max_val:.2f}) - {cards_checked} kart tarandı")
                break  # İlk eşleşme bulunduğunda dur
        
        return detected_cards, cards_checked
    
    def detect_cards(self, screenshot):
        """Ekran görüntüsünde kartları tespit et - multithreaded"""
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
            self.logger.info("Kart taraması başladı (adaptif multithreading)...")
            
            # Adaptif thread sayısını al
            thread_count = self.get_optimal_thread_count()
            
            # Kartları thread sayısına göre böl
            all_card_names = list(self.card_templates.keys())
            cards_per_thread = len(all_card_names) // thread_count
            
            # Thread'ler için kart listeleri
            thread_cards = []
            for i in range(thread_count):
                start_idx = i * cards_per_thread
                end_idx = start_idx + cards_per_thread if i < thread_count - 1 else len(all_card_names)
                thread_cards.append(all_card_names[start_idx:end_idx])
            
            self.logger.info(f"Kartlar {thread_count} thread'e bölündü: {[len(cards) for cards in thread_cards]} kart/thread")
            
            # Thread'leri başlat
            threads = []
            results = []
            
            for i in range(thread_count):
                thread = threading.Thread(
                    target=self._detect_cards_thread,
                    args=(screenshot_resized, thread_cards[i], i, results)
                )
                threads.append(thread)
                thread.start()
            
            # Thread'lerin bitmesini bekle
            for thread in threads:
                thread.join()
            
            # Sonuçları birleştir
            total_cards_checked = 0
            for result in results:
                if result:
                    detected_cards.extend(result['cards'])
                    total_cards_checked += result['cards_checked']
            
            # Eğer hiç eşleşme bulunamadıysa, bu frame'i previous frame olarak ata
            if not detected_cards:
                self.previous_frame = screenshot_resized.copy()
                self.logger.info(f"Hiç eşleşme bulunamadı - {total_cards_checked} kart tarandı ({thread_count} thread), frame previous frame olarak atandı")
            else:
                self.logger.info(f"Eşleşme bulundu, frame previous frame olarak atanmadı")
                    
        except Exception as e:
            self.logger.error(f"Kart tespiti sırasında hata: {str(e)}")
            
        return detected_cards
    
    def _detect_cards_thread(self, screenshot_resized, card_names, thread_id, results):
        """Thread fonksiyonu - kart tespiti yapar"""
        try:
            detected_cards, cards_checked = self.detect_cards_in_range(screenshot_resized, card_names, thread_id)
            results.append({
                'cards': detected_cards,
                'cards_checked': cards_checked,
                'thread_id': thread_id
            })
        except Exception as e:
            self.logger.error(f"Thread {thread_id} hatası: {str(e)}")
            results.append({
                'cards': [],
                'cards_checked': 0,
                'thread_id': thread_id
            })
        
    def get_detection_summary(self, detected_cards):
        """Tespit edilen kartların özetini döndür"""
        if not detected_cards:
            return "Kart tespit edilmedi"
            
        summary = f"{len(detected_cards)} kart tespit edildi:\n"
        for card in detected_cards:
            summary += f"- {card['name']} (güven: {card['confidence']:.2f}, thread: {card.get('thread_id', 'N/A')})\n"
            
        return summary 