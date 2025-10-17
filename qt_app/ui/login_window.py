"""
Login Window for MSA Dashboard
Modern authentication interface with role-based access
"""

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
    QPushButton, QCheckBox, QGroupBox, QMessageBox, QProgressBar,
    QComboBox, QFrame
)
from PyQt5.QtCore import Qt, pyqtSignal, QTimer, QThread, pyqtSlot
from PyQt5.QtGui import QPixmap, QFont, QPalette, QMovie
from ..utils.styles import apply_login_styles, get_status_color


class LoginWorker(QThread):
    """Worker thread for login operations"""
    login_completed = pyqtSignal(dict)
    login_failed = pyqtSignal(str)
    
    def __init__(self, auth_manager, username, password):
        super().__init__()
        self.auth_manager = auth_manager
        self.username = username
        self.password = password
    
    def run(self):
        try:
            result = self.auth_manager.login(self.username, self.password, True)
            self.login_completed.emit(result)
        except Exception as e:
            self.login_failed.emit(str(e))


class LoginWindow(QWidget):
    """Modern login window with authentication"""
    
    # Signals
    login_successful = pyqtSignal(dict)
    login_failed = pyqtSignal(str)
    
    def __init__(self, auth_manager):
        super().__init__()
        self.auth_manager = auth_manager
        self.login_worker = None
        
        self.setup_ui()
        self.setup_connections()
        apply_login_styles(self)
        
        # Check for saved session
        self.check_saved_session()
    
    def setup_ui(self):
        """Setup the login interface"""
        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setAlignment(Qt.AlignCenter)
        main_layout.setSpacing(20)
        
        # Header section
        header_layout = QVBoxLayout()
        header_layout.setAlignment(Qt.AlignCenter)
        
        # Logo/Title
        title_label = QLabel("MSA Dashboard")
        title_label.setProperty("class", "login-title")
        title_label.setAlignment(Qt.AlignCenter)
        
        subtitle_label = QLabel("Military Situational Awareness System")
        subtitle_label.setProperty("class", "login-subtitle")
        subtitle_label.setAlignment(Qt.AlignCenter)
        
        header_layout.addWidget(title_label)
        header_layout.addWidget(subtitle_label)
        
        # Login form
        form_group = QGroupBox()
        form_group.setProperty("class", "login-form")
        form_group.setFixedWidth(400)
        form_layout = QVBoxLayout(form_group)
        form_layout.setSpacing(15)
        
        # Username field
        username_layout = QVBoxLayout()
        username_label = QLabel("Username:")
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Enter your username")
        self.username_input.setMinimumHeight(40)
        username_layout.addWidget(username_label)
        username_layout.addWidget(self.username_input)
        
        # Password field
        password_layout = QVBoxLayout()
        password_label = QLabel("Password:")
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Enter your password")
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setMinimumHeight(40)
        password_layout.addWidget(password_label)
        password_layout.addWidget(self.password_input)
        
        # Role selection (for demo purposes)
        role_layout = QVBoxLayout()
        role_label = QLabel("Quick Login (Demo):")
        self.role_combo = QComboBox()
        self.role_combo.addItems([
            "Select Role...",
            "Commander (commander/cmd123)",
            "Health Officer (health_officer/health123)", 
            "Operations Analyst (analyst/ops123)"
        ])
        self.role_combo.setMinimumHeight(40)
        role_layout.addWidget(role_label)
        role_layout.addWidget(self.role_combo)
        
        # Remember me checkbox
        self.remember_checkbox = QCheckBox("Remember me")
        self.remember_checkbox.setChecked(True)
        
        # Login button
        self.login_button = QPushButton("Login")
        self.login_button.setProperty("class", "primary")
        self.login_button.setMinimumHeight(45)
        self.login_button.setDefault(True)
        
        # Progress bar (hidden initially)
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setRange(0, 0)  # Indeterminate progress
        
        # Status label
        self.status_label = QLabel("")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setVisible(False)
        
        # Add widgets to form
        form_layout.addLayout(username_layout)
        form_layout.addLayout(password_layout)
        form_layout.addLayout(role_layout)
        form_layout.addWidget(self.remember_checkbox)
        form_layout.addWidget(self.login_button)
        form_layout.addWidget(self.progress_bar)
        form_layout.addWidget(self.status_label)
        
        # Add to main layout
        main_layout.addLayout(header_layout)
        main_layout.addWidget(form_group, 0, Qt.AlignCenter)
        
        # Footer
        footer_label = QLabel("© 2024 Military Systems - Secure Access Required")
        footer_label.setAlignment(Qt.AlignCenter)
        footer_label.setStyleSheet("color: #6d6d6d; font-size: 8pt;")
        main_layout.addWidget(footer_label)
    
    def setup_connections(self):
        """Setup signal-slot connections"""
        self.login_button.clicked.connect(self.handle_login)
        self.username_input.returnPressed.connect(self.handle_login)
        self.password_input.returnPressed.connect(self.handle_login)
        self.role_combo.currentTextChanged.connect(self.on_role_selected)
    
    def on_role_selected(self, role_text):
        """Handle quick role selection for demo"""
        if "Commander" in role_text:
            self.username_input.setText("commander")
            self.password_input.setText("cmd123")
        elif "Health" in role_text:
            self.username_input.setText("health_officer")
            self.password_input.setText("health123")
        elif "Analyst" in role_text:
            self.username_input.setText("analyst")
            self.password_input.setText("ops123")
    
    def handle_login(self):
        """Handle login button click"""
        username = self.username_input.text().strip()
        password = self.password_input.text()
        
        # Validate input
        if not username or not password:
            self.show_status("Please enter both username and password", "error")
            return
        
        # Disable UI during login
        self.set_login_state(True)
        
        # Start login in worker thread
        self.login_worker = LoginWorker(self.auth_manager, username, password)
        self.login_worker.login_completed.connect(self.on_login_success)
        self.login_worker.login_failed.connect(self.on_login_error)
        self.login_worker.start()
    
    @pyqtSlot(dict)
    def on_login_success(self, user_data):
        """Handle successful login"""
        self.set_login_state(False)
        self.show_status("Login successful! Loading dashboard...", "success")
        
        # Emit success signal after short delay
        QTimer.singleShot(1000, lambda: self.login_successful.emit(user_data))
    
    @pyqtSlot(str)
    def on_login_error(self, error_message):
        """Handle login error"""
        self.set_login_state(False)
        self.show_status(f"Login failed: {error_message}", "error")
        self.login_failed.emit(error_message)
        
        # Clear password field
        self.password_input.clear()
        self.password_input.setFocus()
    
    def set_login_state(self, logging_in):
        """Set UI state during login process"""
        self.login_button.setEnabled(not logging_in)
        self.username_input.setEnabled(not logging_in)
        self.password_input.setEnabled(not logging_in)
        self.role_combo.setEnabled(not logging_in)
        self.remember_checkbox.setEnabled(not logging_in)
        
        self.progress_bar.setVisible(logging_in)
        
        if logging_in:
            self.login_button.setText("Logging in...")
            self.show_status("Authenticating...", "info")
        else:
            self.login_button.setText("Login")
    
    def show_status(self, message, status_type="info"):
        """Show status message with appropriate styling"""
        self.status_label.setText(message)
        self.status_label.setProperty("class", status_type)
        self.status_label.setVisible(True)
        
        # Auto-hide after 5 seconds for non-error messages
        if status_type != "error":
            QTimer.singleShot(5000, lambda: self.status_label.setVisible(False))
    
    def reset_form(self):
        """Reset the login form"""
        self.username_input.clear()
        self.password_input.clear()
        self.role_combo.setCurrentIndex(0)
        self.status_label.setVisible(False)
        self.progress_bar.setVisible(False)
        self.set_login_state(False)
        self.username_input.setFocus()
    
    def check_saved_session(self):
        """Check if there's a saved session"""
        if self.auth_manager.is_authenticated():
            user_data = {
                'access_token': self.auth_manager.get_token(),
                'user': self.auth_manager.get_current_user()
            }
            self.show_status("Restoring saved session...", "success")
            QTimer.singleShot(1000, lambda: self.login_successful.emit(user_data))
    
    def keyPressEvent(self, event):
        """Handle key press events"""
        if event.key() == Qt.Key_Escape:
            self.reset_form()
        super().keyPressEvent(event)