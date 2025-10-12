#!/usr/bin/env python3
"""
PostgreSQL Health Metrics Data Generator
Web API'nin PostgreSQL veritabanına health metrics örnek verileri ekler
"""

import sys
import os
import random
import requests
from datetime import datetime, timedelta
from typing import List, Dict

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Web API endpoint
API_BASE_URL = "http://localhost:8000"
AUTH_TOKEN = "demo_token"

def get_units() -> List[str]:
    """Web API'den unit listesini al"""
    try:
        headers = {"Authorization": f"Bearer {AUTH_TOKEN}"}
        response = requests.get(f"{API_BASE_URL}/api/units", headers=headers)
        response.raise_for_status()
        
        units_data = response.json()
        unit_ids = [unit['unit_id'] for unit in units_data]
        
        print(f"📊 {len(unit_ids)} adet unit bulundu")
        return unit_ids
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Unit'ler alınamadı: {e}")
        return []

def generate_health_metric(unit_id: str, timestamp: datetime) -> Dict:
    """Gerçekçi health metric verisi oluştur"""
    # Stress seviyesine göre diğer değerleri belirle
    stress_index = random.uniform(0, 100)
    
    if stress_index < 30:  # Düşük stress - normal değerler
        heart_rate = random.randint(60, 90)
        spo2 = random.uniform(96, 100)
        body_temp = random.uniform(36.0, 37.2)
        risk_level = "green"
    elif stress_index < 70:  # Orta stress - yüksek değerler
        heart_rate = random.randint(85, 130)
        spo2 = random.uniform(92, 97)
        body_temp = random.uniform(36.8, 38.0)
        risk_level = "amber"
    else:  # Yüksek stress - kritik değerler
        heart_rate = random.randint(120, 180)
        spo2 = random.uniform(88, 95)
        body_temp = random.uniform(37.5, 39.0)
        risk_level = "red"
    
    return {
        "unit_id": unit_id,
        "heart_rate": heart_rate,
        "spo2": round(spo2, 1),
        "stress_index": round(stress_index, 1),
        "body_temperature": round(body_temp, 1),
        "risk_level": risk_level,
        "timestamp": timestamp.isoformat() + "Z"
    }

def add_health_metric(metric: Dict) -> bool:
    """Web API'ye health metric ekle"""
    try:
        headers = {
            "Authorization": f"Bearer {AUTH_TOKEN}",
            "Content-Type": "application/json"
        }
        
        response = requests.post(
            f"{API_BASE_URL}/api/health-metrics",
            json=metric,
            headers=headers
        )
        response.raise_for_status()
        return True
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Health metric eklenemedi: {e}")
        return False

def add_health_metrics_data():
    """Health metrics verilerini PostgreSQL'e ekle"""
    units = get_units()
    
    if not units:
        print("❌ Hiç unit bulunamadı. Web API çalışıyor mu?")
        return
    
    # Sadece ilk 5 unit için test verisi ekle (hızlı test için)
    test_units = units[:5]
    
    # Son 24 saat için her unit'e health metrics ekle
    now = datetime.utcnow()
    total_records = 0
    success_count = 0
    
    print(f"📊 {len(test_units)} unit için health metrics verileri oluşturuluyor...")
    
    for unit_id in test_units:
        # Her unit için sadece 5 kayıt oluştur (hızlı test için)
        record_count = 5
        
        for i in range(record_count):
            # Rastgele zaman (son 24 saat içinde)
            hours_ago = random.uniform(0, 24)
            timestamp = now - timedelta(hours=hours_ago)
            
            metric = generate_health_metric(unit_id, timestamp)
            
            if add_health_metric(metric):
                success_count += 1
                print(f"  ✓ {unit_id}: {metric['risk_level']} risk")
            
            total_records += 1
    
    print(f"✅ {success_count}/{total_records} health metrics kaydı eklendi")
    
    # Test endpoint'i
    try:
        headers = {"Authorization": f"Bearer {AUTH_TOKEN}"}
        response = requests.get(f"{API_BASE_URL}/api/health-metrics", headers=headers)
        response.raise_for_status()
        
        metrics_data = response.json()
        print(f"📈 Toplam health metrics: {len(metrics_data)}")
        
        # Risk seviyesi dağılımı
        risk_summary = {}
        for metric in metrics_data:
            risk = metric.get('risk_level', 'unknown')
            risk_summary[risk] = risk_summary.get(risk, 0) + 1
        
        print("📊 Risk seviyesi dağılımı:")
        for risk, count in risk_summary.items():
            print(f"   - {risk}: {count}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Health metrics test edilemedi: {e}")

def main():
    """Ana fonksiyon"""
    print("🏥 PostgreSQL Health Metrics Veri Oluşturucu")
    print("=" * 50)
    
    try:
        # Health metrics verilerini ekle
        add_health_metrics_data()
        
        print("\n🎉 Health metrics verileri başarıyla eklendi!")
        print("💡 Artık /api/health-metrics endpoint'i veri döndürecek")
        
    except Exception as e:
        print(f"❌ Hata oluştu: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()