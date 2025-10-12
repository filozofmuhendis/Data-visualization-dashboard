"""
Qt Database Adapter - Bridge between PyQt5 demo data and Web application
Adapts PyQt5 database models to web application format
"""

import sqlite3
import json
from datetime import datetime
from typing import List, Dict, Any, Optional
from pathlib import Path

from .models import Unit, UnitType, RiskLevel, AlertSeverity, Position
from .database import UnitDB, AlertDB, HealthMetricsDB


class QtDatabaseAdapter:
    """Adapter to read PyQt5 demo data and convert to web format"""
    
    def __init__(self, qt_db_path: str = None):
        if qt_db_path is None:
            # Default path to PyQt5 database
            qt_db_path = Path(__file__).parent.parent / "qt_app" / "msa_dashboard.db"
        
        self.qt_db_path = str(qt_db_path)
        self.connection = None
    
    def connect(self):
        """Connect to PyQt5 SQLite database"""
        try:
            self.connection = sqlite3.connect(self.qt_db_path)
            self.connection.row_factory = sqlite3.Row  # Enable dict-like access
            return True
        except Exception as e:
            print(f"Failed to connect to Qt database: {e}")
            return False
    
    def disconnect(self):
        """Disconnect from database"""
        if self.connection:
            self.connection.close()
            self.connection = None
    
    def get_units(self) -> List[Dict[str, Any]]:
        """Get all units from PyQt5 database and convert to web format"""
        if not self.connection:
            if not self.connect():
                return []
        
        try:
            cursor = self.connection.cursor()
            cursor.execute("""
                SELECT unit_id, name, unit_type, location_lat, location_lng, 
                       status, created_at, updated_at, commander, personnel_count,
                       fuel_level, ammunition, speed, heading
                FROM units
                ORDER BY created_at DESC
            """)
            
            units = []
            for row in cursor.fetchall():
                # Map PyQt5 unit types to web unit types
                unit_type_mapping = {
                    'tank': UnitType.ARMOR,
                    'infantry': UnitType.INFANTRY,
                    'artillery': UnitType.ARTILLERY,
                    'reconnaissance': UnitType.RECON,
                    'support': UnitType.SUPPORT,
                    'command': UnitType.COMMAND,
                    'armor': UnitType.ARMOR,
                    'recon': UnitType.RECON
                }
                
                # Map status to risk level
                status_mapping = {
                    'active': RiskLevel.GREEN,
                    'warning': RiskLevel.AMBER,
                    'critical': RiskLevel.RED,
                    'inactive': RiskLevel.AMBER,
                    'operational': RiskLevel.GREEN,
                    'maintenance': RiskLevel.AMBER
                }
                
                unit_data = {
                    'unit_id': row['unit_id'],
                    'name': row['name'],
                    'unit_type': unit_type_mapping.get(row['unit_type'].lower(), UnitType.INFANTRY).value,
                    'position': {
                        'latitude': float(row['location_lat']) if row['location_lat'] else 0.0,
                        'longitude': float(row['location_lng']) if row['location_lng'] else 0.0,
                        'altitude': 0.0
                    },
                    'status': row['status'],
                    'risk_level': status_mapping.get(row['status'].lower(), RiskLevel.GREEN).value,
                    'commander': row['commander'] or 'Unknown',
                    'personnel_count': row['personnel_count'] or 0,
                    'fuel_level': float(row['fuel_level']) if row['fuel_level'] else 0.0,
                    'ammunition': row['ammunition'] or 0,
                    'speed': float(row['speed']) if row['speed'] else 0.0,
                    'heading': float(row['heading']) if row['heading'] else 0.0,
                    'created_at': row['created_at'],
                    'updated_at': row['updated_at']
                }
                units.append(unit_data)
            
            return units
            
        except Exception as e:
            print(f"Error fetching units: {e}")
    def get_alerts(self) -> List[Dict[str, Any]]:
        """Get all alerts from PyQt5 database"""
        if not self.connection:
            if not self.connect():
                return []
        
        try:
            cursor = self.connection.cursor()
            cursor.execute("""
                SELECT alert_id, title, description, alert_type, severity, status,
                       location_lat, location_lng, source, confidence, created_at, 
                       updated_at, resolved_at, assigned_to
                FROM alerts
                ORDER BY created_at DESC
                LIMIT 100
            """)
            
            alerts = []
            for row in cursor.fetchall():
                # Map severity levels
                severity_mapping = {
                    'low': AlertSeverity.INFO,
                    'medium': AlertSeverity.WARNING,
                    'high': AlertSeverity.CRITICAL,
                    'critical': AlertSeverity.EMERGENCY,
                    'info': AlertSeverity.INFO,
                    'warning': AlertSeverity.WARNING,
                    'emergency': AlertSeverity.EMERGENCY
                }
                
                alert_data = {
                    'alert_id': row['alert_id'],
                    'title': row['title'] or 'Alert',
                    'description': row['description'] or 'No description',
                    'alert_type': row['alert_type'] or 'general',
                    'severity': severity_mapping.get(row['severity'].lower() if row['severity'] else 'info', AlertSeverity.INFO).value,
                    'status': row['status'] or 'active',
                    'position': {
                        'latitude': float(row['location_lat']) if row['location_lat'] else 0.0,
                        'longitude': float(row['location_lng']) if row['location_lng'] else 0.0
                    },
                    'source': row['source'] or 'system',
                    'confidence': float(row['confidence']) if row['confidence'] else 0.0,
                    'timestamp': row['created_at'],
                    'updated_at': row['updated_at'],
                    'resolved': row['resolved_at'] is not None,
                    'resolved_at': row['resolved_at'],
                    'assigned_to': row['assigned_to']
                }
                alerts.append(alert_data)
            
            return alerts
            
        except Exception as e:
            print(f"Error fetching alerts: {e}")
            return []
    
    def get_events(self) -> List[Dict[str, Any]]:
        """Get recent events from PyQt5 database"""
        if not self.connection:
            if not self.connect():
                return []
        
        try:
            cursor = self.connection.cursor()
            cursor.execute("""
                SELECT event_id, event_type, severity, latitude, longitude,
                       description, metadata, created_at
                FROM events
                ORDER BY created_at DESC
                LIMIT 200
            """)
            
            events = []
            for row in cursor.fetchall():
                event_data = {
                    'event_id': row['event_id'],
                    'event_type': row['event_type'],
                    'severity': row['severity'],
                    'position': {
                        'latitude': float(row['latitude']),
                        'longitude': float(row['longitude'])
                    },
                    'description': row['description'],
                    'metadata': json.loads(row['metadata']) if row['metadata'] else {},
                    'timestamp': row['created_at']
                }
                events.append(event_data)
            
            return events
            
        except Exception as e:
            print(f"Error fetching events: {e}")
            return []
    
    def get_missions(self) -> List[Dict[str, Any]]:
        """Get missions from PyQt5 database"""
        if not self.connection:
            if not self.connect():
                return []
        
        try:
            cursor = self.connection.cursor()
            cursor.execute("""
                SELECT mission_id, name, mission_type, status,
                       start_time, end_time, description, created_at
                FROM missions
                ORDER BY created_at DESC
            """)
            
            missions = []
            for row in cursor.fetchall():
                mission_data = {
                    'mission_id': row['mission_id'],
                    'name': row['name'],
                    'mission_type': row['mission_type'],
                    'status': row['status'],
                    'start_time': row['start_time'],
                    'end_time': row['end_time'],
                    'description': row['description'],
                    'timestamp': row['created_at']
                }
                missions.append(mission_data)
            
            return missions
            
        except Exception as e:
            print(f"Error fetching missions: {e}")
            return []
    
    def get_dashboard_summary(self) -> Dict[str, Any]:
        """Get dashboard summary statistics"""
        if not self.connection:
            if not self.connect():
                return {}
        
        try:
            cursor = self.connection.cursor()
            
            # Get unit counts by status
            cursor.execute("""
                SELECT status, COUNT(*) as count
                FROM units
                GROUP BY status
            """)
            unit_status = {row['status']: row['count'] for row in cursor.fetchall()}
            
            # Get alert counts by severity
            cursor.execute("""
                SELECT severity, COUNT(*) as count
                FROM alerts
                WHERE resolved_at IS NULL
                GROUP BY severity
            """)
            alert_counts = {row['severity']: row['count'] for row in cursor.fetchall()}
            
            # Get recent activity count
            cursor.execute("""
                SELECT COUNT(*) as count
                FROM events
                WHERE created_at > datetime('now', '-1 hour')
            """)
            recent_events = cursor.fetchone()['count']
            
            return {
                'total_units': sum(unit_status.values()),
                'unit_status': unit_status,
                'active_alerts': sum(alert_counts.values()),
                'alert_counts': alert_counts,
                'recent_events': recent_events,
                'last_updated': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            print(f"Error fetching dashboard summary: {e}")
            return {}


# Global adapter instance
qt_adapter = QtDatabaseAdapter()