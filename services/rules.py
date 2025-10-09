"""
MSA Dashboard - Alert Rules Engine
Implements color-coded risk assessment (red/amber/green) and threshold-based notifications
"""

from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from enum import Enum
from dataclasses import dataclass

from core.models import (
    RiskLevel, AlertSeverity, Unit, HealthMetrics, LogisticsStatus, 
    ThreatDetection, Alert, WeatherData
)
from core.settings import settings


class AlertType(Enum):
    """Types of alerts that can be generated"""
    HEALTH_CRITICAL = "health_critical"
    HEALTH_WARNING = "health_warning"
    LOGISTICS_CRITICAL = "logistics_critical"
    LOGISTICS_WARNING = "logistics_warning"
    THREAT_DETECTED = "threat_detected"
    UNIT_OFFLINE = "unit_offline"
    MISSION_DELAY = "mission_delay"
    WEATHER_WARNING = "weather_warning"
    FUEL_LOW = "fuel_low"
    AMMUNITION_LOW = "ammunition_low"
    MEDICAL_EMERGENCY = "medical_emergency"
    COMMUNICATION_LOST = "communication_lost"
    POSITION_DEVIATION = "position_deviation"
    EQUIPMENT_FAILURE = "equipment_failure"


@dataclass
class RuleThreshold:
    """Defines thresholds for rule evaluation"""
    critical_min: Optional[float] = None
    critical_max: Optional[float] = None
    warning_min: Optional[float] = None
    warning_max: Optional[float] = None
    normal_min: Optional[float] = None
    normal_max: Optional[float] = None


@dataclass
class AlertRule:
    """Defines an alert rule with conditions and actions"""
    rule_id: str
    name: str
    description: str
    alert_type: AlertType
    severity: AlertSeverity
    risk_level: RiskLevel
    threshold: RuleThreshold
    cooldown_minutes: int = 5
    auto_acknowledge: bool = False
    escalation_minutes: Optional[int] = None
    requires_immediate_action: bool = False


class MilitaryRulesEngine:
    """Military-specific rules engine for situational awareness"""
    
    def __init__(self):
        self.rules: Dict[str, AlertRule] = {}
        self.alert_history: List[Dict] = []
        self.active_alerts: Dict[str, Dict] = {}
        self.rule_states: Dict[str, Dict] = {}  # Track rule state for cooldowns
        
        # Initialize military-specific rules
        self._initialize_health_rules()
        self._initialize_logistics_rules()
        self._initialize_threat_rules()
        self._initialize_operational_rules()
        self._initialize_environmental_rules()
    
    def _initialize_health_rules(self):
        """Initialize health monitoring rules"""
        health_rules = [
            AlertRule(
                rule_id="health_heart_rate_critical",
                name="Critical Heart Rate",
                description="Heart rate outside safe operational limits",
                alert_type=AlertType.HEALTH_CRITICAL,
                severity=AlertSeverity.HIGH,
                risk_level=RiskLevel.HIGH,
                threshold=RuleThreshold(
                    critical_min=40, critical_max=180,
                    warning_min=50, warning_max=160
                ),
                cooldown_minutes=2,
                requires_immediate_action=True
            ),
            AlertRule(
                rule_id="health_spo2_critical",
                name="Critical Oxygen Saturation",
                description="Blood oxygen saturation below safe levels",
                alert_type=AlertType.MEDICAL_EMERGENCY,
                severity=AlertSeverity.HIGH,
                risk_level=RiskLevel.HIGH,
                threshold=RuleThreshold(
                    critical_min=88,
                    warning_min=92
                ),
                cooldown_minutes=1,
                requires_immediate_action=True
            ),
            AlertRule(
                rule_id="health_stress_high",
                name="High Stress Level",
                description="Soldier stress index indicates high stress",
                alert_type=AlertType.HEALTH_WARNING,
                severity=AlertSeverity.MEDIUM,
                risk_level=RiskLevel.MEDIUM,
                threshold=RuleThreshold(
                    critical_min=8.0,
                    warning_min=6.0
                ),
                cooldown_minutes=10
            ),
            AlertRule(
                rule_id="health_temperature_extreme",
                name="Extreme Body Temperature",
                description="Body temperature outside normal range",
                alert_type=AlertType.MEDICAL_EMERGENCY,
                severity=AlertSeverity.HIGH,
                risk_level=RiskLevel.HIGH,
                threshold=RuleThreshold(
                    critical_min=35.0, critical_max=39.5,
                    warning_min=36.0, warning_max=38.5
                ),
                cooldown_minutes=3,
                requires_immediate_action=True
            )
        ]
        
        for rule in health_rules:
            self.rules[rule.rule_id] = rule
    
    def _initialize_logistics_rules(self):
        """Initialize logistics monitoring rules"""
        logistics_rules = [
            AlertRule(
                rule_id="logistics_fuel_critical",
                name="Critical Fuel Level",
                description="Vehicle fuel level critically low",
                alert_type=AlertType.FUEL_LOW,
                severity=AlertSeverity.HIGH,
                risk_level=RiskLevel.HIGH,
                threshold=RuleThreshold(
                    critical_max=10.0,
                    warning_max=25.0
                ),
                cooldown_minutes=15,
                requires_immediate_action=True
            ),
            AlertRule(
                rule_id="logistics_ammo_critical",
                name="Critical Ammunition Level",
                description="Ammunition supplies critically low",
                alert_type=AlertType.AMMUNITION_LOW,
                severity=AlertSeverity.HIGH,
                risk_level=RiskLevel.HIGH,
                threshold=RuleThreshold(
                    critical_max=15.0,
                    warning_max=30.0
                ),
                cooldown_minutes=20
            ),
            AlertRule(
                rule_id="logistics_medical_low",
                name="Medical Supplies Low",
                description="Medical supplies below operational threshold",
                alert_type=AlertType.LOGISTICS_WARNING,
                severity=AlertSeverity.MEDIUM,
                risk_level=RiskLevel.MEDIUM,
                threshold=RuleThreshold(
                    critical_max=20.0,
                    warning_max=40.0
                ),
                cooldown_minutes=30
            ),
            AlertRule(
                rule_id="logistics_food_low",
                name="Food Supplies Low",
                description="Food supplies below recommended levels",
                alert_type=AlertType.LOGISTICS_WARNING,
                severity=AlertSeverity.MEDIUM,
                risk_level=RiskLevel.MEDIUM,
                threshold=RuleThreshold(
                    critical_max=25.0,
                    warning_max=50.0
                ),
                cooldown_minutes=60
            )
        ]
        
        for rule in logistics_rules:
            self.rules[rule.rule_id] = rule
    
    def _initialize_threat_rules(self):
        """Initialize threat detection rules"""
        threat_rules = [
            AlertRule(
                rule_id="threat_high_confidence",
                name="High Confidence Threat",
                description="Threat detected with high confidence level",
                alert_type=AlertType.THREAT_DETECTED,
                severity=AlertSeverity.HIGH,
                risk_level=RiskLevel.HIGH,
                threshold=RuleThreshold(
                    critical_min=0.8,
                    warning_min=0.6
                ),
                cooldown_minutes=0,  # No cooldown for threats
                requires_immediate_action=True
            ),
            AlertRule(
                rule_id="threat_weapon_signature",
                name="Weapon Signature Detected",
                description="Weapon heat signature or acoustic signature detected",
                alert_type=AlertType.THREAT_DETECTED,
                severity=AlertSeverity.HIGH,
                risk_level=RiskLevel.HIGH,
                threshold=RuleThreshold(
                    critical_min=0.5
                ),
                cooldown_minutes=0,
                requires_immediate_action=True
            ),
            AlertRule(
                rule_id="threat_multiple_detections",
                name="Multiple Threat Detections",
                description="Multiple threats detected in same area",
                alert_type=AlertType.THREAT_DETECTED,
                severity=AlertSeverity.HIGH,
                risk_level=RiskLevel.HIGH,
                threshold=RuleThreshold(
                    critical_min=3  # 3 or more threats in area
                ),
                cooldown_minutes=5
            )
        ]
        
        for rule in threat_rules:
            self.rules[rule.rule_id] = rule
    
    def _initialize_operational_rules(self):
        """Initialize operational monitoring rules"""
        operational_rules = [
            AlertRule(
                rule_id="unit_offline_extended",
                name="Unit Offline Extended",
                description="Unit has been offline for extended period",
                alert_type=AlertType.UNIT_OFFLINE,
                severity=AlertSeverity.HIGH,
                risk_level=RiskLevel.HIGH,
                threshold=RuleThreshold(
                    critical_min=300,  # 5 minutes
                    warning_min=120    # 2 minutes
                ),
                cooldown_minutes=10,
                requires_immediate_action=True
            ),
            AlertRule(
                rule_id="communication_lost",
                name="Communication Lost",
                description="Communication with unit lost",
                alert_type=AlertType.COMMUNICATION_LOST,
                severity=AlertSeverity.HIGH,
                risk_level=RiskLevel.HIGH,
                threshold=RuleThreshold(
                    critical_min=180,  # 3 minutes
                    warning_min=60     # 1 minute
                ),
                cooldown_minutes=5,
                requires_immediate_action=True
            ),
            AlertRule(
                rule_id="position_deviation",
                name="Position Deviation",
                description="Unit significantly deviated from planned route",
                alert_type=AlertType.POSITION_DEVIATION,
                severity=AlertSeverity.MEDIUM,
                risk_level=RiskLevel.MEDIUM,
                threshold=RuleThreshold(
                    critical_min=2.0,  # 2km deviation
                    warning_min=1.0    # 1km deviation
                ),
                cooldown_minutes=15
            ),
            AlertRule(
                rule_id="mission_delay",
                name="Mission Delay",
                description="Mission timeline significantly behind schedule",
                alert_type=AlertType.MISSION_DELAY,
                severity=AlertSeverity.MEDIUM,
                risk_level=RiskLevel.MEDIUM,
                threshold=RuleThreshold(
                    critical_min=30,   # 30 minutes behind
                    warning_min=15     # 15 minutes behind
                ),
                cooldown_minutes=20
            )
        ]
        
        for rule in operational_rules:
            self.rules[rule.rule_id] = rule
    
    def _initialize_environmental_rules(self):
        """Initialize environmental monitoring rules"""
        environmental_rules = [
            AlertRule(
                rule_id="weather_visibility_low",
                name="Low Visibility",
                description="Weather conditions causing low visibility",
                alert_type=AlertType.WEATHER_WARNING,
                severity=AlertSeverity.MEDIUM,
                risk_level=RiskLevel.MEDIUM,
                threshold=RuleThreshold(
                    critical_max=1.0,  # 1km visibility
                    warning_max=3.0    # 3km visibility
                ),
                cooldown_minutes=30
            ),
            AlertRule(
                rule_id="weather_wind_high",
                name="High Wind Speed",
                description="Wind speed affecting operations",
                alert_type=AlertType.WEATHER_WARNING,
                severity=AlertSeverity.MEDIUM,
                risk_level=RiskLevel.MEDIUM,
                threshold=RuleThreshold(
                    critical_min=50,   # 50 km/h
                    warning_min=35     # 35 km/h
                ),
                cooldown_minutes=45
            ),
            AlertRule(
                rule_id="weather_temperature_extreme",
                name="Extreme Temperature",
                description="Temperature conditions affecting personnel",
                alert_type=AlertType.WEATHER_WARNING,
                severity=AlertSeverity.MEDIUM,
                risk_level=RiskLevel.MEDIUM,
                threshold=RuleThreshold(
                    critical_min=-10, critical_max=45,  # °C
                    warning_min=-5, warning_max=40
                ),
                cooldown_minutes=60
            )
        ]
        
        for rule in environmental_rules:
            self.rules[rule.rule_id] = rule
    
    def evaluate_health_metrics(self, unit_id: str, health: HealthMetrics) -> List[Dict[str, Any]]:
        """Evaluate health metrics against rules"""
        alerts = []
        
        # Heart rate evaluation
        if health.heart_rate is not None:
            alert = self._evaluate_threshold(
                "health_heart_rate_critical",
                health.heart_rate,
                unit_id,
                {"metric": "heart_rate", "value": health.heart_rate, "unit": "bpm"}
            )
            if alert:
                alerts.append(alert)
        
        # SpO2 evaluation
        if health.spo2 is not None:
            alert = self._evaluate_threshold(
                "health_spo2_critical",
                health.spo2,
                unit_id,
                {"metric": "spo2", "value": health.spo2, "unit": "%"}
            )
            if alert:
                alerts.append(alert)
        
        # Stress level evaluation
        if health.stress_level is not None:
            alert = self._evaluate_threshold(
                "health_stress_high",
                health.stress_level,
                unit_id,
                {"metric": "stress_level", "value": health.stress_level, "unit": "index"}
            )
            if alert:
                alerts.append(alert)
        
        # Body temperature evaluation
        if health.body_temperature is not None:
            alert = self._evaluate_threshold(
                "health_temperature_extreme",
                health.body_temperature,
                unit_id,
                {"metric": "body_temperature", "value": health.body_temperature, "unit": "°C"}
            )
            if alert:
                alerts.append(alert)
        
        return alerts
    
    def evaluate_logistics_status(self, unit_id: str, logistics: LogisticsStatus) -> List[Dict[str, Any]]:
        """Evaluate logistics status against rules"""
        alerts = []
        
        # Fuel level evaluation
        if logistics.fuel_percent is not None:
            alert = self._evaluate_threshold(
                "logistics_fuel_critical",
                logistics.fuel_percent,
                unit_id,
                {"metric": "fuel_percent", "value": logistics.fuel_percent, "unit": "%"}
            )
            if alert:
                alerts.append(alert)
        
        # Ammunition evaluation
        if logistics.ammunition_percent is not None:
            alert = self._evaluate_threshold(
                "logistics_ammo_critical",
                logistics.ammunition_percent,
                unit_id,
                {"metric": "ammunition_percent", "value": logistics.ammunition_percent, "unit": "%"}
            )
            if alert:
                alerts.append(alert)
        
        # Medical supplies evaluation
        if logistics.medical_supplies_percent is not None:
            alert = self._evaluate_threshold(
                "logistics_medical_low",
                logistics.medical_supplies_percent,
                unit_id,
                {"metric": "medical_supplies_percent", "value": logistics.medical_supplies_percent, "unit": "%"}
            )
            if alert:
                alerts.append(alert)
        
        # Food supplies evaluation
        if logistics.food_supplies_percent is not None:
            alert = self._evaluate_threshold(
                "logistics_food_low",
                logistics.food_supplies_percent,
                unit_id,
                {"metric": "food_supplies_percent", "value": logistics.food_supplies_percent, "unit": "%"}
            )
            if alert:
                alerts.append(alert)
        
        return alerts
    
    def evaluate_threat_detection(self, threat: ThreatDetection) -> List[Dict[str, Any]]:
        """Evaluate threat detection against rules"""
        alerts = []
        
        # High confidence threat
        if threat.confidence is not None:
            alert = self._evaluate_threshold(
                "threat_high_confidence",
                threat.confidence,
                threat.unit_id or "SYSTEM",
                {
                    "threat_type": threat.threat_type,
                    "confidence": threat.confidence,
                    "location": f"{threat.latitude}, {threat.longitude}"
                }
            )
            if alert:
                alerts.append(alert)
        
        # Weapon signature specific rule
        if threat.threat_type in ["weapon_signature", "sniper_position", "improvised_explosive"]:
            alert = self._evaluate_threshold(
                "threat_weapon_signature",
                threat.confidence or 0.5,
                threat.unit_id or "SYSTEM",
                {
                    "threat_type": threat.threat_type,
                    "confidence": threat.confidence,
                    "location": f"{threat.latitude}, {threat.longitude}"
                }
            )
            if alert:
                alerts.append(alert)
        
        return alerts
    
    def evaluate_unit_status(self, unit: Unit) -> List[Dict[str, Any]]:
        """Evaluate unit operational status"""
        alerts = []
        
        # Check if unit is offline
        if unit.last_seen:
            offline_seconds = (datetime.now() - unit.last_seen).total_seconds()
            alert = self._evaluate_threshold(
                "unit_offline_extended",
                offline_seconds,
                unit.unit_id,
                {
                    "offline_duration": offline_seconds,
                    "last_seen": unit.last_seen.isoformat(),
                    "unit_type": unit.unit_type
                }
            )
            if alert:
                alerts.append(alert)
        
        return alerts
    
    def evaluate_weather_conditions(self, weather: WeatherData) -> List[Dict[str, Any]]:
        """Evaluate weather conditions against operational rules"""
        alerts = []
        
        # Visibility check
        if weather.visibility_km is not None:
            alert = self._evaluate_threshold(
                "weather_visibility_low",
                weather.visibility_km,
                "WEATHER_STATION",
                {
                    "visibility": weather.visibility_km,
                    "location": f"{weather.latitude}, {weather.longitude}"
                }
            )
            if alert:
                alerts.append(alert)
        
        # Wind speed check
        if weather.wind_speed_kmh is not None:
            alert = self._evaluate_threshold(
                "weather_wind_high",
                weather.wind_speed_kmh,
                "WEATHER_STATION",
                {
                    "wind_speed": weather.wind_speed_kmh,
                    "wind_direction": weather.wind_direction_degrees,
                    "location": f"{weather.latitude}, {weather.longitude}"
                }
            )
            if alert:
                alerts.append(alert)
        
        # Temperature check
        if weather.temperature_celsius is not None:
            alert = self._evaluate_threshold(
                "weather_temperature_extreme",
                weather.temperature_celsius,
                "WEATHER_STATION",
                {
                    "temperature": weather.temperature_celsius,
                    "humidity": weather.humidity_percent,
                    "location": f"{weather.latitude}, {weather.longitude}"
                }
            )
            if alert:
                alerts.append(alert)
        
        return alerts
    
    def _evaluate_threshold(
        self, 
        rule_id: str, 
        value: float, 
        entity_id: str, 
        context: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Evaluate a value against rule thresholds"""
        if rule_id not in self.rules:
            return None
        
        rule = self.rules[rule_id]
        threshold = rule.threshold
        
        # Check cooldown
        state_key = f"{rule_id}_{entity_id}"
        if state_key in self.rule_states:
            last_alert = self.rule_states[state_key].get("last_alert")
            if last_alert:
                time_since_alert = (datetime.now() - last_alert).total_seconds() / 60
                if time_since_alert < rule.cooldown_minutes:
                    return None
        
        # Determine severity based on thresholds
        severity = None
        risk_level = RiskLevel.LOW
        
        # Check critical thresholds
        if threshold.critical_min is not None and value < threshold.critical_min:
            severity = AlertSeverity.HIGH
            risk_level = RiskLevel.HIGH
        elif threshold.critical_max is not None and value > threshold.critical_max:
            severity = AlertSeverity.HIGH
            risk_level = RiskLevel.HIGH
        # Check warning thresholds
        elif threshold.warning_min is not None and value < threshold.warning_min:
            severity = AlertSeverity.MEDIUM
            risk_level = RiskLevel.MEDIUM
        elif threshold.warning_max is not None and value > threshold.warning_max:
            severity = AlertSeverity.MEDIUM
            risk_level = RiskLevel.MEDIUM
        
        # No threshold exceeded
        if severity is None:
            return None
        
        # Create alert
        alert_id = f"ALR-{datetime.now().strftime('%Y%m%d%H%M%S')}-{entity_id}-{rule_id[-4:]}"
        
        alert = {
            "alert_id": alert_id,
            "rule_id": rule_id,
            "rule_name": rule.name,
            "alert_type": rule.alert_type.value,
            "severity": severity.value,
            "risk_level": risk_level.value,
            "entity_id": entity_id,
            "message": self._generate_alert_message(rule, value, context),
            "timestamp": datetime.now().isoformat(),
            "acknowledged": False,
            "requires_immediate_action": rule.requires_immediate_action,
            "context": context,
            "threshold_info": {
                "value": value,
                "critical_min": threshold.critical_min,
                "critical_max": threshold.critical_max,
                "warning_min": threshold.warning_min,
                "warning_max": threshold.warning_max
            }
        }
        
        # Update rule state
        if state_key not in self.rule_states:
            self.rule_states[state_key] = {}
        self.rule_states[state_key]["last_alert"] = datetime.now()
        
        # Store alert
        self.active_alerts[alert_id] = alert
        self.alert_history.append(alert)
        
        # Limit history size
        if len(self.alert_history) > 10000:
            self.alert_history = self.alert_history[-5000:]
        
        return alert
    
    def _generate_alert_message(self, rule: AlertRule, value: float, context: Dict[str, Any]) -> str:
        """Generate human-readable alert message"""
        base_message = rule.description
        
        if rule.alert_type == AlertType.HEALTH_CRITICAL:
            metric = context.get("metric", "unknown")
            unit = context.get("unit", "")
            return f"{base_message}: {metric} = {value} {unit}"
        
        elif rule.alert_type == AlertType.LOGISTICS_CRITICAL:
            metric = context.get("metric", "unknown")
            return f"{base_message}: {metric} at {value}%"
        
        elif rule.alert_type == AlertType.THREAT_DETECTED:
            threat_type = context.get("threat_type", "unknown")
            confidence = context.get("confidence", value)
            return f"{base_message}: {threat_type} (confidence: {confidence:.2f})"
        
        elif rule.alert_type == AlertType.UNIT_OFFLINE:
            duration = context.get("offline_duration", value)
            return f"{base_message}: offline for {duration/60:.1f} minutes"
        
        elif rule.alert_type == AlertType.WEATHER_WARNING:
            if "visibility" in context:
                return f"{base_message}: visibility {value} km"
            elif "wind_speed" in context:
                return f"{base_message}: wind speed {value} km/h"
            elif "temperature" in context:
                return f"{base_message}: temperature {value}°C"
        
        return f"{base_message}: value = {value}"
    
    def get_active_alerts(self, severity_filter: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get all active alerts, optionally filtered by severity"""
        alerts = list(self.active_alerts.values())
        
        if severity_filter:
            alerts = [a for a in alerts if a["severity"] == severity_filter]
        
        # Sort by timestamp (newest first) and severity
        severity_order = {"high": 3, "medium": 2, "low": 1}
        alerts.sort(
            key=lambda x: (
                severity_order.get(x["severity"], 0),
                datetime.fromisoformat(x["timestamp"])
            ),
            reverse=True
        )
        
        return alerts
    
    def acknowledge_alert(self, alert_id: str, acknowledged_by: str) -> bool:
        """Acknowledge an alert"""
        if alert_id in self.active_alerts:
            self.active_alerts[alert_id]["acknowledged"] = True
            self.active_alerts[alert_id]["acknowledged_by"] = acknowledged_by
            self.active_alerts[alert_id]["acknowledged_at"] = datetime.now().isoformat()
            return True
        return False
    
    def get_risk_assessment(self, entity_id: str) -> Dict[str, Any]:
        """Get comprehensive risk assessment for an entity"""
        entity_alerts = [
            alert for alert in self.active_alerts.values()
            if alert["entity_id"] == entity_id and not alert["acknowledged"]
        ]
        
        if not entity_alerts:
            return {
                "entity_id": entity_id,
                "overall_risk": "low",
                "risk_score": 0,
                "active_alerts": 0,
                "critical_alerts": 0,
                "assessment_time": datetime.now().isoformat()
            }
        
        # Calculate risk score
        risk_score = 0
        critical_count = 0
        
        for alert in entity_alerts:
            if alert["severity"] == "high":
                risk_score += 10
                critical_count += 1
            elif alert["severity"] == "medium":
                risk_score += 5
            else:
                risk_score += 1
        
        # Determine overall risk level
        if risk_score >= 20 or critical_count >= 2:
            overall_risk = "high"
        elif risk_score >= 10 or critical_count >= 1:
            overall_risk = "medium"
        else:
            overall_risk = "low"
        
        return {
            "entity_id": entity_id,
            "overall_risk": overall_risk,
            "risk_score": risk_score,
            "active_alerts": len(entity_alerts),
            "critical_alerts": critical_count,
            "alert_types": list(set(alert["alert_type"] for alert in entity_alerts)),
            "assessment_time": datetime.now().isoformat(),
            "requires_immediate_attention": any(
                alert["requires_immediate_action"] for alert in entity_alerts
            )
        }
    
    def get_system_health_summary(self) -> Dict[str, Any]:
        """Get overall system health summary"""
        all_alerts = list(self.active_alerts.values())
        unacknowledged_alerts = [a for a in all_alerts if not a["acknowledged"]]
        
        critical_alerts = [a for a in unacknowledged_alerts if a["severity"] == "high"]
        medium_alerts = [a for a in unacknowledged_alerts if a["severity"] == "medium"]
        low_alerts = [a for a in unacknowledged_alerts if a["severity"] == "low"]
        
        # Calculate system risk level
        if len(critical_alerts) >= 3:
            system_risk = "critical"
        elif len(critical_alerts) >= 1 or len(medium_alerts) >= 5:
            system_risk = "high"
        elif len(medium_alerts) >= 2 or len(low_alerts) >= 10:
            system_risk = "medium"
        else:
            system_risk = "low"
        
        return {
            "system_risk_level": system_risk,
            "total_active_alerts": len(unacknowledged_alerts),
            "critical_alerts": len(critical_alerts),
            "medium_alerts": len(medium_alerts),
            "low_alerts": len(low_alerts),
            "immediate_action_required": len([
                a for a in critical_alerts if a["requires_immediate_action"]
            ]),
            "alert_types_summary": self._get_alert_types_summary(unacknowledged_alerts),
            "assessment_time": datetime.now().isoformat()
        }
    
    def _get_alert_types_summary(self, alerts: List[Dict]) -> Dict[str, int]:
        """Get summary of alert types"""
        summary = {}
        for alert in alerts:
            alert_type = alert["alert_type"]
            summary[alert_type] = summary.get(alert_type, 0) + 1
        return summary
    
    def cleanup_old_alerts(self, hours: int = 24):
        """Clean up old acknowledged alerts"""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        
        alerts_to_remove = []
        for alert_id, alert in self.active_alerts.items():
            if alert["acknowledged"]:
                alert_time = datetime.fromisoformat(alert["timestamp"])
                if alert_time < cutoff_time:
                    alerts_to_remove.append(alert_id)
        
        for alert_id in alerts_to_remove:
            del self.active_alerts[alert_id]
        
        return len(alerts_to_remove)


# Global rules engine instance
rules_engine = MilitaryRulesEngine()


# Example usage and testing
if __name__ == "__main__":
    # Test health metrics evaluation
    from core.models import HealthMetrics
    
    # Simulate critical health condition
    critical_health = HealthMetrics(
        unit_id="UNIT-001",
        heart_rate=190,  # Critical high
        spo2=85,         # Critical low
        stress_level=9.0, # Critical high
        body_temperature=40.0,  # Critical high
        timestamp=datetime.now()
    )
    
    alerts = rules_engine.evaluate_health_metrics("UNIT-001", critical_health)
    print(f"Generated {len(alerts)} health alerts:")
    for alert in alerts:
        print(f"  - {alert['rule_name']}: {alert['message']} (Severity: {alert['severity']})")
    
    # Test system health summary
    summary = rules_engine.get_system_health_summary()
    print(f"\nSystem Health Summary:")
    print(f"  Risk Level: {summary['system_risk_level']}")
    print(f"  Active Alerts: {summary['total_active_alerts']}")
    print(f"  Critical: {summary['critical_alerts']}")