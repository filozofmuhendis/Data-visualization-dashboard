"""
Event Logger Service for MSA Dashboard
Automatically logs events to database for historical tracking
"""
from PyQt5.QtCore import QObject, pyqtSignal, QTimer
from datetime import datetime
from typing import Dict, Any, Optional
import logging

from database.database_manager import DatabaseManager
from database.models import Event

class EventLogger(QObject):
    """Service for logging events to database"""
    
    event_logged = pyqtSignal(Event)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.db_manager = DatabaseManager()
        self.logger = logging.getLogger(__name__)
        
        # Auto-cleanup timer (runs daily)
        self.cleanup_timer = QTimer()
        self.cleanup_timer.timeout.connect(self.cleanup_old_events)
        self.cleanup_timer.start(24 * 60 * 60 * 1000)  # 24 hours
    
    def log_event(self, 
                  event_type: str,
                  category: str,
                  title: str,
                  description: str = "",
                  severity: str = "info",
                  source_id: str = "",
                  location_lat: Optional[float] = None,
                  location_lng: Optional[float] = None,
                  metadata: Optional[Dict[str, Any]] = None,
                  user_id: Optional[str] = None) -> Optional[Event]:
        """Log an event to database"""
        try:
            event = Event(
                timestamp=datetime.now(),
                event_type=event_type,
                category=category,
                source_id=source_id,
                title=title,
                description=description,
                severity=severity,
                location_lat=location_lat,
                location_lng=location_lng,
                metadata=metadata,
                user_id=user_id
            )
            
            event_id = self.db_manager.add_event(event)
            event.id = event_id
            
            self.event_logged.emit(event)
            self.logger.info(f"Event logged: {title} (ID: {event_id})")
            
            return event
            
        except Exception as e:
            self.logger.error(f"Failed to log event: {e}")
            return None
    
    def log_user_action(self, action: str, details: str = "", user_id: str = ""):
        """Log user action"""
        return self.log_event(
            event_type="user_action",
            category="system",
            title=f"User Action: {action}",
            description=details,
            severity="info",
            user_id=user_id
        )
    
    def log_system_event(self, event: str, details: str = "", severity: str = "info"):
        """Log system event"""
        return self.log_event(
            event_type="system_event",
            category="system",
            title=f"System: {event}",
            description=details,
            severity=severity
        )
    
    def log_unit_event(self, unit_id: str, event: str, details: str = "", 
                       lat: Optional[float] = None, lng: Optional[float] = None,
                       severity: str = "info"):
        """Log unit-related event"""
        return self.log_event(
            event_type="unit_event",
            category="unit",
            title=f"Unit {unit_id}: {event}",
            description=details,
            severity=severity,
            source_id=unit_id,
            location_lat=lat,
            location_lng=lng
        )
    
    def log_alert_event(self, alert_id: str, event: str, details: str = "",
                        lat: Optional[float] = None, lng: Optional[float] = None,
                        severity: str = "warning"):
        """Log alert-related event"""
        return self.log_event(
            event_type="alert_event",
            category="alert",
            title=f"Alert {alert_id}: {event}",
            description=details,
            severity=severity,
            source_id=alert_id,
            location_lat=lat,
            location_lng=lng
        )
    
    def log_health_event(self, personnel_id: str, event: str, details: str = "",
                         severity: str = "info"):
        """Log health-related event"""
        return self.log_event(
            event_type="health_event",
            category="health",
            title=f"Health {personnel_id}: {event}",
            description=details,
            severity=severity,
            source_id=personnel_id
        )
    
    def log_logistics_event(self, resource_id: str, event: str, details: str = "",
                           severity: str = "info"):
        """Log logistics-related event"""
        return self.log_event(
            event_type="logistics_event",
            category="logistics",
            title=f"Logistics {resource_id}: {event}",
            description=details,
            severity=severity,
            source_id=resource_id
        )
    
    def log_authentication_event(self, username: str, event: str, success: bool = True,
                                ip_address: str = "", details: str = ""):
        """Log authentication event"""
        severity = "info" if success else "warning"
        title = f"Auth: {username} {event}"
        
        metadata = {
            "ip_address": ip_address,
            "success": success
        }
        
        return self.log_event(
            event_type="auth_event",
            category="system",
            title=title,
            description=details,
            severity=severity,
            metadata=metadata,
            user_id=username
        )
    
    def cleanup_old_events(self):
        """Clean up old events (called automatically)"""
        try:
            self.db_manager.cleanup_old_data(days=30)
            self.logger.info("Old events cleaned up successfully")
        except Exception as e:
            self.logger.error(f"Failed to cleanup old events: {e}")

# Global event logger instance
_event_logger = None

def get_event_logger() -> EventLogger:
    """Get global event logger instance"""
    global _event_logger
    if _event_logger is None:
        _event_logger = EventLogger()
    return _event_logger