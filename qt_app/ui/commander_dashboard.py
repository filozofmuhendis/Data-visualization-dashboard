"""
Commander Dashboard for MSA System
Full access dashboard for military commanders
"""

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QGroupBox, QTableWidget, QTableWidgetItem, QHeaderView,
    QProgressBar, QListWidget, QListWidgetItem, QTabWidget,
    QSplitter, QFrame, QGridLayout, QComboBox, QSpinBox,
    QMessageBox, QToolBar, QAction, QStatusBar, QCheckBox,
    QLineEdit, QTextEdit
)
from PyQt5.QtCore import Qt, pyqtSignal, QTimer, pyqtSlot
from PyQt5.QtGui import QFont, QIcon, QPixmap
from PyQt5.QtWebEngineWidgets import QWebEngineView
import json
import tempfile
import os
from datetime import datetime
from utils.styles import get_status_color, get_risk_level_style, get_unit_type_icon
from ui.map_widget import InteractiveMapWidget
from services.auth_manager import get_auth_manager
from services.heatmap_service import get_heatmap_service


class CommanderDashboard(QWidget):
    """Full-featured commander dashboard"""
    
    # Signals
    logout_requested = pyqtSignal()
    
    def __init__(self, api_client):
        super().__init__()
        self.api_client = api_client
        self.current_user = None
        
        # Initialize auth manager
        self.auth_manager = get_auth_manager()
        
        # Initialize update timer
        self.update_timer = QTimer()
        
        # Initialize services
        self.heatmap_service = get_heatmap_service()
        
        # Data storage
        self.current_units = []
        self.current_alerts = []
        
        self.setup_ui()
        self.setup_connections()
        self.setup_timers()
    
    def setup_ui(self):
        """Setup the commander dashboard UI"""
        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)
        
        # Header
        header = self.create_header()
        main_layout.addWidget(header)
        
        # Main content area with splitter
        splitter = QSplitter(Qt.Horizontal)
        
        # Left panel - Map and mission info
        left_panel = self.create_left_panel()
        splitter.addWidget(left_panel)
        
        # Right panel - Units, health, logistics, alerts
        right_panel = self.create_right_panel()
        splitter.addWidget(right_panel)
        
        # Set splitter proportions
        splitter.setSizes([700, 500])
        main_layout.addWidget(splitter)
        
        # Status bar
        self.status_bar = QStatusBar()
        self.status_bar.showMessage("Ready")
        main_layout.addWidget(self.status_bar)
    
    def create_header(self):
        """Create dashboard header with title and controls"""
        header_frame = QFrame()
        header_frame.setFrameStyle(QFrame.StyledPanel)
        header_layout = QHBoxLayout(header_frame)
        
        # Title section
        title_layout = QVBoxLayout()
        title_label = QLabel("Commander Dashboard")
        title_label.setProperty("class", "title")
        
        self.user_label = QLabel("Welcome, Commander")
        self.user_label.setProperty("class", "subtitle")
        
        title_layout.addWidget(title_label)
        title_layout.addWidget(self.user_label)
        
        # System status indicators
        status_layout = QHBoxLayout()
        
        self.system_status_label = QLabel("System: OPERATIONAL")
        self.system_status_label.setStyleSheet(get_risk_level_style("low"))
        
        self.units_status_label = QLabel("Units: 0/0")
        self.alerts_status_label = QLabel("Alerts: 0")
        
        status_layout.addWidget(self.system_status_label)
        status_layout.addWidget(self.units_status_label)
        status_layout.addWidget(self.alerts_status_label)
        
        # Control buttons
        controls_layout = QHBoxLayout()
        
        self.refresh_button = QPushButton("Refresh")
        self.refresh_button.setProperty("class", "primary")
        
        self.settings_button = QPushButton("Settings")
        
        self.logout_button = QPushButton("Logout")
        self.logout_button.setProperty("class", "danger")
        
        controls_layout.addWidget(self.refresh_button)
        controls_layout.addWidget(self.settings_button)
        controls_layout.addWidget(self.logout_button)
        
        # Add to header
        header_layout.addLayout(title_layout)
        header_layout.addStretch()
        header_layout.addLayout(status_layout)
        header_layout.addStretch()
        header_layout.addLayout(controls_layout)
        
        return header_frame
    
    def create_left_panel(self):
        """Create left panel with map and mission info"""
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        
        # Tactical map
        map_group = QGroupBox("Tactical Map")
        map_layout = QVBoxLayout(map_group)
        
        # Use interactive map widget instead of QWebEngineView
        self.map_widget = InteractiveMapWidget()
        self.map_widget.unit_selected.connect(self.on_unit_selected_from_map)
        self.map_widget.map_ready.connect(self.on_map_ready)
        
        map_layout.addWidget(self.map_widget)
        
        # Map controls
        map_controls = QHBoxLayout()
        
        self.map_refresh_button = QPushButton("Refresh Map")
        self.show_threats_checkbox = QPushButton("Toggle Threats")
        self.show_threats_checkbox.setCheckable(True)
        self.show_threats_checkbox.setChecked(True)
        
        # Heatmap controls
        self.heatmap_enabled = QCheckBox("Show Heatmap")
        self.heatmap_enabled.setChecked(True)
        self.heatmap_enabled.toggled.connect(self.toggle_heatmap)
        
        self.routes_enabled = QCheckBox("Show Routes")
        self.routes_enabled.setChecked(True)
        self.routes_enabled.toggled.connect(self.toggle_routes)
        
        self.threat_zones_enabled = QCheckBox("Show Zones")
        self.threat_zones_enabled.setChecked(True)
        self.threat_zones_enabled.toggled.connect(self.toggle_threat_zones)
        
        map_controls.addWidget(self.map_refresh_button)
        map_controls.addWidget(self.show_threats_checkbox)
        map_controls.addWidget(self.heatmap_enabled)
        map_controls.addWidget(self.routes_enabled)
        map_controls.addWidget(self.threat_zones_enabled)
        map_controls.addStretch()
        
        map_layout.addLayout(map_controls)
        
        # Mission status
        mission_group = QGroupBox("Current Mission Status")
        mission_layout = QGridLayout(mission_group)
        
        self.mission_name_label = QLabel("No active mission")
        self.mission_phase_label = QLabel("Phase: Standby")
        self.mission_progress = QProgressBar()
        self.mission_progress.setRange(0, 100)
        
        mission_layout.addWidget(QLabel("Mission:"), 0, 0)
        mission_layout.addWidget(self.mission_name_label, 0, 1)
        mission_layout.addWidget(QLabel("Phase:"), 1, 0)
        mission_layout.addWidget(self.mission_phase_label, 1, 1)
        mission_layout.addWidget(QLabel("Progress:"), 2, 0)
        mission_layout.addWidget(self.mission_progress, 2, 1)
        
        left_layout.addWidget(map_group, 3)
        left_layout.addWidget(mission_group, 1)
        
        return left_widget
    
    def create_right_panel(self):
        """Create right panel with data tables and alerts"""
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        
        # Tab widget for different data views
        tab_widget = QTabWidget()
        
        # Units tab
        units_tab = self.create_units_tab()
        tab_widget.addTab(units_tab, "Units")
        
        # Health tab
        health_tab = self.create_health_tab()
        tab_widget.addTab(health_tab, "Health")
        
        # Logistics tab
        logistics_tab = self.create_logistics_tab()
        tab_widget.addTab(logistics_tab, "Logistics")
        
        # Alerts tab
        alerts_tab = self.create_alerts_tab()
        tab_widget.addTab(alerts_tab, "Alerts")
        
        right_layout.addWidget(tab_widget)
        
        return right_widget
    
    def create_units_tab(self):
        """Create units monitoring tab"""
        units_widget = QWidget()
        units_layout = QVBoxLayout(units_widget)
        
        # Units table
        self.units_table = QTableWidget()
        self.units_table.setColumnCount(7)
        self.units_table.setHorizontalHeaderLabels([
            "Unit ID", "Type", "Position", "Status", "Last Seen", "Risk", "Actions"
        ])
        
        # Configure table
        header = self.units_table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch)
        self.units_table.setAlternatingRowColors(True)
        self.units_table.setSelectionBehavior(QTableWidget.SelectRows)
        
        units_layout.addWidget(self.units_table)
        
        # Units controls
        units_controls = QHBoxLayout()
        
        self.unit_filter_combo = QComboBox()
        self.unit_filter_combo.addItems(["All Units", "Infantry", "Armor", "Artillery", "Recon", "Support", "Command"])
        
        self.risk_filter_combo = QComboBox()
        self.risk_filter_combo.addItems(["All Risk Levels", "Green", "Amber", "Red"])
        
        units_controls.addWidget(QLabel("Filter by Type:"))
        units_controls.addWidget(self.unit_filter_combo)
        units_controls.addWidget(QLabel("Risk Level:"))
        units_controls.addWidget(self.risk_filter_combo)
        units_controls.addStretch()
        
        units_layout.addLayout(units_controls)
        
        return units_widget
    
    def create_health_tab(self):
        """Create health monitoring tab"""
        health_widget = QWidget()
        health_layout = QVBoxLayout(health_widget)
        
        # Health summary
        summary_group = QGroupBox("Health Summary")
        summary_layout = QGridLayout(summary_group)
        
        self.health_good_count = QLabel("0")
        self.health_warning_count = QLabel("0")
        self.health_critical_count = QLabel("0")
        
        summary_layout.addWidget(QLabel("Good:"), 0, 0)
        summary_layout.addWidget(self.health_good_count, 0, 1)
        summary_layout.addWidget(QLabel("Warning:"), 0, 2)
        summary_layout.addWidget(self.health_warning_count, 0, 3)
        summary_layout.addWidget(QLabel("Critical:"), 0, 4)
        summary_layout.addWidget(self.health_critical_count, 0, 5)
        
        # Health details table
        self.health_table = QTableWidget()
        self.health_table.setColumnCount(6)
        self.health_table.setHorizontalHeaderLabels([
            "Unit ID", "Heart Rate", "SpO2", "Stress", "Temperature", "Status"
        ])
        
        header = self.health_table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch)
        self.health_table.setAlternatingRowColors(True)
        
        health_layout.addWidget(summary_group)
        health_layout.addWidget(self.health_table)
        
        return health_widget
    
    def create_logistics_tab(self):
        """Create logistics monitoring tab"""
        logistics_widget = QWidget()
        logistics_layout = QVBoxLayout(logistics_widget)
        
        # Logistics table
        self.logistics_table = QTableWidget()
        self.logistics_table.setColumnCount(6)
        self.logistics_table.setHorizontalHeaderLabels([
            "Unit ID", "Fuel %", "Ammo %", "Medical %", "Food %", "Status"
        ])
        
        header = self.logistics_table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch)
        self.logistics_table.setAlternatingRowColors(True)
        
        logistics_layout.addWidget(self.logistics_table)
        
        return logistics_widget
    
    def create_alerts_tab(self):
        """Create alerts monitoring tab"""
        alerts_widget = QWidget()
        alerts_layout = QVBoxLayout(alerts_widget)
        
        # Alerts controls
        alerts_controls = QHBoxLayout()
        
        self.alert_filter_combo = QComboBox()
        self.alert_filter_combo.addItems(["All Alerts", "Critical", "Warning", "Info"])
        
        self.show_acknowledged_checkbox = QPushButton("Show Acknowledged")
        self.show_acknowledged_checkbox.setCheckable(True)
        
        self.acknowledge_all_button = QPushButton("Acknowledge All")
        self.acknowledge_all_button.setProperty("class", "success")
        
        alerts_controls.addWidget(QLabel("Filter:"))
        alerts_controls.addWidget(self.alert_filter_combo)
        alerts_controls.addWidget(self.show_acknowledged_checkbox)
        alerts_controls.addStretch()
        alerts_controls.addWidget(self.acknowledge_all_button)
        
        # Alerts list
        self.alerts_list = QListWidget()
        self.alerts_list.setAlternatingRowColors(True)
        
        alerts_layout.addLayout(alerts_controls)
        alerts_layout.addWidget(self.alerts_list)
        
        return alerts_widget
    
    def setup_connections(self):
        """Setup signal-slot connections"""
        # Header buttons
        self.refresh_button.clicked.connect(self.refresh_data)
        self.logout_button.clicked.connect(self.logout_requested.emit)
        
        # Map controls
        self.map_refresh_button.clicked.connect(self.refresh_map)
        
        # Filter controls
        self.unit_filter_combo.currentTextChanged.connect(self.filter_units)
        self.risk_filter_combo.currentTextChanged.connect(self.filter_units)
        self.alert_filter_combo.currentTextChanged.connect(self.filter_alerts)
        
        # API client signals
        self.api_client.data_received.connect(self.on_data_received)
        self.api_client.error_occurred.connect(self.on_api_error)
    
    def setup_timers(self):
        """Setup update timers"""
        self.update_timer.timeout.connect(self.refresh_data)
        self.update_timer.start(5000)  # Update every 5 seconds
    
    def initialize_dashboard(self, user_data):
        """Initialize dashboard with user data"""
        self.current_user = user_data.get('user', {})
        user_name = self.current_user.get('full_name', 'Commander')
        self.user_label.setText(f"Welcome, {user_name}")
        
        # Start API client
        self.api_client.start_auto_refresh()
        
        # Initial data load
        self.refresh_data()
        self.refresh_map()
    
    def stop_updates(self):
        """Stop all update timers"""
        self.update_timer.stop()
        self.api_client.stop_auto_refresh()
    
    @pyqtSlot(str, dict)
    def on_data_received(self, endpoint, data):
        """Handle data received from API"""
        if endpoint == "units":
            self.update_units_table(data.get('data', []))
        elif endpoint == "health":
            self.update_health_tab(data.get('data', []))
        elif endpoint == "logistics":
            self.update_logistics_table(data.get('data', []))
        elif endpoint == "alerts":
            self.update_alerts_list(data.get('data', []))
        elif endpoint == "system_status":
            self.update_system_status(data.get('data', {}))
    
    @pyqtSlot(str, str)
    def on_api_error(self, endpoint, error):
        """Handle API errors"""
        self.status_bar.showMessage(f"Error loading {endpoint}: {error}", 5000)
    
    def refresh_data(self):
        """Refresh all dashboard data"""
        self.status_bar.showMessage("Refreshing data...")
        # API client will automatically fetch data and emit signals
    
    def on_map_ready(self):
        """Handle map ready signal"""
        print("Interactive map is ready")
        # Initial data load to map
        if hasattr(self, 'current_units_data'):
            self.map_widget.update_units(self.current_units_data)
        if hasattr(self, 'current_alerts_data'):
            self.map_widget.update_alerts(self.current_alerts_data)
    
    def on_unit_selected_from_map(self, unit_id):
        """Handle unit selection from map"""
        print(f"Unit selected from map: {unit_id}")
        # Find and select the unit in the table
        for row in range(self.units_table.rowCount()):
            item = self.units_table.item(row, 0)
            if item and item.text() == unit_id:
                self.units_table.selectRow(row)
                break
    
    def refresh_map(self):
        """Refresh the tactical map with heatmap and routes"""
        # Refresh the interactive map widget
        if hasattr(self, 'current_units_data'):
            self.map_widget.update_units(self.current_units_data)
        if hasattr(self, 'current_alerts_data'):
            self.map_widget.update_alerts(self.current_alerts_data)
        
        # Update heatmap if enabled
        if self.heatmap_enabled.isChecked():
            self.update_heatmap()
        
        # Update routes if enabled
        if self.routes_enabled.isChecked():
            self.update_routes()
        
        # Update threat zones if enabled
        if self.threat_zones_enabled.isChecked():
            self.update_threat_zones()
    
    def update_units_table(self, units_data):
        """Update units table with new data"""
        self.current_units_data = units_data  # Store for map updates
        self.units_table.setRowCount(len(units_data))
        
        for row, unit in enumerate(units_data):
            self.units_table.setItem(row, 0, QTableWidgetItem(unit.get('unit_id', '')))
            self.units_table.setItem(row, 1, QTableWidgetItem(unit.get('unit_type', '')))
            
            # Position
            pos = unit.get('position', {})
            position_str = f"{pos.get('latitude', 0):.4f}, {pos.get('longitude', 0):.4f}"
            self.units_table.setItem(row, 2, QTableWidgetItem(position_str))
            
            self.units_table.setItem(row, 3, QTableWidgetItem(unit.get('status', '')))
            self.units_table.setItem(row, 4, QTableWidgetItem(unit.get('last_seen', '')))
            
            # Risk level with styling
            risk_item = QTableWidgetItem(unit.get('status', 'green').upper())
            risk_item.setBackground(Qt.green if unit.get('status') == 'green' else 
                                  Qt.yellow if unit.get('status') == 'amber' else Qt.red)
            self.units_table.setItem(row, 5, risk_item)
            
            # Actions button
            actions_item = QTableWidgetItem("View Details")
            self.units_table.setItem(row, 6, actions_item)
        
        # Update status
        self.units_status_label.setText(f"Units: {len(units_data)}/{len(units_data)}")
        
        # Update map with new units data
        if hasattr(self, 'map_widget'):
            self.map_widget.update_units(units_data)
    
    def update_health_tab(self, health_data):
        """Update health monitoring tab"""
        # Update summary counts
        good_count = len([h for h in health_data if h.get('risk_level') == 'green'])
        warning_count = len([h for h in health_data if h.get('risk_level') == 'amber'])
        critical_count = len([h for h in health_data if h.get('risk_level') == 'red'])
        
        self.health_good_count.setText(str(good_count))
        self.health_warning_count.setText(str(warning_count))
        self.health_critical_count.setText(str(critical_count))
        
        # Update table
        self.health_table.setRowCount(len(health_data))
        
        for row, health in enumerate(health_data):
            self.health_table.setItem(row, 0, QTableWidgetItem(health.get('unit_id', '')))
            self.health_table.setItem(row, 1, QTableWidgetItem(str(health.get('heart_rate', 0))))
            self.health_table.setItem(row, 2, QTableWidgetItem(str(health.get('spo2', 0))))
            self.health_table.setItem(row, 3, QTableWidgetItem(str(health.get('stress_index', 0))))
            self.health_table.setItem(row, 4, QTableWidgetItem(str(health.get('body_temperature', 0))))
            
            # Status with color
            status_item = QTableWidgetItem(health.get('risk_level', 'green').upper())
            status_item.setBackground(Qt.green if health.get('risk_level') == 'green' else 
                                    Qt.yellow if health.get('risk_level') == 'amber' else Qt.red)
            self.health_table.setItem(row, 5, status_item)
    
    def update_logistics_table(self, logistics_data):
        """Update logistics table"""
        self.logistics_table.setRowCount(len(logistics_data))
        
        for row, logistics in enumerate(logistics_data):
            self.logistics_table.setItem(row, 0, QTableWidgetItem(logistics.get('unit_id', '')))
            self.logistics_table.setItem(row, 1, QTableWidgetItem(f"{logistics.get('fuel_percent', 0):.1f}%"))
            self.logistics_table.setItem(row, 2, QTableWidgetItem(f"{logistics.get('ammunition_percent', 0):.1f}%"))
            self.logistics_table.setItem(row, 3, QTableWidgetItem(f"{logistics.get('medical_supplies_percent', 0):.1f}%"))
            self.logistics_table.setItem(row, 4, QTableWidgetItem(f"{logistics.get('food_supplies_percent', 0):.1f}%"))
            
            # Overall status
            min_supply = min(
                logistics.get('fuel_percent', 100),
                logistics.get('ammunition_percent', 100),
                logistics.get('medical_supplies_percent', 100),
                logistics.get('food_supplies_percent', 100)
            )
            
            status = "GOOD" if min_supply > 50 else "LOW" if min_supply > 20 else "CRITICAL"
            status_item = QTableWidgetItem(status)
            status_item.setBackground(Qt.green if status == "GOOD" else 
                                    Qt.yellow if status == "LOW" else Qt.red)
            self.logistics_table.setItem(row, 5, status_item)
    
    def update_alerts_list(self, alerts_data):
        """Update alerts list"""
        self.current_alerts_data = alerts_data  # Store for map updates
        self.alerts_list.clear()
        
        for alert in alerts_data:
            alert_text = f"[{alert.get('severity', '').upper()}] {alert.get('title', '')}: {alert.get('message', '')}"
            item = QListWidgetItem(alert_text)
            
            # Color based on severity
            if alert.get('severity') == 'critical':
                item.setForeground(Qt.red)
            elif alert.get('severity') == 'warning':
                item.setForeground(Qt.yellow)
            else:
                item.setForeground(Qt.white)
            
            self.alerts_list.addItem(item)
        
        # Update status
        critical_alerts = len([a for a in alerts_data if a.get('severity') == 'critical'])
        self.alerts_status_label.setText(f"Alerts: {critical_alerts}")
        
        # Update map with new alerts data
        if hasattr(self, 'map_widget'):
            self.map_widget.update_alerts(alerts_data)
    
    def update_system_status(self, status_data):
        """Update system status indicators"""
        health = status_data.get('system_health', 'green')
        
        if health == 'green':
            self.system_status_label.setText("System: OPERATIONAL")
            self.system_status_label.setStyleSheet(get_risk_level_style("low"))
        elif health == 'amber':
            self.system_status_label.setText("System: WARNING")
            self.system_status_label.setStyleSheet(get_risk_level_style("medium"))
        else:
            self.system_status_label.setText("System: CRITICAL")
            self.system_status_label.setStyleSheet(get_risk_level_style("high"))
    
    def filter_units(self):
        """Filter units table based on selected criteria"""
        # Implementation for filtering units
        pass
    
    def filter_alerts(self):
        """Filter alerts based on selected criteria"""
        # Implementation for filtering alerts
        pass
    
    def toggle_heatmap(self, enabled):
        """Toggle heatmap display"""
        if enabled:
            self.update_heatmap()
        else:
            # Clear heatmap
            self.map_widget.update_heatmap([])
    
    def toggle_routes(self, enabled):
        """Toggle routes display"""
        if enabled:
            self.update_routes()
        else:
            # Clear routes
            self.map_widget.update_routes([])
    
    def toggle_threat_zones(self, enabled):
        """Toggle threat zones display"""
        if enabled:
            self.update_threat_zones()
        else:
            # Clear threat zones
            self.map_widget.add_threat_zones([])
    
    def update_heatmap(self):
        """Update threat heatmap on the map"""
        try:
            # Get current alerts data for heatmap
            alerts_data = getattr(self, 'current_alerts_data', [])
            
            # Generate heatmap data using the service
            heatmap_data = self.heatmap_service.generate_threat_heatmap(alerts_data, 24)
            
            # Update map widget
            self.map_widget.update_heatmap(heatmap_data)
            
            # Update statistics
            stats = self.heatmap_service.get_heatmap_statistics(heatmap_data)
            print(f"Heatmap updated: {stats['total_points']} points, max intensity: {stats['max_intensity']:.2f}")
            
        except Exception as e:
            print(f"Error updating heatmap: {e}")
    
    def update_routes(self):
        """Update unit routes on the map"""
        try:
            # Get current units data for routes
            units_data = getattr(self, 'current_units_data', [])
            
            # Generate route data using the service
            routes_data = self.heatmap_service.generate_unit_routes(units_data)
            
            # Convert routes to the format expected by map widget
            routes_list = []
            for route in routes_data:
                routes_list.append({
                    'coordinates': route.coordinates,
                    'color': route.color,
                    'weight': route.weight,
                    'opacity': route.opacity,
                    'dashed': route.dashed,
                    'popup': route.popup,
                    'tooltip': route.tooltip
                })
            
            # Update map widget
            self.map_widget.update_routes(routes_list)
            
            print(f"Routes updated: {len(routes_list)} routes")
            
        except Exception as e:
            print(f"Error updating routes: {e}")
    
    def update_threat_zones(self):
        """Update threat zones on the map"""
        try:
            # Generate threat zones using the service
            threat_zones = self.heatmap_service.generate_threat_zones()
            
            # Convert threat zones to the format expected by map widget
            zones_list = []
            for zone in threat_zones:
                zone_dict = {
                    'type': zone.zone_type,
                    'color': zone.color,
                    'fillColor': zone.fillColor or zone.color,
                    'fillOpacity': zone.fillOpacity,
                    'popup': zone.popup,
                    'tooltip': zone.tooltip
                }
                
                if zone.zone_type == 'circle':
                    zone_dict.update({
                        'lat': zone.lat,
                        'lng': zone.lng,
                        'radius': zone.radius
                    })
                elif zone.zone_type == 'polygon':
                    zone_dict['coordinates'] = zone.coordinates
                
                zones_list.append(zone_dict)
            
            # Update map widget
            self.map_widget.add_threat_zones(zones_list)
            
            print(f"Threat zones updated: {len(zones_list)} zones")
            
        except Exception as e:
            print(f"Error updating threat zones: {e}")