#!/usr/bin/env python3
"""
Health Metrics Data Generator
PyQt5 database'ine health metrics örnek verileri ekler
"""

import sys
import os
import sqlite3
import random
from datetime import datetime, timedelta

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database.database_manager import get_database_manager


def create_health_metrics_table():
    """Health metrics tablosunu oluştur"""
    db_manager = get_database_manager()
    
    with db_manager.get_connection() as connection:
        cursor = connection.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS health_metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                unit_id TEXT NOT NULL,
                heart_rate INTEGER,
                spo2 REAL,
                stress_index REAL,
                body_temperature REAL,
                risk_level TEXT DEFAULT 'green',
                timestamp TEXT NOT NULL,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        connection.commit()
    
    print("✅ Health metrics tablosu oluşturuldu/kontrol edildi")


def get_existing_units():
    """Mevcut unit'leri al"""
    db_manager = get_database_manager()
    
    with db_manager.get_connection() as connection:
        cursor = connection.cursor()
        cursor.execute("SELECT unit_id FROM units")
        units = [row[0] for row in cursor.fetchall()]
    
    print(f"📊 {len(units)} adet unit bulundu")
    return units


def generate_health_metric(unit_id: str, timestamp: datetime):
    """Bir unit için health metric verisi oluştur"""
    # Gerçekçi sağlık verileri
    base_heart_rate = random.randint(60, 100)
    base_spo2 = random.uniform(95, 100)
    base_temp = random.uniform(36.0, 37.5)
    
    # Stres durumuna göre değerleri ayarla
    stress_level = random.uniform(0, 100)
    
    if stress_level > 80:  # Yüksek stres
        heart_rate = base_heart_rate + random.randint(20, 40)
        spo2 = base_spo2 - random.uniform(2, 5)
        body_temp = base_temp + random.uniform(0.5, 1.5)
        risk_level = "red"
    elif stress_level > 50:  # Orta stres
        heart_rate = base_heart_rate + random.randint(10, 25)
        spo2 = base_spo2 - random.uniform(1, 3)
        body_temp = base_temp + random.uniform(0.2, 0.8)
        risk_level = "amber"
    else:  # Normal
        heart_rate = base_heart_rate + random.randint(-5, 15)
        spo2 = base_spo2 - random.uniform(0, 2)
        body_temp = base_temp + random.uniform(-0.3, 0.5)
        risk_level = "green"
    
    # Sınırları kontrol et
    heart_rate = max(40, min(200, heart_rate))
    spo2 = max(85, min(100, spo2))
    body_temp = max(35.0, min(42.0, body_temp))
    stress_level = max(0, min(100, stress_level))
    
    return {
        'unit_id': unit_id,
        'heart_rate': int(heart_rate),
        'spo2': round(spo2, 1),
        'stress_index': round(stress_level, 1),
        'body_temperature': round(body_temp, 1),
        'risk_level': risk_level,
        'timestamp': timestamp.isoformat()
    }


def add_health_metrics_data():
    """Health metrics verilerini ekle"""
    units = get_existing_units()
    
    if not units:
        print("❌ Hiç unit bulunamadı. Önce demo_setup.py çalıştırın.")
        return
    
    db_manager = get_database_manager()
    
    # Son 24 saat için her unit'e health metrics ekle
    now = datetime.now()
    total_records = 0
    
    print("📊 Health metrics verileri oluşturuluyor...")
    
    with db_manager.get_connection() as connection:
        cursor = connection.cursor()
        
        for unit_id in units:
            # Her unit için son 24 saatte 10-20 kayıt oluştur
            record_count = random.randint(10, 20)
            
            for i in range(record_count):
                # Rastgele zaman (son 24 saat içinde)
                hours_ago = random.uniform(0, 24)
                timestamp = now - timedelta(hours=hours_ago)
                
                metric = generate_health_metric(unit_id, timestamp)
                
                cursor.execute('''
                    INSERT INTO health_metrics 
                    (unit_id, heart_rate, spo2, stress_index, body_temperature, risk_level, timestamp)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (
                    metric['unit_id'],
                    metric['heart_rate'],
                    metric['spo2'],
                    metric['stress_index'],
                    metric['body_temperature'],
                    metric['risk_level'],
                    metric['timestamp']
                ))
                
                total_records += 1
        
        connection.commit()
    
    print(f"✅ {total_records} adet health metrics kaydı eklendi")
    
    # Özet bilgi
    with db_manager.get_connection() as connection:
        cursor = connection.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM health_metrics")
        total_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT risk_level, COUNT(*) FROM health_metrics GROUP BY risk_level")
        risk_summary = dict(cursor.fetchall())
    
    print(f"📈 Toplam health metrics: {total_count}")
    print("📊 Risk seviyesi dağılımı:")
    for risk, count in risk_summary.items():
        print(f"   - {risk}: {count}")


def main():
    """Ana fonksiyon"""
    print("🏥 Health Metrics Veri Oluşturucu")
    print("=" * 50)
    
    try:
        # 1. Tabloyu oluştur
        create_health_metrics_table()
        
        # 2. Health metrics verilerini ekle
        add_health_metrics_data()
        
        print("\n🎉 Health metrics verileri başarıyla eklendi!")
        print("💡 Artık /api/health-metrics endpoint'i veri döndürecek")
        
    except Exception as e:
        print(f"❌ Hata oluştu: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()