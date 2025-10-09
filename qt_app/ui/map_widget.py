#!/usr/bin/env python3
"""
Interactive Map Widget with QWebChannel Integration
Real-time map updates using Leaflet and QWebChannel
"""

import json
import os
from PyQt5.QtWidgets import QWidget, QVBoxLayout
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtWebChannel import QWebChannel
from PyQt5.QtCore import QObject, pyqtSlot, pyqtSignal, QUrl, QTimer
from PyQt5.QtGui import QColor

class MapBridge(QObject):
    """Bridge object for communication between Python and JavaScript"""
    
    # Signals to JavaScript
    units_updated = pyqtSignal(str)  # JSON string of units
    alerts_updated = pyqtSignal(str)  # JSON string of alerts
    map_center_changed = pyqtSignal(float, float, int)  # lat, lng, zoom
    
    def __init__(self):
        super().__init__()
        self.units_data = []
        self.alerts_data = []
    
    @pyqtSlot(str)
    def log_message(self, message):
        """Receive log messages from JavaScript"""
        print(f"[Map JS]: {message}")
    
    @pyqtSlot(str)
    def unit_clicked(self, unit_id):
        """Handle unit click from JavaScript"""
        print(f"Unit clicked: {unit_id}")
        # Emit signal to parent widget
        if hasattr(self.parent(), 'unit_selected'):
            self.parent().unit_selected.emit(unit_id)
    
    @pyqtSlot(float, float)
    def map_clicked(self, lat, lng):
        """Handle map click from JavaScript"""
        print(f"Map clicked at: {lat}, {lng}")
    
    def update_units(self, units_data):
        """Update units on the map"""
        self.units_data = units_data
        units_json = json.dumps(units_data)
        self.units_updated.emit(units_json)
    
    def update_alerts(self, alerts_data):
        """Update alerts on the map"""
        self.alerts_data = alerts_data
        alerts_json = json.dumps(alerts_data)
        self.alerts_updated.emit(alerts_json)
    
    def set_map_center(self, lat, lng, zoom=10):
        """Set map center and zoom level"""
        self.map_center_changed.emit(lat, lng, zoom)

class InteractiveMapWidget(QWidget):
    """Interactive map widget with real-time updates"""
    
    # Signals
    unit_selected = pyqtSignal(str)
    map_ready = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.bridge = MapBridge()
        self.web_view = None
        self.channel = None
        self.map_ready_flag = False
        
        self.setup_ui()
        self.setup_web_channel()
        self.load_map()
    
    def setup_ui(self):
        """Setup the widget UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Create web view
        self.web_view = QWebEngineView()
        layout.addWidget(self.web_view)
    
    def setup_web_channel(self):
        """Setup QWebChannel for JavaScript communication"""
        self.channel = QWebChannel()
        self.channel.registerObject("mapBridge", self.bridge)
        self.web_view.page().setWebChannel(self.channel)
        
        # Connect bridge signals
        self.bridge.unit_selected = self.unit_selected
    
    def load_map(self):
        """Load the interactive map HTML"""
        html_content = self.generate_map_html()
        
        # Save to temporary file
        import tempfile
        with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False, encoding='utf-8') as f:
            f.write(html_content)
            temp_path = f.name
        
        # Load the HTML file
        self.web_view.load(QUrl.fromLocalFile(temp_path))
        
        # Set up ready detection
        QTimer.singleShot(2000, self.on_map_ready)
    
    def on_map_ready(self):
        """Called when map is ready"""
        self.map_ready_flag = True
        self.map_ready.emit()
        
        # Set default center (Ankara, Turkey)
        self.set_center(39.9334, 32.8597, 10)
    
    def generate_map_html(self):
        """Generate the HTML content for the interactive map"""
        return """
<!DOCTYPE html>
<html>
<head>
    <title>MSA Interactive Map</title>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    
    <!-- Leaflet CSS -->
    <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
    <!-- Leaflet Heat CSS -->
    <link rel="stylesheet" href="https://unpkg.com/leaflet.heat@0.2.0/dist/leaflet-heat.css" />
    
    <style>
        body {
            margin: 0;
            padding: 0;
            background: #2b2b2b;
        }
        
        #map {
            height: 100vh;
            width: 100%;
        }
        
        .unit-marker {
            border-radius: 50%;
            border: 2px solid #fff;
            box-shadow: 0 2px 4px rgba(0,0,0,0.3);
        }
        
        .unit-popup {
            background: #1e1e1e;
            color: #fff;
            border-radius: 5px;
            padding: 10px;
        }
        
        .alert-marker {
            animation: pulse 2s infinite;
        }
        
        @keyframes pulse {
            0% { transform: scale(1); opacity: 1; }
            50% { transform: scale(1.2); opacity: 0.7; }
            100% { transform: scale(1); opacity: 1; }
        }
        
        .leaflet-popup-content-wrapper {
            background: #1e1e1e;
            color: #fff;
        }
        
        .leaflet-popup-tip {
            background: #1e1e1e;
        }
    </style>
</head>
<body>
    <div id="map"></div>
    
    <!-- Leaflet JavaScript -->
    <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
    <!-- Leaflet Heat JavaScript -->
    <script src="https://unpkg.com/leaflet.heat@0.2.0/dist/leaflet-heat.js"></script>
    <!-- QWebChannel -->
    <script src="qrc:///qtwebchannel/qwebchannel.js"></script>
    
    <script>
        let map;
        let mapBridge;
        let unitMarkers = {};
        let alertMarkers = {};
        let routeLayers = [];
        let threatZoneLayers = [];
        let heatmapLayer = null;
        
        // Unit type icons and colors
        const unitConfig = {
            'infantry': { color: '#4CAF50', icon: '👥' },
            'armor': { color: '#FF9800', icon: '🚗' },
            'artillery': { color: '#F44336', icon: '💥' },
            'recon': { color: '#2196F3', icon: '🔍' },
            'support': { color: '#9C27B0', icon: '🛠️' },
            'command': { color: '#FFD700', icon: '⭐' }
        };
        
        // Alert severity colors
        const alertConfig = {
            'low': { color: '#4CAF50' },
            'medium': { color: '#FF9800' },
            'high': { color: '#F44336' },
            'critical': { color: '#8B0000' }
        };
        
        // Initialize map
        function initMap() {
            map = L.map('map', {
                zoomControl: true,
                attributionControl: false
            }).setView([39.9334, 32.8597], 10);
            
            // Add dark tile layer
            L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png', {
                attribution: '© OpenStreetMap contributors © CARTO',
                subdomains: 'abcd',
                maxZoom: 19
            }).addTo(map);
            
            // Map click handler
            map.on('click', function(e) {
                if (mapBridge) {
                    mapBridge.map_clicked(e.latlng.lat, e.latlng.lng);
                }
            });
            
            console.log('Map initialized');
        }
        
        // Create unit marker
        function createUnitMarker(unit) {
            const config = unitConfig[unit.type] || unitConfig['infantry'];
            
            // Create custom icon
            const iconHtml = `
                <div class="unit-marker" style="
                    background-color: ${config.color};
                    width: 30px;
                    height: 30px;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    font-size: 14px;
                ">
                    ${config.icon}
                </div>
            `;
            
            const customIcon = L.divIcon({
                html: iconHtml,
                className: 'custom-unit-icon',
                iconSize: [30, 30],
                iconAnchor: [15, 15]
            });
            
            const marker = L.marker([unit.lat, unit.lng], { icon: customIcon });
            
            // Popup content
            const popupContent = `
                <div class="unit-popup">
                    <h4>${unit.id}</h4>
                    <p><strong>Type:</strong> ${unit.type}</p>
                    <p><strong>Status:</strong> ${unit.status}</p>
                    <p><strong>Health:</strong> ${unit.health_status || 'Unknown'}</p>
                    <p><strong>Position:</strong> ${unit.lat.toFixed(4)}, ${unit.lng.toFixed(4)}</p>
                    <p><strong>Last Update:</strong> ${unit.timestamp || 'Unknown'}</p>
                </div>
            `;
            
            marker.bindPopup(popupContent);
            
            // Click handler
            marker.on('click', function() {
                if (mapBridge) {
                    mapBridge.unit_clicked(unit.id);
                }
            });
            
            return marker;
        }
        
        // Create alert marker
        function createAlertMarker(alert) {
            const config = alertConfig[alert.severity] || alertConfig['medium'];
            
            const iconHtml = `
                <div class="alert-marker" style="
                    background-color: ${config.color};
                    width: 20px;
                    height: 20px;
                    border-radius: 50%;
                    border: 2px solid #fff;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.5);
                "></div>
            `;
            
            const customIcon = L.divIcon({
                html: iconHtml,
                className: 'custom-alert-icon',
                iconSize: [20, 20],
                iconAnchor: [10, 10]
            });
            
            const marker = L.marker([alert.lat, alert.lng], { icon: customIcon });
            
            const popupContent = `
                <div class="unit-popup">
                    <h4>Alert: ${alert.severity.toUpperCase()}</h4>
                    <p><strong>Message:</strong> ${alert.message}</p>
                    <p><strong>Unit:</strong> ${alert.unit_id || 'Unknown'}</p>
                    <p><strong>Time:</strong> ${alert.timestamp || 'Unknown'}</p>
                </div>
            `;
            
            marker.bindPopup(popupContent);
            
            return marker;
        }
        
        // Update units on map
        function updateUnits(unitsJson) {
            try {
                const units = JSON.parse(unitsJson);
                
                // Clear existing unit markers
                Object.values(unitMarkers).forEach(marker => {
                    map.removeLayer(marker);
                });
                unitMarkers = {};
                
                // Add new unit markers
                units.forEach(unit => {
                    if (unit.lat && unit.lng) {
                        const marker = createUnitMarker(unit);
                        marker.addTo(map);
                        unitMarkers[unit.id] = marker;
                    }
                });
                
                console.log(`Updated ${units.length} units on map`);
            } catch (error) {
                console.error('Error updating units:', error);
            }
        }
        
        // Update alerts on map
        function updateAlerts(alertsJson) {
            try {
                const alerts = JSON.parse(alertsJson);
                
                // Clear existing alert markers
                Object.values(alertMarkers).forEach(marker => {
                    map.removeLayer(marker);
                });
                alertMarkers = {};
                
                // Add new alert markers
                alerts.forEach(alert => {
                    if (alert.lat && alert.lng) {
                        const marker = createAlertMarker(alert);
                        marker.addTo(map);
                        alertMarkers[alert.id] = marker;
                    }
                });
                
                console.log(`Updated ${alerts.length} alerts on map`);
            } catch (error) {
                console.error('Error updating alerts:', error);
            }
        }
        
        // Set map center
        function setMapCenter(lat, lng, zoom) {
            if (map) {
                map.setView([lat, lng], zoom);
                console.log(`Map center set to: ${lat}, ${lng}, zoom: ${zoom}`);
            }
        }
        
        // Initialize QWebChannel
        new QWebChannel(qt.webChannelTransport, function(channel) {
            mapBridge = channel.objects.mapBridge;
            
            // Connect signals
            mapBridge.units_updated.connect(updateUnits);
            mapBridge.alerts_updated.connect(updateAlerts);
            mapBridge.map_center_changed.connect(setMapCenter);
            
            // Log connection
            mapBridge.log_message('QWebChannel connected successfully');
            
            console.log('QWebChannel bridge established');
        });
        
        // Initialize map when page loads
        document.addEventListener('DOMContentLoaded', function() {
            initMap();
        });
    </script>
</body>
</html>
        """
    
    def update_units(self, units_data):
        """Update units on the map"""
        if self.map_ready_flag:
            self.bridge.update_units(units_data)
    
    def update_alerts(self, alerts_data):
        """Update alerts on the map"""
        if self.map_ready_flag:
            self.bridge.update_alerts(alerts_data)
    
    def set_center(self, lat, lng, zoom=10):
        """Set map center and zoom level"""
        if self.map_ready_flag:
            self.bridge.set_map_center(lat, lng, zoom)
    
    def focus_unit(self, unit_id, units_data):
        """Focus on a specific unit"""
        for unit in units_data:
            if unit.get('id') == unit_id:
                self.set_center(unit.get('lat', 39.9334), unit.get('lng', 32.8597), 15)
                break
    
    def update_heatmap(self, heatmap_data):
        """Update heatmap layer with threat density data"""
        try:
            # Convert heatmap data to JavaScript format
            js_heatmap_data = json.dumps(heatmap_data)
            
            # Execute JavaScript to update heatmap
            js_code = f"""
            if (typeof heatmapLayer !== 'undefined' && heatmapLayer) {{
                map.removeLayer(heatmapLayer);
            }}
            
            if ({js_heatmap_data}.length > 0) {{
                heatmapLayer = L.heatLayer({js_heatmap_data}, {{
                    radius: 25,
                    blur: 15,
                    maxZoom: 17,
                    gradient: {{
                        0.0: 'blue',
                        0.2: 'cyan',
                        0.4: 'lime',
                        0.6: 'yellow',
                        0.8: 'orange',
                        1.0: 'red'
                    }}
                }}).addTo(map);
            }}
            """
            
            self.web_view.page().runJavaScript(js_code)
            print(f"Heatmap updated with {len(heatmap_data)} points")
            
        except Exception as e:
            print(f"Error updating heatmap: {e}")
    
    def update_routes(self, routes_data):
        """Update route polylines for unit movements"""
        try:
            # Convert routes data to JavaScript format
            js_routes_data = json.dumps(routes_data)
            
            # Execute JavaScript to update routes
            js_code = f"""
            // Clear existing routes
            if (typeof routeLayers !== 'undefined') {{
                routeLayers.forEach(layer => map.removeLayer(layer));
                routeLayers = [];
            }} else {{
                routeLayers = [];
            }}
            
            // Add new routes
            const routes = {js_routes_data};
            routes.forEach(route => {{
                const color = route.color || '#007acc';
                const weight = route.weight || 3;
                const opacity = route.opacity || 0.7;
                
                const polyline = L.polyline(route.coordinates, {{
                    color: color,
                    weight: weight,
                    opacity: opacity,
                    dashArray: route.dashed ? '10, 10' : null
                }}).addTo(map);
                
                if (route.popup) {{
                    polyline.bindPopup(route.popup);
                }}
                
                if (route.tooltip) {{
                    polyline.bindTooltip(route.tooltip);
                }}
                
                routeLayers.push(polyline);
            }});
            """
            
            self.web_view.page().runJavaScript(js_code)
            print(f"Routes updated with {len(routes_data)} routes")
            
        except Exception as e:
            print(f"Error updating routes: {e}")
    
    def add_threat_zones(self, threat_zones):
        """Add threat zones as colored polygons"""
        try:
            js_zones_data = json.dumps(threat_zones)
            
            js_code = f"""
            // Clear existing threat zones
            if (typeof threatZoneLayers !== 'undefined') {{
                threatZoneLayers.forEach(layer => map.removeLayer(layer));
                threatZoneLayers = [];
            }} else {{
                threatZoneLayers = [];
            }}
            
            // Add new threat zones
            const zones = {js_zones_data};
            zones.forEach(zone => {{
                const color = zone.color || '#ff0000';
                const fillColor = zone.fillColor || color;
                const fillOpacity = zone.fillOpacity || 0.3;
                
                let shape;
                if (zone.type === 'circle') {{
                    shape = L.circle([zone.lat, zone.lng], {{
                        radius: zone.radius,
                        color: color,
                        fillColor: fillColor,
                        fillOpacity: fillOpacity,
                        weight: 2
                    }});
                }} else if (zone.type === 'polygon') {{
                    shape = L.polygon(zone.coordinates, {{
                        color: color,
                        fillColor: fillColor,
                        fillOpacity: fillOpacity,
                        weight: 2
                    }});
                }}
                
                if (shape) {{
                    shape.addTo(map);
                    
                    if (zone.popup) {{
                        shape.bindPopup(zone.popup);
                    }}
                    
                    if (zone.tooltip) {{
                        shape.bindTooltip(zone.tooltip);
                    }}
                    
                    threatZoneLayers.push(shape);
                }}
            }});
            """
            
            self.web_view.page().runJavaScript(js_code)
            print(f"Threat zones updated with {len(threat_zones)} zones")
            
        except Exception as e:
            print(f"Error updating threat zones: {e}")
    
    def set_map_view(self, lat, lng, zoom=10):
        """Set map center and zoom level"""
        try:
            js_code = f"map.setView([{lat}, {lng}], {zoom});"
            self.web_view.page().runJavaScript(js_code)
        except Exception as e:
            print(f"Error setting map view: {e}")
    
    def fit_bounds(self, bounds):
        """Fit map to show all specified bounds"""
        try:
            js_bounds = json.dumps(bounds)
            js_code = f"map.fitBounds({js_bounds});"
            self.web_view.page().runJavaScript(js_code)
        except Exception as e:
            print(f"Error fitting bounds: {e}")