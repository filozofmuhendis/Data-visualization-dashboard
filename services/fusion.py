"""
MSA Dashboard - Data Fusion Service
Combines geographic, health, threat, and logistics data for comprehensive situational awareness
"""

import math
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

from core.models import (
    Unit, HealthMetrics, LogisticsStatus, ThreatDetection, 
    WeatherData, RiskLevel, UnitType
)


class FusionConfidence(Enum):
    """Confidence levels for fused data"""
    VERY_HIGH = "very_high"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    VERY_LOW = "very_low"


@dataclass
class GeographicCluster:
    """Represents a geographic cluster of entities"""
    cluster_id: str
    center_lat: float
    center_lon: float
    radius_km: float
    entities: List[str]
    entity_types: List[str]
    risk_level: RiskLevel
    last_updated: datetime


@dataclass
class TacticalSituation:
    """Represents the tactical situation in an area"""
    area_id: str
    bounds: Tuple[float, float, float, float]  # lat_min, lat_max, lon_min, lon_max
    friendly_units: List[str]
    threat_level: RiskLevel
    threat_count: int
    environmental_factors: Dict[str, Any]
    operational_status: str
    recommendations: List[str]
    confidence: FusionConfidence
    last_updated: datetime


@dataclass
class UnitSituationalAwareness:
    """Complete situational awareness for a unit"""
    unit_id: str
    position: Tuple[float, float]
    health_status: RiskLevel
    logistics_status: RiskLevel
    threat_exposure: RiskLevel
    environmental_impact: RiskLevel
    overall_risk: RiskLevel
    nearby_threats: List[Dict]
    nearby_units: List[Dict]
    mission_impact: str
    recommendations: List[str]
    confidence: FusionConfidence
    last_updated: datetime


class MilitaryDataFusion:
    """Military-specific data fusion engine"""
    
    def __init__(self):
        self.units_cache: Dict[str, Unit] = {}
        self.health_cache: Dict[str, HealthMetrics] = {}
        self.logistics_cache: Dict[str, LogisticsStatus] = {}
        self.threats_cache: Dict[str, ThreatDetection] = {}
        self.weather_cache: Dict[str, WeatherData] = {}
        
        # Fusion parameters
        self.threat_proximity_threshold = 2.0  # km
        self.unit_proximity_threshold = 1.0    # km
        self.weather_influence_radius = 10.0   # km
        self.data_freshness_threshold = 300    # seconds (5 minutes)
    
    def update_unit_data(self, unit: Unit):
        """Update unit data in cache"""
        self.units_cache[unit.unit_id] = unit
    
    def update_health_data(self, health: HealthMetrics):
        """Update health data in cache"""
        self.health_cache[health.unit_id] = health
    
    def update_logistics_data(self, logistics: LogisticsStatus):
        """Update logistics data in cache"""
        self.logistics_cache[logistics.unit_id] = logistics
    
    def update_threat_data(self, threat: ThreatDetection):
        """Update threat data in cache"""
        threat_id = f"{threat.latitude}_{threat.longitude}_{threat.timestamp.isoformat()}"
        self.threats_cache[threat_id] = threat
    
    def update_weather_data(self, weather: WeatherData):
        """Update weather data in cache"""
        weather_id = f"{weather.latitude}_{weather.longitude}"
        self.weather_cache[weather_id] = weather
    
    def get_unit_situational_awareness(self, unit_id: str) -> Optional[UnitSituationalAwareness]:
        """Get comprehensive situational awareness for a unit"""
        if unit_id not in self.units_cache:
            return None
        
        unit = self.units_cache[unit_id]
        
        # Get unit position
        position = (unit.latitude, unit.longitude)
        
        # Assess health status
        health_status = self._assess_health_status(unit_id)
        
        # Assess logistics status
        logistics_status = self._assess_logistics_status(unit_id)
        
        # Assess threat exposure
        threat_exposure, nearby_threats = self._assess_threat_exposure(position)
        
        # Assess environmental impact
        environmental_impact = self._assess_environmental_impact(position)
        
        # Find nearby units
        nearby_units = self._find_nearby_units(unit_id, position)
        
        # Calculate overall risk
        overall_risk = self._calculate_overall_risk(
            health_status, logistics_status, threat_exposure, environmental_impact
        )
        
        # Generate recommendations
        recommendations = self._generate_unit_recommendations(
            unit, health_status, logistics_status, threat_exposure, 
            environmental_impact, nearby_threats, nearby_units
        )
        
        # Calculate confidence
        confidence = self._calculate_fusion_confidence(unit_id)
        
        # Assess mission impact
        mission_impact = self._assess_mission_impact(
            unit, overall_risk, nearby_threats, environmental_impact
        )
        
        return UnitSituationalAwareness(
            unit_id=unit_id,
            position=position,
            health_status=health_status,
            logistics_status=logistics_status,
            threat_exposure=threat_exposure,
            environmental_impact=environmental_impact,
            overall_risk=overall_risk,
            nearby_threats=nearby_threats,
            nearby_units=nearby_units,
            mission_impact=mission_impact,
            recommendations=recommendations,
            confidence=confidence,
            last_updated=datetime.now()
        )
    
    def get_tactical_situation(self, bounds: Tuple[float, float, float, float]) -> TacticalSituation:
        """Get tactical situation for a geographic area"""
        lat_min, lat_max, lon_min, lon_max = bounds
        area_id = f"AREA_{lat_min:.3f}_{lon_min:.3f}_{lat_max:.3f}_{lon_max:.3f}"
        
        # Find units in area
        friendly_units = []
        for unit_id, unit in self.units_cache.items():
            if (lat_min <= unit.latitude <= lat_max and 
                lon_min <= unit.longitude <= lon_max):
                friendly_units.append(unit_id)
        
        # Find threats in area
        area_threats = []
        for threat_id, threat in self.threats_cache.items():
            if (lat_min <= threat.latitude <= lat_max and 
                lon_min <= threat.longitude <= lon_max):
                # Check if threat is recent
                if self._is_data_fresh(threat.timestamp):
                    area_threats.append(threat)
        
        # Calculate threat level
        threat_level = self._calculate_area_threat_level(area_threats)
        
        # Get environmental factors
        environmental_factors = self._get_area_environmental_factors(bounds)
        
        # Determine operational status
        operational_status = self._determine_operational_status(
            friendly_units, area_threats, environmental_factors
        )
        
        # Generate recommendations
        recommendations = self._generate_area_recommendations(
            friendly_units, area_threats, environmental_factors, operational_status
        )
        
        # Calculate confidence
        confidence = self._calculate_area_confidence(
            len(friendly_units), len(area_threats), environmental_factors
        )
        
        return TacticalSituation(
            area_id=area_id,
            bounds=bounds,
            friendly_units=friendly_units,
            threat_level=threat_level,
            threat_count=len(area_threats),
            environmental_factors=environmental_factors,
            operational_status=operational_status,
            recommendations=recommendations,
            confidence=confidence,
            last_updated=datetime.now()
        )
    
    def detect_geographic_clusters(self, cluster_radius_km: float = 2.0) -> List[GeographicCluster]:
        """Detect geographic clusters of units and threats"""
        clusters = []
        processed_entities = set()
        
        # Combine units and threats for clustering
        entities = []
        
        # Add units
        for unit_id, unit in self.units_cache.items():
            entities.append({
                "id": unit_id,
                "type": "unit",
                "subtype": unit.unit_type.value,
                "lat": unit.latitude,
                "lon": unit.longitude,
                "risk": self._assess_unit_overall_risk(unit_id)
            })
        
        # Add recent threats
        for threat_id, threat in self.threats_cache.items():
            if self._is_data_fresh(threat.timestamp):
                entities.append({
                    "id": threat_id,
                    "type": "threat",
                    "subtype": threat.threat_type,
                    "lat": threat.latitude,
                    "lon": threat.longitude,
                    "risk": RiskLevel.HIGH if threat.confidence > 0.7 else RiskLevel.MEDIUM
                })
        
        # Simple clustering algorithm
        cluster_id = 1
        for entity in entities:
            if entity["id"] in processed_entities:
                continue
            
            # Find nearby entities
            cluster_entities = [entity]
            processed_entities.add(entity["id"])
            
            for other_entity in entities:
                if (other_entity["id"] not in processed_entities and
                    self._calculate_distance(
                        entity["lat"], entity["lon"],
                        other_entity["lat"], other_entity["lon"]
                    ) <= cluster_radius_km):
                    cluster_entities.append(other_entity)
                    processed_entities.add(other_entity["id"])
            
            # Create cluster if it has multiple entities or high-risk single entity
            if (len(cluster_entities) > 1 or 
                (len(cluster_entities) == 1 and cluster_entities[0]["risk"] == RiskLevel.HIGH)):
                
                # Calculate cluster center
                center_lat = sum(e["lat"] for e in cluster_entities) / len(cluster_entities)
                center_lon = sum(e["lon"] for e in cluster_entities) / len(cluster_entities)
                
                # Calculate cluster risk
                risk_levels = [e["risk"] for e in cluster_entities]
                if RiskLevel.HIGH in risk_levels:
                    cluster_risk = RiskLevel.HIGH
                elif RiskLevel.MEDIUM in risk_levels:
                    cluster_risk = RiskLevel.MEDIUM
                else:
                    cluster_risk = RiskLevel.LOW
                
                cluster = GeographicCluster(
                    cluster_id=f"CLUSTER_{cluster_id:03d}",
                    center_lat=center_lat,
                    center_lon=center_lon,
                    radius_km=cluster_radius_km,
                    entities=[e["id"] for e in cluster_entities],
                    entity_types=[e["type"] for e in cluster_entities],
                    risk_level=cluster_risk,
                    last_updated=datetime.now()
                )
                
                clusters.append(cluster)
                cluster_id += 1
        
        return clusters
    
    def get_mission_readiness_assessment(self, unit_ids: List[str]) -> Dict[str, Any]:
        """Assess mission readiness for a group of units"""
        if not unit_ids:
            return {}
        
        readiness_scores = []
        health_issues = []
        logistics_issues = []
        threat_concerns = []
        environmental_concerns = []
        
        for unit_id in unit_ids:
            if unit_id not in self.units_cache:
                continue
            
            unit = self.units_cache[unit_id]
            
            # Calculate individual readiness score
            health_score = self._calculate_health_readiness_score(unit_id)
            logistics_score = self._calculate_logistics_readiness_score(unit_id)
            threat_score = self._calculate_threat_readiness_score(unit_id)
            environmental_score = self._calculate_environmental_readiness_score(unit_id)
            
            unit_readiness = (health_score + logistics_score + threat_score + environmental_score) / 4
            readiness_scores.append(unit_readiness)
            
            # Collect issues
            if health_score < 70:
                health_issues.append(f"{unit_id}: Health concerns")
            if logistics_score < 70:
                logistics_issues.append(f"{unit_id}: Logistics shortfall")
            if threat_score < 70:
                threat_concerns.append(f"{unit_id}: High threat exposure")
            if environmental_score < 70:
                environmental_concerns.append(f"{unit_id}: Environmental challenges")
        
        # Calculate overall readiness
        if readiness_scores:
            overall_readiness = sum(readiness_scores) / len(readiness_scores)
        else:
            overall_readiness = 0
        
        # Determine readiness level
        if overall_readiness >= 85:
            readiness_level = "READY"
        elif overall_readiness >= 70:
            readiness_level = "CONDITIONALLY_READY"
        elif overall_readiness >= 50:
            readiness_level = "NOT_READY"
        else:
            readiness_level = "MISSION_CRITICAL_ISSUES"
        
        return {
            "overall_readiness": overall_readiness,
            "readiness_level": readiness_level,
            "unit_count": len(unit_ids),
            "ready_units": len([s for s in readiness_scores if s >= 85]),
            "conditional_units": len([s for s in readiness_scores if 70 <= s < 85]),
            "not_ready_units": len([s for s in readiness_scores if s < 70]),
            "issues": {
                "health": health_issues,
                "logistics": logistics_issues,
                "threats": threat_concerns,
                "environmental": environmental_concerns
            },
            "recommendations": self._generate_mission_readiness_recommendations(
                readiness_level, health_issues, logistics_issues, threat_concerns, environmental_concerns
            ),
            "assessment_time": datetime.now().isoformat()
        }
    
    def _assess_health_status(self, unit_id: str) -> RiskLevel:
        """Assess health status risk level"""
        if unit_id not in self.health_cache:
            return RiskLevel.UNKNOWN
        
        health = self.health_cache[unit_id]
        
        # Check if data is fresh
        if not self._is_data_fresh(health.timestamp):
            return RiskLevel.UNKNOWN
        
        risk_factors = 0
        
        # Heart rate assessment
        if health.heart_rate:
            if health.heart_rate < 40 or health.heart_rate > 180:
                risk_factors += 3
            elif health.heart_rate < 50 or health.heart_rate > 160:
                risk_factors += 2
        
        # SpO2 assessment
        if health.spo2:
            if health.spo2 < 88:
                risk_factors += 3
            elif health.spo2 < 92:
                risk_factors += 2
        
        # Stress level assessment
        if health.stress_level:
            if health.stress_level > 8:
                risk_factors += 3
            elif health.stress_level > 6:
                risk_factors += 2
        
        # Body temperature assessment
        if health.body_temperature:
            if health.body_temperature < 35 or health.body_temperature > 39.5:
                risk_factors += 3
            elif health.body_temperature < 36 or health.body_temperature > 38.5:
                risk_factors += 2
        
        # Convert risk factors to risk level
        if risk_factors >= 6:
            return RiskLevel.HIGH
        elif risk_factors >= 3:
            return RiskLevel.MEDIUM
        elif risk_factors > 0:
            return RiskLevel.LOW
        else:
            return RiskLevel.LOW
    
    def _assess_logistics_status(self, unit_id: str) -> RiskLevel:
        """Assess logistics status risk level"""
        if unit_id not in self.logistics_cache:
            return RiskLevel.UNKNOWN
        
        logistics = self.logistics_cache[unit_id]
        
        # Check if data is fresh
        if not self._is_data_fresh(logistics.timestamp):
            return RiskLevel.UNKNOWN
        
        risk_factors = 0
        
        # Fuel assessment
        if logistics.fuel_percent is not None:
            if logistics.fuel_percent < 10:
                risk_factors += 3
            elif logistics.fuel_percent < 25:
                risk_factors += 2
        
        # Ammunition assessment
        if logistics.ammunition_percent is not None:
            if logistics.ammunition_percent < 15:
                risk_factors += 3
            elif logistics.ammunition_percent < 30:
                risk_factors += 2
        
        # Medical supplies assessment
        if logistics.medical_supplies_percent is not None:
            if logistics.medical_supplies_percent < 20:
                risk_factors += 2
            elif logistics.medical_supplies_percent < 40:
                risk_factors += 1
        
        # Food supplies assessment
        if logistics.food_supplies_percent is not None:
            if logistics.food_supplies_percent < 25:
                risk_factors += 2
            elif logistics.food_supplies_percent < 50:
                risk_factors += 1
        
        # Convert risk factors to risk level
        if risk_factors >= 6:
            return RiskLevel.HIGH
        elif risk_factors >= 3:
            return RiskLevel.MEDIUM
        elif risk_factors > 0:
            return RiskLevel.LOW
        else:
            return RiskLevel.LOW
    
    def _assess_threat_exposure(self, position: Tuple[float, float]) -> Tuple[RiskLevel, List[Dict]]:
        """Assess threat exposure at a position"""
        lat, lon = position
        nearby_threats = []
        
        for threat_id, threat in self.threats_cache.items():
            if not self._is_data_fresh(threat.timestamp):
                continue
            
            distance = self._calculate_distance(lat, lon, threat.latitude, threat.longitude)
            
            if distance <= self.threat_proximity_threshold:
                threat_info = {
                    "threat_id": threat_id,
                    "threat_type": threat.threat_type,
                    "distance_km": distance,
                    "confidence": threat.confidence,
                    "severity": "high" if threat.confidence > 0.7 else "medium"
                }
                nearby_threats.append(threat_info)
        
        # Calculate threat exposure level
        if not nearby_threats:
            return RiskLevel.LOW, []
        
        high_confidence_threats = [t for t in nearby_threats if t["confidence"] > 0.7]
        weapon_threats = [t for t in nearby_threats if "weapon" in t["threat_type"].lower()]
        
        if len(high_confidence_threats) >= 2 or len(weapon_threats) >= 1:
            return RiskLevel.HIGH, nearby_threats
        elif len(nearby_threats) >= 3 or len(high_confidence_threats) >= 1:
            return RiskLevel.MEDIUM, nearby_threats
        else:
            return RiskLevel.LOW, nearby_threats
    
    def _assess_environmental_impact(self, position: Tuple[float, float]) -> RiskLevel:
        """Assess environmental impact at a position"""
        lat, lon = position
        
        # Find nearest weather data
        nearest_weather = None
        min_distance = float('inf')
        
        for weather_id, weather in self.weather_cache.items():
            if not self._is_data_fresh(weather.timestamp):
                continue
            
            distance = self._calculate_distance(lat, lon, weather.latitude, weather.longitude)
            
            if distance <= self.weather_influence_radius and distance < min_distance:
                min_distance = distance
                nearest_weather = weather
        
        if not nearest_weather:
            return RiskLevel.UNKNOWN
        
        risk_factors = 0
        
        # Visibility assessment
        if nearest_weather.visibility_km is not None:
            if nearest_weather.visibility_km < 1:
                risk_factors += 3
            elif nearest_weather.visibility_km < 3:
                risk_factors += 2
        
        # Wind speed assessment
        if nearest_weather.wind_speed_kmh is not None:
            if nearest_weather.wind_speed_kmh > 50:
                risk_factors += 3
            elif nearest_weather.wind_speed_kmh > 35:
                risk_factors += 2
        
        # Temperature assessment
        if nearest_weather.temperature_celsius is not None:
            if (nearest_weather.temperature_celsius < -10 or 
                nearest_weather.temperature_celsius > 45):
                risk_factors += 3
            elif (nearest_weather.temperature_celsius < -5 or 
                  nearest_weather.temperature_celsius > 40):
                risk_factors += 2
        
        # Convert risk factors to risk level
        if risk_factors >= 6:
            return RiskLevel.HIGH
        elif risk_factors >= 3:
            return RiskLevel.MEDIUM
        elif risk_factors > 0:
            return RiskLevel.LOW
        else:
            return RiskLevel.LOW
    
    def _find_nearby_units(self, unit_id: str, position: Tuple[float, float]) -> List[Dict]:
        """Find nearby friendly units"""
        lat, lon = position
        nearby_units = []
        
        for other_unit_id, other_unit in self.units_cache.items():
            if other_unit_id == unit_id:
                continue
            
            distance = self._calculate_distance(lat, lon, other_unit.latitude, other_unit.longitude)
            
            if distance <= self.unit_proximity_threshold:
                unit_info = {
                    "unit_id": other_unit_id,
                    "unit_type": other_unit.unit_type.value,
                    "callsign": other_unit.callsign,
                    "distance_km": distance,
                    "status": other_unit.status
                }
                nearby_units.append(unit_info)
        
        return nearby_units
    
    def _calculate_overall_risk(self, health: RiskLevel, logistics: RiskLevel, 
                              threats: RiskLevel, environment: RiskLevel) -> RiskLevel:
        """Calculate overall risk level from component risks"""
        risk_values = {
            RiskLevel.HIGH: 4,
            RiskLevel.MEDIUM: 3,
            RiskLevel.LOW: 2,
            RiskLevel.UNKNOWN: 1
        }
        
        risks = [health, logistics, threats, environment]
        risk_scores = [risk_values.get(risk, 1) for risk in risks]
        
        # Weight threats and health more heavily
        weighted_score = (
            risk_scores[0] * 1.5 +  # health
            risk_scores[1] * 1.2 +  # logistics
            risk_scores[2] * 1.8 +  # threats
            risk_scores[3] * 1.0    # environment
        ) / 5.5
        
        if weighted_score >= 3.5:
            return RiskLevel.HIGH
        elif weighted_score >= 2.5:
            return RiskLevel.MEDIUM
        else:
            return RiskLevel.LOW
    
    def _calculate_distance(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Calculate distance between two points in kilometers"""
        # Haversine formula
        R = 6371  # Earth's radius in kilometers
        
        dlat = math.radians(lat2 - lat1)
        dlon = math.radians(lon2 - lon1)
        
        a = (math.sin(dlat/2) * math.sin(dlat/2) + 
             math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * 
             math.sin(dlon/2) * math.sin(dlon/2))
        
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
        
        return R * c
    
    def _is_data_fresh(self, timestamp: datetime) -> bool:
        """Check if data is within freshness threshold"""
        return (datetime.now() - timestamp).total_seconds() <= self.data_freshness_threshold
    
    def _generate_unit_recommendations(self, unit: Unit, health: RiskLevel, logistics: RiskLevel,
                                     threats: RiskLevel, environment: RiskLevel,
                                     nearby_threats: List[Dict], nearby_units: List[Dict]) -> List[str]:
        """Generate recommendations for a unit"""
        recommendations = []
        
        # Health recommendations
        if health == RiskLevel.HIGH:
            recommendations.append("IMMEDIATE: Medical attention required")
            recommendations.append("Consider unit evacuation if possible")
        elif health == RiskLevel.MEDIUM:
            recommendations.append("Monitor health status closely")
        
        # Logistics recommendations
        if logistics == RiskLevel.HIGH:
            recommendations.append("URGENT: Resupply required immediately")
            recommendations.append("Coordinate with logistics support")
        elif logistics == RiskLevel.MEDIUM:
            recommendations.append("Plan resupply within next operational window")
        
        # Threat recommendations
        if threats == RiskLevel.HIGH:
            recommendations.append("HIGH THREAT: Consider immediate relocation")
            recommendations.append("Increase security posture")
            if nearby_threats:
                weapon_threats = [t for t in nearby_threats if "weapon" in t["threat_type"]]
                if weapon_threats:
                    recommendations.append("WEAPON THREAT: Take immediate cover")
        elif threats == RiskLevel.MEDIUM:
            recommendations.append("Maintain heightened awareness")
            recommendations.append("Consider route adjustment")
        
        # Environmental recommendations
        if environment == RiskLevel.HIGH:
            recommendations.append("Severe weather conditions - consider shelter")
            recommendations.append("Adjust operational tempo for conditions")
        elif environment == RiskLevel.MEDIUM:
            recommendations.append("Monitor weather conditions")
        
        # Unit coordination recommendations
        if nearby_units:
            recommendations.append(f"Coordinate with {len(nearby_units)} nearby units")
        
        return recommendations
    
    def _calculate_fusion_confidence(self, unit_id: str) -> FusionConfidence:
        """Calculate confidence in fused data"""
        data_sources = 0
        fresh_data = 0
        
        # Check unit data
        if unit_id in self.units_cache:
            data_sources += 1
            if self._is_data_fresh(self.units_cache[unit_id].last_seen or datetime.now()):
                fresh_data += 1
        
        # Check health data
        if unit_id in self.health_cache:
            data_sources += 1
            if self._is_data_fresh(self.health_cache[unit_id].timestamp):
                fresh_data += 1
        
        # Check logistics data
        if unit_id in self.logistics_cache:
            data_sources += 1
            if self._is_data_fresh(self.logistics_cache[unit_id].timestamp):
                fresh_data += 1
        
        if data_sources == 0:
            return FusionConfidence.VERY_LOW
        
        freshness_ratio = fresh_data / data_sources
        
        if freshness_ratio >= 0.8 and data_sources >= 3:
            return FusionConfidence.VERY_HIGH
        elif freshness_ratio >= 0.6 and data_sources >= 2:
            return FusionConfidence.HIGH
        elif freshness_ratio >= 0.4:
            return FusionConfidence.MEDIUM
        elif freshness_ratio >= 0.2:
            return FusionConfidence.LOW
        else:
            return FusionConfidence.VERY_LOW
    
    def _assess_mission_impact(self, unit: Unit, overall_risk: RiskLevel, 
                             nearby_threats: List[Dict], environment: RiskLevel) -> str:
        """Assess impact on mission capability"""
        if overall_risk == RiskLevel.HIGH:
            if nearby_threats and any("weapon" in t["threat_type"] for t in nearby_threats):
                return "MISSION_CRITICAL - Immediate threat to unit survival"
            else:
                return "MISSION_DEGRADED - Significant capability reduction"
        elif overall_risk == RiskLevel.MEDIUM:
            return "MISSION_IMPACTED - Some capability reduction"
        else:
            return "MISSION_CAPABLE - Full operational capability"
    
    def _assess_unit_overall_risk(self, unit_id: str) -> RiskLevel:
        """Quick assessment of unit overall risk"""
        health_risk = self._assess_health_status(unit_id)
        logistics_risk = self._assess_logistics_status(unit_id)
        
        if unit_id in self.units_cache:
            unit = self.units_cache[unit_id]
            position = (unit.latitude, unit.longitude)
            threat_risk, _ = self._assess_threat_exposure(position)
            environmental_risk = self._assess_environmental_impact(position)
        else:
            threat_risk = RiskLevel.UNKNOWN
            environmental_risk = RiskLevel.UNKNOWN
        
        return self._calculate_overall_risk(health_risk, logistics_risk, threat_risk, environmental_risk)
    
    def _calculate_area_threat_level(self, threats: List[ThreatDetection]) -> RiskLevel:
        """Calculate threat level for an area"""
        if not threats:
            return RiskLevel.LOW
        
        high_confidence_threats = [t for t in threats if t.confidence > 0.7]
        weapon_threats = [t for t in threats if "weapon" in t.threat_type.lower()]
        
        if len(weapon_threats) >= 2 or len(high_confidence_threats) >= 3:
            return RiskLevel.HIGH
        elif len(weapon_threats) >= 1 or len(high_confidence_threats) >= 2:
            return RiskLevel.MEDIUM
        else:
            return RiskLevel.LOW
    
    def _get_area_environmental_factors(self, bounds: Tuple[float, float, float, float]) -> Dict[str, Any]:
        """Get environmental factors for an area"""
        lat_min, lat_max, lon_min, lon_max = bounds
        center_lat = (lat_min + lat_max) / 2
        center_lon = (lon_min + lon_max) / 2
        
        # Find weather data in or near the area
        relevant_weather = []
        for weather_id, weather in self.weather_cache.items():
            if (lat_min <= weather.latitude <= lat_max and 
                lon_min <= weather.longitude <= lon_max):
                if self._is_data_fresh(weather.timestamp):
                    relevant_weather.append(weather)
        
        if not relevant_weather:
            return {"status": "no_data"}
        
        # Average weather conditions
        avg_temp = sum(w.temperature_celsius for w in relevant_weather if w.temperature_celsius) / len(relevant_weather)
        avg_wind = sum(w.wind_speed_kmh for w in relevant_weather if w.wind_speed_kmh) / len(relevant_weather)
        avg_visibility = sum(w.visibility_km for w in relevant_weather if w.visibility_km) / len(relevant_weather)
        avg_humidity = sum(w.humidity_percent for w in relevant_weather if w.humidity_percent) / len(relevant_weather)
        
        return {
            "temperature_celsius": avg_temp,
            "wind_speed_kmh": avg_wind,
            "visibility_km": avg_visibility,
            "humidity_percent": avg_humidity,
            "weather_stations": len(relevant_weather)
        }
    
    def _determine_operational_status(self, friendly_units: List[str], threats: List[ThreatDetection],
                                    environmental_factors: Dict[str, Any]) -> str:
        """Determine operational status for an area"""
        if not friendly_units:
            return "NO_FRIENDLY_PRESENCE"
        
        threat_level = self._calculate_area_threat_level(threats)
        
        # Check environmental conditions
        env_risk = RiskLevel.LOW
        if environmental_factors.get("visibility_km", 10) < 1:
            env_risk = RiskLevel.HIGH
        elif environmental_factors.get("wind_speed_kmh", 0) > 50:
            env_risk = RiskLevel.HIGH
        elif (environmental_factors.get("temperature_celsius", 20) < -10 or 
              environmental_factors.get("temperature_celsius", 20) > 45):
            env_risk = RiskLevel.HIGH
        
        if threat_level == RiskLevel.HIGH or env_risk == RiskLevel.HIGH:
            return "HIGH_RISK_OPERATIONS"
        elif threat_level == RiskLevel.MEDIUM or env_risk == RiskLevel.MEDIUM:
            return "ELEVATED_RISK_OPERATIONS"
        else:
            return "NORMAL_OPERATIONS"
    
    def _generate_area_recommendations(self, friendly_units: List[str], threats: List[ThreatDetection],
                                     environmental_factors: Dict[str, Any], operational_status: str) -> List[str]:
        """Generate recommendations for an area"""
        recommendations = []
        
        if operational_status == "HIGH_RISK_OPERATIONS":
            recommendations.append("Consider relocating units from high-risk area")
            recommendations.append("Increase force protection measures")
            recommendations.append("Establish overwatch positions")
        
        if threats:
            weapon_threats = [t for t in threats if "weapon" in t.threat_type.lower()]
            if weapon_threats:
                recommendations.append("WEAPON THREATS DETECTED - Implement immediate security measures")
            recommendations.append(f"Monitor {len(threats)} active threat(s) in area")
        
        if environmental_factors.get("visibility_km", 10) < 3:
            recommendations.append("Low visibility - Adjust movement and operations")
        
        if environmental_factors.get("wind_speed_kmh", 0) > 35:
            recommendations.append("High winds - Consider impact on air operations")
        
        if len(friendly_units) > 5:
            recommendations.append("High unit density - Coordinate movement to avoid congestion")
        
        return recommendations
    
    def _calculate_area_confidence(self, unit_count: int, threat_count: int, 
                                 environmental_factors: Dict[str, Any]) -> FusionConfidence:
        """Calculate confidence in area assessment"""
        data_quality_score = 0
        
        # Unit data quality
        if unit_count > 0:
            data_quality_score += 2
        
        # Threat data quality
        if threat_count > 0:
            data_quality_score += 2
        
        # Environmental data quality
        if environmental_factors.get("weather_stations", 0) > 0:
            data_quality_score += 1
        
        if data_quality_score >= 4:
            return FusionConfidence.HIGH
        elif data_quality_score >= 3:
            return FusionConfidence.MEDIUM
        elif data_quality_score >= 2:
            return FusionConfidence.LOW
        else:
            return FusionConfidence.VERY_LOW
    
    def _calculate_health_readiness_score(self, unit_id: str) -> float:
        """Calculate health readiness score (0-100)"""
        if unit_id not in self.health_cache:
            return 50  # Unknown
        
        health = self.health_cache[unit_id]
        if not self._is_data_fresh(health.timestamp):
            return 50
        
        score = 100
        
        # Heart rate impact
        if health.heart_rate:
            if health.heart_rate < 40 or health.heart_rate > 180:
                score -= 40
            elif health.heart_rate < 50 or health.heart_rate > 160:
                score -= 20
        
        # SpO2 impact
        if health.spo2:
            if health.spo2 < 88:
                score -= 40
            elif health.spo2 < 92:
                score -= 20
        
        # Stress impact
        if health.stress_level:
            if health.stress_level > 8:
                score -= 30
            elif health.stress_level > 6:
                score -= 15
        
        return max(0, score)
    
    def _calculate_logistics_readiness_score(self, unit_id: str) -> float:
        """Calculate logistics readiness score (0-100)"""
        if unit_id not in self.logistics_cache:
            return 50  # Unknown
        
        logistics = self.logistics_cache[unit_id]
        if not self._is_data_fresh(logistics.timestamp):
            return 50
        
        # Weight different supplies
        fuel_score = logistics.fuel_percent or 50
        ammo_score = logistics.ammunition_percent or 50
        medical_score = logistics.medical_supplies_percent or 50
        food_score = logistics.food_supplies_percent or 50
        
        # Weighted average (fuel and ammo are more critical)
        weighted_score = (
            fuel_score * 0.3 +
            ammo_score * 0.3 +
            medical_score * 0.2 +
            food_score * 0.2
        )
        
        return weighted_score
    
    def _calculate_threat_readiness_score(self, unit_id: str) -> float:
        """Calculate threat readiness score (0-100)"""
        if unit_id not in self.units_cache:
            return 50
        
        unit = self.units_cache[unit_id]
        position = (unit.latitude, unit.longitude)
        threat_risk, nearby_threats = self._assess_threat_exposure(position)
        
        if threat_risk == RiskLevel.HIGH:
            return 20
        elif threat_risk == RiskLevel.MEDIUM:
            return 60
        else:
            return 90
    
    def _calculate_environmental_readiness_score(self, unit_id: str) -> float:
        """Calculate environmental readiness score (0-100)"""
        if unit_id not in self.units_cache:
            return 50
        
        unit = self.units_cache[unit_id]
        position = (unit.latitude, unit.longitude)
        env_risk = self._assess_environmental_impact(position)
        
        if env_risk == RiskLevel.HIGH:
            return 30
        elif env_risk == RiskLevel.MEDIUM:
            return 70
        else:
            return 95
    
    def _generate_mission_readiness_recommendations(self, readiness_level: str, health_issues: List[str],
                                                  logistics_issues: List[str], threat_concerns: List[str],
                                                  environmental_concerns: List[str]) -> List[str]:
        """Generate mission readiness recommendations"""
        recommendations = []
        
        if readiness_level == "MISSION_CRITICAL_ISSUES":
            recommendations.append("ABORT MISSION - Critical issues must be resolved")
        elif readiness_level == "NOT_READY":
            recommendations.append("DELAY MISSION - Address readiness issues before proceeding")
        elif readiness_level == "CONDITIONALLY_READY":
            recommendations.append("PROCEED WITH CAUTION - Monitor identified issues closely")
        
        if health_issues:
            recommendations.append(f"Address {len(health_issues)} health concerns")
        
        if logistics_issues:
            recommendations.append(f"Resolve {len(logistics_issues)} logistics shortfalls")
        
        if threat_concerns:
            recommendations.append(f"Mitigate {len(threat_concerns)} threat exposures")
        
        if environmental_concerns:
            recommendations.append(f"Account for {len(environmental_concerns)} environmental factors")
        
        return recommendations


# Global data fusion instance
data_fusion = MilitaryDataFusion()


# Example usage and testing
if __name__ == "__main__":
    from core.models import Unit, HealthMetrics, LogisticsStatus, UnitType
    
    # Create test unit
    test_unit = Unit(
        unit_id="TEST-001",
        callsign="ALPHA-1",
        unit_type=UnitType.INFANTRY,
        latitude=39.9042,
        longitude=32.6195,
        altitude=850.0,
        heading=45.0,
        speed=5.0,
        status="active",
        last_seen=datetime.now()
    )
    
    # Create test health data
    test_health = HealthMetrics(
        unit_id="TEST-001",
        heart_rate=85,
        spo2=98,
        stress_level=4.5,
        body_temperature=37.2,
        timestamp=datetime.now()
    )
    
    # Create test logistics data
    test_logistics = LogisticsStatus(
        unit_id="TEST-001",
        fuel_percent=75.0,
        ammunition_percent=60.0,
        medical_supplies_percent=80.0,
        food_supplies_percent=90.0,
        timestamp=datetime.now()
    )
    
    # Update fusion engine
    data_fusion.update_unit_data(test_unit)
    data_fusion.update_health_data(test_health)
    data_fusion.update_logistics_data(test_logistics)
    
    # Get situational awareness
    sa = data_fusion.get_unit_situational_awareness("TEST-001")
    if sa:
        print(f"Unit Situational Awareness for {sa.unit_id}:")
        print(f"  Overall Risk: {sa.overall_risk.value}")
        print(f"  Health Status: {sa.health_status.value}")
        print(f"  Logistics Status: {sa.logistics_status.value}")
        print(f"  Mission Impact: {sa.mission_impact}")
        print(f"  Recommendations: {len(sa.recommendations)}")
        for rec in sa.recommendations:
            print(f"    - {rec}")
    
    # Test mission readiness
    readiness = data_fusion.get_mission_readiness_assessment(["TEST-001"])
    print(f"\nMission Readiness Assessment:")
    print(f"  Readiness Level: {readiness['readiness_level']}")
    print(f"  Overall Score: {readiness['overall_readiness']:.1f}%")