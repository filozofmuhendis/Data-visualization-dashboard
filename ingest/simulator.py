"""
MSA Dashboard - Data Simulator
Realistic military data simulation for GPS sensors, biosensors, weather, and logistics
"""

import asyncio
import json
import random
import math
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, asdict

from core.models import (
    Unit, HealthMetrics, LogisticsStatus, WeatherData, ThreatDetection,
    Alert, Mission, RiskLevel, UnitType, AlertSeverity, MissionPhase,
    Position
)
from core.settings import settings


@dataclass
class SimulationScenario:
    """Defines a military simulation scenario"""
    name: str
    duration_minutes: int
    unit_count: int
    threat_probability: float
    weather_severity: float
    mission_complexity: int
    description: str


class MilitaryDataSimulator:
    """Main simulator for military operational data"""
    
    def __init__(self):
        self.units: Dict[str, Dict] = {}
        self.missions: Dict[str, Dict] = {}
        self.weather_stations: List[Dict] = []
        self.simulation_start = datetime.now()
        self.scenario: Optional[SimulationScenario] = None
        
        # Ankara region coordinates for realistic positioning
        self.base_lat = 39.9042
        self.base_lon = 32.6195
        self.operation_radius = 0.1  # ~10km radius
        
        # Initialize simulation data
        self._initialize_units()
        self._initialize_missions()
        self._initialize_weather_stations()
    
    def _initialize_units(self):
        """Initialize military units with realistic data"""
        unit_types = [
            ("infantry", "ALPHA", 8),
            ("armor", "BRAVO", 4),
            ("recon", "CHARLIE", 6),
            ("support", "DELTA", 3),
            ("medical", "ECHO", 2)
        ]
        
        for unit_type, callsign, count in unit_types:
            for i in range(1, count + 1):
                unit_id = f"{callsign}-{i:03d}"
                
                # Random position within operation area
                lat_offset = random.uniform(-self.operation_radius, self.operation_radius)
                lon_offset = random.uniform(-self.operation_radius, self.operation_radius)
                
                self.units[unit_id] = {
                    "unit_id": unit_id,
                    "unit_type": unit_type,
                    "callsign": f"{callsign} {i}",
                    "position": {
                        "latitude": self.base_lat + lat_offset,
                        "longitude": self.base_lon + lon_offset,
                        "altitude": random.uniform(800, 1200)
                    },
                    "heading": random.uniform(0, 360),
                    "speed": 0.0,
                    "status": "active",
                    "risk_level": "green",
                    "last_seen": datetime.now(),
                    
                    # Movement parameters
                    "target_lat": None,
                    "target_lon": None,
                    "movement_speed": self._get_unit_speed(unit_type),
                    "patrol_radius": random.uniform(0.01, 0.03),
                    "patrol_center_lat": self.base_lat + lat_offset,
                    "patrol_center_lon": self.base_lon + lon_offset,
                    
                    # Health baseline
                    "health": {
                        "heart_rate_baseline": random.randint(60, 80),
                        "spo2_baseline": random.randint(95, 99),
                        "stress_baseline": random.randint(10, 30),
                        "fatigue_level": 0.0,
                        "last_health_check": datetime.now()
                    },
                    
                    # Logistics
                    "logistics": {
                        "ammo_percent": random.randint(70, 100),
                        "fuel_percent": random.randint(60, 100),
                        "water_percent": random.randint(80, 100),
                        "medical_supplies": random.randint(85, 100),
                        "consumption_rate": self._get_consumption_rate(unit_type)
                    }
                }
    
    def _initialize_missions(self):
        """Initialize active missions"""
        missions = [
            {
                "mission_id": "OP-GUARDIAN-001",
                "name": "Operation Guardian",
                "phase": "execution",
                "progress": 65.0,
                "priority": "high",
                "start_time": datetime.now() - timedelta(hours=4),
                "estimated_completion": datetime.now() + timedelta(hours=2),
                "assigned_units": ["ALPHA-001", "ALPHA-002", "BRAVO-001"],
                "objectives": [
                    {"id": "OBJ-001", "description": "Secure checkpoint Alpha", "status": "completed"},
                    {"id": "OBJ-002", "description": "Establish overwatch position", "status": "in_progress"},
                    {"id": "OBJ-003", "description": "Conduct area sweep", "status": "pending"}
                ]
            },
            {
                "mission_id": "OP-RECON-002",
                "name": "Reconnaissance Patrol",
                "phase": "planning",
                "progress": 15.0,
                "priority": "medium",
                "start_time": datetime.now() + timedelta(hours=1),
                "estimated_completion": datetime.now() + timedelta(hours=6),
                "assigned_units": ["CHARLIE-001", "CHARLIE-002"],
                "objectives": [
                    {"id": "OBJ-004", "description": "Survey northern sector", "status": "pending"},
                    {"id": "OBJ-005", "description": "Report enemy activity", "status": "pending"}
                ]
            }
        ]
        
        for mission in missions:
            self.missions[mission["mission_id"]] = mission
    
    def _initialize_weather_stations(self):
        """Initialize weather monitoring stations"""
        stations = [
            {"id": "WS-001", "name": "Base Station", "lat": self.base_lat, "lon": self.base_lon},
            {"id": "WS-002", "name": "North Outpost", "lat": self.base_lat + 0.05, "lon": self.base_lon},
            {"id": "WS-003", "name": "East Checkpoint", "lat": self.base_lat, "lon": self.base_lon + 0.05}
        ]
        
        for station in stations:
            station.update({
                "temperature": random.uniform(15, 25),
                "humidity": random.uniform(40, 70),
                "wind_speed": random.uniform(5, 15),
                "wind_direction": random.uniform(0, 360),
                "visibility": random.uniform(8, 15),
                "pressure": random.uniform(1010, 1025)
            })
        
        self.weather_stations = stations
    
    def _get_unit_speed(self, unit_type: str) -> float:
        """Get realistic movement speed for unit type (km/h)"""
        speeds = {
            "infantry": random.uniform(3, 6),
            "armor": random.uniform(15, 35),
            "recon": random.uniform(20, 50),
            "support": random.uniform(10, 25),
            "medical": random.uniform(8, 20)
        }
        return speeds.get(unit_type, 5.0)
    
    def _get_consumption_rate(self, unit_type: str) -> Dict[str, float]:
        """Get resource consumption rates per hour"""
        rates = {
            "infantry": {"ammo": 0.5, "fuel": 0.0, "water": 2.0, "medical": 0.1},
            "armor": {"ammo": 2.0, "fuel": 8.0, "water": 1.5, "medical": 0.1},
            "recon": {"ammo": 1.0, "fuel": 5.0, "water": 2.0, "medical": 0.1},
            "support": {"ammo": 0.2, "fuel": 3.0, "water": 1.0, "medical": 0.5},
            "medical": {"ammo": 0.1, "fuel": 2.0, "water": 1.5, "medical": 2.0}
        }
        return rates.get(unit_type, {"ammo": 0.5, "fuel": 2.0, "water": 1.5, "medical": 0.2})
    
    def set_scenario(self, scenario: SimulationScenario):
        """Set the current simulation scenario"""
        self.scenario = scenario
        print(f"Simulation scenario set: {scenario.name}")
        print(f"Description: {scenario.description}")
    
    def simulate_unit_movement(self, unit_id: str) -> Dict[str, Any]:
        """Simulate realistic unit movement"""
        unit = self.units[unit_id]
        
        # Patrol movement pattern
        center_lat = unit["patrol_center_lat"]
        center_lon = unit["patrol_center_lon"]
        radius = unit["patrol_radius"]
        
        # Calculate new position based on patrol pattern
        time_factor = (datetime.now() - self.simulation_start).total_seconds() / 3600
        angle = (time_factor * 30 + hash(unit_id) % 360) % 360  # 30 degrees per hour
        
        lat_offset = radius * math.cos(math.radians(angle))
        lon_offset = radius * math.sin(math.radians(angle))
        
        new_lat = center_lat + lat_offset
        new_lon = center_lon + lon_offset
        
        # Calculate movement
        old_lat = unit["position"]["latitude"]
        old_lon = unit["position"]["longitude"]
        
        # Calculate distance and speed
        distance = math.sqrt((new_lat - old_lat)**2 + (new_lon - old_lon)**2) * 111000  # meters
        time_diff = 5.0  # 5 second updates
        speed = (distance / time_diff) * 3.6 if time_diff > 0 else 0  # km/h
        
        # Calculate heading
        if distance > 1:  # Only update heading if significant movement
            heading = math.degrees(math.atan2(new_lon - old_lon, new_lat - old_lat))
            unit["heading"] = (heading + 360) % 360
        
        # Update position
        unit["position"]["latitude"] = new_lat
        unit["position"]["longitude"] = new_lon
        unit["speed"] = min(speed, unit["movement_speed"])
        unit["last_seen"] = datetime.now()
        
        return {
            "unit_id": unit_id,
            "position": unit["position"],
            "heading": unit["heading"],
            "speed": unit["speed"],
            "timestamp": unit["last_seen"].isoformat()
        }
    
    def simulate_health_metrics(self, unit_id: str) -> Dict[str, Any]:
        """Simulate realistic health metrics with stress factors"""
        unit = self.units[unit_id]
        health = unit["health"]
        
        # Base values
        hr_base = health["heart_rate_baseline"]
        spo2_base = health["spo2_baseline"]
        stress_base = health["stress_baseline"]
        
        # Stress factors
        mission_stress = 0.0
        if any(unit_id in mission["assigned_units"] for mission in self.missions.values()):
            mission_stress = random.uniform(10, 30)
        
        fatigue_stress = health["fatigue_level"] * 20
        environmental_stress = random.uniform(0, 10)
        
        total_stress = stress_base + mission_stress + fatigue_stress + environmental_stress
        
        # Calculate metrics with stress influence
        heart_rate = hr_base + (total_stress * 0.8) + random.uniform(-5, 5)
        heart_rate = max(50, min(180, heart_rate))
        
        spo2 = spo2_base - (total_stress * 0.1) + random.uniform(-2, 1)
        spo2 = max(85, min(100, spo2))
        
        stress_index = min(100, total_stress + random.uniform(-5, 5))
        
        # Update fatigue
        health["fatigue_level"] = min(1.0, health["fatigue_level"] + 0.001)
        
        # Determine risk level
        risk_level = "green"
        if heart_rate > 120 or spo2 < 92 or stress_index > 70:
            risk_level = "red"
        elif heart_rate > 100 or spo2 < 95 or stress_index > 50:
            risk_level = "amber"
        
        health["last_health_check"] = datetime.now()
        
        return {
            "unit_id": unit_id,
            "timestamp": datetime.now().isoformat(),
            "heart_rate": round(heart_rate),
            "spo2": round(spo2, 1),
            "stress_index": round(stress_index),
            "risk_level": risk_level,
            "fatigue_level": round(health["fatigue_level"], 2)
        }
    
    def simulate_logistics_status(self, unit_id: str) -> Dict[str, Any]:
        """Simulate logistics consumption and resupply"""
        unit = self.units[unit_id]
        logistics = unit["logistics"]
        consumption = logistics["consumption_rate"]
        
        # Time-based consumption (per hour)
        hours_passed = 5.0 / 3600  # 5 seconds in hours
        
        # Consume resources
        logistics["ammo_percent"] = max(0, logistics["ammo_percent"] - consumption["ammo"] * hours_passed)
        logistics["fuel_percent"] = max(0, logistics["fuel_percent"] - consumption["fuel"] * hours_passed)
        logistics["water_percent"] = max(0, logistics["water_percent"] - consumption["water"] * hours_passed)
        logistics["medical_supplies"] = max(0, logistics["medical_supplies"] - consumption["medical"] * hours_passed)
        
        # Random resupply events (low probability)
        if random.random() < 0.001:  # 0.1% chance per update
            logistics["ammo_percent"] = min(100, logistics["ammo_percent"] + random.uniform(20, 50))
            logistics["fuel_percent"] = min(100, logistics["fuel_percent"] + random.uniform(30, 70))
            logistics["water_percent"] = min(100, logistics["water_percent"] + random.uniform(40, 80))
            logistics["medical_supplies"] = min(100, logistics["medical_supplies"] + random.uniform(20, 60))
        
        # Determine risk level
        min_level = min(
            logistics["ammo_percent"],
            logistics["fuel_percent"],
            logistics["water_percent"],
            logistics["medical_supplies"]
        )
        
        risk_level = "green"
        if min_level < 20:
            risk_level = "red"
        elif min_level < 40:
            risk_level = "amber"
        
        return {
            "unit_id": unit_id,
            "timestamp": datetime.now().isoformat(),
            "ammo_percent": round(logistics["ammo_percent"], 1),
            "fuel_percent": round(logistics["fuel_percent"], 1),
            "water_percent": round(logistics["water_percent"], 1),
            "medical_supplies": round(logistics["medical_supplies"], 1),
            "risk_level": risk_level
        }
    
    def simulate_weather_data(self) -> List[Dict[str, Any]]:
        """Simulate weather conditions"""
        weather_data = []
        
        for station in self.weather_stations:
            # Gradual weather changes
            station["temperature"] += random.uniform(-0.5, 0.5)
            station["humidity"] += random.uniform(-2, 2)
            station["wind_speed"] += random.uniform(-1, 1)
            station["wind_direction"] = (station["wind_direction"] + random.uniform(-10, 10)) % 360
            station["visibility"] += random.uniform(-0.5, 0.5)
            station["pressure"] += random.uniform(-0.5, 0.5)
            
            # Keep within realistic bounds
            station["temperature"] = max(-10, min(45, station["temperature"]))
            station["humidity"] = max(20, min(100, station["humidity"]))
            station["wind_speed"] = max(0, min(50, station["wind_speed"]))
            station["visibility"] = max(1, min(20, station["visibility"]))
            station["pressure"] = max(980, min(1040, station["pressure"]))
            
            weather_data.append({
                "station_id": station["id"],
                "station_name": station["name"],
                "latitude": station["lat"],
                "longitude": station["lon"],
                "timestamp": datetime.now().isoformat(),
                "temperature": round(station["temperature"], 1),
                "humidity": round(station["humidity"], 1),
                "wind_speed": round(station["wind_speed"], 1),
                "wind_direction": round(station["wind_direction"]),
                "visibility": round(station["visibility"], 1),
                "pressure": round(station["pressure"], 1)
            })
        
        return weather_data
    
    def generate_threat_detection(self) -> Optional[Dict[str, Any]]:
        """Generate random threat detections"""
        if self.scenario and random.random() < self.scenario.threat_probability / 3600:  # Per second probability
            threat_types = ["hostile_vehicle", "suspicious_activity", "weapon_signature", "drone_detection"]
            threat_type = random.choice(threat_types)
            
            # Random location within operation area
            lat = self.base_lat + random.uniform(-self.operation_radius, self.operation_radius)
            lon = self.base_lon + random.uniform(-self.operation_radius, self.operation_radius)
            
            confidence = random.uniform(0.6, 0.95)
            severity = "high" if confidence > 0.8 else "medium" if confidence > 0.7 else "low"
            
            return {
                "threat_id": f"THR-{datetime.now().strftime('%Y%m%d%H%M%S')}-{random.randint(100, 999)}",
                "threat_type": threat_type,
                "latitude": lat,
                "longitude": lon,
                "confidence": round(confidence, 2),
                "severity": severity,
                "detected_by": random.choice(list(self.units.keys())),
                "timestamp": datetime.now().isoformat(),
                "description": f"Detected {threat_type.replace('_', ' ')} with {confidence:.0%} confidence"
            }
        
        return None
    
    def generate_alert(self, alert_type: str, unit_id: str, message: str, severity: str = "medium") -> Dict[str, Any]:
        """Generate system alert"""
        return {
            "alert_id": f"ALT-{datetime.now().strftime('%Y%m%d%H%M%S')}-{random.randint(100, 999)}",
            "unit_id": unit_id,
            "alert_type": alert_type,
            "severity": severity,
            "message": message,
            "timestamp": datetime.now().isoformat(),
            "acknowledged": False,
            "source": "system"
        }
    
    def get_all_units_data(self) -> List[Dict[str, Any]]:
        """Get current data for all units"""
        units_data = []
        for unit_id in self.units:
            unit_data = {
                **self.units[unit_id],
                "position": self.units[unit_id]["position"],
                "timestamp": datetime.now().isoformat()
            }
            units_data.append(unit_data)
        return units_data
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get overall system status"""
        active_units = len([u for u in self.units.values() if u["status"] == "active"])
        critical_units = len([u for u in self.units.values() if u["risk_level"] == "red"])
        
        return {
            "timestamp": datetime.now().isoformat(),
            "total_units": len(self.units),
            "active_units": active_units,
            "critical_units": critical_units,
            "active_missions": len([m for m in self.missions.values() if m["phase"] in ["execution", "planning"]]),
            "system_health": "critical" if critical_units > 3 else "warning" if critical_units > 0 else "operational"
        }


# Predefined scenarios
SCENARIOS = {
    "training": SimulationScenario(
        name="Training Exercise",
        duration_minutes=120,
        unit_count=15,
        threat_probability=0.1,
        weather_severity=0.3,
        mission_complexity=2,
        description="Routine training exercise with minimal threats"
    ),
    "patrol": SimulationScenario(
        name="Border Patrol",
        duration_minutes=480,
        unit_count=20,
        threat_probability=0.3,
        weather_severity=0.5,
        mission_complexity=3,
        description="Active border patrol with moderate threat level"
    ),
    "combat": SimulationScenario(
        name="Combat Operations",
        duration_minutes=360,
        unit_count=25,
        threat_probability=0.7,
        weather_severity=0.8,
        mission_complexity=5,
        description="High-intensity combat operations with significant threats"
    )
}


# Global simulator instance
simulator = MilitaryDataSimulator()