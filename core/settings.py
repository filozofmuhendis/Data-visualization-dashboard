"""
MSA Dashboard - Application Settings
Configuration management using Pydantic Settings
"""

from typing import List, Optional
from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings with environment variable support"""
    
    # Application
    app_name: str = Field(default="MSA Dashboard", description="Application name")
    app_version: str = Field(default="1.0.0", description="Application version")
    debug: bool = Field(default=False, description="Debug mode")
    
    # Server
    host: str = Field(default="0.0.0.0", description="Server host")
    port: int = Field(default=8000, description="Server port")
    reload: bool = Field(default=False, description="Auto-reload on code changes")
    
    # Database
    database_url: str = Field(
        default="sqlite:///./msa_dashboard.db",
        description="Database connection URL"
    )
    database_echo: bool = Field(default=False, description="Echo SQL queries")
    
    # Redis (for caching and real-time data)
    redis_url: Optional[str] = Field(default=None, description="Redis connection URL")
    
    # MQTT Settings (for IoT data ingestion)
    mqtt_broker_host: str = Field(default="localhost", description="MQTT broker host")
    mqtt_broker_port: int = Field(default=1883, description="MQTT broker port")
    mqtt_username: Optional[str] = Field(default=None, description="MQTT username")
    mqtt_password: Optional[str] = Field(default=None, description="MQTT password")
    mqtt_topics: List[str] = Field(
        default=[
            "msa/units/+/position",
            "msa/units/+/health",
            "msa/units/+/logistics",
            "msa/drones/+/threats",
            "msa/weather/+/data"
        ],
        description="MQTT topics to subscribe to"
    )
    
    # Security
    secret_key: str = Field(
        default="your-secret-key-change-in-production",
        description="Secret key for JWT tokens"
    )
    algorithm: str = Field(default="HS256", description="JWT algorithm")
    access_token_expire_minutes: int = Field(
        default=30,
        description="Access token expiration time in minutes"
    )
    
    # Dashboard Settings
    default_refresh_interval: int = Field(
        default=5,
        description="Default dashboard refresh interval in seconds"
    )
    max_alerts_display: int = Field(
        default=50,
        description="Maximum number of alerts to display"
    )
    map_default_zoom: int = Field(default=10, description="Default map zoom level")
    map_default_center: List[float] = Field(
        default=[39.9334, 32.8597],  # Ankara, Turkey
        description="Default map center [lat, lon]"
    )
    
    # Health Monitoring Thresholds
    health_check_interval: int = Field(
        default=30,
        description="Health check interval in seconds"
    )
    critical_heart_rate_min: int = Field(default=50, description="Critical low heart rate")
    critical_heart_rate_max: int = Field(default=200, description="Critical high heart rate")
    critical_spo2_min: float = Field(default=90.0, description="Critical low SpO2")
    critical_stress_max: float = Field(default=85.0, description="Critical stress level")
    
    # Logistics Thresholds
    critical_ammo_threshold: float = Field(
        default=20.0,
        description="Critical ammunition level %"
    )
    critical_fuel_threshold: float = Field(
        default=15.0,
        description="Critical fuel level %"
    )
    critical_medical_threshold: float = Field(
        default=25.0,
        description="Critical medical supplies level %"
    )
    
    # Data Simulation (for development/demo)
    enable_simulation: bool = Field(
        default=True,
        description="Enable data simulation for demo"
    )
    simulation_units_count: int = Field(
        default=12,
        description="Number of units to simulate"
    )
    simulation_update_interval: int = Field(
        default=2,
        description="Simulation update interval in seconds"
    )
    
    # Logging
    log_level: str = Field(default="INFO", description="Logging level")
    log_format: str = Field(
        default="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        description="Log format"
    )
    
    # CORS Settings
    cors_origins: List[str] = Field(
        default=["http://localhost:3000", "http://localhost:8050"],
        description="Allowed CORS origins"
    )
    
    # File Upload
    max_file_size: int = Field(
        default=10 * 1024 * 1024,  # 10MB
        description="Maximum file upload size in bytes"
    )
    upload_directory: str = Field(
        default="./uploads",
        description="Directory for file uploads"
    )
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


# Global settings instance
settings = Settings()


# Role-based dashboard configurations
ROLE_CONFIGS = {
    "commander": {
        "visible_panels": [
            "map",
            "system_status",
            "critical_alerts",
            "mission_overview",
            "unit_summary"
        ],
        "map_layers": [
            "units",
            "threats",
            "missions",
            "weather"
        ],
        "alert_filters": ["critical", "emergency"],
        "refresh_interval": 3
    },
    "health_officer": {
        "visible_panels": [
            "map",
            "health_monitoring",
            "health_alerts",
            "unit_health_details",
            "health_statistics"
        ],
        "map_layers": [
            "units",
            "health_status"
        ],
        "alert_filters": ["warning", "critical", "emergency"],
        "refresh_interval": 5
    },
    "operations_analyst": {
        "visible_panels": [
            "map",
            "logistics_status",
            "mission_progress",
            "performance_metrics",
            "resource_allocation"
        ],
        "map_layers": [
            "units",
            "logistics",
            "missions",
            "supply_routes"
        ],
        "alert_filters": ["info", "warning", "critical"],
        "refresh_interval": 10
    }
}


# Color schemes for risk levels
RISK_COLORS = {
    "green": "#28a745",    # Success green
    "amber": "#ffc107",    # Warning amber
    "red": "#dc3545"       # Danger red
}


# Map configuration
MAP_CONFIG = {
    "tile_layer": "https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png",
    "attribution": "© OpenStreetMap contributors",
    "min_zoom": 3,
    "max_zoom": 18,
    "map_default_center": [39.8283, -98.5795],  # Center of USA
    "map_default_zoom": 4,
    "unit_icon_size": [30, 30],
    "threat_icon_size": [25, 25],
    "cluster_max_zoom": 15
}