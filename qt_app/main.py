"""
MSA Dashboard - PyQt5 Desktop Application
Modern Military Situational Awareness Dashboard with role-based access
"""

import sys
import os
from PyQt5.QtWidgets import QApplication, QMainWindow, QStackedWidget
from PyQt5.QtCore import Qt, QTimer, pyqtSignal
from PyQt5.QtGui import QIcon, QFont

# Import custom modules
from ui.login_window import LoginWindow
from ui.commander_dashboard import CommanderDashboard
from ui.health_dashboard import HealthDashboard
from ui.analyst_dashboard import AnalystDashboard
from services.api_client import APIClient
from services.auth_manager import AuthManager
from utils.styles import apply_dark_theme


class MSAApplication(QMainWindow):
    """Main application window with role-based navigation"""
    
    # Signals
    user_logged_in = pyqtSignal(dict)
    user_logged_out = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("MSA Dashboard - Military Situational Awareness")
        self.setMinimumSize(1400, 900)
        self.resize(1600, 1000)
        
        # Initialize services
        self.api_client = APIClient()
        self.auth_manager = AuthManager()
        
        # Setup UI
        self.setup_ui()
        self.setup_connections()
        
        # Apply dark theme
        apply_dark_theme(self)
        
        # Show login window initially
        self.show_login()
    
    def setup_ui(self):
        """Initialize the UI components"""
        # Central widget with stacked layout
        self.stacked_widget = QStackedWidget()
        self.setCentralWidget(self.stacked_widget)
        
        # Menu bar
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu('File')
        
        logout_action = file_menu.addAction('Logout')
        logout_action.triggered.connect(self.logout)
        
        file_menu.addSeparator()
        
        exit_action = file_menu.addAction('Exit')
        exit_action.triggered.connect(self.close)
        
        # View menu
        view_menu = menubar.addMenu('View')
        
        event_history_action = view_menu.addAction('Event History')
        event_history_action.triggered.connect(self.show_event_history)
        
        # Tools menu
        tools_menu = menubar.addMenu('Tools')
        
        settings_action = tools_menu.addAction('Settings')
        settings_action.triggered.connect(self.show_settings)
        
        # Help menu
        help_menu = menubar.addMenu('Help')
        
        about_action = help_menu.addAction('About')
        about_action.triggered.connect(self.show_about)
        
        # Create windows for different roles
        self.login_window = LoginWindow(self.auth_manager)
        self.commander_dashboard = CommanderDashboard(self.api_client)
        self.health_dashboard = HealthDashboard(self.api_client)
        self.analyst_dashboard = AnalystDashboard(self.api_client)
        
        # Add windows to stack
        self.stacked_widget.addWidget(self.login_window)
        self.stacked_widget.addWidget(self.commander_dashboard)
        self.stacked_widget.addWidget(self.health_dashboard)
        self.stacked_widget.addWidget(self.analyst_dashboard)
    
    def setup_connections(self):
        """Setup signal-slot connections"""
        # Login window connections
        self.login_window.login_successful.connect(self.on_login_successful)
        self.login_window.login_failed.connect(self.on_login_failed)
        
        # Dashboard logout connections
        self.commander_dashboard.logout_requested.connect(self.logout)
        self.health_dashboard.logout_requested.connect(self.logout)
        self.analyst_dashboard.logout_requested.connect(self.logout)
        
        # Auth manager connections
        self.auth_manager.token_expired.connect(self.on_token_expired)
    
    def show_login(self):
        """Show the login window"""
        self.stacked_widget.setCurrentWidget(self.login_window)
        self.login_window.reset_form()
    
    def on_login_successful(self, user_data):
        """Handle successful login"""
        self.user_logged_in.emit(user_data)
        
        # Set API client token
        self.api_client.set_token(user_data.get('access_token'))
        
        # Show appropriate dashboard based on role
        role = user_data.get('user', {}).get('role', 'commander')
        
        if role == 'commander':
            self.stacked_widget.setCurrentWidget(self.commander_dashboard)
            self.commander_dashboard.initialize_dashboard(user_data)
        elif role == 'health':
            self.stacked_widget.setCurrentWidget(self.health_dashboard)
            self.health_dashboard.initialize_dashboard(user_data)
        elif role == 'analyst':
            self.stacked_widget.setCurrentWidget(self.analyst_dashboard)
            self.analyst_dashboard.initialize_dashboard(user_data)
        else:
            # Default to commander dashboard
            self.stacked_widget.setCurrentWidget(self.commander_dashboard)
            self.commander_dashboard.initialize_dashboard(user_data)
    
    def on_login_failed(self, error_message):
        """Handle login failure"""
        print(f"Login failed: {error_message}")
    
    def on_token_expired(self):
        """Handle token expiration"""
        self.logout()
    
    def logout(self):
        """Logout user and return to login screen"""
        self.auth_manager.logout()
        self.api_client.clear_token()
        self.user_logged_out.emit()
        self.show_login()
    
    def show_event_history(self):
        """Show event history window"""
        from ui.event_history_window import EventHistoryWindow
        
        if not hasattr(self, 'event_history_window'):
            self.event_history_window = EventHistoryWindow(self)
        
        self.event_history_window.show()
        self.event_history_window.raise_()
        self.event_history_window.activateWindow()
    
    def show_settings(self):
        """Show settings dialog"""
        from PyQt5.QtWidgets import QMessageBox
        QMessageBox.information(self, "Settings", "Settings dialog will be implemented soon.")
    
    def show_about(self):
        """Show about dialog"""
        from PyQt5.QtWidgets import QMessageBox
        QMessageBox.about(self, "About MSA Dashboard", 
                         "MSA Dashboard v1.0\n\n"
                         "Military Situational Awareness Dashboard\n"
                         "Built with PyQt5 and FastAPI\n\n"
                         "© 2024 MSA Systems")
    
    def closeEvent(self, event):
        """Handle application close"""
        # Stop any running timers or background tasks
        self.commander_dashboard.stop_updates()
        self.health_dashboard.stop_updates()
        self.analyst_dashboard.stop_updates()
        
        event.accept()


def main():
    """Main application entry point"""
    app = QApplication(sys.argv)
    
    # Set application properties
    app.setApplicationName("MSA Dashboard")
    app.setApplicationVersion("1.0.0")
    app.setOrganizationName("Military Systems")
    
    # Set default font
    font = QFont("Segoe UI", 9)
    app.setFont(font)
    
    # Create and show main window
    window = MSAApplication()
    window.show()
    
    # Start event loop
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()