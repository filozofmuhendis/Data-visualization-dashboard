"""
Analyst Dashboard for MSA System
Data analysis and intelligence dashboard for analysts
"""

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QGroupBox, QTableWidget, QTableWidgetItem, QHeaderView,
    QProgressBar, QListWidget, QListWidgetItem, QTabWidget,
    QSplitter, QFrame, QGridLayout, QComboBox, QSpinBox,
    QMessageBox, QScrollArea, QTextEdit, QDateEdit, QTimeEdit,
    QSlider, QCheckBox
)
from PyQt5.QtCore import Qt, pyqtSignal, QTimer, pyqtSlot, QDate, QTime
from PyQt5.QtGui import QFont, QIcon, QPixmap, QPalette
import json
from datetime import datetime, timedelta
from ..utils.styles import get_status_color, get_risk_level_style


class AnalystDashboard(QWidget):
    """Data analysis and intelligence dashboard"""
    
    # Signals
    logout_requested = pyqtSignal()
    
    def __init__(self, api_client):
        super().__init__()
        self.api_client = api_client
        self.current_user = None
        self.update_timer = QTimer()
        
        self.setup_ui()
        self.setup_connections()
        self.setup_timers()
    
    def setup_ui(self):
        """Setup the analyst dashboard UI"""
        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)
        
        # Header
        header = self.create_header()
        main_layout.addWidget(header)
        
        # Main content area with tabs
        tab_widget = QTabWidget()
        
        # Data Analysis tab
        analysis_tab = self.create_analysis_tab()
        tab_widget.addTab(analysis_tab, "Data Analysis")
        
        # Intelligence tab
        intelligence_tab = self.create_intelligence_tab()
        tab_widget.addTab(intelligence_tab, "Intelligence")
        
        # Reports tab
        reports_tab = self.create_reports_tab()
        tab_widget.addTab(reports_tab, "Reports")
        
        # Predictions tab
        predictions_tab = self.create_predictions_tab()
        tab_widget.addTab(predictions_tab, "Predictions")
        
        main_layout.addWidget(tab_widget)
    
    def create_header(self):
        """Create dashboard header"""
        header_frame = QFrame()
        header_frame.setFrameStyle(QFrame.StyledPanel)
        header_layout = QHBoxLayout(header_frame)
        
        # Title section
        title_layout = QVBoxLayout()
        title_label = QLabel("Intelligence & Analysis Dashboard")
        title_label.setProperty("class", "title")
        
        self.user_label = QLabel("Intelligence Analyst")
        self.user_label.setProperty("class", "subtitle")
        
        title_layout.addWidget(title_label)
        title_layout.addWidget(self.user_label)
        
        # Analysis summary
        summary_layout = QHBoxLayout()
        
        self.data_points_label = QLabel("Data Points: 0")
        self.threats_detected_label = QLabel("Threats: 0")
        self.patterns_found_label = QLabel("Patterns: 0")
        self.confidence_label = QLabel("Confidence: 0%")
        
        summary_layout.addWidget(self.data_points_label)
        summary_layout.addWidget(self.threats_detected_label)
        summary_layout.addWidget(self.patterns_found_label)
        summary_layout.addWidget(self.confidence_label)
        
        # Control buttons
        controls_layout = QHBoxLayout()
        
        self.analyze_button = QPushButton("Run Analysis")
        self.analyze_button.setProperty("class", "primary")
        
        self.export_button = QPushButton("Export Data")
        
        self.refresh_button = QPushButton("Refresh")
        
        self.logout_button = QPushButton("Logout")
        
        controls_layout.addWidget(self.analyze_button)
        controls_layout.addWidget(self.export_button)
        controls_layout.addWidget(self.refresh_button)
        controls_layout.addWidget(self.logout_button)
        
        # Add to header
        header_layout.addLayout(title_layout)
        header_layout.addStretch()
        header_layout.addLayout(summary_layout)
        header_layout.addStretch()
        header_layout.addLayout(controls_layout)
        
        return header_frame
    
    def create_analysis_tab(self):
        """Create data analysis tab"""
        analysis_widget = QWidget()
        analysis_layout = QVBoxLayout(analysis_widget)
        
        # Analysis controls
        controls_group = QGroupBox("Analysis Parameters")
        controls_layout = QGridLayout(controls_group)
        
        # Time range
        self.time_range_combo = QComboBox()
        self.time_range_combo.addItems(["Last Hour", "Last 6 Hours", "Last 24 Hours", "Last Week", "Custom"])
        
        # Data sources
        self.data_sources_layout = QVBoxLayout()
        
        self.include_units_cb = QCheckBox("Unit Positions")
        self.include_units_cb.setChecked(True)
        
        self.include_health_cb = QCheckBox("Health Data")
        self.include_health_cb.setChecked(True)
        
        self.include_logistics_cb = QCheckBox("Logistics Data")
        self.include_logistics_cb.setChecked(True)
        
        self.include_weather_cb = QCheckBox("Weather Data")
        self.include_weather_cb.setChecked(False)
        
        self.data_sources_layout.addWidget(self.include_units_cb)
        self.data_sources_layout.addWidget(self.include_health_cb)
        self.data_sources_layout.addWidget(self.include_logistics_cb)
        self.data_sources_layout.addWidget(self.include_weather_cb)
        
        # Analysis type
        self.analysis_type_combo = QComboBox()
        self.analysis_type_combo.addItems([
            "Pattern Recognition", 
            "Anomaly Detection", 
            "Trend Analysis", 
            "Correlation Analysis",
            "Predictive Modeling"
        ])
        
        controls_layout.addWidget(QLabel("Time Range:"), 0, 0)
        controls_layout.addWidget(self.time_range_combo, 0, 1)
        controls_layout.addWidget(QLabel("Data Sources:"), 1, 0)
        controls_layout.addLayout(self.data_sources_layout, 1, 1)
        controls_layout.addWidget(QLabel("Analysis Type:"), 2, 0)
        controls_layout.addWidget(self.analysis_type_combo, 2, 1)
        
        # Results area
        results_group = QGroupBox("Analysis Results")
        results_layout = QVBoxLayout(results_group)
        
        # Results table
        self.results_table = QTableWidget()
        self.results_table.setColumnCount(5)
        self.results_table.setHorizontalHeaderLabels([
            "Finding", "Type", "Confidence", "Impact", "Timestamp"
        ])
        
        header = self.results_table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch)
        self.results_table.setAlternatingRowColors(True)
        
        results_layout.addWidget(self.results_table)
        
        # Analysis summary
        summary_text = QTextEdit()
        summary_text.setMaximumHeight(150)
        summary_text.setPlaceholderText("Analysis summary will appear here...")
        summary_text.setReadOnly(True)
        
        results_layout.addWidget(QLabel("Summary:"))
        results_layout.addWidget(summary_text)
        
        analysis_layout.addWidget(controls_group)
        analysis_layout.addWidget(results_group)
        
        return analysis_widget
    
    def create_intelligence_tab(self):
        """Create intelligence monitoring tab"""
        intel_widget = QWidget()
        intel_layout = QHBoxLayout(intel_widget)
        
        # Left panel - Threat assessment
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        
        # Threat levels
        threat_group = QGroupBox("Threat Assessment")
        threat_layout = QVBoxLayout(threat_group)
        
        # Threat level indicators
        threat_indicators = QGridLayout()
        
        self.threat_level_label = QLabel("MODERATE")
        self.threat_level_label.setProperty("class", "threat-level")
        self.threat_level_label.setAlignment(Qt.AlignCenter)
        
        self.kinetic_threat_bar = QProgressBar()
        self.kinetic_threat_bar.setRange(0, 100)
        self.kinetic_threat_bar.setValue(30)
        
        self.cyber_threat_bar = QProgressBar()
        self.cyber_threat_bar.setRange(0, 100)
        self.cyber_threat_bar.setValue(15)
        
        self.environmental_threat_bar = QProgressBar()
        self.environmental_threat_bar.setRange(0, 100)
        self.environmental_threat_bar.setValue(45)
        
        threat_indicators.addWidget(QLabel("Overall Threat Level:"), 0, 0, 1, 2)
        threat_indicators.addWidget(self.threat_level_label, 1, 0, 1, 2)
        
        threat_indicators.addWidget(QLabel("Kinetic Threats:"), 2, 0)
        threat_indicators.addWidget(self.kinetic_threat_bar, 2, 1)
        
        threat_indicators.addWidget(QLabel("Cyber Threats:"), 3, 0)
        threat_indicators.addWidget(self.cyber_threat_bar, 3, 1)
        
        threat_indicators.addWidget(QLabel("Environmental:"), 4, 0)
        threat_indicators.addWidget(self.environmental_threat_bar, 4, 1)
        
        threat_layout.addLayout(threat_indicators)
        
        # Threat sources
        sources_group = QGroupBox("Threat Sources")
        sources_layout = QVBoxLayout(sources_group)
        
        self.threat_sources_list = QListWidget()
        self.threat_sources_list.setMaximumHeight(200)
        sources_layout.addWidget(self.threat_sources_list)
        
        left_layout.addWidget(threat_group)
        left_layout.addWidget(sources_group)
        
        # Right panel - Intelligence reports
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        
        # Recent intelligence
        intel_group = QGroupBox("Intelligence Reports")
        intel_group_layout = QVBoxLayout(intel_group)
        
        self.intel_reports_table = QTableWidget()
        self.intel_reports_table.setColumnCount(4)
        self.intel_reports_table.setHorizontalHeaderLabels([
            "Report ID", "Classification", "Source", "Timestamp"
        ])
        
        header = self.intel_reports_table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch)
        self.intel_reports_table.setAlternatingRowColors(True)
        
        intel_group_layout.addWidget(self.intel_reports_table)
        
        # Report details
        details_group = QGroupBox("Report Details")
        details_layout = QVBoxLayout(details_group)
        
        self.report_details = QTextEdit()
        self.report_details.setMaximumHeight(200)
        self.report_details.setPlaceholderText("Select a report to view details...")
        self.report_details.setReadOnly(True)
        
        details_layout.addWidget(self.report_details)
        
        right_layout.addWidget(intel_group)
        right_layout.addWidget(details_group)
        
        # Add panels to main layout
        intel_layout.addWidget(left_panel)
        intel_layout.addWidget(right_panel)
        
        return intel_widget
    
    def create_reports_tab(self):
        """Create reports generation tab"""
        reports_widget = QWidget()
        reports_layout = QVBoxLayout(reports_widget)
        
        # Report generation controls
        generation_group = QGroupBox("Generate Report")
        generation_layout = QGridLayout(generation_group)
        
        # Report type
        self.report_type_combo = QComboBox()
        self.report_type_combo.addItems([
            "Situation Report (SITREP)",
            "Intelligence Summary",
            "Threat Assessment",
            "Unit Status Report",
            "Health Summary",
            "Logistics Report"
        ])
        
        # Time period
        self.report_period_combo = QComboBox()
        self.report_period_combo.addItems([
            "Current Status",
            "Last 6 Hours", 
            "Last 24 Hours",
            "Last Week",
            "Custom Period"
        ])
        
        # Classification level
        self.classification_combo = QComboBox()
        self.classification_combo.addItems([
            "UNCLASSIFIED",
            "CONFIDENTIAL", 
            "SECRET",
            "TOP SECRET"
        ])
        
        # Generate button
        self.generate_report_button = QPushButton("Generate Report")
        self.generate_report_button.setProperty("class", "primary")
        
        generation_layout.addWidget(QLabel("Report Type:"), 0, 0)
        generation_layout.addWidget(self.report_type_combo, 0, 1)
        generation_layout.addWidget(QLabel("Time Period:"), 1, 0)
        generation_layout.addWidget(self.report_period_combo, 1, 1)
        generation_layout.addWidget(QLabel("Classification:"), 2, 0)
        generation_layout.addWidget(self.classification_combo, 2, 1)
        generation_layout.addWidget(self.generate_report_button, 3, 0, 1, 2)
        
        # Report preview
        preview_group = QGroupBox("Report Preview")
        preview_layout = QVBoxLayout(preview_group)
        
        self.report_preview = QTextEdit()
        self.report_preview.setPlaceholderText("Generated report will appear here...")
        
        # Report actions
        actions_layout = QHBoxLayout()
        
        self.save_report_button = QPushButton("Save Report")
        self.export_pdf_button = QPushButton("Export PDF")
        self.send_report_button = QPushButton("Send Report")
        
        actions_layout.addWidget(self.save_report_button)
        actions_layout.addWidget(self.export_pdf_button)
        actions_layout.addWidget(self.send_report_button)
        actions_layout.addStretch()
        
        preview_layout.addWidget(self.report_preview)
        preview_layout.addLayout(actions_layout)
        
        reports_layout.addWidget(generation_group)
        reports_layout.addWidget(preview_group)
        
        return reports_widget
    
    def create_predictions_tab(self):
        """Create predictive analysis tab"""
        predictions_widget = QWidget()
        predictions_layout = QVBoxLayout(predictions_widget)
        
        # Prediction controls
        controls_group = QGroupBox("Prediction Parameters")
        controls_layout = QGridLayout(controls_group)
        
        # Prediction type
        self.prediction_type_combo = QComboBox()
        self.prediction_type_combo.addItems([
            "Unit Movement Prediction",
            "Health Risk Prediction", 
            "Supply Depletion Forecast",
            "Threat Emergence Prediction",
            "Weather Impact Analysis"
        ])
        
        # Time horizon
        self.time_horizon_combo = QComboBox()
        self.time_horizon_combo.addItems([
            "Next Hour",
            "Next 6 Hours",
            "Next 24 Hours", 
            "Next Week"
        ])
        
        # Confidence threshold
        self.confidence_slider = QSlider(Qt.Horizontal)
        self.confidence_slider.setRange(50, 95)
        self.confidence_slider.setValue(80)
        
        self.confidence_value_label = QLabel("80%")
        
        # Run prediction button
        self.run_prediction_button = QPushButton("Run Prediction")
        self.run_prediction_button.setProperty("class", "primary")
        
        controls_layout.addWidget(QLabel("Prediction Type:"), 0, 0)
        controls_layout.addWidget(self.prediction_type_combo, 0, 1)
        controls_layout.addWidget(QLabel("Time Horizon:"), 1, 0)
        controls_layout.addWidget(self.time_horizon_combo, 1, 1)
        controls_layout.addWidget(QLabel("Min Confidence:"), 2, 0)
        
        confidence_layout = QHBoxLayout()
        confidence_layout.addWidget(self.confidence_slider)
        confidence_layout.addWidget(self.confidence_value_label)
        controls_layout.addLayout(confidence_layout, 2, 1)
        
        controls_layout.addWidget(self.run_prediction_button, 3, 0, 1, 2)
        
        # Predictions results
        results_group = QGroupBox("Prediction Results")
        results_layout = QVBoxLayout(results_group)
        
        # Predictions table
        self.predictions_table = QTableWidget()
        self.predictions_table.setColumnCount(5)
        self.predictions_table.setHorizontalHeaderLabels([
            "Prediction", "Probability", "Confidence", "Time Frame", "Impact"
        ])
        
        header = self.predictions_table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch)
        self.predictions_table.setAlternatingRowColors(True)
        
        results_layout.addWidget(self.predictions_table)
        
        # Prediction details
        details_text = QTextEdit()
        details_text.setMaximumHeight(150)
        details_text.setPlaceholderText("Detailed prediction analysis will appear here...")
        details_text.setReadOnly(True)
        
        results_layout.addWidget(QLabel("Analysis Details:"))
        results_layout.addWidget(details_text)
        
        predictions_layout.addWidget(controls_group)
        predictions_layout.addWidget(results_group)
        
        return predictions_widget
    
    def setup_connections(self):
        """Setup signal-slot connections"""
        # Header buttons
        self.refresh_button.clicked.connect(self.refresh_data)
        self.logout_button.clicked.connect(self.logout_requested.emit)
        self.analyze_button.clicked.connect(self.run_analysis)
        self.export_button.clicked.connect(self.export_data)
        
        # Analysis controls
        self.time_range_combo.currentTextChanged.connect(self.update_analysis_parameters)
        self.analysis_type_combo.currentTextChanged.connect(self.update_analysis_parameters)
        
        # Report generation
        self.generate_report_button.clicked.connect(self.generate_report)
        self.save_report_button.clicked.connect(self.save_report)
        
        # Predictions
        self.run_prediction_button.clicked.connect(self.run_predictions)
        self.confidence_slider.valueChanged.connect(self.update_confidence_label)
        
        # Intelligence reports selection
        self.intel_reports_table.itemSelectionChanged.connect(self.on_report_selected)
        
        # API client signals
        self.api_client.data_received.connect(self.on_data_received)
        self.api_client.error_occurred.connect(self.on_api_error)
    
    def setup_timers(self):
        """Setup update timers"""
        self.update_timer.timeout.connect(self.refresh_data)
        self.update_timer.start(10000)  # Update every 10 seconds
    
    def initialize_dashboard(self, user_data):
        """Initialize dashboard with user data"""
        self.current_user = user_data.get('user', {})
        user_name = self.current_user.get('full_name', 'Intelligence Analyst')
        self.user_label.setText(f"{user_name}")
        
        # Start API client
        self.api_client.start_auto_refresh()
        
        # Initial data load
        self.refresh_data()
        self.load_sample_data()
    
    def stop_updates(self):
        """Stop all update timers"""
        self.update_timer.stop()
        self.api_client.stop_auto_refresh()
    
    def load_sample_data(self):
        """Load sample data for demonstration"""
        # Sample threat sources
        threat_sources = [
            "Hostile Activity - Grid 123456",
            "Cyber Intrusion Attempt",
            "Weather Warning - Severe Storm",
            "Supply Route Disruption"
        ]
        
        for source in threat_sources:
            self.threat_sources_list.addItem(source)
        
        # Sample intelligence reports
        self.intel_reports_table.setRowCount(3)
        reports = [
            ["INTEL-001", "CONFIDENTIAL", "HUMINT", "2024-01-15 14:30"],
            ["INTEL-002", "SECRET", "SIGINT", "2024-01-15 13:45"],
            ["INTEL-003", "UNCLASSIFIED", "OSINT", "2024-01-15 12:15"]
        ]
        
        for row, report in enumerate(reports):
            for col, data in enumerate(report):
                self.intel_reports_table.setItem(row, col, QTableWidgetItem(data))
    
    @pyqtSlot(str, dict)
    def on_data_received(self, endpoint, data):
        """Handle data received from API"""
        if endpoint == "dashboard_data":
            self.update_analysis_summary(data.get('data', {}))
    
    @pyqtSlot(str, str)
    def on_api_error(self, endpoint, error):
        """Handle API errors"""
        QMessageBox.warning(self, "API Error", f"Error loading {endpoint}: {error}")
    
    def refresh_data(self):
        """Refresh analyst dashboard data"""
        # API client will automatically fetch data
        pass
    
    def update_analysis_summary(self, data):
        """Update analysis summary indicators"""
        # Mock data for demonstration
        self.data_points_label.setText("Data Points: 1,247")
        self.threats_detected_label.setText("Threats: 3")
        self.patterns_found_label.setText("Patterns: 7")
        self.confidence_label.setText("Confidence: 87%")
    
    def run_analysis(self):
        """Run data analysis"""
        analysis_type = self.analysis_type_combo.currentText()
        time_range = self.time_range_combo.currentText()
        
        QMessageBox.information(
            self, 
            "Analysis Started", 
            f"Running {analysis_type} for {time_range}..."
        )
        
        # Mock results
        self.results_table.setRowCount(3)
        results = [
            ["Anomalous movement pattern detected", "Pattern", "85%", "Medium", "2024-01-15 14:30"],
            ["Supply depletion trend identified", "Trend", "92%", "High", "2024-01-15 14:25"],
            ["Communication frequency spike", "Anomaly", "78%", "Low", "2024-01-15 14:20"]
        ]
        
        for row, result in enumerate(results):
            for col, data in enumerate(result):
                self.results_table.setItem(row, col, QTableWidgetItem(data))
    
    def export_data(self):
        """Export analysis data"""
        QMessageBox.information(self, "Export", "Analysis data exported successfully.")
    
    def generate_report(self):
        """Generate intelligence report"""
        report_type = self.report_type_combo.currentText()
        classification = self.classification_combo.currentText()
        
        # Mock report content
        report_content = f"""
{classification}

{report_type}
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

EXECUTIVE SUMMARY:
Current operational status shows moderate threat levels with 3 active concerns.
All units are operational with 87% overall readiness.

THREAT ASSESSMENT:
- Kinetic threats: LOW (30%)
- Cyber threats: LOW (15%) 
- Environmental: MODERATE (45%)

RECOMMENDATIONS:
1. Continue monitoring hostile activity in Grid 123456
2. Implement additional cyber security measures
3. Prepare for potential weather impact

{classification}
        """
        
        self.report_preview.setText(report_content)
    
    def save_report(self):
        """Save generated report"""
        if self.report_preview.toPlainText().strip():
            QMessageBox.information(self, "Report Saved", "Report has been saved successfully.")
        else:
            QMessageBox.warning(self, "No Report", "Please generate a report first.")
    
    def run_predictions(self):
        """Run predictive analysis"""
        prediction_type = self.prediction_type_combo.currentText()
        time_horizon = self.time_horizon_combo.currentText()
        
        QMessageBox.information(
            self, 
            "Prediction Started", 
            f"Running {prediction_type} for {time_horizon}..."
        )
        
        # Mock predictions
        self.predictions_table.setRowCount(3)
        predictions = [
            ["Unit ALPHA-001 will require resupply", "78%", "85%", "Next 6 Hours", "Medium"],
            ["Weather will impact operations", "65%", "82%", "Next 24 Hours", "High"],
            ["Potential equipment failure", "45%", "73%", "Next Week", "Low"]
        ]
        
        for row, prediction in enumerate(predictions):
            for col, data in enumerate(prediction):
                self.predictions_table.setItem(row, col, QTableWidgetItem(data))
    
    def update_confidence_label(self, value):
        """Update confidence threshold label"""
        self.confidence_value_label.setText(f"{value}%")
    
    def update_analysis_parameters(self):
        """Update analysis parameters based on selections"""
        # Implementation for updating analysis parameters
        pass
    
    def on_report_selected(self):
        """Handle intelligence report selection"""
        current_row = self.intel_reports_table.currentRow()
        if current_row >= 0:
            report_id = self.intel_reports_table.item(current_row, 0).text()
            
            # Mock report details
            details = f"""
Report ID: {report_id}
Classification: CONFIDENTIAL
Source: Human Intelligence (HUMINT)
Date/Time: 2024-01-15 14:30:00

SUBJECT: Hostile Activity Observation

DETAILS:
Observed increased vehicle movement in Grid 123456 during hours of 1200-1400.
Approximately 6-8 vehicles, mixed civilian and military pattern.
No direct threat observed but pattern is unusual for this area.

ASSESSMENT:
Recommend continued surveillance of the area.
Confidence level: HIGH (85%)

DISTRIBUTION:
- Commander, Task Force Alpha
- Intelligence Section
- Operations Center
            """
            
            self.report_details.setText(details)