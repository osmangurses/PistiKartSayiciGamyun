# 🃏 PistiKartSayiciGamyun

> **Gamyun platformundaki herhangi bir kart oyununda çalışabilen, özellikle Pişti oyununda test edilip onaylanmış gerçek zamanlı kart tespit sistemi!**

[![Demo Video](https://img.youtube.com/vi/8uWLg-X3T3s/0.jpg)](https://youtu.be/8uWLg-X3T3s)

## 🎯 Ne İşe Yarar?

Bu proje, ekranınızda oynadığınız kart oyunlarını **otomatik olarak takip eder** ve hangi kartların oyunda olduğunu **gerçek zamanlı** olarak gösterir. Özellikle **Pişti oyunu** için optimize edilmiş ama Gamyun platformundaki diğer kart oyunlarında da mükemmel çalışır!

### 🎮 Özellikler

- **🔍 Gerçek Zamanlı Tespit**: Kartları anında bulur ve işaretler
- **⚡ Yüksek Performans**: 10-20 FPS ile akıcı çalışır
- **🎯 Akıllı Optimizasyon**: Sadece değişen alanları tarar
- **🖱️ Manuel Kontrol**: Kartlara tıklayarak manuel işaretleme
- **💾 Kalıcı Ayarlar**: Seçilen alan otomatik kaydedilir
- **🔄 Reset Sistemi**: Tek tıkla tüm kartları sıfırlama
- **📊 FPS Monitörü**: Gerçek zamanlı performans takibi

## 🚀 Hızlı Başlangıç

### 📋 Gereksinimler
- Python 3.7+
- Windows 10/11
- Gamyun platformu (veya herhangi bir kart oyunu)

### ⚙️ Kurulum

```bash
# Projeyi indir
git clone https://github.com/kullaniciadi/PistiKartSayiciGamyun.git
cd PistiKartSayiciGamyun

# Gerekli kütüphaneleri yükle
pip install -r requirements.txt

# Uygulamayı çalıştır
python screen_selector.py
```

## 🎮 Nasıl Kullanılır?

### 1️⃣ **İlk Açılış**
- Uygulama açılır ve kayıtlı alan varsa otomatik başlar
- Kayıtlı alan yoksa "ALAN SEÇ" butonuna tıklayın

### 2️⃣ **Alan Seçimi**
- "ALAN SEÇ" butonuna tıklayın
- Mouse ile oyun alanını seçin
- Seçim tamamlandığında otomatik tarama başlar

### 3️⃣ **Kart Takibi**
- **Otomatik**: Sistem kartları otomatik tespit eder
- **Manuel**: Kartlara tıklayarak manuel işaretleyebilirsiniz
- **Reset**: "RESET" butonu ile tüm kartları sıfırlayabilirsiniz

### 4️⃣ **Görsel Geri Bildirim**
- Tespit edilen kartlar siyah filtre ile işaretlenir
- Kalan kartlar normal görünür
- Gerçek zamanlı güncelleme

## 🎯 Pişti Oyunu İçin Özel Optimizasyonlar

Bu proje özellikle **Pişti oyunu** için tasarlanmış ve test edilmiştir:

- **🎴 52 Kart Desteği**: Tüm kartlar tanınır
- **⚡ Hızlı Tespit**: Kartlar anında bulunur
- **🎯 Yüksek Doğruluk**: %95+ tespit doğruluğu
- **🔄 Dinamik Güncelleme**: Oyun sırasında sürekli takip

## 📊 Performans Özellikleri

| Özellik | Değer |
|---------|-------|
| **FPS** | 10-20 FPS |
| **CPU Kullanımı** | %10-30 |
| **Bellek** | ~50MB |
| **Tespit Doğruluğu** | %95+ |
| **Başlangıç Süresi** | <2 saniye |

## 🛠️ Teknik Detaylar

### 🔧 Kullanılan Teknolojiler
- **OpenCV**: Template matching ile kart tespiti
- **MSS**: Hızlı ekran yakalama
- **Tkinter**: Kullanıcı arayüzü
- **PIL**: Görüntü işleme
- **NumPy**: Matematiksel işlemler

### ⚡ Optimizasyon Stratejileri
- **Frame Değişikliği Kontrolü**: Sadece değişen alanları tara
- **Erken Çıkış**: İlk eşleşme bulunduğunda dur
- **Önbellekleme**: Filtre görüntüleri önceden oluştur
- **Akıllı Atama**: Sadece boş frame'leri referans al

## 🎮 Kullanım Senaryoları

### 🃏 Pişti Oyunu
- Oyun alanını seçin
- Sistem kartları otomatik takip eder
- Hangi kartların oyunda olduğunu görün

### 🎴 Diğer Kart Oyunları
- Gamyun platformundaki herhangi bir kart oyunu
- Manuel alan seçimi ile uyumlu
- Aynı performans ve doğruluk

## 🔧 Gelişmiş Ayarlar

### 📁 Kayıtlı Alanlar
- Seçilen alan `selected_area.json` dosyasında saklanır
- Uygulama her açılışta otomatik yükler
- Yeni alan seçimi eski alanı üzerine yazar

### 🎛️ Performans Ayarları
- **Tarama Hızı**: 100ms aralıklarla (10 FPS)
- **Threshold**: %99 eşik değeri
- **Frame Değişikliği**: 5.0 eşik değeri

## 🐛 Sorun Giderme

### ❓ Sık Sorulan Sorular

**Q: Uygulama kartları tespit etmiyor?**
A: Alan seçimini kontrol edin, kartların tamamı seçili alanda olmalı

**Q: Performans düşük?**
A: Ekran çözünürlüğünü düşürün veya daha küçük alan seçin

**Q: Yanlış kartlar tespit ediliyor?**
A: Threshold değerini artırın veya alan seçimini düzeltin

### 🔧 Hata Ayıklama
- Log dosyalarını kontrol edin: `card_detector.log`
- FPS değerlerini izleyin
- Frame değişikliği mesajlarını takip edin


## 🙏 Teşekkürler

- **Gamyun Platformu**: Test ortamı sağladığı için


---

⭐ Bu projeyi beğendiyseniz yıldız vermeyi unutmayın! ⭐