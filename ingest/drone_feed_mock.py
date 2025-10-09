"""
MSA Dashboard - Drone Feed Mock
Simulates drone surveillance data and threat detection for military operations
"""

import asyncio
import json
import random
import math
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

from core.models import ThreatDetection, AlertSeverity, RiskLevel
from core.settings import settings


class DroneType(Enum):
    """Types of military drones"""
    SURVEILLANCE = "surveillance"
    COMBAT = "combat"
    RECONNAISSANCE = "reconnaissance"
    LOGISTICS = "logistics"


class ThreatType(Enum):
    """Types of threats that can be detected"""
    HOSTILE_VEHICLE = "hostile_vehicle"
    SUSPICIOUS_ACTIVITY = "suspicious_activity"
    WEAPON_SIGNATURE = "weapon_signature"
    DRONE_DETECTION = "drone_detection"
    PERSONNEL_MOVEMENT = "personnel_movement"
    IMPROVISED_EXPLOSIVE = "improvised_explosive"
    SNIPER_POSITION = "sniper_position"
    COMMUNICATION_INTERCEPT = "communication_intercept"


@dataclass
class DroneUnit:
    """Represents a military drone unit"""
    drone_id: str
    drone_type: DroneType
    callsign: str
    latitude: float
    longitude: float
    altitude: float
    heading: float
    speed: float
    fuel_percent: float
    status: str
    mission_area: Tuple[float, float, float, float]  # lat_min, lat_max, lon_min, lon_max
    sensor_range: float  # km
    last_update: datetime


class DroneFeedSimulator:
    """Simulates realistic drone surveillance and threat detection"""
    
    def __init__(self):
        self.drones: Dict[str, DroneUnit] = {}
        self.active_threats: Dict[str, Dict] = {}
        self.detection_history: List[Dict] = []
        
        # Ankara region for operations
        self.base_lat = 39.9042
        self.base_lon = 32.6195
        self.operation_radius = 0.2  # ~20km radius
        
        # Initialize drone fleet
        self._initialize_drone_fleet()
        
        # Threat detection parameters
        self.threat_probabilities = {
            ThreatType.HOSTILE_VEHICLE: 0.02,
            ThreatType.SUSPICIOUS_ACTIVITY: 0.05,
            ThreatType.WEAPON_SIGNATURE: 0.01,
            ThreatType.DRONE_DETECTION: 0.008,
            ThreatType.PERSONNEL_MOVEMENT: 0.08,
            ThreatType.IMPROVISED_EXPLOSIVE: 0.005,
            ThreatType.SNIPER_POSITION: 0.003,
            ThreatType.COMMUNICATION_INTERCEPT: 0.015
        }
    
    def _initialize_drone_fleet(self):
        """Initialize military drone fleet"""
        drone_configs = [
            {
                "drone_id": "UAV-HAWK-001",
                "drone_type": DroneType.SURVEILLANCE,
                "callsign": "HAWK-1",
                "altitude": 3000,
                "sensor_range": 15.0
            },
            {
                "drone_id": "UAV-HAWK-002", 
                "drone_type": DroneType.SURVEILLANCE,
                "callsign": "HAWK-2",
                "altitude": 2800,
                "sensor_range": 15.0
            },
            {
                "drone_id": "UAV-EAGLE-001",
                "drone_type": DroneType.RECONNAISSANCE,
                "callsign": "EAGLE-1",
                "altitude": 4500,
                "sensor_range": 25.0
            },
            {
                "drone_id": "UAV-FALCON-001",
                "drone_type": DroneType.COMBAT,
                "callsign": "FALCON-1",
                "altitude": 2000,
                "sensor_range": 10.0
            },
            {
                "drone_id": "UAV-RAVEN-001",
                "drone_type": DroneType.LOGISTICS,
                "callsign": "RAVEN-1",
                "altitude": 1500,
                "sensor_range": 8.0
            }
        ]
        
        for config in drone_configs:
            # Random starting position within operation area
            lat_offset = random.uniform(-self.operation_radius, self.operation_radius)
            lon_offset = random.uniform(-self.operation_radius, self.operation_radius)
            
            # Define mission area for each drone
            area_size = 0.05  # 5km area
            mission_area = (
                self.base_lat + lat_offset - area_size,
                self.base_lat + lat_offset + area_size,
                self.base_lon + lon_offset - area_size,
                self.base_lon + lon_offset + area_size
            )
            
            drone = DroneUnit(
                drone_id=config["drone_id"],
                drone_type=config["drone_type"],
                callsign=config["callsign"],
                latitude=self.base_lat + lat_offset,
                longitude=self.base_lon + lon_offset,
                altitude=config["altitude"],
                heading=random.uniform(0, 360),
                speed=random.uniform(80, 150),  # km/h
                fuel_percent=random.uniform(70, 100),
                status="active",
                mission_area=mission_area,
                sensor_range=config["sensor_range"],
                last_update=datetime.now()
            )
            
            self.drones[drone.drone_id] = drone
    
    def update_drone_positions(self):
        """Update drone positions based on patrol patterns"""
        for drone in self.drones.values():
            if drone.status != "active":
                continue
            
            # Calculate new position based on patrol pattern
            time_factor = (datetime.now() - drone.last_update).total_seconds() / 3600
            
            # Different patrol patterns for different drone types
            if drone.drone_type == DroneType.SURVEILLANCE:
                # Figure-8 pattern
                t = (datetime.now().timestamp() / 1800) % (2 * math.pi)  # 30-minute cycle
                center_lat = (drone.mission_area[0] + drone.mission_area[1]) / 2
                center_lon = (drone.mission_area[2] + drone.mission_area[3]) / 2
                
                lat_range = (drone.mission_area[1] - drone.mission_area[0]) / 4
                lon_range = (drone.mission_area[3] - drone.mission_area[2]) / 4
                
                drone.latitude = center_lat + lat_range * math.sin(t)
                drone.longitude = center_lon + lon_range * math.sin(2 * t)
                
            elif drone.drone_type == DroneType.RECONNAISSANCE:
                # Linear sweep pattern
                t = (datetime.now().timestamp() / 3600) % 2  # 2-hour cycle
                if t < 1:
                    # West to East
                    progress = t
                    drone.latitude = (drone.mission_area[0] + drone.mission_area[1]) / 2
                    drone.longitude = drone.mission_area[2] + progress * (drone.mission_area[3] - drone.mission_area[2])
                else:
                    # East to West
                    progress = 2 - t
                    drone.latitude = (drone.mission_area[0] + drone.mission_area[1]) / 2
                    drone.longitude = drone.mission_area[2] + progress * (drone.mission_area[3] - drone.mission_area[2])
            
            else:
                # Circular patrol
                t = (datetime.now().timestamp() / 2400) % (2 * math.pi)  # 40-minute cycle
                center_lat = (drone.mission_area[0] + drone.mission_area[1]) / 2
                center_lon = (drone.mission_area[2] + drone.mission_area[3]) / 2
                radius = min(
                    (drone.mission_area[1] - drone.mission_area[0]) / 3,
                    (drone.mission_area[3] - drone.mission_area[2]) / 3
                )
                
                drone.latitude = center_lat + radius * math.cos(t)
                drone.longitude = center_lon + radius * math.sin(t)
            
            # Update heading based on movement
            # Calculate heading from previous position (simplified)
            drone.heading = (drone.heading + random.uniform(-10, 10)) % 360
            
            # Update fuel consumption
            fuel_consumption = 0.5 + (drone.speed / 200) * 0.5  # %/hour
            drone.fuel_percent = max(0, drone.fuel_percent - fuel_consumption / 720)  # Per 5-second update
            
            # Check if drone needs to return to base
            if drone.fuel_percent < 20:
                drone.status = "returning_to_base"
            elif drone.fuel_percent < 10:
                drone.status = "emergency_landing"
            
            drone.last_update = datetime.now()
    
    def detect_threats(self) -> List[Dict[str, Any]]:
        """Simulate threat detection by drones"""
        detections = []
        
        for drone in self.drones.values():
            if drone.status != "active":
                continue
            
            # Check for threats within sensor range
            for threat_type, probability in self.threat_probabilities.items():
                # Adjust probability based on drone type
                adjusted_probability = probability
                if drone.drone_type == DroneType.SURVEILLANCE:
                    adjusted_probability *= 1.5
                elif drone.drone_type == DroneType.RECONNAISSANCE:
                    adjusted_probability *= 2.0
                elif drone.drone_type == DroneType.COMBAT:
                    adjusted_probability *= 1.2
                
                # Random threat detection
                if random.random() < adjusted_probability / 720:  # Per 5-second update
                    detection = self._generate_threat_detection(drone, threat_type)
                    if detection:
                        detections.append(detection)
        
        return detections
    
    def _generate_threat_detection(self, drone: DroneUnit, threat_type: ThreatType) -> Optional[Dict[str, Any]]:
        """Generate a threat detection event"""
        # Random location within drone's sensor range
        max_distance = drone.sensor_range / 111  # Convert km to degrees (approximate)
        
        angle = random.uniform(0, 2 * math.pi)
        distance = random.uniform(0.1, max_distance)
        
        threat_lat = drone.latitude + distance * math.cos(angle)
        threat_lon = drone.longitude + distance * math.sin(angle)
        
        # Generate threat ID
        threat_id = f"THR-{datetime.now().strftime('%Y%m%d%H%M%S')}-{random.randint(1000, 9999)}"
        
        # Calculate confidence based on drone type and distance
        base_confidence = {
            DroneType.SURVEILLANCE: 0.85,
            DroneType.RECONNAISSANCE: 0.90,
            DroneType.COMBAT: 0.80,
            DroneType.LOGISTICS: 0.70
        }.get(drone.drone_type, 0.75)
        
        # Reduce confidence with distance
        distance_factor = max(0.3, 1 - (distance * 111 / drone.sensor_range))
        confidence = base_confidence * distance_factor * random.uniform(0.8, 1.0)
        
        # Determine severity
        severity = "low"
        if threat_type in [ThreatType.WEAPON_SIGNATURE, ThreatType.IMPROVISED_EXPLOSIVE, ThreatType.SNIPER_POSITION]:
            severity = "high" if confidence > 0.7 else "medium"
        elif threat_type in [ThreatType.HOSTILE_VEHICLE, ThreatType.DRONE_DETECTION]:
            severity = "medium" if confidence > 0.6 else "low"
        
        # Generate description
        descriptions = {
            ThreatType.HOSTILE_VEHICLE: f"Unidentified vehicle detected moving at high speed",
            ThreatType.SUSPICIOUS_ACTIVITY: f"Unusual personnel movement pattern observed",
            ThreatType.WEAPON_SIGNATURE: f"Weapon heat signature detected",
            ThreatType.DRONE_DETECTION: f"Unauthorized drone activity identified",
            ThreatType.PERSONNEL_MOVEMENT: f"Large group movement detected",
            ThreatType.IMPROVISED_EXPLOSIVE: f"Potential IED signature identified",
            ThreatType.SNIPER_POSITION: f"Possible sniper position detected",
            ThreatType.COMMUNICATION_INTERCEPT: f"Hostile communication intercepted"
        }
        
        detection = {
            "threat_id": threat_id,
            "threat_type": threat_type.value,
            "latitude": threat_lat,
            "longitude": threat_lon,
            "confidence": round(confidence, 3),
            "severity": severity,
            "detected_by": drone.drone_id,
            "detector_type": "drone",
            "timestamp": datetime.now().isoformat(),
            "description": descriptions.get(threat_type, f"Threat detected: {threat_type.value}"),
            "sensor_data": {
                "detection_range": round(distance * 111, 2),  # km
                "drone_altitude": drone.altitude,
                "sensor_type": self._get_sensor_type(threat_type),
                "environmental_conditions": self._get_environmental_conditions()
            }
        }
        
        # Store in active threats
        self.active_threats[threat_id] = detection
        self.detection_history.append(detection)
        
        # Limit history size
        if len(self.detection_history) > 1000:
            self.detection_history = self.detection_history[-500:]
        
        return detection
    
    def _get_sensor_type(self, threat_type: ThreatType) -> str:
        """Get the sensor type used for detection"""
        sensor_mapping = {
            ThreatType.HOSTILE_VEHICLE: "thermal_imaging",
            ThreatType.SUSPICIOUS_ACTIVITY: "optical_camera",
            ThreatType.WEAPON_SIGNATURE: "thermal_imaging",
            ThreatType.DRONE_DETECTION: "radar",
            ThreatType.PERSONNEL_MOVEMENT: "motion_sensor",
            ThreatType.IMPROVISED_EXPLOSIVE: "chemical_sensor",
            ThreatType.SNIPER_POSITION: "acoustic_sensor",
            ThreatType.COMMUNICATION_INTERCEPT: "signal_intelligence"
        }
        return sensor_mapping.get(threat_type, "multi_sensor")
    
    def _get_environmental_conditions(self) -> Dict[str, Any]:
        """Get current environmental conditions affecting detection"""
        return {
            "visibility": random.uniform(5, 15),  # km
            "cloud_cover": random.uniform(0, 80),  # %
            "wind_speed": random.uniform(5, 25),  # km/h
            "temperature": random.uniform(10, 30),  # °C
            "time_of_day": datetime.now().strftime("%H:%M")
        }
    
    def generate_surveillance_report(self, drone_id: str) -> Dict[str, Any]:
        """Generate comprehensive surveillance report for a drone"""
        if drone_id not in self.drones:
            return {}
        
        drone = self.drones[drone_id]
        
        # Get recent detections by this drone
        recent_detections = [
            d for d in self.detection_history[-50:]
            if d["detected_by"] == drone_id and 
            datetime.fromisoformat(d["timestamp"]) > datetime.now() - timedelta(hours=1)
        ]
        
        # Calculate area coverage
        mission_area_size = (
            (drone.mission_area[1] - drone.mission_area[0]) * 
            (drone.mission_area[3] - drone.mission_area[2]) * 
            111 * 111  # Convert to km²
        )
        
        report = {
            "drone_id": drone_id,
            "callsign": drone.callsign,
            "report_timestamp": datetime.now().isoformat(),
            "mission_status": {
                "status": drone.status,
                "fuel_remaining": drone.fuel_percent,
                "altitude": drone.altitude,
                "current_position": {
                    "latitude": drone.latitude,
                    "longitude": drone.longitude
                },
                "mission_area_coverage": round(mission_area_size, 2)
            },
            "surveillance_summary": {
                "total_detections": len(recent_detections),
                "high_priority_threats": len([d for d in recent_detections if d["severity"] == "high"]),
                "average_confidence": round(
                    sum(d["confidence"] for d in recent_detections) / max(1, len(recent_detections)), 3
                ),
                "threat_types_detected": list(set(d["threat_type"] for d in recent_detections))
            },
            "recent_detections": recent_detections[-10:],  # Last 10 detections
            "operational_metrics": {
                "flight_time": random.uniform(2, 8),  # hours
                "distance_covered": random.uniform(50, 200),  # km
                "sensor_uptime": random.uniform(95, 100),  # %
                "communication_quality": random.uniform(85, 100)  # %
            }
        }
        
        return report
    
    def get_drone_status(self) -> List[Dict[str, Any]]:
        """Get status of all drones"""
        status_list = []
        
        for drone in self.drones.values():
            status = {
                "drone_id": drone.drone_id,
                "callsign": drone.callsign,
                "drone_type": drone.drone_type.value,
                "status": drone.status,
                "position": {
                    "latitude": drone.latitude,
                    "longitude": drone.longitude,
                    "altitude": drone.altitude
                },
                "heading": drone.heading,
                "speed": drone.speed,
                "fuel_percent": drone.fuel_percent,
                "sensor_range": drone.sensor_range,
                "last_update": drone.last_update.isoformat(),
                "mission_area": {
                    "lat_min": drone.mission_area[0],
                    "lat_max": drone.mission_area[1],
                    "lon_min": drone.mission_area[2],
                    "lon_max": drone.mission_area[3]
                }
            }
            status_list.append(status)
        
        return status_list
    
    def get_active_threats(self) -> List[Dict[str, Any]]:
        """Get all active threat detections"""
        # Remove old threats (older than 2 hours)
        cutoff_time = datetime.now() - timedelta(hours=2)
        active_threats = {}
        
        for threat_id, threat_data in self.active_threats.items():
            threat_time = datetime.fromisoformat(threat_data["timestamp"])
            if threat_time > cutoff_time:
                active_threats[threat_id] = threat_data
        
        self.active_threats = active_threats
        return list(self.active_threats.values())
    
    def acknowledge_threat(self, threat_id: str, acknowledged_by: str) -> bool:
        """Acknowledge a threat detection"""
        if threat_id in self.active_threats:
            self.active_threats[threat_id]["acknowledged"] = True
            self.active_threats[threat_id]["acknowledged_by"] = acknowledged_by
            self.active_threats[threat_id]["acknowledged_at"] = datetime.now().isoformat()
            return True
        return False
    
    async def run_simulation(self, duration_seconds: int = 3600):
        """Run the drone simulation for specified duration"""
        print(f"Starting drone simulation for {duration_seconds} seconds...")
        
        start_time = datetime.now()
        update_interval = 5  # seconds
        
        while (datetime.now() - start_time).total_seconds() < duration_seconds:
            # Update drone positions
            self.update_drone_positions()
            
            # Detect threats
            new_detections = self.detect_threats()
            
            if new_detections:
                print(f"New threat detections: {len(new_detections)}")
                for detection in new_detections:
                    print(f"  - {detection['threat_type']} detected by {detection['detected_by']} "
                          f"(confidence: {detection['confidence']:.2f})")
            
            # Wait for next update
            await asyncio.sleep(update_interval)
        
        print("Drone simulation completed")


# Global drone simulator instance
drone_simulator = DroneFeedSimulator()


# Example usage and testing
if __name__ == "__main__":
    async def main():
        # Run simulation for 60 seconds
        await drone_simulator.run_simulation(60)
        
        # Print final status
        print("\nFinal Drone Status:")
        for status in drone_simulator.get_drone_status():
            print(f"  {status['callsign']}: {status['status']} - Fuel: {status['fuel_percent']:.1f}%")
        
        print(f"\nActive Threats: {len(drone_simulator.get_active_threats())}")
        print(f"Total Detections: {len(drone_simulator.detection_history)}")
    
    # Run the example
    asyncio.run(main())