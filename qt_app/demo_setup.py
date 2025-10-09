#!/usr/bin/env python3
"""
Demo Setup Script
Demo sistemini kurmak ve test etmek için kullanılan ana script
"""

import sys
import os
import logging
import argparse
from datetime import datetime

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from services.data_loader import get_data_loader
from database.database_manager import get_database_manager


def setup_logging():
    """Logging sistemini kur"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('demo_setup.log')
        ]
    )


def initialize_database():
    """Veritabanını başlat"""
    print("🔧 Veritabanı başlatılıyor...")
    db_manager = get_database_manager()
    db_manager.init_database()
    print("✅ Veritabanı başarıyla başlatıldı")


def clear_data():
    """Tüm demo verilerini temizle"""
    print("🧹 Mevcut demo verileri temizleniyor...")
    data_loader = get_data_loader()
    data_loader.clear_all_data()
    print("✅ Demo verileri temizlendi")


def load_scenario(scenario_name: str):
    """Belirli bir senaryo yükle"""
    print(f"📊 '{scenario_name}' senaryosu yükleniyor...")
    data_loader = get_data_loader()
    
    if scenario_name == "realistic":
        results = data_loader.create_realistic_scenario()
        print("✅ Gerçekçi askeri senaryo oluşturuldu")
        print(f"📈 Veri özeti:")
        for key, value in results["data_counts"].items():
            print(f"   - {key}: {value}")
    else:
        results = data_loader.load_scenario_data(scenario_name)
        print(f"✅ '{scenario_name}' senaryosu yüklendi")
        print(f"📈 Yüklenen veriler:")
        for key, value in results.items():
            print(f"   - {key}: {len(value)} adet")


def show_data_summary():
    """Veritabanındaki veri özetini göster"""
    print("📊 Veritabanı veri özeti:")
    data_loader = get_data_loader()
    summary = data_loader.get_data_summary()
    
    total_records = sum(summary.values())
    print(f"   Toplam kayıt: {total_records}")
    print("   Tablo detayları:")
    
    for table, count in summary.items():
        print(f"   - {table}: {count} kayıt")


def test_database_operations():
    """Veritabanı işlemlerini test et"""
    print("🧪 Veritabanı işlemleri test ediliyor...")
    
    try:
        db_manager = get_database_manager()
        data_loader = get_data_loader()
        
        # Test verisi oluştur
        print("   Test verisi oluşturuluyor...")
        unit = data_loader.data_generator.generate_unit()
        alert = data_loader.data_generator.generate_alert()
        mission = data_loader.data_generator.generate_mission()
        
        # Veritabanına ekle
        unit_id = db_manager.add_unit(unit)
        alert_id = db_manager.add_alert(alert)
        mission_id = db_manager.add_mission(mission)
        
        print(f"   ✅ Test verileri eklendi (Unit: {unit_id}, Alert: {alert_id}, Mission: {mission_id})")
        
        # Verileri geri oku
        units = db_manager.get_all_units()
        alerts = db_manager.get_all_alerts()
        
        print(f"   ✅ Veriler başarıyla okundu ({len(units)} unit, {len(alerts)} alert)")
        
        print("✅ Veritabanı işlemleri test başarılı")
        
    except Exception as e:
        print(f"❌ Veritabanı test hatası: {e}")
        raise


def main():
    """Ana fonksiyon"""
    parser = argparse.ArgumentParser(description="Demo Sistem Kurulum Aracı")
    parser.add_argument("--action", choices=["init", "clear", "load", "summary", "test", "full-setup"], 
                       default="full-setup", help="Yapılacak işlem")
    parser.add_argument("--scenario", choices=["default", "small", "large", "crisis", "realistic"], 
                       default="realistic", help="Yüklenecek senaryo")
    parser.add_argument("--verbose", "-v", action="store_true", help="Detaylı çıktı")
    
    args = parser.parse_args()
    
    # Logging kurulumu
    setup_logging()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    print("🚀 Demo Sistem Kurulum Aracı")
    print("=" * 50)
    print(f"Başlangıç zamanı: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    try:
        if args.action == "init":
            initialize_database()
            
        elif args.action == "clear":
            clear_data()
            
        elif args.action == "load":
            load_scenario(args.scenario)
            
        elif args.action == "summary":
            show_data_summary()
            
        elif args.action == "test":
            initialize_database()
            test_database_operations()
            
        elif args.action == "full-setup":
            print("🔄 Tam kurulum başlatılıyor...")
            print()
            
            # 1. Veritabanını başlat
            initialize_database()
            print()
            
            # 2. Mevcut verileri temizle
            clear_data()
            print()
            
            # 3. Test işlemlerini çalıştır
            test_database_operations()
            print()
            
            # 4. Senaryo yükle
            load_scenario(args.scenario)
            print()
            
            # 5. Özet göster
            show_data_summary()
            print()
            
            print("🎉 Demo sistem kurulumu tamamlandı!")
            print("💡 Artık uygulamayı çalıştırabilirsiniz: python main.py")
    
    except Exception as e:
        print(f"❌ Hata oluştu: {e}")
        logging.error(f"Setup failed: {e}", exc_info=True)
        sys.exit(1)
    
    print()
    print(f"Bitiş zamanı: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 50)


if __name__ == "__main__":
    main()