"""
Event History Window for MSA Dashboard
Shows historical events with filtering and search capabilities
"""
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, 
                             QTableWidgetItem, QHeaderView, QPushButton, QLineEdit,
                             QComboBox, QDateEdit, QLabel, QGroupBox, QCheckBox,
                             QMessageBox, QProgressBar, QSplitter, QTextEdit,
                             QFrame, QGridLayout)
from PyQt5.QtCore import Qt, QDate, QTimer, pyqtSignal, QThread, pyqtSlot
from PyQt5.QtGui import QColor, QFont, QIcon
from datetime import datetime, timedelta
import json

from database.database_manager import DatabaseManager
from database.models import Event
from utils.styles import get_status_color, get_risk_level_style

class EventHistoryWorker(QThread):
    """Worker thread for loading events"""
    events_loaded = pyqtSignal(list)
    error_occurred = pyqtSignal(str)
    
    def __init__(self, db_manager, filters):
        super().__init__()
        self.db_manager = db_manager
        self.filters = filters
    
    def run(self):
        """Load events from database"""
        try:
            events = self.db_manager.get_events(**self.filters)
            self.events_loaded.emit(events)
        except Exception as e:
            self.error_occurred.emit(str(e))

class EventHistoryWindow(QWidget):
    """Event History Window"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.db_manager = DatabaseManager()
        self.current_events = []
        self.worker = None
        
        self.setWindowTitle("Event History - MSA Dashboard")
        self.setGeometry(100, 100, 1200, 800)
        
        self.setup_ui()
        self.setup_connections()
        self.load_events()
    
    def setup_ui(self):
        """Setup the user interface"""
        layout = QVBoxLayout(self)
        
        # Header
        header_layout = QHBoxLayout()
        
        title_label = QLabel("Event History")
        title_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #ffffff;")
        header_layout.addWidget(title_label)
        
        header_layout.addStretch()
        
        # Refresh button
        self.refresh_btn = QPushButton("🔄 Refresh")
        self.refresh_btn.setStyleSheet("""
            QPushButton {
                background-color: #007acc;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #005a9e;
            }
        """)
        header_layout.addWidget(self.refresh_btn)
        
        layout.addLayout(header_layout)
        
        # Filters section
        filters_group = QGroupBox("Filters")
        filters_layout = QGridLayout(filters_group)
        
        # Search
        filters_layout.addWidget(QLabel("Search:"), 0, 0)
        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("Search in title or description...")
        filters_layout.addWidget(self.search_edit, 0, 1)
        
        # Category filter
        filters_layout.addWidget(QLabel("Category:"), 0, 2)
        self.category_combo = QComboBox()
        self.category_combo.addItems(["All", "unit", "alert", "health", "logistics", "system"])
        filters_layout.addWidget(self.category_combo, 0, 3)
        
        # Severity filter
        filters_layout.addWidget(QLabel("Severity:"), 1, 0)
        self.severity_combo = QComboBox()
        self.severity_combo.addItems(["All", "info", "warning", "error", "critical"])
        filters_layout.addWidget(self.severity_combo, 1, 1)
        
        # Date range
        filters_layout.addWidget(QLabel("From:"), 1, 2)
        self.start_date = QDateEdit()
        self.start_date.setDate(QDate.currentDate().addDays(-7))
        self.start_date.setCalendarPopup(True)
        filters_layout.addWidget(self.start_date, 1, 3)
        
        filters_layout.addWidget(QLabel("To:"), 2, 0)
        self.end_date = QDateEdit()
        self.end_date.setDate(QDate.currentDate())
        self.end_date.setCalendarPopup(True)
        filters_layout.addWidget(self.end_date, 2, 1)
        
        # Show acknowledged
        self.show_acknowledged = QCheckBox("Show Acknowledged")
        self.show_acknowledged.setChecked(True)
        filters_layout.addWidget(self.show_acknowledged, 2, 2)
        
        # Apply filters button
        self.apply_filters_btn = QPushButton("Apply Filters")
        self.apply_filters_btn.setStyleSheet("""
            QPushButton {
                background-color: #28a745;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #218838;
            }
        """)
        filters_layout.addWidget(self.apply_filters_btn, 2, 3)
        
        layout.addWidget(filters_group)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)
        
        # Main content splitter
        splitter = QSplitter(Qt.Horizontal)
        
        # Events table
        self.events_table = QTableWidget()
        self.events_table.setColumnCount(8)
        self.events_table.setHorizontalHeaderLabels([
            "Time", "Category", "Type", "Title", "Severity", "Source", "Status", "User"
        ])
        
        # Set column widths
        header = self.events_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)  # Time
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)  # Category
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)  # Type
        header.setSectionResizeMode(3, QHeaderView.Stretch)           # Title
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)  # Severity
        header.setSectionResizeMode(5, QHeaderView.ResizeToContents)  # Source
        header.setSectionResizeMode(6, QHeaderView.ResizeToContents)  # Status
        header.setSectionResizeMode(7, QHeaderView.ResizeToContents)  # User
        
        self.events_table.setAlternatingRowColors(True)
        self.events_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.events_table.setStyleSheet("""
            QTableWidget {
                background-color: #2d2d30;
                color: #ffffff;
                gridline-color: #3e3e42;
                selection-background-color: #007acc;
            }
            QTableWidget::item {
                padding: 8px;
                border-bottom: 1px solid #3e3e42;
            }
            QHeaderView::section {
                background-color: #3c3c3c;
                color: #ffffff;
                padding: 8px;
                border: 1px solid #3e3e42;
                font-weight: bold;
            }
        """)
        
        splitter.addWidget(self.events_table)
        
        # Event details panel
        details_panel = QWidget()
        details_layout = QVBoxLayout(details_panel)
        
        details_label = QLabel("Event Details")
        details_label.setStyleSheet("font-size: 14px; font-weight: bold; color: #ffffff;")
        details_layout.addWidget(details_label)
        
        self.details_text = QTextEdit()
        self.details_text.setReadOnly(True)
        self.details_text.setStyleSheet("""
            QTextEdit {
                background-color: #2d2d30;
                color: #ffffff;
                border: 1px solid #3e3e42;
                border-radius: 4px;
                padding: 8px;
                font-family: 'Consolas', 'Monaco', monospace;
            }
        """)
        details_layout.addWidget(self.details_text)
        
        # Action buttons
        actions_layout = QHBoxLayout()
        
        self.acknowledge_btn = QPushButton("Acknowledge")
        self.acknowledge_btn.setEnabled(False)
        self.acknowledge_btn.setStyleSheet("""
            QPushButton {
                background-color: #ffc107;
                color: #000000;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #e0a800;
            }
            QPushButton:disabled {
                background-color: #6c757d;
                color: #ffffff;
            }
        """)
        actions_layout.addWidget(self.acknowledge_btn)
        
        self.export_btn = QPushButton("Export Selected")
        self.export_btn.setStyleSheet("""
            QPushButton {
                background-color: #17a2b8;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #138496;
            }
        """)
        actions_layout.addWidget(self.export_btn)
        
        actions_layout.addStretch()
        details_layout.addLayout(actions_layout)
        
        splitter.addWidget(details_panel)
        splitter.setSizes([800, 400])
        
        layout.addWidget(splitter)
        
        # Status bar
        status_layout = QHBoxLayout()
        self.status_label = QLabel("Ready")
        self.status_label.setStyleSheet("color: #ffffff; padding: 4px;")
        status_layout.addWidget(self.status_label)
        
        status_layout.addStretch()
        
        self.count_label = QLabel("Events: 0")
        self.count_label.setStyleSheet("color: #ffffff; padding: 4px;")
        status_layout.addWidget(self.count_label)
        
        layout.addLayout(status_layout)
    
    def setup_connections(self):
        """Setup signal connections"""
        self.refresh_btn.clicked.connect(self.load_events)
        self.apply_filters_btn.clicked.connect(self.apply_filters)
        self.events_table.itemSelectionChanged.connect(self.on_event_selected)
        self.acknowledge_btn.clicked.connect(self.acknowledge_event)
        self.export_btn.clicked.connect(self.export_events)
        
        # Auto-apply filters on change
        self.search_edit.textChanged.connect(self.on_filter_changed)
        self.category_combo.currentTextChanged.connect(self.on_filter_changed)
        self.severity_combo.currentTextChanged.connect(self.on_filter_changed)
    
    def on_filter_changed(self):
        """Handle filter changes"""
        # Auto-apply filters after a short delay
        if hasattr(self, 'filter_timer'):
            self.filter_timer.stop()
        
        self.filter_timer = QTimer()
        self.filter_timer.setSingleShot(True)
        self.filter_timer.timeout.connect(self.apply_filters)
        self.filter_timer.start(500)  # 500ms delay
    
    def apply_filters(self):
        """Apply current filters and reload events"""
        self.load_events()
    
    def load_events(self):
        """Load events from database with current filters"""
        if self.worker and self.worker.isRunning():
            return
        
        # Show progress
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)  # Indeterminate
        self.status_label.setText("Loading events...")
        
        # Prepare filters
        filters = {
            'limit': 1000,
            'offset': 0
        }
        
        # Category filter
        if self.category_combo.currentText() != "All":
            filters['category'] = self.category_combo.currentText()
        
        # Severity filter
        if self.severity_combo.currentText() != "All":
            filters['severity'] = self.severity_combo.currentText()
        
        # Date range
        start_date = self.start_date.date().toPyDate()
        end_date = self.end_date.date().toPyDate()
        filters['start_date'] = datetime.combine(start_date, datetime.min.time())
        filters['end_date'] = datetime.combine(end_date, datetime.max.time())
        
        # Start worker thread
        self.worker = EventHistoryWorker(self.db_manager, filters)
        self.worker.events_loaded.connect(self.on_events_loaded)
        self.worker.error_occurred.connect(self.on_error)
        self.worker.start()
    
    @pyqtSlot(list)
    def on_events_loaded(self, events):
        """Handle loaded events"""
        self.current_events = events
        self.populate_table()
        
        self.progress_bar.setVisible(False)
        self.status_label.setText("Events loaded successfully")
        self.count_label.setText(f"Events: {len(events)}")
    
    @pyqtSlot(str)
    def on_error(self, error_msg):
        """Handle loading error"""
        self.progress_bar.setVisible(False)
        self.status_label.setText(f"Error: {error_msg}")
        
        QMessageBox.critical(self, "Error", f"Failed to load events:\n{error_msg}")
    
    def populate_table(self):
        """Populate events table"""
        # Apply text search filter
        search_text = self.search_edit.text().lower()
        filtered_events = []
        
        for event in self.current_events:
            if search_text:
                if (search_text not in event.title.lower() and 
                    search_text not in event.description.lower()):
                    continue
            
            # Apply acknowledged filter
            if not self.show_acknowledged.isChecked() and event.acknowledged:
                continue
            
            filtered_events.append(event)
        
        # Update table
        self.events_table.setRowCount(len(filtered_events))
        
        for row, event in enumerate(filtered_events):
            # Time
            time_str = event.timestamp.strftime("%Y-%m-%d %H:%M:%S") if event.timestamp else "N/A"
            self.events_table.setItem(row, 0, QTableWidgetItem(time_str))
            
            # Category
            category_item = QTableWidgetItem(event.category.upper())
            category_item.setData(Qt.UserRole, event)  # Store event object
            self.events_table.setItem(row, 1, category_item)
            
            # Type
            self.events_table.setItem(row, 2, QTableWidgetItem(event.event_type))
            
            # Title
            self.events_table.setItem(row, 3, QTableWidgetItem(event.title))
            
            # Severity
            severity_item = QTableWidgetItem(event.severity.upper())
            severity_item.setBackground(QColor(get_risk_level_style(event.severity)))
            self.events_table.setItem(row, 4, severity_item)
            
            # Source
            self.events_table.setItem(row, 5, QTableWidgetItem(event.source_id or "N/A"))
            
            # Status
            status = "Acknowledged" if event.acknowledged else "Active"
            status_item = QTableWidgetItem(status)
            status_item.setBackground(QColor(get_status_color(status)))
            self.events_table.setItem(row, 6, status_item)
            
            # User
            user = event.acknowledged_by if event.acknowledged else event.user_id or "System"
            self.events_table.setItem(row, 7, QTableWidgetItem(user))
        
        self.count_label.setText(f"Events: {len(filtered_events)}")
    
    def on_event_selected(self):
        """Handle event selection"""
        current_row = self.events_table.currentRow()
        if current_row >= 0:
            # Get event from first column item
            item = self.events_table.item(current_row, 1)
            if item:
                event = item.data(Qt.UserRole)
                if event:
                    self.show_event_details(event)
                    self.acknowledge_btn.setEnabled(not event.acknowledged)
    
    def show_event_details(self, event: Event):
        """Show detailed event information"""
        details = f"""Event Details:

ID: {event.id}
Timestamp: {event.timestamp.strftime('%Y-%m-%d %H:%M:%S') if event.timestamp else 'N/A'}
Category: {event.category}
Type: {event.event_type}
Title: {event.title}
Description: {event.description}
Severity: {event.severity}
Source ID: {event.source_id or 'N/A'}
User ID: {event.user_id or 'N/A'}

Location:
  Latitude: {event.location_lat or 'N/A'}
  Longitude: {event.location_lng or 'N/A'}

Status:
  Acknowledged: {'Yes' if event.acknowledged else 'No'}
  Acknowledged By: {event.acknowledged_by or 'N/A'}
  Acknowledged At: {event.acknowledged_at.strftime('%Y-%m-%d %H:%M:%S') if event.acknowledged_at else 'N/A'}

Metadata:
{json.dumps(event.metadata, indent=2) if event.metadata else 'None'}
"""
        
        self.details_text.setPlainText(details)
    
    def acknowledge_event(self):
        """Acknowledge selected event"""
        current_row = self.events_table.currentRow()
        if current_row >= 0:
            item = self.events_table.item(current_row, 1)
            if item:
                event = item.data(Qt.UserRole)
                if event and not event.acknowledged:
                    # TODO: Get current user from auth manager
                    current_user = "admin"  # Placeholder
                    
                    if self.db_manager.acknowledge_event(event.id, current_user):
                        QMessageBox.information(self, "Success", "Event acknowledged successfully")
                        self.load_events()  # Refresh
                    else:
                        QMessageBox.warning(self, "Error", "Failed to acknowledge event")
    
    def export_events(self):
        """Export selected events to JSON"""
        selected_rows = set()
        for item in self.events_table.selectedItems():
            selected_rows.add(item.row())
        
        if not selected_rows:
            QMessageBox.information(self, "Info", "Please select events to export")
            return
        
        events_to_export = []
        for row in selected_rows:
            item = self.events_table.item(row, 1)
            if item:
                event = item.data(Qt.UserRole)
                if event:
                    events_to_export.append(event.to_dict())
        
        if events_to_export:
            from PyQt5.QtWidgets import QFileDialog
            filename, _ = QFileDialog.getSaveFileName(
                self, "Export Events", "events_export.json", "JSON Files (*.json)"
            )
            
            if filename:
                try:
                    with open(filename, 'w', encoding='utf-8') as f:
                        json.dump(events_to_export, f, indent=2, ensure_ascii=False)
                    
                    QMessageBox.information(self, "Success", f"Events exported to {filename}")
                except Exception as e:
                    QMessageBox.critical(self, "Error", f"Failed to export events:\n{str(e)}")
    
    def closeEvent(self, event):
        """Handle window close"""
        if self.worker and self.worker.isRunning():
            self.worker.quit()
            self.worker.wait()
        event.accept()