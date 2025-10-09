"""
MSA Dashboard - Role Management Service
Handles user authentication, role-based access control, and customized dashboard configurations
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional, Set, Any
from dataclasses import dataclass
from enum import Enum
import hashlib
import secrets
import jwt

from core.models import UserRole
from core.settings import settings


class Permission(Enum):
    """System permissions"""
    VIEW_ALL_UNITS = "view_all_units"
    VIEW_HEALTH_DATA = "view_health_data"
    VIEW_LOGISTICS_DATA = "view_logistics_data"
    VIEW_THREAT_DATA = "view_threat_data"
    VIEW_MISSION_DATA = "view_mission_data"
    MANAGE_ALERTS = "manage_alerts"
    ACKNOWLEDGE_ALERTS = "acknowledge_alerts"
    MODIFY_THRESHOLDS = "modify_thresholds"
    CONTROL_UNITS = "control_units"
    VIEW_ANALYTICS = "view_analytics"
    SYSTEM_ADMIN = "system_admin"
    EXPORT_DATA = "export_data"


@dataclass
class UserSession:
    """User session information"""
    user_id: str
    username: str
    role: UserRole
    permissions: Set[Permission]
    login_time: datetime
    last_activity: datetime
    session_token: str
    expires_at: datetime


@dataclass
class DashboardLayout:
    """Dashboard layout configuration for a role"""
    role: UserRole
    panels: List[str]
    panel_configs: Dict[str, Dict[str, Any]]
    default_filters: Dict[str, Any]
    refresh_intervals: Dict[str, int]
    color_scheme: Dict[str, str]
    map_config: Dict[str, Any]


class RoleManager:
    """Manages user roles, permissions, and dashboard configurations"""
    
    def __init__(self):
        self.active_sessions: Dict[str, UserSession] = {}
        self.role_permissions = self._initialize_role_permissions()
        self.dashboard_layouts = self._initialize_dashboard_layouts()
        self.session_timeout = timedelta(hours=8)
    
    def _initialize_role_permissions(self) -> Dict[UserRole, Set[Permission]]:
        """Initialize role-based permissions"""
        return {
            UserRole.COMMANDER: {
                Permission.VIEW_ALL_UNITS,
                Permission.VIEW_HEALTH_DATA,
                Permission.VIEW_LOGISTICS_DATA,
                Permission.VIEW_THREAT_DATA,
                Permission.VIEW_MISSION_DATA,
                Permission.MANAGE_ALERTS,
                Permission.ACKNOWLEDGE_ALERTS,
                Permission.CONTROL_UNITS,
                Permission.VIEW_ANALYTICS,
                Permission.EXPORT_DATA
            },
            UserRole.HEALTH_OFFICER: {
                Permission.VIEW_ALL_UNITS,
                Permission.VIEW_HEALTH_DATA,
                Permission.VIEW_LOGISTICS_DATA,
                Permission.ACKNOWLEDGE_ALERTS,
                Permission.MODIFY_THRESHOLDS,
                Permission.VIEW_ANALYTICS,
                Permission.EXPORT_DATA
            },
            UserRole.OPERATIONS_ANALYST: {
                Permission.VIEW_ALL_UNITS,
                Permission.VIEW_LOGISTICS_DATA,
                Permission.VIEW_THREAT_DATA,
                Permission.VIEW_MISSION_DATA,
                Permission.VIEW_ANALYTICS,
                Permission.EXPORT_DATA
            }
        }
    
    def _initialize_dashboard_layouts(self) -> Dict[UserRole, DashboardLayout]:
        """Initialize role-specific dashboard layouts"""
        layouts = {}
        
        # Commander Layout - Full operational overview
        layouts[UserRole.COMMANDER] = DashboardLayout(
            role=UserRole.COMMANDER,
            panels=[
                "map_panel",
                "mission_status_panel",
                "alert_console",
                "system_status_panel",
                "health_summary_panel",
                "logistics_summary_panel"
            ],
            panel_configs={
                "map_panel": {
                    "show_all_units": True,
                    "show_threats": True,
                    "show_weather": True,
                    "show_missions": True,
                    "cluster_units": True,
                    "default_zoom": 10
                },
                "mission_status_panel": {
                    "show_timeline": True,
                    "show_objectives": True,
                    "show_progress": True,
                    "show_resources": True
                },
                "alert_console": {
                    "show_all_alerts": True,
                    "auto_refresh": True,
                    "sound_alerts": True,
                    "max_alerts": 20
                },
                "system_status_panel": {
                    "show_unit_count": True,
                    "show_alert_summary": True,
                    "show_system_health": True,
                    "show_connectivity": True
                },
                "health_summary_panel": {
                    "show_critical_only": False,
                    "show_trends": True,
                    "show_statistics": True
                },
                "logistics_summary_panel": {
                    "show_all_resources": True,
                    "show_trends": True,
                    "show_predictions": True
                }
            },
            default_filters={
                "unit_types": ["all"],
                "risk_levels": ["all"],
                "time_range": "24h"
            },
            refresh_intervals={
                "map_panel": 5,
                "mission_status_panel": 30,
                "alert_console": 2,
                "system_status_panel": 10,
                "health_summary_panel": 15,
                "logistics_summary_panel": 30
            },
            color_scheme={
                "primary": "#1f2937",
                "secondary": "#374151",
                "accent": "#3b82f6",
                "success": "#10b981",
                "warning": "#f59e0b",
                "danger": "#ef4444",
                "info": "#06b6d4"
            },
            map_config={
                "default_center": [39.9042, 32.6195],
                "default_zoom": 10,
                "max_zoom": 18,
                "show_satellite": True,
                "show_terrain": True
            }
        )
        
        # Health Officer Layout - Health-focused view
        layouts[UserRole.HEALTH_OFFICER] = DashboardLayout(
            role=UserRole.HEALTH_OFFICER,
            panels=[
                "map_panel",
                "health_monitoring_panel",
                "health_analytics_panel",
                "alert_console",
                "medical_logistics_panel"
            ],
            panel_configs={
                "map_panel": {
                    "show_all_units": True,
                    "show_threats": False,
                    "show_weather": True,
                    "show_missions": False,
                    "cluster_units": False,
                    "default_zoom": 12,
                    "color_by": "health_status"
                },
                "health_monitoring_panel": {
                    "show_vital_signs": True,
                    "show_trends": True,
                    "show_alerts": True,
                    "show_statistics": True,
                    "real_time_updates": True
                },
                "health_analytics_panel": {
                    "show_health_trends": True,
                    "show_risk_analysis": True,
                    "show_predictions": True,
                    "show_correlations": True
                },
                "alert_console": {
                    "show_health_alerts_only": True,
                    "auto_refresh": True,
                    "sound_alerts": True,
                    "max_alerts": 15
                },
                "medical_logistics_panel": {
                    "show_medical_supplies": True,
                    "show_evacuation_routes": True,
                    "show_medical_facilities": True
                }
            },
            default_filters={
                "unit_types": ["all"],
                "risk_levels": ["high", "medium"],
                "time_range": "12h",
                "health_metrics": ["all"]
            },
            refresh_intervals={
                "map_panel": 10,
                "health_monitoring_panel": 5,
                "health_analytics_panel": 60,
                "alert_console": 3,
                "medical_logistics_panel": 30
            },
            color_scheme={
                "primary": "#065f46",
                "secondary": "#047857",
                "accent": "#10b981",
                "success": "#059669",
                "warning": "#d97706",
                "danger": "#dc2626",
                "info": "#0891b2"
            },
            map_config={
                "default_center": [39.9042, 32.6195],
                "default_zoom": 12,
                "max_zoom": 16,
                "show_satellite": False,
                "show_terrain": True
            }
        )
        
        # Operations Analyst Layout - Analytics-focused view
        layouts[UserRole.OPERATIONS_ANALYST] = DashboardLayout(
            role=UserRole.OPERATIONS_ANALYST,
            panels=[
                "map_panel",
                "mission_analytics_panel",
                "logistics_analytics_panel",
                "threat_analysis_panel",
                "performance_metrics_panel"
            ],
            panel_configs={
                "map_panel": {
                    "show_all_units": True,
                    "show_threats": True,
                    "show_weather": True,
                    "show_missions": True,
                    "cluster_units": True,
                    "default_zoom": 8,
                    "show_analytics_overlay": True
                },
                "mission_analytics_panel": {
                    "show_mission_progress": True,
                    "show_efficiency_metrics": True,
                    "show_resource_utilization": True,
                    "show_timeline_analysis": True
                },
                "logistics_analytics_panel": {
                    "show_consumption_trends": True,
                    "show_supply_predictions": True,
                    "show_efficiency_analysis": True,
                    "show_cost_analysis": True
                },
                "threat_analysis_panel": {
                    "show_threat_patterns": True,
                    "show_risk_assessment": True,
                    "show_threat_predictions": True,
                    "show_vulnerability_analysis": True
                },
                "performance_metrics_panel": {
                    "show_unit_performance": True,
                    "show_mission_success_rates": True,
                    "show_operational_efficiency": True,
                    "show_comparative_analysis": True
                }
            },
            default_filters={
                "unit_types": ["all"],
                "risk_levels": ["all"],
                "time_range": "7d",
                "analysis_type": "operational"
            },
            refresh_intervals={
                "map_panel": 15,
                "mission_analytics_panel": 120,
                "logistics_analytics_panel": 300,
                "threat_analysis_panel": 60,
                "performance_metrics_panel": 180
            },
            color_scheme={
                "primary": "#1e3a8a",
                "secondary": "#1e40af",
                "accent": "#3b82f6",
                "success": "#059669",
                "warning": "#d97706",
                "danger": "#dc2626",
                "info": "#0284c7"
            },
            map_config={
                "default_center": [39.9042, 32.6195],
                "default_zoom": 8,
                "max_zoom": 14,
                "show_satellite": True,
                "show_terrain": False,
                "show_analytics": True
            }
        )
        
        return layouts
    
    def authenticate_user(self, username: str, password: str) -> Optional[UserSession]:
        """Authenticate user and create session"""
        # In a real implementation, this would check against a database
        # For demo purposes, we'll use predefined users
        demo_users = {
            "commander": {"password": "cmd123", "role": UserRole.COMMANDER},
            "health_officer": {"password": "health123", "role": UserRole.HEALTH_OFFICER},
            "analyst": {"password": "ops123", "role": UserRole.OPERATIONS_ANALYST}
        }
        
        if username not in demo_users:
            return None
        
        # Simple password check (in production, use proper hashing)
        if demo_users[username]["password"] != password:
            return None
        
        # Create session
        user_role = demo_users[username]["role"]
        session_token = self._generate_session_token()
        
        session = UserSession(
            user_id=f"user_{username}",
            username=username,
            role=user_role,
            permissions=self.role_permissions[user_role],
            login_time=datetime.now(),
            last_activity=datetime.now(),
            session_token=session_token,
            expires_at=datetime.now() + self.session_timeout
        )
        
        self.active_sessions[session_token] = session
        return session
    
    def validate_session(self, session_token: str) -> Optional[UserSession]:
        """Validate session token and return session if valid"""
        if session_token not in self.active_sessions:
            return None
        
        session = self.active_sessions[session_token]
        
        # Check if session has expired
        if datetime.now() > session.expires_at:
            del self.active_sessions[session_token]
            return None
        
        # Update last activity
        session.last_activity = datetime.now()
        return session
    
    def logout_user(self, session_token: str) -> bool:
        """Logout user and invalidate session"""
        if session_token in self.active_sessions:
            del self.active_sessions[session_token]
            return True
        return False
    
    def has_permission(self, session_token: str, permission: Permission) -> bool:
        """Check if user has specific permission"""
        session = self.validate_session(session_token)
        if not session:
            return False
        
        return permission in session.permissions
    
    def get_dashboard_layout(self, role: UserRole) -> Optional[DashboardLayout]:
        """Get dashboard layout for role"""
        return self.dashboard_layouts.get(role)
    
    def get_user_dashboard_config(self, session_token: str) -> Optional[Dict[str, Any]]:
        """Get complete dashboard configuration for user"""
        session = self.validate_session(session_token)
        if not session:
            return None
        
        layout = self.get_dashboard_layout(session.role)
        if not layout:
            return None
        
        return {
            "user_info": {
                "user_id": session.user_id,
                "username": session.username,
                "role": session.role.value,
                "permissions": [p.value for p in session.permissions]
            },
            "layout": {
                "panels": layout.panels,
                "panel_configs": layout.panel_configs,
                "default_filters": layout.default_filters,
                "refresh_intervals": layout.refresh_intervals,
                "color_scheme": layout.color_scheme,
                "map_config": layout.map_config
            },
            "session_info": {
                "login_time": session.login_time.isoformat(),
                "last_activity": session.last_activity.isoformat(),
                "expires_at": session.expires_at.isoformat()
            }
        }
    
    def filter_data_by_permissions(self, session_token: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Filter data based on user permissions"""
        session = self.validate_session(session_token)
        if not session:
            return {}
        
        filtered_data = {}
        
        # Filter based on permissions
        if Permission.VIEW_ALL_UNITS in session.permissions:
            filtered_data["units"] = data.get("units", [])
        
        if Permission.VIEW_HEALTH_DATA in session.permissions:
            filtered_data["health_metrics"] = data.get("health_metrics", [])
        
        if Permission.VIEW_LOGISTICS_DATA in session.permissions:
            filtered_data["logistics"] = data.get("logistics", [])
        
        if Permission.VIEW_THREAT_DATA in session.permissions:
            filtered_data["threats"] = data.get("threats", [])
        
        if Permission.VIEW_MISSION_DATA in session.permissions:
            filtered_data["missions"] = data.get("missions", [])
        
        # Always include alerts if user can view any data
        if session.permissions:
            filtered_data["alerts"] = data.get("alerts", [])
        
        return filtered_data
    
    def get_role_specific_alerts(self, session_token: str, alerts: List[Dict]) -> List[Dict]:
        """Filter alerts based on user role"""
        session = self.validate_session(session_token)
        if not session:
            return []
        
        if session.role == UserRole.COMMANDER:
            # Commanders see all alerts
            return alerts
        
        elif session.role == UserRole.HEALTH_OFFICER:
            # Health officers see health-related alerts
            health_alert_types = ["health_critical", "health_warning", "medical_emergency"]
            return [alert for alert in alerts if alert.get("alert_type") in health_alert_types]
        
        elif session.role == UserRole.OPERATIONS_ANALYST:
            # Analysts see operational and logistics alerts
            ops_alert_types = ["logistics_critical", "mission_update", "operational_warning"]
            return [alert for alert in alerts if alert.get("alert_type") in ops_alert_types]
        
        return []
    
    def get_active_sessions(self) -> List[Dict[str, Any]]:
        """Get list of active sessions (admin function)"""
        sessions = []
        current_time = datetime.now()
        
        for token, session in self.active_sessions.items():
            if current_time <= session.expires_at:
                sessions.append({
                    "user_id": session.user_id,
                    "username": session.username,
                    "role": session.role.value,
                    "login_time": session.login_time.isoformat(),
                    "last_activity": session.last_activity.isoformat(),
                    "expires_at": session.expires_at.isoformat()
                })
        
        return sessions
    
    def cleanup_expired_sessions(self):
        """Remove expired sessions"""
        current_time = datetime.now()
        expired_tokens = [
            token for token, session in self.active_sessions.items()
            if current_time > session.expires_at
        ]
        
        for token in expired_tokens:
            del self.active_sessions[token]
    
    def _generate_session_token(self) -> str:
        """Generate secure session token"""
        return secrets.token_urlsafe(32)
    
    def _hash_password(self, password: str) -> str:
        """Hash password (for production use)"""
        salt = secrets.token_hex(16)
        password_hash = hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 100000)
        return f"{salt}:{password_hash.hex()}"
    
    def _verify_password(self, password: str, password_hash: str) -> bool:
        """Verify password against hash (for production use)"""
        try:
            salt, hash_hex = password_hash.split(':')
            password_check = hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 100000)
            return password_check.hex() == hash_hex
        except ValueError:
            return False
    
    def create_jwt_token(self, session: UserSession) -> str:
        """Create JWT token for API authentication"""
        payload = {
            "user_id": session.user_id,
            "username": session.username,
            "role": session.role.value,
            "permissions": [p.value for p in session.permissions],
            "exp": session.expires_at.timestamp(),
            "iat": datetime.now().timestamp()
        }
        
        return jwt.encode(payload, settings.secret_key, algorithm="HS256")
    
    def verify_jwt_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Verify JWT token and return payload"""
        try:
            payload = jwt.decode(token, settings.secret_key, algorithms=["HS256"])
            return payload
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None


# Global role manager instance
role_manager = RoleManager()


# Example usage and testing
if __name__ == "__main__":
    # Test authentication
    session = role_manager.authenticate_user("commander", "cmd123")
    if session:
        print(f"Authenticated: {session.username} as {session.role.value}")
        
        # Test permissions
        can_control = role_manager.has_permission(session.session_token, Permission.CONTROL_UNITS)
        print(f"Can control units: {can_control}")
        
        # Get dashboard config
        config = role_manager.get_user_dashboard_config(session.session_token)
        if config:
            print(f"Dashboard panels: {config['layout']['panels']}")
            print(f"Color scheme: {config['layout']['color_scheme']['primary']}")
    
    # Test health officer
    health_session = role_manager.authenticate_user("health_officer", "health123")
    if health_session:
        print(f"\nHealth Officer authenticated: {health_session.username}")
        health_config = role_manager.get_user_dashboard_config(health_session.session_token)
        if health_config:
            print(f"Health Officer panels: {health_config['layout']['panels']}")
    
    # Test analyst
    analyst_session = role_manager.authenticate_user("analyst", "ops123")
    if analyst_session:
        print(f"\nAnalyst authenticated: {analyst_session.username}")
        analyst_config = role_manager.get_user_dashboard_config(analyst_session.session_token)
        if analyst_config:
            print(f"Analyst panels: {analyst_config['layout']['panels']}")