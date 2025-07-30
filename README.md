# Kart Tespit Sistemi

Bu Python uygulaması, ekranın belirli bir bölümünü mouse ile seçmenizi, seçtiğiniz alanı UI'da görüntülemenizi ve CROPPEDCARDS klasöründeki kart şablonlarını kullanarak kart tespiti yapmanızı sağlar.

## Özellikler

- Mouse ile ekran alanı seçimi
- Seçilen alanın koordinatlarını ve boyutlarını görüntüleme
- Otomatik kart tespiti (her saniye)
- CROPPEDCARDS klasöründeki kart şablonlarını kullanma
- Gerçek zamanlı kart tespit sonuçları
- Kullanıcı dostu arayüz

## Kurulum

1. Gerekli kütüphaneleri yükleyin:
```bash
pip install -r requirements.txt
```

## Kullanım

1. Uygulamayı çalıştırın:
```bash
python screen_selector.py
```

2. "Ekran Seç" butonuna tıklayın
3. Mouse ile istediğiniz alanı seçin
4. Seçim tamamlandığında otomatik olarak kart tespiti başlar
5. Her saniye seçilen alan taranır ve tespit edilen kartlar gösterilir

## Kontroller

- **Mouse**: Alan seçimi için
- **ESC**: Seçimi iptal etmek için

## Dosya Yapısı

```
CursorCardDetector/
├── screen_selector.py      # Ana uygulama (ekran seçici ve UI)
├── card_detector.py        # Kart tespit modülü
├── CROPPEDCARDS/          # Kart şablonları klasörü
│   ├── Hearts Ace.png
│   ├── Hearts King.png
│   └── ... (diğer kartlar)
├── requirements.txt        # Gerekli kütüphaneler
└── README.md              # Bu dosya
```

## Gereksinimler

- Python 3.7+
- Windows 10/11 (test edildi)
- Gerekli Python kütüphaneleri (requirements.txt dosyasında listelenmiştir) 