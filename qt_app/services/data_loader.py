"""
Data Loader Service
Veritabanına demo verilerini yüklemek için kullanılan servis
"""

import logging
from typing import List, Dict, Any
from datetime import datetime, timedelta
import random

from ..database.database_manager import get_database_manager
from .demo_data_generator import DemoDataGenerator
from ..database.models import Unit, Alert, Mission, Equipment, Event, SystemMetric


class DataLoader:
    """Demo verilerini veritabanına yükleyen servis"""
    
    def __init__(self):
        self.db_manager = get_database_manager()
        self.data_generator = DemoDataGenerator()
        self.logger = logging.getLogger(__name__)
        
    def clear_all_data(self):
        """Tüm demo verilerini temizle"""
        try:
            with self.db_manager.get_connection() as conn:
                cursor = conn.cursor()
                
                # Tabloları temizle
                tables = ['units', 'alerts', 'missions', 'equipment', 'events', 'system_metrics']
                for table in tables:
                    cursor.execute(f"DELETE FROM {table}")
                    self.logger.info(f"Cleared {table} table")
                
                conn.commit()
                self.logger.info("All demo data cleared successfully")
                
        except Exception as e:
            self.logger.error(f"Failed to clear data: {e}")
            raise
    
    def load_units(self, count: int = 50) -> List[int]:
        """Askeri birlikleri yükle"""
        unit_ids = []
        try:
            self.logger.info(f"Loading {count} units...")
            
            for i in range(count):
                unit = self.data_generator.generate_unit()
                unit_id = self.db_manager.add_unit(unit)
                unit_ids.append(unit_id)
                
                if (i + 1) % 10 == 0:
                    self.logger.info(f"Loaded {i + 1}/{count} units")
            
            self.logger.info(f"Successfully loaded {count} units")
            return unit_ids
            
        except Exception as e:
            self.logger.error(f"Failed to load units: {e}")
            raise
    
    def load_alerts(self, count: int = 30) -> List[int]:
        """Uyarıları yükle"""
        alert_ids = []
        try:
            self.logger.info(f"Loading {count} alerts...")
            
            for i in range(count):
                alert = self.data_generator.generate_alert()
                alert_id = self.db_manager.add_alert(alert)
                alert_ids.append(alert_id)
                
                if (i + 1) % 10 == 0:
                    self.logger.info(f"Loaded {i + 1}/{count} alerts")
            
            self.logger.info(f"Successfully loaded {count} alerts")
            return alert_ids
            
        except Exception as e:
            self.logger.error(f"Failed to load alerts: {e}")
            raise
    
    def load_missions(self, count: int = 20) -> List[int]:
        """Görevleri yükle"""
        mission_ids = []
        try:
            self.logger.info(f"Loading {count} missions...")
            
            for i in range(count):
                mission = self.data_generator.generate_mission()
                mission_id = self.db_manager.add_mission(mission)
                mission_ids.append(mission_id)
                
                if (i + 1) % 5 == 0:
                    self.logger.info(f"Loaded {i + 1}/{count} missions")
            
            self.logger.info(f"Successfully loaded {count} missions")
            return mission_ids
            
        except Exception as e:
            self.logger.error(f"Failed to load missions: {e}")
            raise
    
    def load_equipment(self, count: int = 100) -> List[int]:
        """Ekipmanları yükle"""
        equipment_ids = []
        try:
            self.logger.info(f"Loading {count} equipment items...")
            
            for i in range(count):
                equipment = self.data_generator.generate_equipment()
                equipment_id = self.db_manager.add_equipment(equipment)
                equipment_ids.append(equipment_id)
                
                if (i + 1) % 20 == 0:
                    self.logger.info(f"Loaded {i + 1}/{count} equipment items")
            
            self.logger.info(f"Successfully loaded {count} equipment items")
            return equipment_ids
            
        except Exception as e:
            self.logger.error(f"Failed to load equipment: {e}")
            raise
    
    def load_events(self, count: int = 200) -> List[int]:
        """Olayları yükle"""
        event_ids = []
        try:
            self.logger.info(f"Loading {count} events...")
            
            for i in range(count):
                event = self.data_generator.generate_event()
                event_id = self.db_manager.add_event(event)
                event_ids.append(event_id)
                
                if (i + 1) % 50 == 0:
                    self.logger.info(f"Loaded {i + 1}/{count} events")
            
            self.logger.info(f"Successfully loaded {count} events")
            return event_ids
            
        except Exception as e:
            self.logger.error(f"Failed to load events: {e}")
            raise
    
    def load_system_metrics(self, count: int = 500) -> List[int]:
        """Sistem metriklerini yükle"""
        metric_ids = []
        try:
            self.logger.info(f"Loading {count} system metrics...")
            
            for i in range(count):
                metric = self.data_generator.generate_system_metric()
                metric_id = self.db_manager.add_metric(metric)
                metric_ids.append(metric_id)
                
                if (i + 1) % 100 == 0:
                    self.logger.info(f"Loaded {i + 1}/{count} metrics")
            
            self.logger.info(f"Successfully loaded {count} system metrics")
            return metric_ids
            
        except Exception as e:
            self.logger.error(f"Failed to load system metrics: {e}")
            raise
    
    def load_scenario_data(self, scenario_name: str = "default") -> Dict[str, List[int]]:
        """Belirli bir senaryo için veri yükle"""
        scenarios = {
            "default": {
                "units": 50,
                "alerts": 30,
                "missions": 20,
                "equipment": 100,
                "events": 200,
                "metrics": 500
            },
            "small": {
                "units": 20,
                "alerts": 15,
                "missions": 10,
                "equipment": 50,
                "events": 100,
                "metrics": 200
            },
            "large": {
                "units": 100,
                "alerts": 60,
                "missions": 40,
                "equipment": 200,
                "events": 500,
                "metrics": 1000
            },
            "crisis": {
                "units": 75,
                "alerts": 50,
                "missions": 30,
                "equipment": 150,
                "events": 300,
                "metrics": 750
            }
        }
        
        if scenario_name not in scenarios:
            scenario_name = "default"
            
        scenario = scenarios[scenario_name]
        
        self.logger.info(f"Loading scenario: {scenario_name}")
        
        results = {}
        
        # Verileri sırayla yükle
        results["units"] = self.load_units(scenario["units"])
        results["alerts"] = self.load_alerts(scenario["alerts"])
        results["missions"] = self.load_missions(scenario["missions"])
        results["equipment"] = self.load_equipment(scenario["equipment"])
        results["events"] = self.load_events(scenario["events"])
        results["metrics"] = self.load_system_metrics(scenario["metrics"])
        
        self.logger.info(f"Scenario '{scenario_name}' loaded successfully")
        return results
    
    def get_data_summary(self) -> Dict[str, int]:
        """Veritabanındaki veri özetini getir"""
        try:
            with self.db_manager.get_connection() as conn:
                cursor = conn.cursor()
                
                summary = {}
                tables = ['units', 'alerts', 'missions', 'equipment', 'events', 'system_metrics']
                
                for table in tables:
                    cursor.execute(f"SELECT COUNT(*) FROM {table}")
                    count = cursor.fetchone()[0]
                    summary[table] = count
                
                return summary
                
        except Exception as e:
            self.logger.error(f"Failed to get data summary: {e}")
            return {}
    
    def create_realistic_scenario(self) -> Dict[str, Any]:
        """Gerçekçi bir askeri senaryo oluştur"""
        try:
            self.logger.info("Creating realistic military scenario...")
            
            # Önce mevcut verileri temizle
            self.clear_all_data()
            
            # Ana üs ve birimler
            base_units = []
            for i in range(5):
                unit = self.data_generator.generate_unit()
                unit.unit_type = "Base"
                unit.status = "Active"
                unit.personnel_count = random.randint(100, 500)
                base_units.append(unit)
            
            # Patrol birimleri
            patrol_units = []
            for i in range(15):
                unit = self.data_generator.generate_unit()
                unit.unit_type = "Patrol"
                unit.status = random.choice(["Active", "On Mission", "Standby"])
                unit.personnel_count = random.randint(4, 12)
                patrol_units.append(unit)
            
            # Araç birimleri
            vehicle_units = []
            for i in range(20):
                unit = self.data_generator.generate_unit()
                unit.unit_type = random.choice(["Tank", "APC", "Helicopter", "Drone"])
                unit.status = random.choice(["Active", "Maintenance", "On Mission"])
                unit.personnel_count = random.randint(1, 8)
                vehicle_units.append(unit)
            
            # Tüm birimleri yükle
            all_units = base_units + patrol_units + vehicle_units
            unit_ids = []
            for unit in all_units:
                unit_id = self.db_manager.add_unit(unit)
                unit_ids.append(unit_id)
            
            # Kritik uyarılar oluştur
            critical_alerts = []
            for i in range(10):
                alert = self.data_generator.generate_alert()
                alert.severity = "Critical"
                alert.status = "Active"
                alert.alert_type = random.choice(["Enemy Contact", "Security Breach", "Equipment Failure"])
                critical_alerts.append(alert)
            
            # Normal uyarılar
            normal_alerts = []
            for i in range(20):
                alert = self.data_generator.generate_alert()
                alert.severity = random.choice(["Medium", "Low"])
                alert.status = random.choice(["Active", "Investigating", "Resolved"])
                normal_alerts.append(alert)
            
            # Uyarıları yükle
            all_alerts = critical_alerts + normal_alerts
            alert_ids = []
            for alert in all_alerts:
                alert_id = self.db_manager.add_alert(alert)
                alert_ids.append(alert_id)
            
            # Aktif görevler
            active_missions = []
            for i in range(8):
                mission = self.data_generator.generate_mission()
                mission.status = "Active"
                mission.priority = random.choice(["High", "Critical"])
                mission.start_time = datetime.now() - timedelta(hours=random.randint(1, 48))
                active_missions.append(mission)
            
            # Planlanan görevler
            planned_missions = []
            for i in range(12):
                mission = self.data_generator.generate_mission()
                mission.status = "Planned"
                mission.priority = random.choice(["Medium", "Low"])
                mission.start_time = datetime.now() + timedelta(hours=random.randint(1, 168))
                planned_missions.append(mission)
            
            # Görevleri yükle
            all_missions = active_missions + planned_missions
            mission_ids = []
            for mission in all_missions:
                mission_id = self.db_manager.add_mission(mission)
                mission_ids.append(mission_id)
            
            # Ekipmanları yükle
            equipment_ids = self.load_equipment(80)
            
            # Son 24 saatin olaylarını yükle
            recent_events = []
            for i in range(150):
                event = self.data_generator.generate_event()
                event.timestamp = datetime.now() - timedelta(hours=random.randint(0, 24))
                recent_events.append(event)
            
            event_ids = []
            for event in recent_events:
                event_id = self.db_manager.add_event(event)
                event_ids.append(event_id)
            
            # Sistem metriklerini yükle
            metric_ids = self.load_system_metrics(300)
            
            scenario_summary = {
                "scenario_name": "Realistic Military Operations",
                "created_at": datetime.now().isoformat(),
                "data_counts": {
                    "units": len(unit_ids),
                    "alerts": len(alert_ids),
                    "missions": len(mission_ids),
                    "equipment": len(equipment_ids),
                    "events": len(event_ids),
                    "metrics": len(metric_ids)
                },
                "unit_breakdown": {
                    "bases": len(base_units),
                    "patrols": len(patrol_units),
                    "vehicles": len(vehicle_units)
                },
                "alert_breakdown": {
                    "critical": len(critical_alerts),
                    "normal": len(normal_alerts)
                },
                "mission_breakdown": {
                    "active": len(active_missions),
                    "planned": len(planned_missions)
                }
            }
            
            self.logger.info("Realistic scenario created successfully")
            return scenario_summary
            
        except Exception as e:
            self.logger.error(f"Failed to create realistic scenario: {e}")
            raise


# Singleton instance
_data_loader = None

def get_data_loader() -> DataLoader:
    """Get singleton data loader instance"""
    global _data_loader
    if _data_loader is None:
        _data_loader = DataLoader()
    return _data_loader