"""
Demo Data Generator for MSA Dashboard
Generates realistic military simulation data for testing and demonstration
"""
import random
import json
from datetime import datetime, timedelta
from typing import List, Dict, Any, Tuple
from dataclasses import dataclass
import uuid

from database.models import Unit, Alert, Mission, Equipment, Event, SystemMetric

class DemoDataGenerator:
    """Generates realistic demo data for military operations"""
    
    def __init__(self):
        """Initialize demo data generator"""
        self.unit_names = [
            "Alpha Company", "Bravo Squad", "Charlie Platoon", "Delta Force", "Echo Team",
            "Foxtrot Unit", "Golf Squadron", "Hotel Battalion", "India Regiment", "Juliet Division",
            "Kilo Brigade", "Lima Corps", "Mike Detachment", "November Group", "Oscar Wing"
        ]
        
        self.commanders = [
            "Col. Johnson", "Maj. Smith", "Capt. Williams", "Lt. Brown", "Sgt. Davis",
            "Col. Miller", "Maj. Wilson", "Capt. Moore", "Lt. Taylor", "Sgt. Anderson",
            "Col. Thomas", "Maj. Jackson", "Capt. White", "Lt. Harris", "Sgt. Martin"
        ]
        
        self.mission_types = ["patrol", "reconnaissance", "assault", "defense", "support"]
        self.unit_types = ["infantry", "armor", "air", "naval", "special"]
        self.alert_types = ["threat", "equipment", "personnel", "weather", "intel"]
        self.equipment_types = ["vehicle", "weapon", "communication", "medical", "supply"]
        
        # Türkiye koordinatları (Ankara çevresi)
        self.base_lat = 39.9334
        self.base_lng = 32.8597
        self.operation_radius = 0.5  # degrees (~55km)
        
    def generate_coordinates(self, center_lat: float = None, center_lng: float = None, 
                           radius: float = None) -> Tuple[float, float]:
        """Generate random coordinates within operation area"""
        if center_lat is None:
            center_lat = self.base_lat
        if center_lng is None:
            center_lng = self.base_lng
        if radius is None:
            radius = self.operation_radius
            
        # Generate random offset within radius
        angle = random.uniform(0, 2 * 3.14159)
        distance = random.uniform(0, radius)
        
        lat = center_lat + distance * random.uniform(-1, 1)
        lng = center_lng + distance * random.uniform(-1, 1)
        
        return lat, lng
    
    def generate_unit(self) -> Unit:
        """Generate a single military unit"""
        units = self.generate_units(1)
        return units[0]
    
    def generate_alert(self) -> Alert:
        """Generate a single alert"""
        alerts = self.generate_alerts(1)
        return alerts[0]
    
    def generate_mission(self) -> Mission:
        """Generate a single mission"""
        missions = self.generate_missions(1)
        return missions[0]
    
    def generate_equipment(self) -> Equipment:
        """Generate a single equipment item"""
        equipment = self.generate_equipment_items(1)
        return equipment[0]
    
    def generate_event(self) -> Event:
        """Generate a single event"""
        events = self.generate_events(1)
        return events[0]
    
    def generate_system_metric(self) -> SystemMetric:
        """Generate a single system metric"""
        metrics = self.generate_system_metrics(1)
        return metrics[0]
    
    def generate_units(self, count: int = 20) -> List[Unit]:
        """Generate military units"""
        units = []
        
        for i in range(count):
            unit_id = f"UNIT-{str(uuid.uuid4())[:8].upper()}"
            lat, lng = self.generate_coordinates()
            
            unit = Unit(
                unit_id=unit_id,
                name=random.choice(self.unit_names),
                unit_type=random.choice(self.unit_types),
                status=random.choice(["active", "inactive", "maintenance", "deployed"]),
                location_lat=lat,
                location_lng=lng,
                altitude=random.uniform(100, 2000) if random.random() > 0.7 else None,
                heading=random.uniform(0, 360),
                speed=random.uniform(0, 80) if random.random() > 0.5 else 0,
                fuel_level=random.uniform(20, 100),
                ammunition=random.randint(50, 500),
                personnel_count=random.randint(5, 50),
                commander=random.choice(self.commanders),
                mission_id=None,  # Will be assigned later
                last_contact=datetime.now() - timedelta(minutes=random.randint(1, 120)),
                created_at=datetime.now() - timedelta(days=random.randint(1, 30)),
                updated_at=datetime.now()
            )
            units.append(unit)
            
        return units
    
    def generate_alerts(self, count: int = 15) -> List[Alert]:
        """Generate threat alerts"""
        alerts = []
        
        threat_titles = [
            "Suspicious Activity Detected", "Equipment Malfunction", "Personnel Missing",
            "Weather Warning", "Intelligence Report", "Perimeter Breach", "Communication Loss",
            "Vehicle Breakdown", "Medical Emergency", "Supply Shortage", "Hostile Contact",
            "Radar Contact", "Cyber Threat", "Infrastructure Damage", "Unauthorized Access"
        ]
        
        for i in range(count):
            alert_id = f"ALERT-{str(uuid.uuid4())[:8].upper()}"
            lat, lng = self.generate_coordinates()
            
            alert = Alert(
                alert_id=alert_id,
                title=random.choice(threat_titles),
                description=f"Alert generated at {datetime.now().strftime('%H:%M')} - Requires immediate attention",
                alert_type=random.choice(self.alert_types),
                severity=random.choice(["low", "medium", "high", "critical"]),
                status=random.choice(["active", "resolved", "investigating"]),
                location_lat=lat,
                location_lng=lng,
                radius=random.uniform(100, 5000),  # meters
                source=random.choice(["sensor", "intel", "manual", "automated"]),
                confidence=random.uniform(0.3, 1.0),
                created_at=datetime.now() - timedelta(hours=random.randint(1, 48)),
                updated_at=datetime.now(),
                resolved_at=datetime.now() if random.random() > 0.7 else None,
                assigned_to=random.choice(self.commanders) if random.random() > 0.5 else None
            )
            alerts.append(alert)
            
        return alerts
    
    def generate_missions(self, count: int = 10, units: List[Unit] = None) -> List[Mission]:
        """Generate military missions"""
        missions = []
        
        mission_names = [
            "Operation Thunder", "Mission Falcon", "Task Force Eagle", "Operation Storm",
            "Mission Phoenix", "Operation Lightning", "Task Force Viper", "Mission Hawk",
            "Operation Tornado", "Mission Cobra", "Operation Blizzard", "Task Force Wolf"
        ]
        
        for i in range(count):
            mission_id = f"MISSION-{str(uuid.uuid4())[:8].upper()}"
            lat, lng = self.generate_coordinates()
            
            # Assign random units to mission
            assigned_unit_ids = []
            if units:
                num_units = random.randint(1, min(5, len(units)))
                assigned_units_sample = random.sample(units, num_units)
                assigned_unit_ids = [unit.unit_id for unit in assigned_units_sample]
                
                # Update units with mission_id
                for unit in assigned_units_sample:
                    unit.mission_id = mission_id
            
            objectives = [
                "Secure the area",
                "Gather intelligence",
                "Neutralize threats",
                "Establish communication",
                "Provide support"
            ]
            
            mission = Mission(
                mission_id=mission_id,
                name=random.choice(mission_names),
                description=f"Strategic operation in sector {random.randint(1, 10)}",
                mission_type=random.choice(self.mission_types),
                status=random.choice(["planned", "active", "completed", "cancelled", "paused"]),
                priority=random.choice(["low", "medium", "high", "critical"]),
                start_time=datetime.now() + timedelta(hours=random.randint(-24, 48)),
                end_time=datetime.now() + timedelta(hours=random.randint(48, 168)),
                estimated_duration=random.randint(60, 1440),  # minutes
                commander=random.choice(self.commanders),
                assigned_units=json.dumps(assigned_unit_ids),
                objectives=json.dumps(random.sample(objectives, random.randint(2, 4))),
                location_lat=lat,
                location_lng=lng,
                area_of_operation=json.dumps([
                    [lat + 0.01, lng + 0.01],
                    [lat + 0.01, lng - 0.01],
                    [lat - 0.01, lng - 0.01],
                    [lat - 0.01, lng + 0.01]
                ]),
                created_at=datetime.now() - timedelta(days=random.randint(1, 14)),
                updated_at=datetime.now()
            )
            missions.append(mission)
            
        return missions
    
    def generate_equipment_items(self, count: int = 30, units: List[Unit] = None) -> List[Equipment]:
        """Generate military equipment"""
        equipment_list = []
        
        equipment_names = {
            "vehicle": ["M1A2 Abrams", "HMMWV", "Bradley IFV", "Stryker", "MRAP"],
            "weapon": ["M4 Carbine", "M249 SAW", "M240B", "AT4", "Javelin"],
            "communication": ["AN/PRC-152", "SINCGARS", "Satellite Phone", "Radio Set", "GPS Unit"],
            "medical": ["Field Hospital", "Ambulance", "Medical Kit", "Defibrillator", "Stretcher"],
            "supply": ["Fuel Truck", "Supply Trailer", "Water Purifier", "Generator", "Cargo Container"]
        }
        
        for i in range(count):
            equipment_id = f"EQ-{str(uuid.uuid4())[:8].upper()}"
            eq_type = random.choice(self.equipment_types)
            lat, lng = self.generate_coordinates()
            
            equipment = Equipment(
                equipment_id=equipment_id,
                name=random.choice(equipment_names[eq_type]),
                equipment_type=eq_type,
                status=random.choice(["operational", "maintenance", "damaged", "destroyed"]),
                condition=random.choice(["excellent", "good", "fair", "poor"]),
                location_lat=lat,
                location_lng=lng,
                assigned_unit=random.choice(units).unit_id if units and random.random() > 0.3 else None,
                maintenance_due=datetime.now() + timedelta(days=random.randint(7, 90)),
                last_maintenance=datetime.now() - timedelta(days=random.randint(1, 60)),
                specifications=json.dumps({
                    "weight": f"{random.randint(10, 5000)} kg",
                    "range": f"{random.randint(100, 10000)} km",
                    "capacity": f"{random.randint(1, 100)} units"
                }),
                created_at=datetime.now() - timedelta(days=random.randint(30, 365)),
                updated_at=datetime.now()
            )
            equipment_list.append(equipment)
            
        return equipment_list
    
    def generate_events(self, count: int = 50, units: List[Unit] = None, 
                       alerts: List[Alert] = None) -> List[Event]:
        """Generate system events"""
        events = []
        
        event_types = [
            "unit_movement", "alert_created", "mission_started", "equipment_maintenance",
            "user_login", "system_startup", "communication_established", "threat_detected",
            "mission_completed", "unit_deployed", "alert_resolved", "equipment_repaired"
        ]
        
        for i in range(count):
            event_type = random.choice(event_types)
            category = random.choice(["unit", "alert", "health", "logistics", "system"])
            
            # Generate source_id based on category
            source_id = ""
            if category == "unit" and units:
                source_id = random.choice(units).unit_id
            elif category == "alert" and alerts:
                source_id = random.choice(alerts).alert_id
            else:
                source_id = f"SYS-{random.randint(1000, 9999)}"
            
            lat, lng = self.generate_coordinates() if random.random() > 0.5 else (None, None)
            
            event = Event(
                timestamp=datetime.now() - timedelta(hours=random.randint(1, 168)),
                event_type=event_type,
                category=category,
                source_id=source_id,
                title=f"{event_type.replace('_', ' ').title()}",
                description=f"Automated event generated for {category} operations",
                severity=random.choice(["info", "warning", "error", "critical"]),
                location_lat=lat,
                location_lng=lng,
                metadata=json.dumps({
                    "auto_generated": True,
                    "confidence": random.uniform(0.5, 1.0),
                    "priority": random.choice(["low", "medium", "high"])
                }),
                user_id=f"user_{random.randint(1, 10)}",
                acknowledged=random.random() > 0.6,
                acknowledged_by=random.choice(self.commanders) if random.random() > 0.7 else None,
                acknowledged_at=datetime.now() if random.random() > 0.7 else None
            )
            events.append(event)
            
        return events
    
    def generate_system_metrics(self, count: int = 100) -> List[SystemMetric]:
        """Generate system performance metrics"""
        metrics = []
        
        metric_names = [
            "cpu_usage", "memory_usage", "disk_usage", "network_latency",
            "response_time", "active_users", "database_connections", "error_rate",
            "throughput", "availability", "temperature", "power_consumption"
        ]
        
        for i in range(count):
            metric_name = random.choice(metric_names)
            
            # Generate realistic values based on metric type
            if metric_name in ["cpu_usage", "memory_usage", "disk_usage"]:
                value = random.uniform(10, 95)
                unit = "%"
            elif metric_name == "network_latency":
                value = random.uniform(1, 500)
                unit = "ms"
            elif metric_name == "response_time":
                value = random.uniform(50, 2000)
                unit = "ms"
            elif metric_name in ["active_users", "database_connections"]:
                value = random.randint(1, 100)
                unit = "count"
            elif metric_name == "temperature":
                value = random.uniform(20, 80)
                unit = "°C"
            else:
                value = random.uniform(0, 100)
                unit = "units"
            
            metric = SystemMetric(
                timestamp=datetime.now() - timedelta(minutes=random.randint(1, 1440)),
                metric_name=metric_name,
                metric_value=value,
                unit=unit,
                category=random.choice(["performance", "health", "security"]),
                source=random.choice(["server", "client", "network", "database"])
            )
            metrics.append(metric)
            
        return metrics
    
    def generate_complete_dataset(self) -> Dict[str, List]:
        """Generate a complete dataset with all entities"""
        print("Generating demo dataset...")
        
        # Generate in order to maintain relationships
        units = self.generate_units(25)
        print(f"Generated {len(units)} units")
        
        missions = self.generate_missions(12, units)
        print(f"Generated {len(missions)} missions")
        
        alerts = self.generate_alerts(20)
        print(f"Generated {len(alerts)} alerts")
        
        equipment = self.generate_equipment_items(40, units)
        print(f"Generated {len(equipment)} equipment items")
        
        events = self.generate_events(75, units, alerts)
        print(f"Generated {len(events)} events")
        
        metrics = self.generate_system_metrics(150)
        print(f"Generated {len(metrics)} system metrics")
        
        return {
            "units": units,
            "missions": missions,
            "alerts": alerts,
            "equipment": equipment,
            "events": events,
            "metrics": metrics
        }

# Singleton instance
_demo_generator = None

def get_demo_generator() -> DemoDataGenerator:
    """Get singleton demo data generator instance"""
    global _demo_generator
    if _demo_generator is None:
        _demo_generator = DemoDataGenerator()
    return _demo_generator