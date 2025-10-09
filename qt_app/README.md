# MSA Dashboard - PyQt5 Application

Modern PyQt5 tabanlı Askeri Durum Farkındalığı (MSA) Dashboard uygulaması.

## Özellikler

### 🔐 Kimlik Doğrulama
- Güvenli giriş sistemi
- Rol tabanlı erişim kontrolü
- Oturum yönetimi

### 👥 Rol Tabanlı Dashboard'lar

#### Commander Dashboard
- Tam yetkili komuta kontrol paneli
- Taktik durum haritası
- Birim durumu ve konumları
- Sağlık ve lojistik özeti
- Uyarı yönetimi
- Görev durumu takibi

#### Health Dashboard
- Sağlık personeli için özel panel
- Personel sağlık durumu izleme
- Vital signs takibi
- Sağlık uyarıları
- Tıbbi notlar
- Acil durum yönetimi

#### Analyst Dashboard
- İstihbarat ve analiz paneli
- Veri analizi araçları
- Tehdit değerlendirmesi
- Rapor üretimi
- Tahmin modelleri
- İstihbarat raporları

### 🎨 Modern UI/UX
- Koyu tema tasarım
- Responsive layout
- Gerçek zamanlı güncellemeler
- Interaktif grafikler ve tablolar

## Kurulum

### Gereksinimler
```bash
pip install -r requirements.txt
```

### Çalıştırma
```bash
python main.py
```

## Kullanım

### Giriş Bilgileri (Demo)
- **Commander**: `commander` / `password123`
- **Health Officer**: `health` / `password123`  
- **Analyst**: `analyst` / `password123`

### API Bağlantısı
Uygulama FastAPI backend'e bağlanır:
- **Base URL**: `http://localhost:8000`
- **Endpoints**: `/api/units`, `/api/health`, `/api/alerts`, vb.

## Mimari

```
qt_app/
├── main.py                 # Ana uygulama
├── ui/                     # UI bileşenleri
│   ├── login_window.py     # Giriş ekranı
│   ├── commander_dashboard.py
│   ├── health_dashboard.py
│   └── analyst_dashboard.py
├── services/               # Servisler
│   ├── api_client.py       # API istemcisi
│   └── auth_manager.py     # Kimlik doğrulama
└── utils/                  # Yardımcı araçlar
    └── styles.py           # CSS stilleri
```

## Özellikler

### Real-time Data
- 3-10 saniye arası otomatik güncelleme
- WebSocket desteği (gelecek sürüm)
- Canlı harita güncellemeleri

### Security
- Token tabanlı kimlik doğrulama
- Rol tabanlı yetkilendirme
- Güvenli API iletişimi

### Extensibility
- Modüler tasarım
- Plugin desteği hazır
- Kolay tema değişimi

## Geliştirme

### Yeni Dashboard Ekleme
1. `ui/` klasöründe yeni dashboard sınıfı oluştur
2. `main.py`'da dashboard'u kaydet
3. `auth_manager.py`'da rol tanımla

### API Endpoint Ekleme
1. `api_client.py`'da yeni method ekle
2. Dashboard'da signal-slot bağlantısı yap
3. UI'da veri görüntüleme ekle

## Lisans
MIT License