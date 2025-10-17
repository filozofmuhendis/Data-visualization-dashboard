"""
Authentication Manager for MSA Dashboard
Handles user authentication, token management, and session persistence
"""

import json
import os
from datetime import datetime, timedelta
from .event_logger import get_event_logger
from typing import Dict, Optional, Any
from PyQt5.QtCore import QObject, pyqtSignal, QTimer, QSettings
from PyQt5.QtWidgets import QMessageBox


class AuthManager(QObject):
    """Manages user authentication and session state"""
    
    # Signals
    token_expired = pyqtSignal()
    user_data_changed = pyqtSignal(dict)
    
    def __init__(self):
        super().__init__()
        self.settings = QSettings("MSA", "Dashboard")
        self.current_user = None
        self.token = None
        self.token_expiry = None
        
        # Timer to check token expiry
        self.token_timer = QTimer()
        self.token_timer.timeout.connect(self.check_token_expiry)
        self.token_timer.start(60000)  # Check every minute
        
        # Load saved session if available
        self.load_session()
    
    def login(self, username: str, password: str, remember_me: bool = False) -> Dict[str, Any]:
        """
        Process login credentials
        Returns user data if successful, raises exception if failed
        """
        # Validate credentials (this would normally call API)
        user_data = self._validate_credentials(username, password)
        
        if user_data:
            self.current_user = user_data.get('user', {})
            self.token = user_data.get('access_token')
            
            # Calculate token expiry (assuming 24 hours)
            self.token_expiry = datetime.now() + timedelta(hours=24)
            
            # Save session if remember me is checked
            if remember_me:
                self.save_session(user_data)
            
            # Log authentication event
            event_logger = get_event_logger()
            event_logger.log_authentication_event(
                username=username,
                event="login",
                success=True,
                details=f"Role: {self.current_user.get('role')}"
            )
            
            self.user_data_changed.emit(self.current_user)
            return user_data
        else:
            # Log failed authentication
            event_logger = get_event_logger()
            event_logger.log_authentication_event(
                username=username,
                event="login_failed",
                success=False,
                details="Invalid credentials"
            )
            raise Exception("Invalid username or password")
    
    def logout(self):
        """Logout current user and clear session"""
        if self.current_user:
            # Log logout event
            event_logger = get_event_logger()
            event_logger.log_authentication_event(
                username=self.current_user.get('username', 'unknown'),
                event="logout",
                success=True,
                details="User logged out"
            )
        
        self.current_user = None
        self.token = None
        self.token_expiry = None
        self.clear_session()
    
    def is_authenticated(self) -> bool:
        """Check if user is currently authenticated"""
        return (self.current_user is not None and 
                self.token is not None and 
                self.is_token_valid())
    
    def is_token_valid(self) -> bool:
        """Check if current token is still valid"""
        if not self.token_expiry:
            return False
        return datetime.now() < self.token_expiry
    
    def get_current_user(self) -> Optional[Dict[str, Any]]:
        """Get current user data"""
        return self.current_user
    
    def get_token(self) -> Optional[str]:
        """Get current authentication token"""
        return self.token if self.is_token_valid() else None
    
    def get_user_role(self) -> Optional[str]:
        """Get current user's role"""
        if self.current_user:
            return self.current_user.get('role')
        return None
    
    def has_permission(self, permission: str) -> bool:
        """Check if current user has specific permission"""
        role = self.get_user_role()
        if not role:
            return False
        
        # Define role permissions (aligned with backend roles)
        permissions = {
            'commander': [
                'view_all_units', 'view_health', 'view_logistics', 
                'view_missions', 'view_alerts', 'acknowledge_alerts',
                'update_units', 'create_missions', 'system_admin'
            ],
            'health_officer': [
                'view_health', 'view_units_limited', 'view_alerts_health',
                'acknowledge_health_alerts', 'view_logistics_medical'
            ],
            'operations_analyst': [
                'view_units_limited', 'view_logistics', 'view_missions',
                'view_alerts_ops', 'acknowledge_ops_alerts', 'view_analytics'
            ]
        }
        
        return permission in permissions.get(role, [])
    
    def check_token_expiry(self):
        """Check if token is about to expire or has expired"""
        if self.token_expiry:
            now = datetime.now()
            
            # If token expired, emit signal
            if now >= self.token_expiry:
                self.token_expired.emit()
            
            # If token expires in 5 minutes, show warning
            elif (self.token_expiry - now).total_seconds() < 300:
                self._show_token_warning()
    
    def refresh_token(self) -> bool:
        """Refresh the authentication token"""
        # This would normally call the API to refresh the token
        # For now, just extend the expiry
        if self.token:
            self.token_expiry = datetime.now() + timedelta(hours=24)
            return True
        return False
    
    def save_session(self, user_data: Dict[str, Any]):
        """Save session data to persistent storage"""
        session_data = {
            'user': user_data.get('user', {}),
            'token': user_data.get('access_token'),
            'expiry': self.token_expiry.isoformat() if self.token_expiry else None,
            'saved_at': datetime.now().isoformat()
        }
        
        self.settings.setValue('session', json.dumps(session_data))
    
    def load_session(self):
        """Load saved session data"""
        try:
            session_json = self.settings.value('session', '')
            if session_json:
                session_data = json.loads(session_json)
                
                # Check if session is still valid
                expiry_str = session_data.get('expiry')
                if expiry_str:
                    expiry = datetime.fromisoformat(expiry_str)
                    if datetime.now() < expiry:
                        self.current_user = session_data.get('user', {})
                        self.token = session_data.get('token')
                        self.token_expiry = expiry
                        return True
                
                # Session expired, clear it
                self.clear_session()
        except (json.JSONDecodeError, ValueError, KeyError):
            # Invalid session data, clear it
            self.clear_session()
        
        return False
    
    def clear_session(self):
        """Clear saved session data"""
        self.settings.remove('session')
    
    def _validate_credentials(self, username: str, password: str) -> Optional[Dict[str, Any]]:
        """
        Validate user credentials by calling the web API
        """
        import requests
        
        try:
            # Call the actual web API for authentication
            response = requests.post(
                "http://localhost:8000/api/auth/login",
                json={"username": username, "password": password},
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                server_data = response.json()
                # Normalize backend response: map user_info -> user
                user_info = server_data.get('user_info', {})
                normalized = {
                    'access_token': server_data.get('access_token'),
                    'token_type': server_data.get('token_type', 'bearer'),
                    'user': {
                        'user_id': user_info.get('user_id'),
                        'username': user_info.get('username'),
                        'role': user_info.get('role'),
                        # Provide sensible defaults if not present
                        'full_name': user_info.get('full_name', user_info.get('username', 'User')),
                        'email': user_info.get('email', '')
                    },
                    'expires_at': server_data.get('expires_at')
                }
                return normalized
            else:
                return None
                
        except requests.exceptions.RequestException as e:
            print(f"API authentication failed: {e}")
            
            # Fallback to mock authentication if API is not available
            users = {
                'admin': {
                    'password': 'admin123',
                    'user': {
                        'user_id': 'admin',
                        'username': 'admin',
                        'role': 'commander',
                        'full_name': 'System Administrator',
                        'email': 'admin@msa.mil'
                    }
                },
                'commander': {
                    'password': 'cmd123',
                    'user': {
                        'user_id': 'cmd001',
                        'username': 'commander',
                        'role': 'commander',
                        'full_name': 'Field Commander',
                        'email': 'commander@msa.mil'
                    }
                },
                'health_officer': {
                    'password': 'health123',
                    'user': {
                        'user_id': 'med001',
                        'username': 'health_officer',
                        'role': 'health_officer',
                        'full_name': 'Medical Officer',
                        'email': 'medical@msa.mil'
                    }
                },
                'analyst': {
                    'password': 'ops123',
                    'user': {
                        'user_id': 'ops001',
                        'username': 'analyst',
                        'role': 'operations_analyst',
                        'full_name': 'Operations Analyst',
                        'email': 'analyst@msa.mil'
                    }
                }
            }
            
            user_info = users.get(username)
            if user_info and user_info['password'] == password:
                return {
                    'access_token': f'mock_token_{username}_{datetime.now().timestamp()}',
                    'token_type': 'bearer',
                    'user': user_info['user']
                }
            
            return None
    
    def _show_token_warning(self):
        """Show token expiry warning"""
        # This could be implemented to show a system tray notification
        # or a dialog warning about token expiry
        pass


# Global auth manager instance
_auth_manager = None

def get_auth_manager() -> AuthManager:
    """Get the global auth manager instance"""
    global _auth_manager
    if _auth_manager is None:
        _auth_manager = AuthManager()
    return _auth_manager