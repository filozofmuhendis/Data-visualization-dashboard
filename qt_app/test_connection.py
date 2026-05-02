#!/usr/bin/env python3
"""
Test script to verify PyQt5 application connection to FastAPI backend
"""

import sys
import requests
import json
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QPushButton, QTextEdit
from PyQt5.QtCore import QThread, pyqtSignal, Qt
from PyQt5.QtGui import QFont

class ConnectionTestWorker(QThread):
    """Worker thread for testing API connections"""
    result_ready = pyqtSignal(str)
    
    def __init__(self, base_url="http://localhost:8000"):
        super().__init__()
        self.base_url = base_url
    
    def run(self):
        """Test various API endpoints"""
        results = []
        
        # Test endpoints
        endpoints = [
            "/",
            "/health",
            "/api/units",
            "/api/health",
            "/api/alerts",
            "/api/system/status"
        ]
        
        for endpoint in endpoints:
            try:
                url = f"{self.base_url}{endpoint}"
                response = requests.get(url, timeout=5)
                
                if response.status_code == 200:
                    results.append(f"✅ {endpoint}: OK ({response.status_code})")
                    if endpoint == "/api/units":
                        data = response.json()
                        results.append(f"   📊 Units count: {len(data)}")
                    elif endpoint == "/api/health":
                        data = response.json()
                        results.append(f"   🏥 Health metrics available: {len(data)}")
                    elif endpoint == "/api/alerts":
                        data = response.json()
                        results.append(f"   🚨 Active alerts: {len(data)}")
                else:
                    results.append(f"⚠️ {endpoint}: {response.status_code}")
                    
            except requests.exceptions.ConnectionError:
                results.append(f"❌ {endpoint}: Connection refused")
            except requests.exceptions.Timeout:
                results.append(f"⏱️ {endpoint}: Timeout")
            except Exception as e:
                results.append(f"❌ {endpoint}: {str(e)}")
        
        # Test authentication endpoint
        try:
            auth_data = {
                "username": "commander",
                "password": "cmd123"
            }
            response = requests.post(f"{self.base_url}/api/auth/login", json=auth_data, timeout=5)
            if response.status_code == 200:
                results.append("✅ Authentication: Login successful")
                token = response.json().get("access_token")
                if token:
                    results.append("✅ Token received")
                else:
                    results.append("⚠️ No token in response")
            else:
                results.append(f"⚠️ Authentication: {response.status_code}")
        except Exception as e:
            results.append(f"❌ Authentication: {str(e)}")
        
        self.result_ready.emit("\n".join(results))

class ConnectionTestWindow(QWidget):
    """Simple window to test API connections"""
    
    def __init__(self):
        super().__init__()
        self.init_ui()
        
    def init_ui(self):
        """Initialize the UI"""
        self.setWindowTitle("MSA Dashboard - Backend Connection Test")
        self.setGeometry(100, 100, 600, 500)
        
        # Layout
        layout = QVBoxLayout()
        
        # Title
        title = QLabel("MSA Dashboard Backend Connection Test")
        title.setFont(QFont("Arial", 16, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        # Test button
        self.test_btn = QPushButton("Test Backend Connection")
        self.test_btn.clicked.connect(self.start_test)
        layout.addWidget(self.test_btn)
        
        # Results area
        self.results_text = QTextEdit()
        self.results_text.setReadOnly(True)
        self.results_text.setFont(QFont("Consolas", 10))
        layout.addWidget(self.results_text)
        
        # Status label
        self.status_label = QLabel("Ready to test...")
        layout.addWidget(self.status_label)
        
        self.setLayout(layout)
        
        # Apply dark theme
        self.setStyleSheet("""
            QWidget {
                background-color: #2b2b2b;
                color: #ffffff;
            }
            QPushButton {
                background-color: #0078d4;
                border: none;
                padding: 10px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #106ebe;
            }
            QPushButton:pressed {
                background-color: #005a9e;
            }
            QTextEdit {
                background-color: #1e1e1e;
                border: 1px solid #3c3c3c;
                border-radius: 5px;
                padding: 10px;
            }
            QLabel {
                padding: 5px;
            }
        """)
    
    def start_test(self):
        """Start the connection test"""
        self.test_btn.setEnabled(False)
        self.status_label.setText("Testing connections...")
        self.results_text.clear()
        
        # Start worker thread
        self.worker = ConnectionTestWorker()
        self.worker.result_ready.connect(self.on_test_complete)
        self.worker.start()
    
    def on_test_complete(self, results):
        """Handle test completion"""
        self.results_text.setText(results)
        self.status_label.setText("Test completed!")
        self.test_btn.setEnabled(True)

def main():
    """Main function"""
    app = QApplication(sys.argv)
    
    # Create and show the test window
    window = ConnectionTestWindow()
    window.show()
    
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()