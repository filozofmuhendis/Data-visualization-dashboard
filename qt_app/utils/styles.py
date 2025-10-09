"""
Styling utilities for MSA Dashboard
Modern dark theme and custom widget styles
"""

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPalette, QColor, QFont
from PyQt5.QtWidgets import QApplication


def apply_dark_theme(app_or_widget):
    """Apply modern dark theme to application or widget"""
    
    # Dark theme stylesheet
    dark_stylesheet = """
    /* Main Application Style */
    QMainWindow {
        background-color: #1e1e1e;
        color: #ffffff;
    }
    
    /* General Widget Styles */
    QWidget {
        background-color: #1e1e1e;
        color: #ffffff;
        font-family: 'Segoe UI', Arial, sans-serif;
        font-size: 9pt;
    }
    
    /* Buttons */
    QPushButton {
        background-color: #2d2d30;
        border: 1px solid #3e3e42;
        border-radius: 4px;
        padding: 8px 16px;
        color: #ffffff;
        font-weight: 500;
    }
    
    QPushButton:hover {
        background-color: #3e3e42;
        border-color: #007acc;
    }
    
    QPushButton:pressed {
        background-color: #007acc;
    }
    
    QPushButton:disabled {
        background-color: #2d2d30;
        color: #6d6d6d;
        border-color: #3e3e42;
    }
    
    /* Primary Button */
    QPushButton[class="primary"] {
        background-color: #007acc;
        border-color: #007acc;
    }
    
    QPushButton[class="primary"]:hover {
        background-color: #1f8ad3;
    }
    
    /* Danger Button */
    QPushButton[class="danger"] {
        background-color: #d73a49;
        border-color: #d73a49;
    }
    
    QPushButton[class="danger"]:hover {
        background-color: #e36d76;
    }
    
    /* Success Button */
    QPushButton[class="success"] {
        background-color: #28a745;
        border-color: #28a745;
    }
    
    QPushButton[class="success"]:hover {
        background-color: #34ce57;
    }
    
    /* Input Fields */
    QLineEdit, QTextEdit, QPlainTextEdit {
        background-color: #2d2d30;
        border: 1px solid #3e3e42;
        border-radius: 4px;
        padding: 8px;
        color: #ffffff;
        selection-background-color: #007acc;
    }
    
    QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus {
        border-color: #007acc;
    }
    
    /* ComboBox */
    QComboBox {
        background-color: #2d2d30;
        border: 1px solid #3e3e42;
        border-radius: 4px;
        padding: 8px;
        color: #ffffff;
        min-width: 100px;
    }
    
    QComboBox:hover {
        border-color: #007acc;
    }
    
    QComboBox::drop-down {
        border: none;
        width: 20px;
    }
    
    QComboBox::down-arrow {
        image: url(down_arrow.png);
        width: 12px;
        height: 12px;
    }
    
    QComboBox QAbstractItemView {
        background-color: #2d2d30;
        border: 1px solid #3e3e42;
        selection-background-color: #007acc;
        color: #ffffff;
    }
    
    /* Labels */
    QLabel {
        color: #ffffff;
        background: transparent;
    }
    
    QLabel[class="title"] {
        font-size: 18pt;
        font-weight: bold;
        color: #ffffff;
    }
    
    QLabel[class="subtitle"] {
        font-size: 12pt;
        font-weight: 500;
        color: #cccccc;
    }
    
    QLabel[class="error"] {
        color: #f85149;
    }
    
    QLabel[class="success"] {
        color: #3fb950;
    }
    
    QLabel[class="warning"] {
        color: #f0883e;
    }
    
    /* Group Boxes */
    QGroupBox {
        background-color: #252526;
        border: 1px solid #3e3e42;
        border-radius: 6px;
        margin-top: 10px;
        padding-top: 10px;
        font-weight: 500;
    }
    
    QGroupBox::title {
        subcontrol-origin: margin;
        left: 10px;
        padding: 0 8px 0 8px;
        color: #ffffff;
        background-color: #252526;
    }
    
    /* Progress Bars */
    QProgressBar {
        background-color: #2d2d30;
        border: 1px solid #3e3e42;
        border-radius: 4px;
        text-align: center;
        color: #ffffff;
        height: 20px;
    }
    
    QProgressBar::chunk {
        background-color: #007acc;
        border-radius: 3px;
    }
    
    /* Health Status Progress Bars */
    QProgressBar[class="health-good"]::chunk {
        background-color: #3fb950;
    }
    
    QProgressBar[class="health-warning"]::chunk {
        background-color: #f0883e;
    }
    
    QProgressBar[class="health-critical"]::chunk {
        background-color: #f85149;
    }
    
    /* List Widgets */
    QListWidget {
        background-color: #2d2d30;
        border: 1px solid #3e3e42;
        border-radius: 4px;
        color: #ffffff;
        alternate-background-color: #252526;
    }
    
    QListWidget::item {
        padding: 8px;
        border-bottom: 1px solid #3e3e42;
    }
    
    QListWidget::item:selected {
        background-color: #007acc;
    }
    
    QListWidget::item:hover {
        background-color: #3e3e42;
    }
    
    /* Table Widgets */
    QTableWidget {
        background-color: #2d2d30;
        border: 1px solid #3e3e42;
        border-radius: 4px;
        color: #ffffff;
        gridline-color: #3e3e42;
        alternate-background-color: #252526;
    }
    
    QTableWidget::item {
        padding: 8px;
    }
    
    QTableWidget::item:selected {
        background-color: #007acc;
    }
    
    QHeaderView::section {
        background-color: #252526;
        color: #ffffff;
        padding: 8px;
        border: 1px solid #3e3e42;
        font-weight: 500;
    }
    
    /* Tree Widgets */
    QTreeWidget {
        background-color: #2d2d30;
        border: 1px solid #3e3e42;
        border-radius: 4px;
        color: #ffffff;
        alternate-background-color: #252526;
    }
    
    QTreeWidget::item {
        padding: 4px;
    }
    
    QTreeWidget::item:selected {
        background-color: #007acc;
    }
    
    /* Scroll Bars */
    QScrollBar:vertical {
        background-color: #2d2d30;
        width: 12px;
        border-radius: 6px;
    }
    
    QScrollBar::handle:vertical {
        background-color: #3e3e42;
        border-radius: 6px;
        min-height: 20px;
    }
    
    QScrollBar::handle:vertical:hover {
        background-color: #007acc;
    }
    
    QScrollBar:horizontal {
        background-color: #2d2d30;
        height: 12px;
        border-radius: 6px;
    }
    
    QScrollBar::handle:horizontal {
        background-color: #3e3e42;
        border-radius: 6px;
        min-width: 20px;
    }
    
    QScrollBar::handle:horizontal:hover {
        background-color: #007acc;
    }
    
    /* Tab Widgets */
    QTabWidget::pane {
        background-color: #252526;
        border: 1px solid #3e3e42;
        border-radius: 4px;
    }
    
    QTabBar::tab {
        background-color: #2d2d30;
        color: #ffffff;
        padding: 8px 16px;
        margin-right: 2px;
        border-top-left-radius: 4px;
        border-top-right-radius: 4px;
    }
    
    QTabBar::tab:selected {
        background-color: #007acc;
    }
    
    QTabBar::tab:hover {
        background-color: #3e3e42;
    }
    
    /* Splitters */
    QSplitter::handle {
        background-color: #3e3e42;
    }
    
    QSplitter::handle:horizontal {
        width: 2px;
    }
    
    QSplitter::handle:vertical {
        height: 2px;
    }
    
    /* Menu Bar */
    QMenuBar {
        background-color: #2d2d30;
        color: #ffffff;
        border-bottom: 1px solid #3e3e42;
    }
    
    QMenuBar::item {
        padding: 8px 12px;
    }
    
    QMenuBar::item:selected {
        background-color: #007acc;
    }
    
    /* Menus */
    QMenu {
        background-color: #2d2d30;
        border: 1px solid #3e3e42;
        color: #ffffff;
    }
    
    QMenu::item {
        padding: 8px 24px;
    }
    
    QMenu::item:selected {
        background-color: #007acc;
    }
    
    /* Status Bar */
    QStatusBar {
        background-color: #2d2d30;
        color: #ffffff;
        border-top: 1px solid #3e3e42;
    }
    
    /* Tool Bar */
    QToolBar {
        background-color: #2d2d30;
        border: 1px solid #3e3e42;
        spacing: 4px;
    }
    
    QToolButton {
        background-color: transparent;
        border: 1px solid transparent;
        border-radius: 4px;
        padding: 6px;
        color: #ffffff;
    }
    
    QToolButton:hover {
        background-color: #3e3e42;
        border-color: #007acc;
    }
    
    QToolButton:pressed {
        background-color: #007acc;
    }
    
    /* Checkboxes and Radio Buttons */
    QCheckBox, QRadioButton {
        color: #ffffff;
        spacing: 8px;
    }
    
    QCheckBox::indicator, QRadioButton::indicator {
        width: 16px;
        height: 16px;
    }
    
    QCheckBox::indicator:unchecked {
        background-color: #2d2d30;
        border: 1px solid #3e3e42;
        border-radius: 2px;
    }
    
    QCheckBox::indicator:checked {
        background-color: #007acc;
        border: 1px solid #007acc;
        border-radius: 2px;
    }
    
    /* Sliders */
    QSlider::groove:horizontal {
        background-color: #3e3e42;
        height: 6px;
        border-radius: 3px;
    }
    
    QSlider::handle:horizontal {
        background-color: #007acc;
        width: 16px;
        height: 16px;
        border-radius: 8px;
        margin: -5px 0;
    }
    
    QSlider::handle:horizontal:hover {
        background-color: #1f8ad3;
    }
    
    /* Spin Boxes */
    QSpinBox, QDoubleSpinBox {
        background-color: #2d2d30;
        border: 1px solid #3e3e42;
        border-radius: 4px;
        padding: 4px;
        color: #ffffff;
    }
    
    QSpinBox:focus, QDoubleSpinBox:focus {
        border-color: #007acc;
    }
    """
    
    app_or_widget.setStyleSheet(dark_stylesheet)


def get_status_color(status: str) -> str:
    """Get color for status indicators"""
    colors = {
        'green': '#3fb950',
        'amber': '#f0883e', 
        'red': '#f85149',
        'blue': '#007acc',
        'gray': '#6d6d6d'
    }
    return colors.get(status.lower(), colors['gray'])


def get_risk_level_style(risk_level: str) -> str:
    """Get stylesheet for risk level indicators"""
    styles = {
        'low': 'background-color: #3fb950; color: white; border-radius: 4px; padding: 4px 8px;',
        'medium': 'background-color: #f0883e; color: white; border-radius: 4px; padding: 4px 8px;',
        'high': 'background-color: #f85149; color: white; border-radius: 4px; padding: 4px 8px;',
        'critical': 'background-color: #d73a49; color: white; border-radius: 4px; padding: 4px 8px;'
    }
    return styles.get(risk_level.lower(), styles['low'])


def get_unit_type_icon(unit_type: str) -> str:
    """Get icon character for unit types"""
    icons = {
        'infantry': '👥',
        'armor': '🚗',
        'artillery': '🎯',
        'recon': '🔍',
        'support': '🔧',
        'command': '⭐'
    }
    return icons.get(unit_type.lower(), '📍')


def apply_login_styles(widget):
    """Apply special styles for login window"""
    login_style = """
    QWidget {
        background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1,
                                   stop: 0 #1e1e1e, stop: 1 #2d2d30);
    }
    
    QLabel[class="login-title"] {
        font-size: 24pt;
        font-weight: bold;
        color: #ffffff;
        margin-bottom: 20px;
    }
    
    QLabel[class="login-subtitle"] {
        font-size: 12pt;
        color: #cccccc;
        margin-bottom: 30px;
    }
    
    QGroupBox[class="login-form"] {
        background-color: rgba(45, 45, 48, 0.9);
        border: 1px solid #3e3e42;
        border-radius: 8px;
        padding: 20px;
    }
    """
    
    widget.setStyleSheet(widget.styleSheet() + login_style)