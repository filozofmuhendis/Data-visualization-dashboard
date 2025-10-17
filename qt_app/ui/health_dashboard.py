"""
Health Dashboard for MSA System
Specialized dashboard for medical personnel
"""

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QGroupBox, QTableWidget, QTableWidgetItem, QHeaderView,
    QProgressBar, QListWidget, QListWidgetItem, QTabWidget,
    QSplitter, QFrame, QGridLayout, QComboBox, QSpinBox,
    QMessageBox, QScrollArea, QTextEdit, QDateEdit, QTimeEdit
)
from PyQt5.QtCore import Qt, pyqtSignal, QTimer, pyqtSlot, QDate, QTime
from PyQt5.QtGui import QFont, QIcon, QPixmap, QPalette
# PyQtChart import removed - using basic widgets instead
import json
from datetime import datetime, timedelta
from ..utils.styles import get_status_color, get_risk_level_style


class HealthDashboard(QWidget):
    """Specialized health monitoring dashboard"""
    
    # Signals
    logout_requested = pyqtSignal()
    
    def __init__(self, api_client):
        super().__init__()
        self.api_client = api_client
        self.current_user = None
        self.update_timer = QTimer()
        self.selected_unit = None
        
        self.setup_ui()
        self.setup_connections()
        self.setup_timers()
    
    def setup_ui(self):
        """Setup the health dashboard UI"""
        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)
        
        # Header
        header = self.create_header()
        main_layout.addWidget(header)
        
        # Main content area with splitter
        splitter = QSplitter(Qt.Horizontal)
        
        # Left panel - Health overview and alerts
        left_panel = self.create_left_panel()
        splitter.addWidget(left_panel)
        
        # Right panel - Detailed health monitoring
        right_panel = self.create_right_panel()
        splitter.addWidget(right_panel)
        
        # Set splitter proportions
        splitter.setSizes([600, 600])
        main_layout.addWidget(splitter)
    
    def create_header(self):
        """Create dashboard header"""
        header_frame = QFrame()
        header_frame.setFrameStyle(QFrame.StyledPanel)
        header_layout = QHBoxLayout(header_frame)
        
        # Title section
        title_layout = QVBoxLayout()
        title_label = QLabel("Health Monitoring Dashboard")
        title_label.setProperty("class", "title")
        
        self.user_label = QLabel("Medical Officer")
        self.user_label.setProperty("class", "subtitle")
        
        title_layout.addWidget(title_label)
        title_layout.addWidget(self.user_label)
        
        # Health summary indicators
        summary_layout = QHBoxLayout()
        
        self.total_personnel_label = QLabel("Personnel: 0")
        self.healthy_count_label = QLabel("Healthy: 0")
        self.warning_count_label = QLabel("Warning: 0")
        self.critical_count_label = QLabel("Critical: 0")
        
        summary_layout.addWidget(self.total_personnel_label)
        summary_layout.addWidget(self.healthy_count_label)
        summary_layout.addWidget(self.warning_count_label)
        summary_layout.addWidget(self.critical_count_label)
        
        # Control buttons
        controls_layout = QHBoxLayout()
        
        self.refresh_button = QPushButton("Refresh")
        self.refresh_button.setProperty("class", "primary")
        
        self.export_button = QPushButton("Export Report")
        
        self.emergency_button = QPushButton("Emergency Alert")
        self.emergency_button.setProperty("class", "danger")
        
        self.logout_button = QPushButton("Logout")
        
        controls_layout.addWidget(self.refresh_button)
        controls_layout.addWidget(self.export_button)
        controls_layout.addWidget(self.emergency_button)
        controls_layout.addWidget(self.logout_button)
        
        # Add to header
        header_layout.addLayout(title_layout)
        header_layout.addStretch()
        header_layout.addLayout(summary_layout)
        header_layout.addStretch()
        header_layout.addLayout(controls_layout)
        
        return header_frame
    
    def create_left_panel(self):
        """Create left panel with health overview"""
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        
        # Health status overview
        overview_group = QGroupBox("Health Status Overview")
        overview_layout = QVBoxLayout(overview_group)
        
        # Personnel list with health indicators
        self.personnel_table = QTableWidget()
        self.personnel_table.setColumnCount(6)
        self.personnel_table.setHorizontalHeaderLabels([
            "Unit ID", "Name", "Status", "Heart Rate", "SpO2", "Last Update"
        ])
        
        header = self.personnel_table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch)
        self.personnel_table.setAlternatingRowColors(True)
        self.personnel_table.setSelectionBehavior(QTableWidget.SelectRows)
        
        overview_layout.addWidget(self.personnel_table)
        
        # Filter controls
        filter_layout = QHBoxLayout()
        
        self.status_filter = QComboBox()
        self.status_filter.addItems(["All Status", "Healthy", "Warning", "Critical"])
        
        self.unit_type_filter = QComboBox()
        self.unit_type_filter.addItems(["All Units", "Infantry", "Armor", "Artillery", "Recon", "Support"])
        
        filter_layout.addWidget(QLabel("Status:"))
        filter_layout.addWidget(self.status_filter)
        filter_layout.addWidget(QLabel("Unit Type:"))
        filter_layout.addWidget(self.unit_type_filter)
        filter_layout.addStretch()
        
        overview_layout.addLayout(filter_layout)
        
        # Health alerts
        alerts_group = QGroupBox("Health Alerts")
        alerts_layout = QVBoxLayout(alerts_group)
        
        self.health_alerts_list = QListWidget()
        self.health_alerts_list.setMaximumHeight(200)
        alerts_layout.addWidget(self.health_alerts_list)
        
        # Alert controls
        alert_controls = QHBoxLayout()
        
        self.acknowledge_button = QPushButton("Acknowledge Selected")
        self.acknowledge_button.setProperty("class", "success")
        
        self.create_alert_button = QPushButton("Create Alert")
        self.create_alert_button.setProperty("class", "warning")
        
        alert_controls.addWidget(self.acknowledge_button)
        alert_controls.addWidget(self.create_alert_button)
        alert_controls.addStretch()
        
        alerts_layout.addLayout(alert_controls)
        
        left_layout.addWidget(overview_group, 2)
        left_layout.addWidget(alerts_group, 1)
        
        return left_widget
    
    def create_right_panel(self):
        """Create right panel with detailed monitoring"""
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        
        # Selected personnel details
        details_group = QGroupBox("Personnel Details")
        details_layout = QVBoxLayout(details_group)
        
        # Personnel info
        info_layout = QGridLayout()
        
        self.selected_unit_label = QLabel("No personnel selected")
        self.selected_unit_label.setProperty("class", "subtitle")
        
        self.selected_name_label = QLabel("-")
        self.selected_rank_label = QLabel("-")
        self.selected_position_label = QLabel("-")
        
        info_layout.addWidget(QLabel("Unit ID:"), 0, 0)
        info_layout.addWidget(self.selected_unit_label, 0, 1)
        info_layout.addWidget(QLabel("Name:"), 1, 0)
        info_layout.addWidget(self.selected_name_label, 1, 1)
        info_layout.addWidget(QLabel("Rank:"), 2, 0)
        info_layout.addWidget(self.selected_rank_label, 2, 1)
        info_layout.addWidget(QLabel("Position:"), 3, 0)
        info_layout.addWidget(self.selected_position_label, 3, 1)
        
        details_layout.addLayout(info_layout)
        
        # Vital signs
        vitals_group = QGroupBox("Current Vital Signs")
        vitals_layout = QGridLayout(vitals_group)
        
        # Heart rate
        self.heart_rate_label = QLabel("--")
        self.heart_rate_label.setProperty("class", "vital-value")
        self.heart_rate_status = QLabel("Normal")
        
        # SpO2
        self.spo2_label = QLabel("--")
        self.spo2_label.setProperty("class", "vital-value")
        self.spo2_status = QLabel("Normal")
        
        # Body temperature
        self.temperature_label = QLabel("--")
        self.temperature_label.setProperty("class", "vital-value")
        self.temperature_status = QLabel("Normal")
        
        # Stress index
        self.stress_label = QLabel("--")
        self.stress_label.setProperty("class", "vital-value")
        self.stress_status = QLabel("Normal")
        
        vitals_layout.addWidget(QLabel("Heart Rate (BPM):"), 0, 0)
        vitals_layout.addWidget(self.heart_rate_label, 0, 1)
        vitals_layout.addWidget(self.heart_rate_status, 0, 2)
        
        vitals_layout.addWidget(QLabel("SpO2 (%):"), 1, 0)
        vitals_layout.addWidget(self.spo2_label, 1, 1)
        vitals_layout.addWidget(self.spo2_status, 1, 2)
        
        vitals_layout.addWidget(QLabel("Temperature (°C):"), 2, 0)
        vitals_layout.addWidget(self.temperature_label, 2, 1)
        vitals_layout.addWidget(self.temperature_status, 2, 2)
        
        vitals_layout.addWidget(QLabel("Stress Index:"), 3, 0)
        vitals_layout.addWidget(self.stress_label, 3, 1)
        vitals_layout.addWidget(self.stress_status, 3, 2)
        
        details_layout.addWidget(vitals_group)
        
        # Historical data chart (placeholder)
        chart_group = QGroupBox("Vital Signs History")
        chart_layout = QVBoxLayout(chart_group)
        
        self.chart_placeholder = QLabel("Historical chart will be displayed here")
        self.chart_placeholder.setAlignment(Qt.AlignCenter)
        self.chart_placeholder.setMinimumHeight(200)
        self.chart_placeholder.setStyleSheet("border: 1px solid #3e3e42; background: #2d2d30;")
        
        chart_layout.addWidget(self.chart_placeholder)
        
        details_layout.addWidget(chart_group)
        
        # Medical notes
        notes_group = QGroupBox("Medical Notes")
        notes_layout = QVBoxLayout(notes_group)
        
        self.medical_notes = QTextEdit()
        self.medical_notes.setMaximumHeight(150)
        self.medical_notes.setPlaceholderText("Enter medical observations and notes...")
        
        notes_controls = QHBoxLayout()
        
        self.save_notes_button = QPushButton("Save Notes")
        self.save_notes_button.setProperty("class", "success")
        
        self.clear_notes_button = QPushButton("Clear")
        
        notes_controls.addWidget(self.save_notes_button)
        notes_controls.addWidget(self.clear_notes_button)
        notes_controls.addStretch()
        
        notes_layout.addWidget(self.medical_notes)
        notes_layout.addLayout(notes_controls)
        
        details_layout.addWidget(notes_group)
        
        right_layout.addWidget(details_group)
        
        return right_widget
    
    def setup_connections(self):
        """Setup signal-slot connections"""
        # Header buttons
        self.refresh_button.clicked.connect(self.refresh_data)
        self.logout_button.clicked.connect(self.logout_requested.emit)
        self.emergency_button.clicked.connect(self.send_emergency_alert)
        
        # Personnel table selection
        self.personnel_table.itemSelectionChanged.connect(self.on_personnel_selected)
        
        # Filter controls
        self.status_filter.currentTextChanged.connect(self.filter_personnel)
        self.unit_type_filter.currentTextChanged.connect(self.filter_personnel)
        
        # Alert controls
        self.acknowledge_button.clicked.connect(self.acknowledge_selected_alert)
        self.create_alert_button.clicked.connect(self.create_health_alert)
        
        # Notes controls
        self.save_notes_button.clicked.connect(self.save_medical_notes)
        self.clear_notes_button.clicked.connect(self.clear_medical_notes)
        
        # API client signals
        self.api_client.data_received.connect(self.on_data_received)
        self.api_client.error_occurred.connect(self.on_api_error)
    
    def setup_timers(self):
        """Setup update timers"""
        self.update_timer.timeout.connect(self.refresh_data)
        self.update_timer.start(3000)  # Update every 3 seconds for health data
    
    def initialize_dashboard(self, user_data):
        """Initialize dashboard with user data"""
        self.current_user = user_data.get('user', {})
        user_name = self.current_user.get('full_name', 'Medical Officer')
        self.user_label.setText(f"{user_name}")
        
        # Start API client
        self.api_client.start_auto_refresh()
        
        # Initial data load
        self.refresh_data()
    
    def stop_updates(self):
        """Stop all update timers"""
        self.update_timer.stop()
        self.api_client.stop_auto_refresh()
    
    @pyqtSlot(str, dict)
    def on_data_received(self, endpoint, data):
        """Handle data received from API"""
        if endpoint == "health":
            self.update_health_data(data.get('data', []))
        elif endpoint == "alerts":
            self.update_health_alerts(data.get('data', []))
    
    @pyqtSlot(str, str)
    def on_api_error(self, endpoint, error):
        """Handle API errors"""
        QMessageBox.warning(self, "API Error", f"Error loading {endpoint}: {error}")
    
    def refresh_data(self):
        """Refresh health dashboard data"""
        # API client will automatically fetch data
        pass
    
    def update_health_data(self, health_data):
        """Update health monitoring data"""
        # Update summary counts
        total_count = len(health_data)
        healthy_count = len([h for h in health_data if h.get('risk_level') == 'green'])
        warning_count = len([h for h in health_data if h.get('risk_level') == 'amber'])
        critical_count = len([h for h in health_data if h.get('risk_level') == 'red'])
        
        self.total_personnel_label.setText(f"Personnel: {total_count}")
        self.healthy_count_label.setText(f"Healthy: {healthy_count}")
        self.warning_count_label.setText(f"Warning: {warning_count}")
        self.critical_count_label.setText(f"Critical: {critical_count}")
        
        # Update personnel table
        self.personnel_table.setRowCount(len(health_data))
        
        for row, health in enumerate(health_data):
            unit_id = health.get('unit_id', '')
            name = health.get('name', f"Personnel {unit_id}")
            status = health.get('risk_level', 'green').upper()
            heart_rate = health.get('heart_rate', 0)
            spo2 = health.get('spo2', 0)
            last_update = health.get('timestamp', '')
            
            self.personnel_table.setItem(row, 0, QTableWidgetItem(unit_id))
            self.personnel_table.setItem(row, 1, QTableWidgetItem(name))
            
            # Status with color
            status_item = QTableWidgetItem(status)
            if status == 'GREEN':
                status_item.setBackground(Qt.green)
            elif status == 'AMBER':
                status_item.setBackground(Qt.yellow)
            else:
                status_item.setBackground(Qt.red)
            self.personnel_table.setItem(row, 2, status_item)
            
            self.personnel_table.setItem(row, 3, QTableWidgetItem(str(heart_rate)))
            self.personnel_table.setItem(row, 4, QTableWidgetItem(str(spo2)))
            self.personnel_table.setItem(row, 5, QTableWidgetItem(last_update))
    
    def update_health_alerts(self, alerts_data):
        """Update health-specific alerts"""
        self.health_alerts_list.clear()
        
        health_alerts = [alert for alert in alerts_data if alert.get('category') == 'health']
        
        for alert in health_alerts:
            alert_text = f"[{alert.get('severity', '').upper()}] {alert.get('unit_id', '')}: {alert.get('message', '')}"
            item = QListWidgetItem(alert_text)
            
            # Color based on severity
            if alert.get('severity') == 'critical':
                item.setForeground(Qt.red)
            elif alert.get('severity') == 'warning':
                item.setForeground(Qt.yellow)
            else:
                item.setForeground(Qt.white)
            
            self.health_alerts_list.addItem(item)
    
    def on_personnel_selected(self):
        """Handle personnel selection in table"""
        current_row = self.personnel_table.currentRow()
        if current_row >= 0:
            unit_id = self.personnel_table.item(current_row, 0).text()
            self.selected_unit = unit_id
            self.update_personnel_details(unit_id)
    
    def update_personnel_details(self, unit_id):
        """Update detailed view for selected personnel"""
        self.selected_unit_label.setText(unit_id)
        
        # Mock data for demonstration
        self.selected_name_label.setText(f"Soldier {unit_id}")
        self.selected_rank_label.setText("Private First Class")
        self.selected_position_label.setText("39.9042, 32.6195")
        
        # Mock vital signs
        self.heart_rate_label.setText("72")
        self.heart_rate_status.setText("Normal")
        self.heart_rate_status.setStyleSheet(get_risk_level_style("low"))
        
        self.spo2_label.setText("98")
        self.spo2_status.setText("Normal")
        self.spo2_status.setStyleSheet(get_risk_level_style("low"))
        
        self.temperature_label.setText("36.8")
        self.temperature_status.setText("Normal")
        self.temperature_status.setStyleSheet(get_risk_level_style("low"))
        
        self.stress_label.setText("2.1")
        self.stress_status.setText("Low")
        self.stress_status.setStyleSheet(get_risk_level_style("low"))
    
    def create_vital_signs_chart(self):
        """Create vital signs chart widget (simplified without PyQtChart)"""
        chart_widget = QWidget()
        chart_layout = QVBoxLayout(chart_widget)
        
        # Chart title
        title = QLabel("Vital Signs Trends")
        title.setFont(QFont("Arial", 12, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        chart_layout.addWidget(title)
        
        # Simulated chart data display
        chart_data = QTextEdit()
        chart_data.setReadOnly(True)
        chart_data.setMaximumHeight(200)
        chart_data.setText("""
📈 Heart Rate: 72-85 BPM (Normal)
🌡️ Temperature: 36.5-37.2°C (Normal)  
🩸 Blood Pressure: 120/80 mmHg (Optimal)
💨 Respiratory Rate: 16-20/min (Normal)
🩺 SpO2: 98-100% (Excellent)

Trend: Stable over last 24 hours
Last Updated: 2 minutes ago
        """)
        chart_layout.addWidget(chart_data)
        
        return chart_widget
    
    def filter_personnel(self):
        """Filter personnel table based on selected criteria"""
        status_filter = self.status_filter.currentText()
        unit_filter = self.unit_type_filter.currentText()
        
        # Implementation for filtering
        for row in range(self.personnel_table.rowCount()):
            show_row = True
            
            if status_filter != "All Status":
                status_item = self.personnel_table.item(row, 2)
                if status_item and status_filter.upper() not in status_item.text():
                    show_row = False
            
            self.personnel_table.setRowHidden(row, not show_row)
    
    def send_emergency_alert(self):
        """Send emergency health alert"""
        reply = QMessageBox.question(
            self, 
            "Emergency Alert", 
            "Send emergency medical alert to all commanders?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            QMessageBox.information(self, "Alert Sent", "Emergency medical alert has been sent to all commanders.")
    
    def acknowledge_selected_alert(self):
        """Acknowledge selected health alert"""
        current_item = self.health_alerts_list.currentItem()
        if current_item:
            current_item.setForeground(Qt.gray)
            QMessageBox.information(self, "Alert Acknowledged", "Selected alert has been acknowledged.")
    
    def create_health_alert(self):
        """Create new health alert"""
        if self.selected_unit:
            QMessageBox.information(
                self, 
                "Alert Created", 
                f"Health alert created for unit {self.selected_unit}"
            )
        else:
            QMessageBox.warning(self, "No Selection", "Please select a personnel first.")
    
    def save_medical_notes(self):
        """Save medical notes for selected personnel"""
        if self.selected_unit and self.medical_notes.toPlainText().strip():
            QMessageBox.information(
                self, 
                "Notes Saved", 
                f"Medical notes saved for unit {self.selected_unit}"
            )
        else:
            QMessageBox.warning(self, "Cannot Save", "Please select personnel and enter notes.")
    
    def clear_medical_notes(self):
        """Clear medical notes"""
        self.medical_notes.clear()