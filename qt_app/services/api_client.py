"""
API Client for MSA Dashboard
Handles HTTP requests to FastAPI backend
"""

import requests
import json
from typing import Dict, List, Optional, Any
from PyQt5.QtCore import QObject, pyqtSignal, QTimer
from PyQt5.QtNetwork import QNetworkAccessManager, QNetworkRequest, QNetworkReply
from PyQt5.QtCore import QUrl, QByteArray


class APIClient(QObject):
    """HTTP client for communicating with FastAPI backend"""
    
    # Signals for async operations
    data_received = pyqtSignal(str, dict)  # endpoint, data
    error_occurred = pyqtSignal(str, str)  # endpoint, error_message
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        super().__init__()
        self.base_url = base_url.rstrip('/')
        self.token = None
        self.session = requests.Session()
        
        # Setup network manager for Qt-based requests
        self.network_manager = QNetworkAccessManager()
        
        # Auto-refresh timer
        self.refresh_timer = QTimer()
        self.refresh_timer.timeout.connect(self.refresh_all_data)
        self.refresh_interval = 5000  # 5 seconds
    
    def set_token(self, token: str):
        """Set authentication token"""
        self.token = token
        self.session.headers.update({
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        })
    
    def clear_token(self):
        """Clear authentication token"""
        self.token = None
        if 'Authorization' in self.session.headers:
            del self.session.headers['Authorization']
    
    def start_auto_refresh(self):
        """Start automatic data refresh"""
        if not self.refresh_timer.isActive():
            self.refresh_timer.start(self.refresh_interval)
    
    def stop_auto_refresh(self):
        """Stop automatic data refresh"""
        self.refresh_timer.stop()
    
    def set_refresh_interval(self, interval_ms: int):
        """Set refresh interval in milliseconds"""
        self.refresh_interval = interval_ms
        if self.refresh_timer.isActive():
            self.refresh_timer.stop()
            self.refresh_timer.start(self.refresh_interval)
    
    # Authentication methods
    def login(self, username: str, password: str) -> Dict[str, Any]:
        """Login to the system"""
        try:
            response = self.session.post(
                f"{self.base_url}/api/auth/login",
                json={"username": username, "password": password}
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise Exception(f"Login failed: {str(e)}")
    
    def logout(self) -> bool:
        """Logout from the system"""
        try:
            if self.token:
                response = self.session.post(f"{self.base_url}/api/auth/logout")
                response.raise_for_status()
            return True
        except requests.exceptions.RequestException:
            return False
    
    def get_current_user(self) -> Dict[str, Any]:
        """Get current user information"""
        try:
            response = self.session.get(f"{self.base_url}/api/auth/me")
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise Exception(f"Failed to get user info: {str(e)}")
    
    # Data fetching methods
    def get_units(self, status: Optional[str] = None, unit_type: Optional[str] = None) -> List[Dict]:
        """Get all units with optional filtering"""
        try:
            params = {}
            if status:
                params['status'] = status
            if unit_type:
                params['unit_type'] = unit_type
            
            response = self.session.get(f"{self.base_url}/api/units", params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            self.error_occurred.emit("units", str(e))
            return []
    
    def get_health_metrics(self, unit_id: Optional[str] = None) -> List[Dict]:
        """Get health metrics"""
        try:
            params = {}
            if unit_id:
                params['unit_id'] = unit_id
            
            response = self.session.get(f"{self.base_url}/api/health-metrics", params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            self.error_occurred.emit("health", str(e))
            return []
    
    def get_logistics(self, unit_id: Optional[str] = None) -> List[Dict]:
        """Get logistics status"""
        try:
            params = {}
            if unit_id:
                params['unit_id'] = unit_id
            
            response = self.session.get(f"{self.base_url}/api/logistics", params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            self.error_occurred.emit("logistics", str(e))
            return []
    
    def get_alerts(self, severity: Optional[str] = None, acknowledged: Optional[bool] = None) -> List[Dict]:
        """Get alerts with filtering"""
        try:
            params = {}
            if severity:
                params['severity'] = severity
            if acknowledged is not None:
                params['acknowledged'] = acknowledged
            
            response = self.session.get(f"{self.base_url}/api/alerts", params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            self.error_occurred.emit("alerts", str(e))
            return []
    
    def get_missions(self) -> List[Dict]:
        """Get missions data"""
        try:
            response = self.session.get(f"{self.base_url}/api/missions")
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            self.error_occurred.emit("missions", str(e))
            return []
    
    def get_weather(self) -> List[Dict]:
        """Get weather data"""
        try:
            response = self.session.get(f"{self.base_url}/api/weather")
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            self.error_occurred.emit("weather", str(e))
            return []
    
    def get_threats(self) -> List[Dict]:
        """Get threat detections"""
        try:
            response = self.session.get(f"{self.base_url}/api/threats")
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            self.error_occurred.emit("threats", str(e))
            return []
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get system status"""
        try:
            response = self.session.get(f"{self.base_url}/api/system-status")
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            self.error_occurred.emit("system_status", str(e))
            return {}
    
    # Action methods
    def acknowledge_alert(self, alert_id: str) -> bool:
        """Acknowledge an alert"""
        try:
            response = self.session.post(f"{self.base_url}/api/alerts/{alert_id}/acknowledge")
            response.raise_for_status()
            return True
        except requests.exceptions.RequestException as e:
            self.error_occurred.emit("acknowledge_alert", str(e))
            return False
    
    def update_unit(self, unit_id: str, update_data: Dict) -> bool:
        """Update unit information"""
        try:
            response = self.session.put(f"{self.base_url}/api/units/{unit_id}", json=update_data)
            response.raise_for_status()
            return True
        except requests.exceptions.RequestException as e:
            self.error_occurred.emit("update_unit", str(e))
            return False
    
    # Bulk data refresh
    def refresh_all_data(self):
        """Refresh all data and emit signals"""
        if not self.token:
            return
        
        try:
            # Get all data
            units = self.get_units()
            health = self.get_health_metrics()
            logistics = self.get_logistics()
            alerts = self.get_alerts()
            missions = self.get_missions()
            weather = self.get_weather()
            threats = self.get_threats()
            system_status = self.get_system_status()
            
            # Emit signals with data
            self.data_received.emit("units", {"data": units})
            self.data_received.emit("health", {"data": health})
            self.data_received.emit("logistics", {"data": logistics})
            self.data_received.emit("alerts", {"data": alerts})
            self.data_received.emit("missions", {"data": missions})
            self.data_received.emit("weather", {"data": weather})
            self.data_received.emit("threats", {"data": threats})
            self.data_received.emit("system_status", {"data": system_status})
            
        except Exception as e:
            self.error_occurred.emit("refresh_all", str(e))
    
    # Dashboard data endpoint
    def get_dashboard_data(self) -> Dict[str, Any]:
        """Get complete dashboard data"""
        try:
            response = self.session.get(f"{self.base_url}/api/dashboard-data")
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            self.error_occurred.emit("dashboard_data", str(e))
            return {}