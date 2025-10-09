"""
Database models for MSA Dashboard
"""
from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Dict, Any
import json

@dataclass
class Event:
    """Event model for storing historical events"""
    id: Optional[int] = None
    timestamp: Optional[datetime] = None
    event_type: str = ""
    category: str = ""  # unit, alert, health, logistics, system
    source_id: str = ""  # unit_id, alert_id, etc.
    title: str = ""
    description: str = ""
    severity: str = "info"  # info, warning, error, critical
    location_lat: Optional[float] = None
    location_lng: Optional[float] = None
    metadata: Optional[Dict[str, Any]] = None
    user_id: Optional[str] = None
    acknowledged: bool = False
    acknowledged_by: Optional[str] = None
    acknowledged_at: Optional[datetime] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'id': self.id,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
            'event_type': self.event_type,
            'category': self.category,
            'source_id': self.source_id,
            'title': self.title,
            'description': self.description,
            'severity': self.severity,
            'location_lat': self.location_lat,
            'location_lng': self.location_lng,
            'metadata': json.dumps(self.metadata) if self.metadata else None,
            'user_id': self.user_id,
            'acknowledged': self.acknowledged,
            'acknowledged_by': self.acknowledged_by,
            'acknowledged_at': self.acknowledged_at.isoformat() if self.acknowledged_at else None
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Event':
        """Create from dictionary"""
        return cls(
            id=data.get('id'),
            timestamp=datetime.fromisoformat(data['timestamp']) if data.get('timestamp') else None,
            event_type=data.get('event_type', ''),
            category=data.get('category', ''),
            source_id=data.get('source_id', ''),
            title=data.get('title', ''),
            description=data.get('description', ''),
            severity=data.get('severity', 'info'),
            location_lat=data.get('location_lat'),
            location_lng=data.get('location_lng'),
            metadata=json.loads(data['metadata']) if data.get('metadata') else None,
            user_id=data.get('user_id'),
            acknowledged=bool(data.get('acknowledged', False)),
            acknowledged_by=data.get('acknowledged_by'),
            acknowledged_at=datetime.fromisoformat(data['acknowledged_at']) if data.get('acknowledged_at') else None
        )

@dataclass
class UserSession:
    """User session model"""
    id: Optional[int] = None
    user_id: str = ""
    username: str = ""
    role: str = ""
    login_time: Optional[datetime] = None
    logout_time: Optional[datetime] = None
    ip_address: str = ""
    user_agent: str = ""
    session_token: str = ""
    is_active: bool = True
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'username': self.username,
            'role': self.role,
            'login_time': self.login_time.isoformat() if self.login_time else None,
            'logout_time': self.logout_time.isoformat() if self.logout_time else None,
            'ip_address': self.ip_address,
            'user_agent': self.user_agent,
            'session_token': self.session_token,
            'is_active': self.is_active
        }

@dataclass
class SystemMetric:
    """System metrics model"""
    id: Optional[int] = None
    timestamp: Optional[datetime] = None
    metric_name: str = ""
    metric_value: float = 0.0
    unit: str = ""
    category: str = ""  # performance, health, security, etc.
    source: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'id': self.id,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
            'metric_name': self.metric_name,
            'metric_value': self.metric_value,
            'unit': self.unit,
            'category': self.category,
            'source': self.source
        }

@dataclass
class Unit:
    """Military unit model"""
    id: Optional[int] = None
    unit_id: str = ""
    name: str = ""
    unit_type: str = ""  # infantry, armor, air, naval, special
    status: str = "active"  # active, inactive, maintenance, deployed
    location_lat: Optional[float] = None
    location_lng: Optional[float] = None
    altitude: Optional[float] = None
    heading: Optional[float] = None
    speed: Optional[float] = None
    fuel_level: Optional[float] = None
    ammunition: Optional[int] = None
    personnel_count: Optional[int] = None
    commander: str = ""
    mission_id: Optional[str] = None
    last_contact: Optional[datetime] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'id': self.id,
            'unit_id': self.unit_id,
            'name': self.name,
            'unit_type': self.unit_type,
            'status': self.status,
            'location_lat': self.location_lat,
            'location_lng': self.location_lng,
            'altitude': self.altitude,
            'heading': self.heading,
            'speed': self.speed,
            'fuel_level': self.fuel_level,
            'ammunition': self.ammunition,
            'personnel_count': self.personnel_count,
            'commander': self.commander,
            'mission_id': self.mission_id,
            'last_contact': self.last_contact.isoformat() if self.last_contact else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

@dataclass
class Alert:
    """Alert/threat model"""
    id: Optional[int] = None
    alert_id: str = ""
    title: str = ""
    description: str = ""
    alert_type: str = ""  # threat, equipment, personnel, weather, intel
    severity: str = "low"  # low, medium, high, critical
    status: str = "active"  # active, resolved, investigating
    location_lat: Optional[float] = None
    location_lng: Optional[float] = None
    radius: Optional[float] = None  # affected area radius in meters
    source: str = ""  # sensor, intel, manual, automated
    confidence: Optional[float] = None  # 0.0 to 1.0
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    resolved_at: Optional[datetime] = None
    assigned_to: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'id': self.id,
            'alert_id': self.alert_id,
            'title': self.title,
            'description': self.description,
            'alert_type': self.alert_type,
            'severity': self.severity,
            'status': self.status,
            'location_lat': self.location_lat,
            'location_lng': self.location_lng,
            'radius': self.radius,
            'source': self.source,
            'confidence': self.confidence,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'resolved_at': self.resolved_at.isoformat() if self.resolved_at else None,
            'assigned_to': self.assigned_to
        }

@dataclass
class Mission:
    """Mission model"""
    id: Optional[int] = None
    mission_id: str = ""
    name: str = ""
    description: str = ""
    mission_type: str = ""  # patrol, reconnaissance, assault, defense, support
    status: str = "planned"  # planned, active, completed, cancelled, paused
    priority: str = "medium"  # low, medium, high, critical
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    estimated_duration: Optional[int] = None  # minutes
    commander: str = ""
    assigned_units: Optional[str] = None  # JSON array of unit_ids
    objectives: Optional[str] = None  # JSON array of objectives
    location_lat: Optional[float] = None
    location_lng: Optional[float] = None
    area_of_operation: Optional[str] = None  # JSON polygon coordinates
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'id': self.id,
            'mission_id': self.mission_id,
            'name': self.name,
            'description': self.description,
            'mission_type': self.mission_type,
            'status': self.status,
            'priority': self.priority,
            'start_time': self.start_time.isoformat() if self.start_time else None,
            'end_time': self.end_time.isoformat() if self.end_time else None,
            'estimated_duration': self.estimated_duration,
            'commander': self.commander,
            'assigned_units': self.assigned_units,
            'objectives': self.objectives,
            'location_lat': self.location_lat,
            'location_lng': self.location_lng,
            'area_of_operation': self.area_of_operation,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

@dataclass
class Equipment:
    """Equipment model"""
    id: Optional[int] = None
    equipment_id: str = ""
    name: str = ""
    equipment_type: str = ""  # vehicle, weapon, communication, medical, supply
    status: str = "operational"  # operational, maintenance, damaged, destroyed
    condition: str = "good"  # excellent, good, fair, poor
    location_lat: Optional[float] = None
    location_lng: Optional[float] = None
    assigned_unit: Optional[str] = None
    maintenance_due: Optional[datetime] = None
    last_maintenance: Optional[datetime] = None
    specifications: Optional[str] = None  # JSON object
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'id': self.id,
            'equipment_id': self.equipment_id,
            'name': self.name,
            'equipment_type': self.equipment_type,
            'status': self.status,
            'condition': self.condition,
            'location_lat': self.location_lat,
            'location_lng': self.location_lng,
            'assigned_unit': self.assigned_unit,
            'maintenance_due': self.maintenance_due.isoformat() if self.maintenance_due else None,
            'last_maintenance': self.last_maintenance.isoformat() if self.last_maintenance else None,
            'specifications': self.specifications,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }