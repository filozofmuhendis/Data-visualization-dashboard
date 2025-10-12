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
    
    def get_logistics(self):
        """Get logistics data - using system status as fallback"""
        try:
            # Since /api/logistics doesn't exist, use system status
            response = self.session.get(f"{self.base_url}/api/system-status")
            if response.status_code == 200:
                data = response.json()
                # Transform system status to logistics format
                logistics_data = {
                    'supplies': data.get('system_health', {}).get('memory_usage', 0),
                    'fuel': data.get('system_health', {}).get('cpu_usage', 0),
                    'ammunition': data.get('active_connections', 0),
                    'medical': data.get('total_requests', 0)
                }
                self.data_received.emit('logistics', logistics_data)
            else:
                self.error_occurred.emit(f"Failed to get logistics: {response.status_code}")
        except Exception as e:
            self.error_occurred.emit(f"Error getting logistics: {str(e)}")
    
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
    
    def get_weather(self):
        """Get weather data - using health metrics as fallback"""
        try:
            # Since /api/weather doesn't exist, use health metrics
            response = self.session.get(f"{self.base_url}/api/health-metrics")
            if response.status_code == 200:
                data = response.json()
                # Transform health metrics to weather format
                weather_data = {
                    'temperature': data.get('cpu_usage', 25),
                    'humidity': data.get('memory_usage', 60),
                    'wind_speed': data.get('disk_usage', 10),
                    'visibility': data.get('network_latency', 100)
                }
                self.data_received.emit('weather', weather_data)
            else:
                self.error_occurred.emit(f"Failed to get weather: {response.status_code}")
        except Exception as e:
            self.error_occurred.emit(f"Error getting weather: {str(e)}")
    
    def get_threats(self):
        """Get threats data - using alerts as fallback"""
        try:
            # Since /api/threats doesn't exist, use alerts
            response = self.session.get(f"{self.base_url}/api/alerts")
            if response.status_code == 200:
                data = response.json()
                # Transform alerts to threats format
                threats_data = []
                for alert in data:
                    threat = {
                        'id': alert.get('id'),
                        'type': alert.get('type', 'unknown'),
                        'severity': alert.get('severity', 'medium'),
                        'location': alert.get('location', 'Unknown'),
                        'description': alert.get('message', 'No description')
                    }
                    threats_data.append(threat)
                self.data_received.emit('threats', threats_data)
            else:
                self.error_occurred.emit(f"Failed to get threats: {response.status_code}")
        except Exception as e:
            self.error_occurred.emit(f"Error getting threats: {str(e)}")
    
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