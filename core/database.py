"""
MSA Dashboard - Database Models and Configuration
SQLAlchemy models and database setup
"""

from datetime import datetime
from typing import Optional
from sqlalchemy import (
    Column, String, Integer, Float, Boolean, DateTime, Text, 
    ForeignKey, Enum as SQLEnum, JSON, Index
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import create_engine
import uuid

from .models import RiskLevel, UnitType, AlertSeverity, MissionPhase, UserRole
from .settings import settings

Base = declarative_base()


# Database Models
class UnitDB(Base):
    """Unit database model"""
    __tablename__ = "units"
    
    unit_id = Column(String(50), primary_key=True)
    name = Column(String(100), nullable=False)
    unit_type = Column(SQLEnum(UnitType), nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    altitude = Column(Float, nullable=True)
    heading = Column(Float, nullable=True)
    speed = Column(Float, nullable=True)
    status = Column(SQLEnum(RiskLevel), default=RiskLevel.GREEN)
    last_seen = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    health_metrics = relationship("HealthMetricsDB", back_populates="unit")
    logistics = relationship("LogisticsStatusDB", back_populates="unit")
    alerts = relationship("AlertDB", back_populates="unit")
    
    # Indexes for performance
    __table_args__ = (
        Index('idx_unit_status', 'status'),
        Index('idx_unit_type', 'unit_type'),
        Index('idx_unit_last_seen', 'last_seen'),
        Index('idx_unit_location', 'latitude', 'longitude'),
    )


class HealthMetricsDB(Base):
    """Health metrics database model"""
    __tablename__ = "health_metrics"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    unit_id = Column(String(50), ForeignKey("units.unit_id"), nullable=False)
    heart_rate = Column(Integer, nullable=True)
    spo2 = Column(Float, nullable=True)
    stress_index = Column(Float, nullable=True)
    body_temperature = Column(Float, nullable=True)
    risk_level = Column(SQLEnum(RiskLevel), default=RiskLevel.GREEN)
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    unit = relationship("UnitDB", back_populates="health_metrics")
    
    # Indexes for time-series queries
    __table_args__ = (
        Index('idx_health_unit_time', 'unit_id', 'timestamp'),
        Index('idx_health_risk', 'risk_level'),
        Index('idx_health_timestamp', 'timestamp'),
    )


class LogisticsStatusDB(Base):
    """Logistics status database model"""
    __tablename__ = "logistics_status"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    unit_id = Column(String(50), ForeignKey("units.unit_id"), nullable=False)
    ammunition_pct = Column(Float, nullable=False)
    fuel_pct = Column(Float, nullable=False)
    medical_supplies_pct = Column(Float, nullable=False)
    food_water_pct = Column(Float, nullable=False)
    risk_level = Column(SQLEnum(RiskLevel), default=RiskLevel.GREEN)
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    unit = relationship("UnitDB", back_populates="logistics")
    
    # Indexes
    __table_args__ = (
        Index('idx_logistics_unit_time', 'unit_id', 'timestamp'),
        Index('idx_logistics_risk', 'risk_level'),
    )


class WeatherDataDB(Base):
    """Weather data database model"""
    __tablename__ = "weather_data"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    station_id = Column(String(50), nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    altitude = Column(Float, nullable=True)
    temperature = Column(Float, nullable=False)
    humidity = Column(Float, nullable=False)
    wind_speed = Column(Float, nullable=False)
    wind_direction = Column(Float, nullable=False)
    visibility = Column(Float, nullable=False)
    pressure = Column(Float, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    # Indexes
    __table_args__ = (
        Index('idx_weather_station_time', 'station_id', 'timestamp'),
        Index('idx_weather_location', 'latitude', 'longitude'),
    )


class ThreatDetectionDB(Base):
    """Threat detection database model"""
    __tablename__ = "threat_detections"
    
    detection_id = Column(String(50), primary_key=True)
    source_unit_id = Column(String(50), nullable=False)
    threat_type = Column(String(100), nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    altitude = Column(Float, nullable=True)
    confidence = Column(Float, nullable=False)
    severity = Column(SQLEnum(AlertSeverity), nullable=False)
    description = Column(Text, nullable=True)
    image_url = Column(String(500), nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    # Indexes
    __table_args__ = (
        Index('idx_threat_severity_time', 'severity', 'timestamp'),
        Index('idx_threat_location', 'latitude', 'longitude'),
        Index('idx_threat_source', 'source_unit_id'),
    )


class AlertDB(Base):
    """Alert database model"""
    __tablename__ = "alerts"
    
    alert_id = Column(String(50), primary_key=True)
    unit_id = Column(String(50), ForeignKey("units.unit_id"), nullable=True)
    alert_type = Column(String(100), nullable=False)
    severity = Column(SQLEnum(AlertSeverity), nullable=False)
    title = Column(String(200), nullable=False)
    message = Column(Text, nullable=False)
    acknowledged = Column(Boolean, default=False)
    acknowledged_by = Column(String(100), nullable=True)
    acknowledged_at = Column(DateTime, nullable=True)
    resolved = Column(Boolean, default=False)
    resolved_at = Column(DateTime, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    unit = relationship("UnitDB", back_populates="alerts")
    
    # Indexes
    __table_args__ = (
        Index('idx_alert_severity_time', 'severity', 'timestamp'),
        Index('idx_alert_unit', 'unit_id'),
        Index('idx_alert_acknowledged', 'acknowledged'),
        Index('idx_alert_resolved', 'resolved'),
    )


class MissionDB(Base):
    """Mission database model"""
    __tablename__ = "missions"
    
    mission_id = Column(String(50), primary_key=True)
    name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    phase = Column(SQLEnum(MissionPhase), default=MissionPhase.PLANNING)
    progress_pct = Column(Float, default=0.0)
    start_time = Column(DateTime, nullable=True)
    estimated_end_time = Column(DateTime, nullable=True)
    actual_end_time = Column(DateTime, nullable=True)
    assigned_units = Column(JSON, nullable=True)  # List of unit IDs
    objectives = Column(JSON, nullable=True)  # List of objectives
    status = Column(SQLEnum(RiskLevel), default=RiskLevel.GREEN)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    objectives_rel = relationship("MissionObjectiveDB", back_populates="mission")
    
    # Indexes
    __table_args__ = (
        Index('idx_mission_phase', 'phase'),
        Index('idx_mission_status', 'status'),
    )


class MissionObjectiveDB(Base):
    """Mission objective database model"""
    __tablename__ = "mission_objectives"
    
    objective_id = Column(String(50), primary_key=True)
    mission_id = Column(String(50), ForeignKey("missions.mission_id"), nullable=False)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    completed = Column(Boolean, default=False)
    completed_at = Column(DateTime, nullable=True)
    priority = Column(Integer, default=1)
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    mission = relationship("MissionDB", back_populates="objectives_rel")


class UserDB(Base):
    """User database model for authentication"""
    __tablename__ = "users"
    
    user_id = Column(String(50), primary_key=True)
    username = Column(String(100), unique=True, nullable=False)
    email = Column(String(200), unique=True, nullable=False)
    hashed_password = Column(String(200), nullable=False)
    full_name = Column(String(200), nullable=True)
    role = Column(SQLEnum(UserRole), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_login = Column(DateTime, nullable=True)


# Database Engine and Session
def create_database_engine():
    """Create database engine based on settings"""
    engine = create_engine(
        settings.database_url,
        echo=settings.database_echo,
        pool_pre_ping=True,
        pool_recycle=300
    )
    return engine


def get_session_maker():
    """Get SQLAlchemy session maker"""
    engine = create_database_engine()
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    return SessionLocal


def create_tables():
    """Create all database tables"""
    engine = create_database_engine()
    Base.metadata.create_all(bind=engine)


def get_db():
    """Dependency to get database session"""
    SessionLocal = get_session_maker()
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Database initialization
engine = create_database_engine()
SessionLocal = get_session_maker()