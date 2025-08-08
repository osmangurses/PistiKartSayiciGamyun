# 🎴 Kart Sayıcı - Kullanım Kılavuzu

## 📋 Genel Bakış
Kart Sayıcı, Gamyun platformundaki kart oyunları (özellikle Pisti) için geliştirilmiş gerçek zamanlı kart tespit uygulamasıdır.

## 🚀 Kurulum ve Çalıştırma

### Windows için:
1. `KartSayici.exe` dosyasını indirin
2. Dosyayı çift tıklayarak çalıştırın
3. Uygulama otomatik olarak açılacaktır

### Python ile Çalıştırma:
```bash
pip install -r requirements.txt
python screen_selector.py
```

## 🎮 Kullanım Adımları

### 1. Alan Seçimi
- **"🎯 ALAN SEÇ"** butonuna tıklayın
- Ekranda tespit etmek istediğiniz kart alanını seçin
- Seçim tamamlandığında alan otomatik olarak kaydedilir

### 2. Otomatik Tarama
- **"▶️ BAŞLAT"** butonuna tıklayarak taramayı başlatın
- Buton **"⏸️ DURDUR"** olarak değişecek
- Tespit edilen kartlar UI'da siyah filtre ile işaretlenir

### 3. Manuel Mod
- **"🔒 MANUEL MOD"** checkbox'ını işaretleyin
- Bu durumda otomatik tarama durur
- Kartları manuel olarak tıklayarak işaretleyebilirsiniz

### 4. Reset İşlemi
- **"🔄 RESET"** butonuna tıklayın
- Tüm tespit edilen kartlar temizlenir
- Kartlar normal haline döner

## 🎯 Özellikler

### ✅ Gerçek Zamanlı Tespit
- Sürekli ekran taraması
- Adaptif multithreading sistemi
- FPS optimizasyonu

### ✅ Akıllı Performans
- Frame differencing (değişmeyen ekranları atlar)
- Early exit (kart bulunduğunda diğerlerini taramaz)
- CPU kullanımına göre thread sayısı ayarlanır

### ✅ Kullanıcı Dostu Arayüz
- Modern, yuvarlatılmış butonlar
- Hover efektleri
- Renk kodlu durum göstergeleri

### ✅ Kalıcı Ayarlar
- Seçilen alan otomatik kaydedilir
- Uygulama yeniden açıldığında alan hatırlanır

## 🎮 Oyun Uyumluluğu

### Desteklenen Oyunlar:
- ✅ **Pisti** (Gamyun)
- ✅ **Batak** (Gamyun)
- ✅ **Koz** (Gamyun)
- ✅ Diğer kart oyunları

### Sistem Gereksinimleri:
- Windows 10/11
- Minimum 4GB RAM
- Çok çekirdekli işlemci (önerilen)

## 🔧 Sorun Giderme

### Uygulama Açılmıyor:
1. Windows Defender'ı geçici olarak devre dışı bırakın
2. Dosyayı yönetici olarak çalıştırın
3. Antivirüs programınızı kontrol edin

### Kart Tespit Edilmiyor:
1. Alan seçimini kontrol edin
2. Ekran çözünürlüğünü kontrol edin
3. Oyun penceresinin tam ekran olduğundan emin olun

### Performans Sorunları:
1. Manuel modu kullanın
2. Diğer uygulamaları kapatın
3. CPU kullanımını kontrol edin

## 📊 Performans Metrikleri

### FPS (Frames Per Second):
- **Normal**: 15-20 FPS
- **Optimize**: 25-30 FPS
- **Minimum**: 5 FPS

### CPU Kullanımı:
- **Düşük**: %10-20
- **Orta**: %20-40
- **Yüksek**: %40+ (thread sayısı azalır)

## 🎯 İpuçları

1. **En İyi Sonuç İçin:**
   - Oyunu tam ekran yapın
   - Alan seçimini kartların tam üzerine yapın
   - Gereksiz uygulamaları kapatın

2. **Performans İçin:**
   - Manuel modu kullanın
   - Sadece gerekli kartları işaretleyin
   - Düzenli reset yapın

3. **Doğruluk İçin:**
   - İyi aydınlatma sağlayın
   - Ekran çözünürlüğünü kontrol edin
   - Kart görsellerinin net olduğundan emin olun

## 📞 Destek

Sorun yaşarsanız:
1. Log dosyalarını kontrol edin
2. Sistem gereksinimlerini kontrol edin
3. Farklı oyun alanları deneyin

---

**🎴 Kart Sayıcı v1.0** - Gamyun Platformu için Özel Geliştirilmiştir 