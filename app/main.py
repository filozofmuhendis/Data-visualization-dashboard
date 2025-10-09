"""  
MSA Dashboard - Main FastAPI Application
FastAPI backend with REST endpoints, WebSocket support, and Dash integration
"""

import asyncio
import json
import logging
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from contextlib import asynccontextmanager

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Depends, HTTPException, status, Query, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.wsgi import WSGIMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from sqlalchemy import desc, and_, or_

# Import Dash app
import dash
from dash import Dash
from dash import html, dcc
import plotly.graph_objects as go

# Local imports
from core.models import (
    Unit, UnitUpdate, HealthMetrics, LogisticsStatus, WeatherData,
    ThreatDetection, Alert, Mission, SystemStatus, DashboardData,
    WSMessage, WSUnitUpdate, WSAlertMessage, WSHealthUpdate, WSThreatAlert,
    RiskLevel, AlertSeverity, UnitType, MissionPhase, UserRole
)
from core.database import get_db, create_tables, UnitDB, HealthMetricsDB, LogisticsStatusDB, AlertDB, engine
from core.settings import settings, ROLE_CONFIGS
from services.role_manager import role_manager, Permission
from app.dash_layout import create_dashboard_layout
from app.dash_callbacks import register_callbacks

# Configure logging
logging.basicConfig(level=getattr(logging, settings.log_level))
logger = logging.getLogger(__name__)


class ConnectionManager:
    """WebSocket connection manager for real-time updates"""
    
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self.user_connections: Dict[str, WebSocket] = {}
    
    async def connect(self, websocket: WebSocket, user_id: Optional[str] = None):
        await websocket.accept()
        self.active_connections.append(websocket)
        if user_id:
            self.user_connections[user_id] = websocket
        logger.info(f"WebSocket connected. Total connections: {len(self.active_connections)}")
    
    def disconnect(self, websocket: WebSocket, user_id: Optional[str] = None):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        if user_id and user_id in self.user_connections:
            del self.user_connections[user_id]
        logger.info(f"WebSocket disconnected. Total connections: {len(self.active_connections)}")
    
    async def send_personal_message(self, message: str, websocket: WebSocket):
        try:
            await websocket.send_text(message)
        except Exception as e:
            logger.error(f"Error sending personal message: {e}")
    
    async def broadcast(self, message: str):
        disconnected = []
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except Exception as e:
                logger.error(f"Error broadcasting message: {e}")
                disconnected.append(connection)
        
        # Remove disconnected connections
        for conn in disconnected:
            if conn in self.active_connections:
                self.active_connections.remove(conn)
    
    async def send_to_role(self, message: str, role: str):
        """Send message to users with specific role (future implementation)"""
        # This would require user role tracking in connections
        await self.broadcast(message)


# Global connection manager
manager = ConnectionManager()


# Create Dash app
dash_app = Dash(
    __name__,
    requests_pathname_prefix="/dashboard/",
    external_stylesheets=[
        "https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap"
    ],
    meta_tags=[
        {"name": "viewport", "content": "width=device-width, initial-scale=1.0"},
        {"name": "description", "content": "Military Situational Awareness Dashboard"},
    ]
)

# Set up Dash layout and callbacks
dash_app.layout = create_dashboard_layout()
register_callbacks(dash_app)

# Configure Dash app
dash_app.title = "MSA Dashboard"
dash_app.config.suppress_callback_exceptions = True


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    logger.info("Starting MSA Dashboard...")
    create_tables()
    logger.info("Database tables created/verified")
    
    # Start background tasks
    asyncio.create_task(background_data_processor())
    
    yield
    
    # Shutdown
    logger.info("Shutting down MSA Dashboard...")


# Create FastAPI app
app = FastAPI(
    title="MSA Dashboard API",
    description="Military Situational Awareness Dashboard API",
    version=settings.app_version,
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount Dash app
app.mount("/dashboard", WSGIMiddleware(dash_app.server))


# Background task for data processing
async def background_data_processor():
    """Background task to process and broadcast data updates"""
    while True:
        try:
            # This would typically process incoming data from MQTT, databases, etc.
            # For now, we'll just sleep
            await asyncio.sleep(settings.default_refresh_interval)
            
            # Example: Check for critical alerts and broadcast
            # await check_and_broadcast_critical_alerts()
            
        except Exception as e:
            logger.error(f"Error in background processor: {e}")
            await asyncio.sleep(5)


# REST API endpoints

# Authentication endpoints
@app.post("/api/auth/login")
async def login(credentials: dict):
    """User login endpoint"""
    username = credentials.get("username")
    password = credentials.get("password")
    
    if not username or not password:
        raise HTTPException(status_code=400, detail="Username and password required")
    
    session = role_manager.authenticate_user(username, password)
    if not session:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    # Create JWT token
    jwt_token = role_manager.create_jwt_token(session)
    
    return {
        "access_token": jwt_token,
        "token_type": "bearer",
        "user_info": {
            "user_id": session.user_id,
            "username": session.username,
            "role": session.role.value
        },
        "expires_at": session.expires_at.isoformat()
    }

@app.post("/api/auth/logout")
async def logout(authorization: str = Header(None)):
    """User logout endpoint"""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid authorization header")
    
    token = authorization.split(" ")[1]
    payload = role_manager.verify_jwt_token(token)
    
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    # In a real implementation, you'd maintain a blacklist of invalidated tokens
    return {"message": "Logged out successfully"}

@app.get("/api/auth/me")
async def get_current_user(authorization: str = Header(None)):
    """Get current user information"""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid authorization header")
    
    token = authorization.split(" ")[1]
    payload = role_manager.verify_jwt_token(token)
    
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    return {
        "user_id": payload["user_id"],
        "username": payload["username"],
        "role": payload["role"],
        "permissions": payload["permissions"]
    }

# Role-based dashboard configuration
@app.get("/api/dashboard-config")
async def get_dashboard_config(authorization: str = Header(None)):
    """Get role-based dashboard configuration"""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid authorization header")
    
    token = authorization.split(" ")[1]
    payload = role_manager.verify_jwt_token(token)
    
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    try:
        user_role = UserRole(payload["role"])
        layout = role_manager.get_dashboard_layout(user_role)
        
        if not layout:
            raise HTTPException(status_code=404, detail="Dashboard layout not found")
        
        return {
            "role": user_role.value,
            "panels": layout.panels,
            "panel_configs": layout.panel_configs,
            "default_filters": layout.default_filters,
            "refresh_intervals": layout.refresh_intervals,
            "color_scheme": layout.color_scheme,
            "map_config": layout.map_config
        }
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid role")

# Helper function to verify permissions
def verify_permission(authorization: str, required_permission: Permission) -> dict:
    """Verify user has required permission"""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid authorization header")
    
    token = authorization.split(" ")[1]
    payload = role_manager.verify_jwt_token(token)
    
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    user_permissions = [Permission(p) for p in payload["permissions"]]
    if required_permission not in user_permissions:
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    
    return payload

@app.get("/")
async def root():
    """Redirect to dashboard"""
    return {"message": "MSA Dashboard API", "dashboard_url": "/dashboard/"}


@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow(),
        "version": settings.app_version
    }


# Unit endpoints
@app.get("/api/units", response_model=List[Unit])
async def get_units(
    status: Optional[RiskLevel] = None,
    unit_type: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get all units with optional filtering"""
    query = db.query(UnitDB)
    
    if status:
        query = query.filter(UnitDB.status == status)
    if unit_type:
        query = query.filter(UnitDB.unit_type == unit_type)
    
    units = query.all()
    
    # Convert to Pydantic models
    result = []
    for unit in units:
        result.append(Unit(
            unit_id=unit.unit_id,
            name=unit.name,
            unit_type=unit.unit_type,
            position={
                "latitude": unit.latitude,
                "longitude": unit.longitude,
                "altitude": unit.altitude
            },
            heading=unit.heading,
            speed=unit.speed,
            status=unit.status,
            last_seen=unit.last_seen,
            timestamp=unit.updated_at
        ))
    
    return result


@app.get("/api/units/{unit_id}", response_model=Unit)
async def get_unit(unit_id: str, db: Session = Depends(get_db)):
    """Get specific unit by ID"""
    unit = db.query(UnitDB).filter(UnitDB.unit_id == unit_id).first()
    if not unit:
        raise HTTPException(status_code=404, detail="Unit not found")
    
    return Unit(
        unit_id=unit.unit_id,
        name=unit.name,
        unit_type=unit.unit_type,
        position={
            "latitude": unit.latitude,
            "longitude": unit.longitude,
            "altitude": unit.altitude
        },
        heading=unit.heading,
        speed=unit.speed,
        status=unit.status,
        last_seen=unit.last_seen,
        timestamp=unit.updated_at
    )


@app.post("/api/units/{unit_id}/update")
async def update_unit(
    unit_id: str,
    update: UnitUpdate,
    db: Session = Depends(get_db)
):
    """Update unit position and status"""
    unit = db.query(UnitDB).filter(UnitDB.unit_id == unit_id).first()
    if not unit:
        raise HTTPException(status_code=404, detail="Unit not found")
    
    # Update fields
    if update.position:
        unit.latitude = update.position.latitude
        unit.longitude = update.position.longitude
        if update.position.altitude:
            unit.altitude = update.position.altitude
    
    if update.heading is not None:
        unit.heading = update.heading
    if update.speed is not None:
        unit.speed = update.speed
    if update.status:
        unit.status = update.status
    
    unit.last_seen = datetime.utcnow()
    unit.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(unit)
    
    # Broadcast update via WebSocket
    unit_data = Unit(
        unit_id=unit.unit_id,
        name=unit.name,
        unit_type=unit.unit_type,
        position={
            "latitude": unit.latitude,
            "longitude": unit.longitude,
            "altitude": unit.altitude
        },
        heading=unit.heading,
        speed=unit.speed,
        status=unit.status,
        last_seen=unit.last_seen,
        timestamp=unit.updated_at
    )
    
    ws_message = WSUnitUpdate(data=unit_data)
    await manager.broadcast(ws_message.model_dump_json())
    
    return {"status": "updated", "unit_id": unit_id}


# Health endpoints
@app.get("/api/health-metrics", response_model=List[HealthMetrics])
async def get_health_metrics(
    unit_id: Optional[str] = None,
    hours: int = 24,
    db: Session = Depends(get_db)
):
    """Get health metrics with optional filtering"""
    query = db.query(HealthMetricsDB)
    
    if unit_id:
        query = query.filter(HealthMetricsDB.unit_id == unit_id)
    
    # Filter by time range
    since = datetime.utcnow() - timedelta(hours=hours)
    query = query.filter(HealthMetricsDB.timestamp >= since)
    
    metrics = query.order_by(desc(HealthMetricsDB.timestamp)).limit(1000).all()
    
    result = []
    for metric in metrics:
        result.append(HealthMetrics(
            unit_id=metric.unit_id,
            heart_rate=metric.heart_rate,
            spo2=metric.spo2,
            stress_index=metric.stress_index,
            body_temperature=metric.body_temperature,
            risk_level=metric.risk_level,
            timestamp=metric.timestamp
        ))
    
    return result


@app.post("/api/health-metrics")
async def create_health_metric(
    metric: HealthMetrics,
    db: Session = Depends(get_db)
):
    """Create new health metric entry"""
    db_metric = HealthMetricsDB(
        unit_id=metric.unit_id,
        heart_rate=metric.heart_rate,
        spo2=metric.spo2,
        stress_index=metric.stress_index,
        body_temperature=metric.body_temperature,
        risk_level=metric.risk_level,
        timestamp=metric.timestamp
    )
    
    db.add(db_metric)
    db.commit()
    db.refresh(db_metric)
    
    # Broadcast health update
    ws_message = WSHealthUpdate(data=metric)
    await manager.broadcast(ws_message.model_dump_json())
    
    return {"status": "created", "id": db_metric.id}


# Alert endpoints
@app.get("/api/alerts", response_model=List[Alert])
async def get_alerts(
    severity: Optional[AlertSeverity] = None,
    acknowledged: Optional[bool] = None,
    resolved: Optional[bool] = None,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Get alerts with filtering"""
    query = db.query(AlertDB)
    
    if severity:
        query = query.filter(AlertDB.severity == severity)
    if acknowledged is not None:
        query = query.filter(AlertDB.acknowledged == acknowledged)
    if resolved is not None:
        query = query.filter(AlertDB.resolved == resolved)
    
    alerts = query.order_by(desc(AlertDB.timestamp)).limit(limit).all()
    
    result = []
    for alert in alerts:
        result.append(Alert(
            alert_id=alert.alert_id,
            unit_id=alert.unit_id,
            alert_type=alert.alert_type,
            severity=alert.severity,
            title=alert.title,
            message=alert.message,
            acknowledged=alert.acknowledged,
            acknowledged_by=alert.acknowledged_by,
            acknowledged_at=alert.acknowledged_at,
            resolved=alert.resolved,
            resolved_at=alert.resolved_at,
            timestamp=alert.timestamp
        ))
    
    return result


@app.post("/api/alerts")
async def create_alert(alert: Alert, db: Session = Depends(get_db)):
    """Create new alert"""
    db_alert = AlertDB(
        alert_id=alert.alert_id,
        unit_id=alert.unit_id,
        alert_type=alert.alert_type,
        severity=alert.severity,
        title=alert.title,
        message=alert.message,
        timestamp=alert.timestamp
    )
    
    db.add(db_alert)
    db.commit()
    db.refresh(db_alert)
    
    # Broadcast alert
    ws_message = WSAlertMessage(data=alert)
    await manager.broadcast(ws_message.model_dump_json())
    
    return {"status": "created", "alert_id": alert.alert_id}


@app.put("/api/alerts/{alert_id}/acknowledge")
async def acknowledge_alert(
    alert_id: str,
    acknowledged_by: str,
    db: Session = Depends(get_db)
):
    """Acknowledge an alert"""
    alert = db.query(AlertDB).filter(AlertDB.alert_id == alert_id).first()
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    
    alert.acknowledged = True
    alert.acknowledged_by = acknowledged_by
    alert.acknowledged_at = datetime.utcnow()
    
    db.commit()
    
    return {"status": "acknowledged", "alert_id": alert_id}


# System status endpoint
@app.get("/api/system-status", response_model=SystemStatus)
async def get_system_status(db: Session = Depends(get_db)):
    """Get overall system status"""
    total_units = db.query(UnitDB).count()
    active_units = db.query(UnitDB).filter(
        UnitDB.last_seen >= datetime.utcnow() - timedelta(minutes=5)
    ).count()
    
    critical_alerts = db.query(AlertDB).filter(
        and_(
            AlertDB.severity.in_([AlertSeverity.CRITICAL, AlertSeverity.EMERGENCY]),
            AlertDB.resolved == False
        )
    ).count()
    
    # Determine system health
    if critical_alerts > 0:
        system_health = RiskLevel.RED
    elif active_units < total_units * 0.9:
        system_health = RiskLevel.AMBER
    else:
        system_health = RiskLevel.GREEN
    
    return SystemStatus(
        total_units=total_units,
        active_units=active_units,
        critical_alerts=critical_alerts,
        active_missions=0,  # TODO: Implement mission counting
        system_health=system_health
    )


# WebSocket endpoint
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket, user_id: Optional[str] = None):
    """WebSocket endpoint for real-time updates"""
    await manager.connect(websocket, user_id)
    try:
        while True:
            # Keep connection alive and handle incoming messages
            data = await websocket.receive_text()
            message = json.loads(data)
            
            # Handle different message types
            if message.get("type") == "ping":
                await websocket.send_text(json.dumps({"type": "pong"}))
            elif message.get("type") == "subscribe":
                # Handle subscription to specific data types
                await websocket.send_text(json.dumps({
                    "type": "subscribed",
                    "channels": message.get("channels", [])
                }))
            
    except WebSocketDisconnect:
        manager.disconnect(websocket, user_id)
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        manager.disconnect(websocket, user_id)


# Dashboard configuration endpoint
@app.get("/api/dashboard-config/{role}")
async def get_dashboard_config(role: str):
    """Get dashboard configuration for specific role"""
    if role not in ROLE_CONFIGS:
        raise HTTPException(status_code=404, detail="Role configuration not found")
    
    return ROLE_CONFIGS[role]


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.server_host,
        port=settings.server_port,
        reload=settings.debug,
        log_level="info"
    )