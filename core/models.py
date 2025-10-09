"""
MSA Dashboard - Core Data Models
Pydantic models for military situational awareness data
"""

from datetime import datetime
from enum import Enum
from typing import Optional, List
from pydantic import BaseModel, Field


class RiskLevel(str, Enum):
    """Risk level enumeration with color coding"""
    GREEN = "green"      # Normal status
    AMBER = "amber"      # Medium risk
    RED = "red"          # Critical risk


class UnitType(str, Enum):
    """Military unit types"""
    INFANTRY = "infantry"
    ARMOR = "armor"
    ARTILLERY = "artillery"
    RECON = "recon"
    SUPPORT = "support"
    COMMAND = "command"


class AlertSeverity(str, Enum):
    """Alert severity levels"""
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"
    EMERGENCY = "emergency"


class MissionPhase(str, Enum):
    """Mission phase status"""
    PLANNING = "planning"
    PREPARATION = "preparation"
    EXECUTION = "execution"
    CONSOLIDATION = "consolidation"
    COMPLETED = "completed"


class UserRole(str, Enum):
    """User roles for dashboard access"""
    COMMANDER = "commander"
    HEALTH_OFFICER = "health_officer"
    OPERATIONS_ANALYST = "operations_analyst"


# Base Models
class BaseTimestampModel(BaseModel):
    """Base model with timestamp"""
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class Position(BaseModel):
    """Geographic position"""
    latitude: float = Field(..., ge=-90, le=90, description="Latitude in degrees")
    longitude: float = Field(..., ge=-180, le=180, description="Longitude in degrees")
    altitude: Optional[float] = Field(None, description="Altitude in meters")


# Unit Models
class Unit(BaseTimestampModel):
    """Military unit basic information"""
    unit_id: str = Field(..., description="Unique unit identifier")
    name: str = Field(..., description="Unit name/callsign")
    unit_type: UnitType
    position: Position
    heading: Optional[float] = Field(None, ge=0, le=360, description="Heading in degrees")
    speed: Optional[float] = Field(None, ge=0, description="Speed in km/h")
    status: RiskLevel = Field(default=RiskLevel.GREEN)
    last_seen: datetime = Field(default_factory=datetime.utcnow)


class UnitUpdate(BaseModel):
    """Unit position and status update"""
    unit_id: str
    position: Optional[Position] = None
    heading: Optional[float] = Field(None, ge=0, le=360)
    speed: Optional[float] = Field(None, ge=0)
    status: Optional[RiskLevel] = None


# Health Models
class HealthMetrics(BaseTimestampModel):
    """Soldier health metrics from biosensors"""
    unit_id: str
    heart_rate: Optional[int] = Field(None, ge=30, le=220, description="Heart rate in BPM")
    spo2: Optional[float] = Field(None, ge=0, le=100, description="Blood oxygen saturation %")
    stress_index: Optional[float] = Field(None, ge=0, le=100, description="Stress level 0-100")
    body_temperature: Optional[float] = Field(None, ge=30, le=45, description="Body temperature in Celsius")
    risk_level: RiskLevel = Field(default=RiskLevel.GREEN)


class HealthThresholds(BaseModel):
    """Health monitoring thresholds"""
    heart_rate_min: int = Field(default=60)
    heart_rate_max: int = Field(default=180)
    spo2_min: float = Field(default=95.0)
    stress_max: float = Field(default=70.0)
    temp_min: float = Field(default=36.0)
    temp_max: float = Field(default=38.5)


# Logistics Models
class LogisticsStatus(BaseTimestampModel):
    """Unit logistics status"""
    unit_id: str
    ammunition_pct: float = Field(..., ge=0, le=100, description="Ammunition level %")
    fuel_pct: float = Field(..., ge=0, le=100, description="Fuel level %")
    medical_supplies_pct: float = Field(..., ge=0, le=100, description="Medical supplies %")
    food_water_pct: float = Field(..., ge=0, le=100, description="Food and water %")
    risk_level: RiskLevel = Field(default=RiskLevel.GREEN)


# Weather Models
class WeatherData(BaseTimestampModel):
    """Weather station data"""
    station_id: str
    position: Position
    temperature: float = Field(..., description="Temperature in Celsius")
    humidity: float = Field(..., ge=0, le=100, description="Humidity %")
    wind_speed: float = Field(..., ge=0, description="Wind speed in km/h")
    wind_direction: float = Field(..., ge=0, le=360, description="Wind direction in degrees")
    visibility: float = Field(..., ge=0, description="Visibility in km")
    pressure: Optional[float] = Field(None, description="Atmospheric pressure in hPa")


# Threat Models
class ThreatDetection(BaseTimestampModel):
    """Threat detection from drones/sensors"""
    detection_id: str
    source_unit_id: str  # Drone or sensor unit
    threat_type: str = Field(..., description="Type of threat detected")
    position: Position
    confidence: float = Field(..., ge=0, le=1, description="Detection confidence 0-1")
    severity: AlertSeverity
    description: Optional[str] = None
    image_url: Optional[str] = None


# Alert Models
class Alert(BaseTimestampModel):
    """System alert/notification"""
    alert_id: str
    unit_id: Optional[str] = None
    alert_type: str = Field(..., description="Type of alert")
    severity: AlertSeverity
    title: str = Field(..., description="Alert title")
    message: str = Field(..., description="Alert message")
    acknowledged: bool = Field(default=False)
    acknowledged_by: Optional[str] = None
    acknowledged_at: Optional[datetime] = None
    resolved: bool = Field(default=False)
    resolved_at: Optional[datetime] = None


# Mission Models
class Mission(BaseTimestampModel):
    """Mission information"""
    mission_id: str
    name: str = Field(..., description="Mission name")
    description: Optional[str] = None
    phase: MissionPhase = Field(default=MissionPhase.PLANNING)
    progress_pct: float = Field(default=0.0, ge=0, le=100, description="Mission progress %")
    start_time: Optional[datetime] = None
    estimated_end_time: Optional[datetime] = None
    actual_end_time: Optional[datetime] = None
    assigned_units: List[str] = Field(default_factory=list, description="List of unit IDs")
    objectives: List[str] = Field(default_factory=list, description="Mission objectives")
    status: RiskLevel = Field(default=RiskLevel.GREEN)


class MissionObjective(BaseTimestampModel):
    """Individual mission objective"""
    objective_id: str
    mission_id: str
    title: str
    description: Optional[str] = None
    completed: bool = Field(default=False)
    completed_at: Optional[datetime] = None
    priority: int = Field(default=1, ge=1, le=5, description="Priority 1-5")


# Dashboard Models
class DashboardConfig(BaseModel):
    """Dashboard configuration for different user roles"""
    user_role: UserRole
    visible_panels: List[str] = Field(default_factory=list)
    map_layers: List[str] = Field(default_factory=list)
    alert_filters: List[AlertSeverity] = Field(default_factory=list)
    refresh_interval: int = Field(default=5, description="Refresh interval in seconds")


# API Response Models
class SystemStatus(BaseModel):
    """Overall system status"""
    total_units: int
    active_units: int
    critical_alerts: int
    active_missions: int
    system_health: RiskLevel
    last_updated: datetime = Field(default_factory=datetime.utcnow)


class DashboardData(BaseModel):
    """Complete dashboard data payload"""
    units: List[Unit]
    health_metrics: List[HealthMetrics]
    logistics: List[LogisticsStatus]
    alerts: List[Alert]
    missions: List[Mission]
    weather: List[WeatherData]
    threats: List[ThreatDetection]
    system_status: SystemStatus
    timestamp: datetime = Field(default_factory=datetime.utcnow)


# WebSocket Message Models
class WSMessage(BaseModel):
    """WebSocket message base"""
    message_type: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class WSUnitUpdate(WSMessage):
    """WebSocket unit update message"""
    message_type: str = "unit_update"
    data: Unit


class WSAlertMessage(WSMessage):
    """WebSocket alert message"""
    message_type: str = "alert"
    data: Alert


class WSHealthUpdate(WSMessage):
    """WebSocket health update message"""
    message_type: str = "health_update"
    data: HealthMetrics


class WSThreatAlert(WSMessage):
    """WebSocket threat alert message"""
    message_type: str = "threat_alert"
    data: ThreatDetection