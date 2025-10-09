"""
Database Manager for MSA Dashboard
Handles SQLite database operations for persistent data storage
"""
import sqlite3
import os
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from contextlib import contextmanager
import json
import logging

from .models import Event, UserSession, SystemMetric, Unit, Alert, Mission, Equipment

class DatabaseManager:
    """SQLite database manager for MSA Dashboard"""
    
    def __init__(self, db_path: str = "msa_dashboard.db"):
        """Initialize database manager"""
        self.db_path = db_path
        self.logger = logging.getLogger(__name__)
        self.init_database()
    
    def init_database(self):
        """Initialize database and create tables"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                # Create events table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS events (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        timestamp TEXT NOT NULL,
                        event_type TEXT NOT NULL,
                        category TEXT NOT NULL,
                        source_id TEXT,
                        title TEXT NOT NULL,
                        description TEXT,
                        severity TEXT DEFAULT 'info',
                        location_lat REAL,
                        location_lng REAL,
                        metadata TEXT,
                        user_id TEXT,
                        acknowledged BOOLEAN DEFAULT FALSE,
                        acknowledged_by TEXT,
                        acknowledged_at TEXT,
                        created_at TEXT DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                
                # Create user_sessions table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS user_sessions (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id TEXT NOT NULL,
                        username TEXT NOT NULL,
                        role TEXT NOT NULL,
                        login_time TEXT NOT NULL,
                        logout_time TEXT,
                        ip_address TEXT,
                        user_agent TEXT,
                        session_token TEXT UNIQUE,
                        is_active BOOLEAN DEFAULT TRUE,
                        created_at TEXT DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                
                # Create system_metrics table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS system_metrics (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        timestamp TEXT NOT NULL,
                        metric_name TEXT NOT NULL,
                        metric_value REAL NOT NULL,
                        unit TEXT,
                        category TEXT,
                        source TEXT,
                        created_at TEXT DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                
                # Create units table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS units (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        unit_id TEXT UNIQUE NOT NULL,
                        name TEXT NOT NULL,
                        unit_type TEXT NOT NULL,
                        status TEXT DEFAULT 'active',
                        location_lat REAL,
                        location_lng REAL,
                        altitude REAL,
                        heading REAL,
                        speed REAL,
                        fuel_level REAL,
                        ammunition INTEGER,
                        personnel_count INTEGER,
                        commander TEXT,
                        mission_id TEXT,
                        last_contact TEXT,
                        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                        updated_at TEXT DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                
                # Create alerts table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS alerts (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        alert_id TEXT UNIQUE NOT NULL,
                        title TEXT NOT NULL,
                        description TEXT,
                        alert_type TEXT NOT NULL,
                        severity TEXT DEFAULT 'low',
                        status TEXT DEFAULT 'active',
                        location_lat REAL,
                        location_lng REAL,
                        radius REAL,
                        source TEXT,
                        confidence REAL,
                        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                        updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
                        resolved_at TEXT,
                        assigned_to TEXT
                    )
                ''')
                
                # Create missions table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS missions (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        mission_id TEXT UNIQUE NOT NULL,
                        name TEXT NOT NULL,
                        description TEXT,
                        mission_type TEXT NOT NULL,
                        status TEXT DEFAULT 'planned',
                        priority TEXT DEFAULT 'medium',
                        start_time TEXT,
                        end_time TEXT,
                        estimated_duration INTEGER,
                        commander TEXT,
                        assigned_units TEXT,
                        objectives TEXT,
                        location_lat REAL,
                        location_lng REAL,
                        area_of_operation TEXT,
                        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                        updated_at TEXT DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                
                # Create equipment table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS equipment (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        equipment_id TEXT UNIQUE NOT NULL,
                        name TEXT NOT NULL,
                        equipment_type TEXT NOT NULL,
                        status TEXT DEFAULT 'operational',
                        condition TEXT DEFAULT 'good',
                        location_lat REAL,
                        location_lng REAL,
                        assigned_unit TEXT,
                        maintenance_due TEXT,
                        last_maintenance TEXT,
                        specifications TEXT,
                        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                        updated_at TEXT DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                
                # Create indexes for better performance
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_events_timestamp ON events(timestamp)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_events_category ON events(category)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_events_severity ON events(severity)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_sessions_user_id ON user_sessions(user_id)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_metrics_timestamp ON system_metrics(timestamp)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_units_type ON units(unit_type)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_units_status ON units(status)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_alerts_severity ON alerts(severity)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_alerts_status ON alerts(status)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_missions_status ON missions(status)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_equipment_type ON equipment(equipment_type)')
                
                conn.commit()
                self.logger.info("Database initialized successfully")
                
        except Exception as e:
            self.logger.error(f"Failed to initialize database: {e}")
            raise
    
    @contextmanager
    def get_connection(self):
        """Get database connection with context manager"""
        conn = None
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row  # Enable column access by name
            yield conn
        except Exception as e:
            if conn:
                conn.rollback()
            self.logger.error(f"Database error: {e}")
            raise
        finally:
            if conn:
                conn.close()
    
    # Event operations
    def add_event(self, event: Event) -> int:
        """Add new event to database"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                if not event.timestamp:
                    event.timestamp = datetime.now()
                
                cursor.execute('''
                    INSERT INTO events (
                        timestamp, event_type, category, source_id, title, description,
                        severity, location_lat, location_lng, metadata, user_id,
                        acknowledged, acknowledged_by, acknowledged_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    event.timestamp.isoformat(),
                    event.event_type,
                    event.category,
                    event.source_id,
                    event.title,
                    event.description,
                    event.severity,
                    event.location_lat,
                    event.location_lng,
                    json.dumps(event.metadata) if event.metadata else None,
                    event.user_id,
                    event.acknowledged,
                    event.acknowledged_by,
                    event.acknowledged_at.isoformat() if event.acknowledged_at else None
                ))
                
                event_id = cursor.lastrowid
                conn.commit()
                self.logger.info(f"Event added with ID: {event_id}")
                return event_id
                
        except Exception as e:
            self.logger.error(f"Failed to add event: {e}")
            raise
    
    def get_events(self, 
                   limit: int = 100, 
                   offset: int = 0,
                   category: Optional[str] = None,
                   severity: Optional[str] = None,
                   start_date: Optional[datetime] = None,
                   end_date: Optional[datetime] = None) -> List[Event]:
        """Get events with filtering options"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                query = "SELECT * FROM events WHERE 1=1"
                params = []
                
                if category:
                    query += " AND category = ?"
                    params.append(category)
                
                if severity:
                    query += " AND severity = ?"
                    params.append(severity)
                
                if start_date:
                    query += " AND timestamp >= ?"
                    params.append(start_date.isoformat())
                
                if end_date:
                    query += " AND timestamp <= ?"
                    params.append(end_date.isoformat())
                
                query += " ORDER BY timestamp DESC LIMIT ? OFFSET ?"
                params.extend([limit, offset])
                
                cursor.execute(query, params)
                rows = cursor.fetchall()
                
                events = []
                for row in rows:
                    event_data = dict(row)
                    if event_data['metadata']:
                        event_data['metadata'] = json.loads(event_data['metadata'])
                    events.append(Event.from_dict(event_data))
                
                return events
                
        except Exception as e:
            self.logger.error(f"Failed to get events: {e}")
            return []
    
    def acknowledge_event(self, event_id: int, acknowledged_by: str) -> bool:
        """Acknowledge an event"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    UPDATE events 
                    SET acknowledged = TRUE, acknowledged_by = ?, acknowledged_at = ?
                    WHERE id = ?
                ''', (acknowledged_by, datetime.now().isoformat(), event_id))
                
                conn.commit()
                return cursor.rowcount > 0
                
        except Exception as e:
            self.logger.error(f"Failed to acknowledge event: {e}")
            return False
    
    # User session operations
    def create_session(self, session: UserSession) -> int:
        """Create new user session"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                if not session.login_time:
                    session.login_time = datetime.now()
                
                cursor.execute('''
                    INSERT INTO user_sessions (
                        user_id, username, role, login_time, ip_address,
                        user_agent, session_token, is_active
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    session.user_id,
                    session.username,
                    session.role,
                    session.login_time.isoformat(),
                    session.ip_address,
                    session.user_agent,
                    session.session_token,
                    session.is_active
                ))
                
                session_id = cursor.lastrowid
                conn.commit()
                return session_id
                
        except Exception as e:
            self.logger.error(f"Failed to create session: {e}")
            raise
    
    def end_session(self, session_token: str) -> bool:
        """End user session"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    UPDATE user_sessions 
                    SET is_active = FALSE, logout_time = ?
                    WHERE session_token = ? AND is_active = TRUE
                ''', (datetime.now().isoformat(), session_token))
                
                conn.commit()
                return cursor.rowcount > 0
                
        except Exception as e:
            self.logger.error(f"Failed to end session: {e}")
            return False
    
    # System metrics operations
    def add_metric(self, metric: SystemMetric) -> int:
        """Add system metric"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                if not metric.timestamp:
                    metric.timestamp = datetime.now()
                
                cursor.execute('''
                    INSERT INTO system_metrics (
                        timestamp, metric_name, metric_value, unit, category, source
                    ) VALUES (?, ?, ?, ?, ?, ?)
                ''', (
                    metric.timestamp.isoformat(),
                    metric.metric_name,
                    metric.metric_value,
                    metric.unit,
                    metric.category,
                    metric.source
                ))
                
                metric_id = cursor.lastrowid
                conn.commit()
                return metric_id
                
        except Exception as e:
            self.logger.error(f"Failed to add metric: {e}")
            raise
    
    def get_metrics(self, 
                    metric_name: Optional[str] = None,
                    category: Optional[str] = None,
                    hours: int = 24) -> List[SystemMetric]:
        """Get system metrics for specified time period"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                start_time = datetime.now() - timedelta(hours=hours)
                
                query = "SELECT * FROM system_metrics WHERE timestamp >= ?"
                params = [start_time.isoformat()]
                
                if metric_name:
                    query += " AND metric_name = ?"
                    params.append(metric_name)
                
                if category:
                    query += " AND category = ?"
                    params.append(category)
                
                query += " ORDER BY timestamp DESC"
                
                cursor.execute(query, params)
                rows = cursor.fetchall()
                
                metrics = []
                for row in rows:
                    metric = SystemMetric(
                        id=row['id'],
                        timestamp=datetime.fromisoformat(row['timestamp']),
                        metric_name=row['metric_name'],
                        metric_value=row['metric_value'],
                        unit=row['unit'],
                        category=row['category'],
                        source=row['source']
                    )
                    metrics.append(metric)
                
                return metrics
                
        except Exception as e:
            self.logger.error(f"Failed to get metrics: {e}")
            return []
    
    # New methods for demo data
    def add_unit(self, unit: Unit) -> int:
        """Add military unit"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                if not unit.created_at:
                    unit.created_at = datetime.now()
                if not unit.updated_at:
                    unit.updated_at = datetime.now()
                
                cursor.execute('''
                    INSERT INTO units (
                        unit_id, name, unit_type, status, location_lat, location_lng,
                        altitude, heading, speed, fuel_level, ammunition, personnel_count,
                        commander, mission_id, last_contact, created_at, updated_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    unit.unit_id, unit.name, unit.unit_type, unit.status,
                    unit.location_lat, unit.location_lng, unit.altitude, unit.heading,
                    unit.speed, unit.fuel_level, unit.ammunition, unit.personnel_count,
                    unit.commander, unit.mission_id,
                    unit.last_contact.isoformat() if unit.last_contact else None,
                    unit.created_at.isoformat(), unit.updated_at.isoformat()
                ))
                
                unit_id = cursor.lastrowid
                conn.commit()
                return unit_id
                
        except Exception as e:
            self.logger.error(f"Failed to add unit: {e}")
            raise
    
    def add_alert(self, alert: Alert) -> int:
        """Add alert"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                if not alert.created_at:
                    alert.created_at = datetime.now()
                if not alert.updated_at:
                    alert.updated_at = datetime.now()
                
                cursor.execute('''
                    INSERT INTO alerts (
                        alert_id, title, description, alert_type, severity, status,
                        location_lat, location_lng, radius, source, confidence,
                        created_at, updated_at, resolved_at, assigned_to
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    alert.alert_id, alert.title, alert.description, alert.alert_type,
                    alert.severity, alert.status, alert.location_lat, alert.location_lng,
                    alert.radius, alert.source, alert.confidence,
                    alert.created_at.isoformat(), alert.updated_at.isoformat(),
                    alert.resolved_at.isoformat() if alert.resolved_at else None,
                    alert.assigned_to
                ))
                
                alert_id = cursor.lastrowid
                conn.commit()
                return alert_id
                
        except Exception as e:
            self.logger.error(f"Failed to add alert: {e}")
            raise
    
    def add_mission(self, mission: Mission) -> int:
        """Add mission"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                if not mission.created_at:
                    mission.created_at = datetime.now()
                if not mission.updated_at:
                    mission.updated_at = datetime.now()
                
                cursor.execute('''
                    INSERT INTO missions (
                        mission_id, name, description, mission_type, status, priority,
                        start_time, end_time, estimated_duration, commander,
                        assigned_units, objectives, location_lat, location_lng,
                        area_of_operation, created_at, updated_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    mission.mission_id, mission.name, mission.description, mission.mission_type,
                    mission.status, mission.priority,
                    mission.start_time.isoformat() if mission.start_time else None,
                    mission.end_time.isoformat() if mission.end_time else None,
                    mission.estimated_duration, mission.commander, mission.assigned_units,
                    mission.objectives, mission.location_lat, mission.location_lng,
                    mission.area_of_operation, mission.created_at.isoformat(),
                    mission.updated_at.isoformat()
                ))
                
                mission_id = cursor.lastrowid
                conn.commit()
                return mission_id
                
        except Exception as e:
            self.logger.error(f"Failed to add mission: {e}")
            raise
    
    def add_equipment(self, equipment: Equipment) -> int:
        """Add equipment"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                if not equipment.created_at:
                    equipment.created_at = datetime.now()
                if not equipment.updated_at:
                    equipment.updated_at = datetime.now()
                
                cursor.execute('''
                    INSERT INTO equipment (
                        equipment_id, name, equipment_type, status, condition,
                        location_lat, location_lng, assigned_unit, maintenance_due,
                        last_maintenance, specifications, created_at, updated_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    equipment.equipment_id, equipment.name, equipment.equipment_type,
                    equipment.status, equipment.condition, equipment.location_lat,
                    equipment.location_lng, equipment.assigned_unit,
                    equipment.maintenance_due.isoformat() if equipment.maintenance_due else None,
                    equipment.last_maintenance.isoformat() if equipment.last_maintenance else None,
                    equipment.specifications, equipment.created_at.isoformat(),
                    equipment.updated_at.isoformat()
                ))
                
                equipment_id = cursor.lastrowid
                conn.commit()
                return equipment_id
                
        except Exception as e:
            self.logger.error(f"Failed to add equipment: {e}")
            raise
    
    def get_all_units(self) -> List[Unit]:
        """Get all units"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM units ORDER BY created_at DESC")
                rows = cursor.fetchall()
                
                units = []
                for row in rows:
                    unit = Unit(
                        id=row['id'],
                        unit_id=row['unit_id'],
                        name=row['name'],
                        unit_type=row['unit_type'],
                        status=row['status'],
                        location_lat=row['location_lat'],
                        location_lng=row['location_lng'],
                        altitude=row['altitude'],
                        heading=row['heading'],
                        speed=row['speed'],
                        fuel_level=row['fuel_level'],
                        ammunition=row['ammunition'],
                        personnel_count=row['personnel_count'],
                        commander=row['commander'],
                        mission_id=row['mission_id'],
                        last_contact=datetime.fromisoformat(row['last_contact']) if row['last_contact'] else None,
                        created_at=datetime.fromisoformat(row['created_at']) if row['created_at'] else None,
                        updated_at=datetime.fromisoformat(row['updated_at']) if row['updated_at'] else None
                    )
                    units.append(unit)
                
                return units
                
        except Exception as e:
            self.logger.error(f"Failed to get units: {e}")
            return []
    
    def get_all_alerts(self) -> List[Alert]:
        """Get all alerts"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM alerts ORDER BY created_at DESC")
                rows = cursor.fetchall()
                
                alerts = []
                for row in rows:
                    alert = Alert(
                        id=row['id'],
                        alert_id=row['alert_id'],
                        title=row['title'],
                        description=row['description'],
                        alert_type=row['alert_type'],
                        severity=row['severity'],
                        status=row['status'],
                        location_lat=row['location_lat'],
                        location_lng=row['location_lng'],
                        radius=row['radius'],
                        source=row['source'],
                        confidence=row['confidence'],
                        created_at=datetime.fromisoformat(row['created_at']) if row['created_at'] else None,
                        updated_at=datetime.fromisoformat(row['updated_at']) if row['updated_at'] else None,
                        resolved_at=datetime.fromisoformat(row['resolved_at']) if row['resolved_at'] else None,
                        assigned_to=row['assigned_to']
                    )
                    alerts.append(alert)
                
                return alerts
                
        except Exception as e:
            self.logger.error(f"Failed to get alerts: {e}")
            return []

    # Utility methods
    def cleanup_old_data(self, days: int = 30):
        """Clean up old data older than specified days"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                cutoff_date = datetime.now() - timedelta(days=days)
                cutoff_str = cutoff_date.isoformat()
                
                # Clean old events (keep critical events longer)
                cursor.execute('''
                    DELETE FROM events 
                    WHERE timestamp < ? AND severity NOT IN ('critical', 'error')
                ''', (cutoff_str,))
                
                # Clean old metrics
                cursor.execute('''
                    DELETE FROM system_metrics 
                    WHERE timestamp < ?
                ''', (cutoff_str,))
                
                # Clean old inactive sessions
                cursor.execute('''
                    DELETE FROM user_sessions 
                    WHERE login_time < ? AND is_active = FALSE
                ''', (cutoff_str,))
                
                conn.commit()
                self.logger.info(f"Cleaned up data older than {days} days")
                
        except Exception as e:
            self.logger.error(f"Failed to cleanup old data: {e}")
    
    def get_database_stats(self) -> Dict[str, Any]:
        """Get database statistics"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                stats = {}
                
                # Event counts
                cursor.execute("SELECT COUNT(*) FROM events")
                stats['total_events'] = cursor.fetchone()[0]
                
                cursor.execute("SELECT COUNT(*) FROM events WHERE acknowledged = FALSE")
                stats['unacknowledged_events'] = cursor.fetchone()[0]
                
                # Session counts
                cursor.execute("SELECT COUNT(*) FROM user_sessions WHERE is_active = TRUE")
                stats['active_sessions'] = cursor.fetchone()[0]
                
                # Metric counts
                cursor.execute("SELECT COUNT(*) FROM system_metrics")
                stats['total_metrics'] = cursor.fetchone()[0]
                
                # Database size
                stats['db_size_mb'] = os.path.getsize(self.db_path) / (1024 * 1024)
                
                return stats
                
        except Exception as e:
            self.logger.error(f"Failed to get database stats: {e}")
            return {}


# Singleton instance
_db_manager = None

def get_database_manager() -> DatabaseManager:
    """Get singleton database manager instance"""
    global _db_manager
    if _db_manager is None:
        _db_manager = DatabaseManager()
    return _db_manager