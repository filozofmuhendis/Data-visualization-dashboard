"""
MSA Dashboard - Dash Callbacks
Real-time callbacks for data updates, user interactions, and WebSocket integration
Enhanced with Qt demo data integration
"""

import json
import asyncio
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import requests
import logging
import websockets

import dash
from dash import Input, Output, State, callback, clientside_callback, ClientsideFunction, html, dcc, ctx, no_update
from dash.exceptions import PreventUpdate
import dash_leaflet as dl
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd

from core.models import (
    Unit, HealthMetrics, LogisticsStatus, Alert, Mission, 
    RiskLevel, UnitType, AlertSeverity, MissionPhase
)
from core.settings import settings, RISK_COLORS, ROLE_CONFIGS
from app.dash_layout import create_gauge_chart, create_time_series_chart
from services.role_manager import RoleManager, UserRole, Permission

# Initialize role manager
role_manager = RoleManager()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# API base URL for demo data
API_BASE_URL = "http://localhost:8000/api"

# Initialize Dash app (will be set by main.py)
app = None


def fetch_demo_data(endpoint: str, params: dict = None) -> List[Dict]:
    """Fetch data from demo API endpoints"""
    try:
        url = f"{API_BASE_URL}/{endpoint}"
        headers = {"Authorization": "Bearer demo_token"}  # Demo token
        response = requests.get(url, headers=headers, params=params or {}, timeout=5)
        
        if response.status_code == 200:
            return response.json()
        else:
            logger.warning(f"API call failed for {endpoint}: {response.status_code}")
            return []
    except Exception as e:
        logger.error(f"Error fetching demo data from {endpoint}: {e}")
        return []


def fetch_units_data(unit_types=None, risk_levels=None) -> List[Dict]:
    """Fetch units data from demo API"""
    params = {}
    if unit_types and unit_types != "all":
        params["unit_type"] = unit_types if isinstance(unit_types, list) else [unit_types]
    if risk_levels and risk_levels != "all":
        params["status"] = risk_levels if isinstance(risk_levels, list) else [risk_levels]
    
    return fetch_demo_data("units", params)


def fetch_alerts_data(time_range=None) -> List[Dict]:
    """Fetch alerts data from demo API"""
    params = {}
    if time_range:
        params["time_range"] = time_range
    
    return fetch_demo_data("alerts", params)


def fetch_missions_data() -> List[Dict]:
    """Fetch missions data from demo API"""
    return fetch_demo_data("missions")


def fetch_events_data(time_range=None) -> List[Dict]:
    """Fetch events data from demo API"""
    params = {}
    if time_range:
        params["time_range"] = time_range
    
    return fetch_demo_data("events", params)


def fetch_dashboard_summary() -> Dict:
    """Fetch dashboard summary from demo API"""
    try:
        summary_data = fetch_demo_data("dashboard-summary")
        return summary_data[0] if summary_data else {}
    except:
        return {}


def register_callbacks(dash_app):
    """Register all callbacks with the Dash app"""
    global app
    app = dash_app
    
    # Register all callback functions
    register_data_callbacks()
    register_map_callbacks()
    register_health_callbacks()
    register_mission_callbacks()
    register_alerts_callbacks()
    register_logistics_callbacks()
    register_control_callbacks()
    register_system_callbacks()
    register_role_callbacks()


def register_data_callbacks():
    """Register callbacks for data fetching and updates"""
    
    @app.callback(
        [
            Output("units-data", "children"),
            Output("health-data", "children"),
            Output("alerts-data", "children"),
            Output("missions-data", "children"),
            Output("events-data", "children"),  # Added events data
            Output("logistics-data", "children"),
            Output("system-status", "children"),
            Output("system-status", "className"),
            Output("last-update-time", "children")
        ],
        [
            Input("data-refresh-interval", "n_intervals"),  # Updated interval ID
            Input("manual-refresh", "n_clicks"),
            Input("unit-type-filter", "value"),
            Input("risk-filter", "value"),
            Input("time-range", "value")
        ],
        [State("current-role", "children")]
    )
    def update_dashboard_data(n_intervals, manual_refresh, unit_types, risk_levels, time_range, current_role):
        """Fetch and update all dashboard data from demo API"""
        try:
            # Fetch data from demo API endpoints
            units_data = fetch_units_data(unit_types, risk_levels)
            alerts_data = fetch_alerts_data(time_range)
            missions_data = fetch_missions_data()
            events_data = fetch_events_data(time_range)
            
            # Generate mock health and logistics data for now
            health_data = generate_mock_health_data(units_data)
            logistics_data = generate_mock_logistics_data(units_data)
            
            # Determine system status based on alerts
            critical_alerts = len([a for a in alerts_data if a.get("severity") == "critical"])
            warning_alerts = len([a for a in alerts_data if a.get("severity") == "warning"])
            
            if critical_alerts > 5:
                system_status = "Critical"
                status_class = "status-indicator critical"
            elif critical_alerts > 0 or warning_alerts > 10:
                system_status = "Warning"
                status_class = "status-indicator warning"
            else:
                system_status = "Online"
                status_class = "status-indicator online"
            
            # Update timestamp
            update_time = datetime.now().strftime("%H:%M:%S")
            
            logger.info(f"Dashboard data updated: {len(units_data)} units, {len(alerts_data)} alerts, {len(missions_data)} missions, {len(events_data)} events")
            
            return (
                json.dumps(units_data),
                json.dumps(health_data),
                json.dumps(alerts_data),
                json.dumps(missions_data),
                json.dumps(events_data),  # Added events data
                json.dumps(logistics_data),
                system_status,
                status_class,
                update_time
            )
            
        except Exception as e:
            logger.error(f"Error updating dashboard data: {e}")
            # Return empty data instead of preventing update
            return (
                json.dumps([]),
                json.dumps([]),
                json.dumps([]),
                json.dumps([]),
                json.dumps([]),
                json.dumps([]),
                "Offline",
                "status-indicator offline",
                datetime.now().strftime("%H:%M:%S")
            )


def generate_mock_health_data(units_data: List[Dict]) -> List[Dict]:
    """Generate mock health data based on units"""
    import random
    health_data = []
    
    for unit in units_data[:10]:  # Limit to first 10 units
        health_data.append({
            "unit_id": unit.get("id"),
            "unit_name": unit.get("name", "Unknown"),
            "heart_rate": random.randint(60, 120),
            "body_temp": round(random.uniform(36.0, 38.5), 1),
            "stress_level": random.randint(1, 10),
            "fatigue_level": random.randint(1, 10),
            "timestamp": datetime.now().isoformat()
        })
    
    return health_data


def generate_mock_logistics_data(units_data: List[Dict]) -> List[Dict]:
    """Generate mock logistics data based on units"""
    import random
    logistics_data = []
    
    for unit in units_data[:15]:  # Limit to first 15 units
        logistics_data.append({
            "unit_id": unit.get("id"),
            "unit_name": unit.get("name", "Unknown"),
            "fuel_level": random.randint(20, 100),
            "ammo_level": random.randint(30, 100),
            "food_level": random.randint(40, 100),
            "water_level": random.randint(50, 100),
            "medical_supplies": random.randint(25, 100),
            "last_resupply": (datetime.now() - timedelta(hours=random.randint(1, 48))).isoformat()
        })
    
    return logistics_data


def register_map_callbacks():
    """Register callbacks for map interactions"""
    
    @app.callback(
        [
            Output("units-layer", "children"),
            Output("threats-layer", "children"),
            Output("weather-layer", "children")
        ],
        [
            Input("units-data", "children"),
            Input("alerts-data", "children"),
            Input("map-style", "value")
        ]
    )
    def update_map_layers(units_data_json, alerts_data_json, map_style):
        """Update map layers with units, threats, and weather data"""
        if not units_data_json:
            raise PreventUpdate
            
        try:
            units_data = json.loads(units_data_json)
            alerts_data = json.loads(alerts_data_json) if alerts_data_json else []
            
            # Create unit markers
            unit_markers = []
            for unit in units_data:
                risk_level = unit.get("risk_level", "green")
                color = RISK_COLORS.get(risk_level, RISK_COLORS["green"])
                
                marker = dl.CircleMarker(
                    center=[unit["latitude"], unit["longitude"]],
                    radius=8,
                    color=color,
                    fill=True,
                    fillColor=color,
                    fillOpacity=0.8,
                    children=[
                        dl.Tooltip(
                            f"Unit: {unit['unit_id']}\n"
                            f"Type: {unit['unit_type']}\n"
                            f"Status: {unit['status']}\n"
                            f"Risk: {risk_level.upper()}"
                        ),
                        dl.Popup([
                            f"Unit ID: {unit['unit_id']}",
                            f"Type: {unit['unit_type']}",
                            f"Status: {unit['status']}",
                            f"Last Seen: {unit.get('last_seen', 'Unknown')}"
                        ])
                    ]
                )
                unit_markers.append(marker)
            
            # Create threat markers
            threat_markers = []
            for alert in alerts_data:
                if alert.get("alert_type") == "threat" and alert.get("latitude") and alert.get("longitude"):
                    severity = alert.get("severity", "info")
                    color = "#ff0000" if severity == "critical" else "#ff8800" if severity == "warning" else "#ffff00"
                    
                    threat_marker = dl.CircleMarker(
                        center=[alert["latitude"], alert["longitude"]],
                        radius=12,
                        color=color,
                        fill=True,
                        fillColor=color,
                        fillOpacity=0.6,
                        children=[
                            dl.Tooltip(f"Threat Alert: {alert.get('message', 'Unknown threat')}"),
                            dl.Popup([
                                f"Alert: {alert.get('message', 'Unknown')}",
                                f"Severity: {severity.upper()}",
                                f"Time: {alert.get('timestamp', 'Unknown')}"
                            ])
                        ]
                    )
                    threat_markers.append(threat_marker)
            
            # Weather layer (placeholder)
            weather_markers = []
            
            return unit_markers, threat_markers, weather_markers
            
        except Exception as e:
            print(f"Error updating map layers: {e}")
            return [], [], []
    
    @app.callback(
        Output("tactical-map", "center"),
        [Input("center-map-btn", "n_clicks")],
        prevent_initial_call=True
    )
    def center_map(n_clicks):
        """Center map on default location"""
        if n_clicks:
            return settings.map_default_center
        raise PreventUpdate


def register_health_callbacks():
    """Register callbacks for health monitoring panel"""
    
    @app.callback(
        [
            Output("critical-health-count", "children"),
            Output("warning-health-count", "children"),
            Output("normal-health-count", "children"),
            Output("heart-rate-chart", "figure"),
            Output("spo2-chart", "figure"),
            Output("stress-chart", "figure"),
            Output("health-alerts-table", "data")
        ],
        [
            Input("health-data", "children"),
            Input("units-data", "children"),
            Input("alerts-data", "children")
        ],
        [State("current-role", "children")]
    )
    def update_health_panel(health_data_json, units_data_json, alerts_data_json, current_role):
        """Update health monitoring panel"""
        if not health_data_json:
            raise PreventUpdate
            
        try:
            health_data = json.loads(health_data_json)
            units_data = json.loads(units_data_json) if units_data_json else []
            alerts_data = json.loads(alerts_data_json) if alerts_data_json else []
            
            # Count health status
            critical_count = len([h for h in health_data if h.get("risk_level") == "red"])
            warning_count = len([h for h in health_data if h.get("risk_level") == "amber"])
            normal_count = len([h for h in health_data if h.get("risk_level") == "green"])
            
            # Create health charts
            hr_chart = create_health_time_series(health_data, "heart_rate", "Heart Rate (BPM)", "red")
            spo2_chart = create_health_time_series(health_data, "spo2", "SpO2 (%)", "blue")
            stress_chart = create_health_time_series(health_data, "stress_index", "Stress Index", "orange")
            
            # Health alerts table data
            health_alerts = [
                alert for alert in alerts_data 
                if alert.get("alert_type") in ["health", "medical"]
            ]
            
            health_table_data = [
                {
                    "unit_id": alert.get("unit_id", "Unknown"),
                    "alert_type": alert.get("message", "Health Alert"),
                    "severity": alert.get("severity", "info").upper(),
                    "timestamp": alert.get("timestamp", "Unknown"),
                    "status": "Active" if alert.get("acknowledged", False) else "Pending"
                }
                for alert in health_alerts[:10]  # Limit to 10 most recent
            ]
            
            return (
                critical_count,
                warning_count, 
                normal_count,
                hr_chart,
                spo2_chart,
                stress_chart,
                health_table_data
            )
            
        except Exception as e:
            print(f"Error updating health panel: {e}")
            return 0, 0, 0, {}, {}, {}, []


def register_mission_callbacks():
    """Register callbacks for mission status panel"""
    
    @app.callback(
        [
            Output("active-missions-count", "children"),
            Output("mission-completion-rate", "children"),
            Output("critical-objectives-count", "children"),
            Output("mission-progress-chart", "figure"),
            Output("mission-timeline-table", "data")
        ],
        [Input("missions-data", "children")],
        [State("current-role", "children")]
    )
    def update_mission_panel(missions_data_json, current_role):
        """Update mission status panel"""
        if not missions_data_json:
            raise PreventUpdate
            
        try:
            missions_data = json.loads(missions_data_json)
            
            # Mission statistics
            active_missions = len([m for m in missions_data if m.get("phase") != "completed"])
            total_progress = sum([m.get("progress_pct", 0) for m in missions_data])
            avg_completion = round(total_progress / len(missions_data)) if missions_data else 0
            critical_objectives = len([m for m in missions_data if m.get("priority") == "critical"])
            
            # Mission progress chart
            progress_chart = create_mission_progress_chart(missions_data)
            
            # Mission timeline table
            timeline_data = [
                {
                    "name": mission.get("name", "Unknown Mission"),
                    "phase": mission.get("phase", "unknown").upper(),
                    "progress_pct": f"{mission.get('progress_pct', 0)}%",
                    "status": get_mission_status(mission),
                    "estimated_end_time": mission.get("estimated_end_time", "TBD")
                }
                for mission in missions_data
            ]
            
            return (
                active_missions,
                avg_completion,
                critical_objectives,
                progress_chart,
                timeline_data
            )
            
        except Exception as e:
            print(f"Error updating mission panel: {e}")
            return 0, 0, 0, {}, []


def register_alerts_callbacks():
    """Register callbacks for alerts panel"""
    
    @app.callback(
        [
            Output("emergency-alerts-count", "children"),
            Output("critical-alerts-count", "children"),
            Output("warning-alerts-count", "children"),
            Output("info-alerts-count", "children"),
            Output("active-alerts-list", "children")
        ],
        [
            Input("alerts-data", "children"),
            Input("ack-all-btn", "n_clicks"),
            Input("clear-resolved-btn", "n_clicks")
        ]
    )
    def update_alerts_panel(alerts_data_json, ack_clicks, clear_clicks, **kwargs):
        """Update alerts panel"""
        if not alerts_data_json:
            raise PreventUpdate
            
        try:
            alerts_data = json.loads(alerts_data_json)
            
            # Count alerts by severity
            emergency_count = len([a for a in alerts_data if a.get("severity") == "emergency"])
            critical_count = len([a for a in alerts_data if a.get("severity") == "critical"])
            warning_count = len([a for a in alerts_data if a.get("severity") == "warning"])
            info_count = len([a for a in alerts_data if a.get("severity") == "info"])
            
            # Create active alerts list
            active_alerts = create_alerts_list(alerts_data)
            
            return (
                emergency_count,
                critical_count,
                warning_count,
                info_count,
                active_alerts
            )
            
        except Exception as e:
            print(f"Error updating alerts panel: {e}")
            return 0, 0, 0, 0, []


def register_logistics_callbacks():
    """Register callbacks for logistics panel"""
    
    @app.callback(
        [
            Output("ammo-gauge", "figure"),
            Output("fuel-gauge", "figure"),
            Output("medical-gauge", "figure"),
            Output("food-gauge", "figure"),
            Output("resource-trends-chart", "figure"),
            Output("critical-supplies-table", "data")
        ],
        [Input("logistics-data", "children")],
        [State("current-role", "children")]
    )
    def update_logistics_panel(logistics_data_json, current_role):
        """Update logistics panel"""
        if not logistics_data_json:
            raise PreventUpdate
            
        try:
            logistics_data = json.loads(logistics_data_json)
            
            # Calculate average resource levels
            ammo_avg = calculate_resource_average(logistics_data, "ammo_pct")
            fuel_avg = calculate_resource_average(logistics_data, "fuel_pct")
            medical_avg = calculate_resource_average(logistics_data, "medical_pct")
            food_avg = calculate_resource_average(logistics_data, "food_pct")
            
            # Create gauge charts
            ammo_gauge = create_gauge_chart(ammo_avg, "Ammunition", {"low": 20, "medium": 50})
            fuel_gauge = create_gauge_chart(fuel_avg, "Fuel", {"low": 25, "medium": 60})
            medical_gauge = create_gauge_chart(medical_avg, "Medical", {"low": 30, "medium": 70})
            food_gauge = create_gauge_chart(food_avg, "Food & Water", {"low": 20, "medium": 50})
            
            # Resource trends chart
            trends_chart = create_resource_trends_chart(logistics_data)
            
            # Critical supplies table
            critical_supplies = [
                {
                    "unit_id": item.get("unit_id", "Unknown"),
                    "resource_type": get_critical_resource_type(item),
                    "level_pct": f"{get_lowest_resource_level(item)}%",
                    "status": get_resource_status(item),
                    "timestamp": item.get("timestamp", "Unknown")
                }
                for item in logistics_data
                if has_critical_resources(item)
            ]
            
            return (
                ammo_gauge,
                fuel_gauge,
                medical_gauge,
                food_gauge,
                trends_chart,
                critical_supplies[:10]  # Limit to 10 most critical
            )
            
        except Exception as e:
            print(f"Error updating logistics panel: {e}")
            return {}, {}, {}, {}, {}, []


def register_control_callbacks():
    """Register callbacks for control panel interactions"""
    
    # Role-based panel visibility
    @app.callback(
        [Output('main-dashboard', 'style'),
         Output('health-panel-container', 'style'),
         Output('mission-panel-container', 'style'),
         Output('logistics-panel-container', 'style')],
        [Input('dashboard-config-store', 'data'),
         Input('user-session-store', 'data')]
    )
    def update_panel_visibility(config_data, session_data):
        if not session_data or not session_data.get('authenticated'):
            return {'display': 'none'}, {'display': 'none'}, {'display': 'none'}, {'display': 'none'}
        
        # Show main dashboard
        main_style = {'display': 'block'}
        
        # Default panel styles
        health_style = {'display': 'block'}
        mission_style = {'display': 'block'}
        logistics_style = {'display': 'block'}
        
        # Role-based panel visibility
        if config_data and 'visible_panels' in config_data:
            visible_panels = config_data['visible_panels']
            health_style = {'display': 'block' if 'health' in visible_panels else 'none'}
            mission_style = {'display': 'block' if 'mission' in visible_panels else 'none'}
            logistics_style = {'display': 'block' if 'logistics' in visible_panels else 'none'}
        
        return main_style, health_style, mission_style, logistics_style
    
    # Logout functionality
    @app.callback(
        [Output('user-session-store', 'data', allow_duplicate=True),
         Output('login-modal', 'is_open', allow_duplicate=True)],
        [Input('logout-button', 'n_clicks')],
        prevent_initial_call=True
    )
    def handle_logout(n_clicks):
        if n_clicks:
            return {}, True
        return no_update, no_update
    
    # Map updates with role-based filtering
    @app.callback(
        Output('tactical-map', 'children'),
        [Input('units-data-store', 'data'),
         Input('threats-data-store', 'data'),
         Input('dashboard-config-store', 'data')]
    )
    def update_map(units_data, threats_data, config_data):
        if not units_data:
            return []
        
        map_children = []
        
        # Add unit markers
        for unit in units_data:
            if unit.get('latitude') and unit.get('longitude'):
                # Role-based unit filtering
                show_unit = True
                if config_data and 'map_config' in config_data:
                    map_config = config_data['map_config']
                    if 'unit_types' in map_config:
                        show_unit = unit.get('unit_type') in map_config['unit_types']
                
                if show_unit:
                    status_color = get_status_color(unit.get('status', 'unknown'))
                    map_children.append(
                        dl.CircleMarker(
                            center=[unit['latitude'], unit['longitude']],
                            radius=8,
                            children=[
                                dl.Tooltip(f"{unit.get('callsign', 'Unknown')} - {unit.get('status', 'Unknown')}")
                            ],
                            color=status_color,
                            fillColor=status_color,
                            fillOpacity=0.7
                        )
                    )
        
        # Add threat markers (if user has permission)
        if threats_data and config_data and config_data.get('show_threats', True):
            for threat in threats_data:
                if threat.get('latitude') and threat.get('longitude'):
                    map_children.append(
                        dl.CircleMarker(
                            center=[threat['latitude'], threat['longitude']],
                            radius=6,
                            children=[
                                dl.Tooltip(f"Threat: {threat.get('threat_type', 'Unknown')}")
                            ],
                            color='red',
                            fillColor='red',
                            fillOpacity=0.8
                        )
                    )
        
        return map_children
    
    # Health metrics with role-based access
    @app.callback(
        [Output('health-summary-cards', 'children'),
         Output('health-trends-chart', 'figure')],
        [Input('health-data-store', 'data'),
         Input('dashboard-config-store', 'data')]
    )
    def update_health_panel(health_data, config_data):
        if not health_data:
            return [], {}
        
        # Check if user has health data access
        if config_data and not config_data.get('show_health_details', True):
            return [html.Div("Access Restricted", className="access-restricted")], {}
        
        # Create summary cards
        summary_cards = []
        if health_data:
            avg_heart_rate = sum(h.get('heart_rate', 0) for h in health_data) / len(health_data)
            avg_stress = sum(h.get('stress_level', 0) for h in health_data) / len(health_data)
            
            summary_cards = [
                create_metric_card("Avg Heart Rate", f"{avg_heart_rate:.0f} BPM", "heart"),
                create_metric_card("Avg Stress Level", f"{avg_stress:.1f}", "stress"),
                create_metric_card("Active Personnel", str(len(set(h.get('unit_id') for h in health_data))), "personnel")
            ]
        
        # Create trends chart
        if health_data:
            df = pd.DataFrame(health_data)
            fig = px.line(df, x='timestamp', y='heart_rate', color='unit_id',
                         title='Heart Rate Trends')
            fig.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font_color='white'
            )
        else:
            fig = {}
        
        return summary_cards, fig
    
    # Alert acknowledgment with permission check
    @app.callback(
        Output('alerts-data-store', 'data', allow_duplicate=True),
        [Input({'type': 'acknowledge-btn', 'index': dash.dependencies.ALL}, 'n_clicks')],
        [State('alerts-data-store', 'data'),
         State('user-session-store', 'data')],
        prevent_initial_call=True
    )
    def acknowledge_alert(n_clicks_list, alerts_data, session_data):
        if not any(n_clicks_list) or not session_data or not session_data.get('authenticated'):
            return no_update
        
        # Find which button was clicked
        ctx_triggered = ctx.triggered[0]
        if ctx_triggered['prop_id'] != '.':
            alert_index = eval(ctx_triggered['prop_id'].split('.')[0])['index']
            
            try:
                headers = {'Authorization': f"Bearer {session_data['token']}"}
                alert_id = alerts_data[alert_index]['alert_id']
                response = requests.post(
                    f'http://localhost:8000/api/alerts/{alert_id}/acknowledge',
                    headers=headers
                )
                
                if response.status_code == 200:
                    # Remove acknowledged alert from local data
                    updated_alerts = [a for i, a in enumerate(alerts_data) if i != alert_index]
                    return updated_alerts
            except Exception as e:
                logger.error(f"Error acknowledging alert: {e}")
        
        return no_update


def register_system_callbacks():
    """Register system-level callbacks"""
    
    # Client-side callback for real-time clock
    clientside_callback(
        """
        function(n_intervals) {
            const now = new Date();
            return now.toLocaleTimeString();
        }
        """,
        Output("system-clock", "children"),
        [Input("interval-component", "n_intervals")]
    )


# Helper functions for data processing and chart creation

def fetch_units_data(unit_types=None, risk_levels=None) -> List[Dict]:
    """Simulate fetching units data"""
    # This would be replaced with actual API calls
    sample_units = [
        {
            "unit_id": "ALPHA-001",
            "unit_type": "infantry",
            "latitude": 39.9042,
            "longitude": 32.6195,
            "status": "active",
            "risk_level": "green",
            "last_seen": datetime.now().isoformat()
        },
        {
            "unit_id": "BRAVO-002", 
            "unit_type": "armor",
            "latitude": 39.9142,
            "longitude": 32.6295,
            "status": "active",
            "risk_level": "amber",
            "last_seen": datetime.now().isoformat()
        },
        {
            "unit_id": "CHARLIE-003",
            "unit_type": "recon",
            "latitude": 39.8942,
            "longitude": 32.6095,
            "status": "active", 
            "risk_level": "red",
            "last_seen": datetime.now().isoformat()
        }
    ]
    
    # Apply filters
    if unit_types and "all" not in unit_types:
        sample_units = [u for u in sample_units if u["unit_type"] in unit_types]
    
    if risk_levels and "all" not in risk_levels:
        sample_units = [u for u in sample_units if u["risk_level"] in risk_levels]
    
    return sample_units


def fetch_health_data(time_range_hours=24) -> List[Dict]:
    """Simulate fetching health data"""
    import random
    
    sample_health = []
    for i in range(10):  # 10 data points
        timestamp = datetime.now() - timedelta(hours=time_range_hours * i / 10)
        sample_health.append({
            "unit_id": f"UNIT-{i+1:03d}",
            "heart_rate": random.randint(60, 120),
            "spo2": random.randint(85, 100),
            "stress_index": random.randint(0, 100),
            "risk_level": random.choice(["green", "amber", "red"]),
            "timestamp": timestamp.isoformat()
        })
    
    return sample_health


def fetch_alerts_data(time_range_hours=24) -> List[Dict]:
    """Simulate fetching alerts data"""
    import random
    
    sample_alerts = []
    alert_types = ["health", "threat", "logistics", "communication", "equipment"]
    severities = ["info", "warning", "critical", "emergency"]
    
    for i in range(15):  # 15 alerts
        timestamp = datetime.now() - timedelta(hours=random.randint(0, time_range_hours))
        sample_alerts.append({
            "alert_id": f"ALERT-{i+1:03d}",
            "unit_id": f"UNIT-{random.randint(1, 10):03d}",
            "alert_type": random.choice(alert_types),
            "severity": random.choice(severities),
            "message": f"Sample alert message {i+1}",
            "timestamp": timestamp.isoformat(),
            "acknowledged": random.choice([True, False]),
            "latitude": 39.9042 + random.uniform(-0.1, 0.1),
            "longitude": 32.6195 + random.uniform(-0.1, 0.1)
        })
    
    return sample_alerts


def fetch_missions_data() -> List[Dict]:
    """Simulate fetching missions data"""
    import random
    
    sample_missions = [
        {
            "mission_id": "MISSION-001",
            "name": "Operation Thunder",
            "phase": "execution",
            "progress_pct": 75,
            "priority": "high",
            "estimated_end_time": "2024-01-15 18:00:00"
        },
        {
            "mission_id": "MISSION-002", 
            "name": "Recon Alpha",
            "phase": "planning",
            "progress_pct": 25,
            "priority": "medium",
            "estimated_end_time": "2024-01-16 12:00:00"
        },
        {
            "mission_id": "MISSION-003",
            "name": "Supply Run Beta",
            "phase": "execution",
            "progress_pct": 90,
            "priority": "critical",
            "estimated_end_time": "2024-01-15 14:00:00"
        }
    ]
    
    return sample_missions


def fetch_logistics_data() -> List[Dict]:
    """Simulate fetching logistics data"""
    import random
    
    sample_logistics = []
    for i in range(8):  # 8 units
        sample_logistics.append({
            "unit_id": f"UNIT-{i+1:03d}",
            "ammo_pct": random.randint(10, 100),
            "fuel_pct": random.randint(15, 100),
            "medical_pct": random.randint(20, 100),
            "food_pct": random.randint(25, 100),
            "timestamp": datetime.now().isoformat()
        })
    
    return sample_logistics


def create_health_time_series(health_data, metric, title, color):
    """Create time series chart for health metrics"""
    if not health_data:
        return {}
    
    # Group by timestamp and calculate average
    df = pd.DataFrame(health_data)
    if metric not in df.columns:
        return {}
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df["timestamp"],
        y=df[metric],
        mode="lines+markers",
        name=title,
        line=dict(color=color, width=2),
        marker=dict(size=6)
    ))
    
    fig.update_layout(
        title=title,
        xaxis_title="Time",
        yaxis_title=title,
        height=200,
        margin=dict(l=40, r=20, t=40, b=40),
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font={"color": "white", "size": 10}
    )
    
    return fig


def create_mission_progress_chart(missions_data):
    """Create mission progress chart"""
    if not missions_data:
        return {}
    
    df = pd.DataFrame(missions_data)
    
    fig = go.Figure(data=[
        go.Bar(
            x=df["name"],
            y=df["progress_pct"],
            marker_color=[
                RISK_COLORS["red"] if p < 30 else 
                RISK_COLORS["amber"] if p < 70 else 
                RISK_COLORS["green"] 
                for p in df["progress_pct"]
            ]
        )
    ])
    
    fig.update_layout(
        title="Mission Progress",
        xaxis_title="Missions",
        yaxis_title="Progress (%)",
        height=250,
        margin=dict(l=40, r=20, t=40, b=40),
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font={"color": "white", "size": 10}
    )
    
    return fig


def create_alerts_list(alerts_data):
    """Create active alerts list components"""
    from dash import html
    
    if not alerts_data:
        return html.Div("No active alerts", className="no-alerts")
    
    # Sort by severity and timestamp
    severity_order = {"emergency": 0, "critical": 1, "warning": 2, "info": 3}
    sorted_alerts = sorted(
        alerts_data, 
        key=lambda x: (severity_order.get(x.get("severity", "info"), 3), x.get("timestamp", ""))
    )
    
    alert_items = []
    for alert in sorted_alerts[:10]:  # Show top 10 alerts
        severity = alert.get("severity", "info")
        alert_item = html.Div([
            html.Div([
                html.Strong(alert.get("message", "Unknown Alert")),
                html.Br(),
                html.Small(f"Unit: {alert.get('unit_id', 'Unknown')} | {alert.get('timestamp', 'Unknown')}")
            ])
        ], className=f"alert-item {severity}")
        alert_items.append(alert_item)
    
    return alert_items


def create_resource_trends_chart(logistics_data):
    """Create resource trends chart"""
    if not logistics_data:
        return {}
    
    df = pd.DataFrame(logistics_data)
    
    fig = go.Figure()
    
    # Add traces for each resource type
    resources = ["ammo_pct", "fuel_pct", "medical_pct", "food_pct"]
    colors = ["red", "blue", "green", "orange"]
    names = ["Ammunition", "Fuel", "Medical", "Food & Water"]
    
    for resource, color, name in zip(resources, colors, names):
        if resource in df.columns:
            avg_value = df[resource].mean()
            fig.add_trace(go.Scatter(
                x=df["unit_id"],
                y=df[resource],
                mode="lines+markers",
                name=name,
                line=dict(color=color, width=2)
            ))
    
    fig.update_layout(
        title="Resource Levels by Unit",
        xaxis_title="Units",
        yaxis_title="Resource Level (%)",
        height=200,
        margin=dict(l=40, r=20, t=40, b=40),
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font={"color": "white", "size": 10}
    )
    
    return fig


# Utility functions

def calculate_resource_average(logistics_data, resource_type):
    """Calculate average resource level"""
    if not logistics_data:
        return 0
    
    values = [item.get(resource_type, 0) for item in logistics_data]
    return round(sum(values) / len(values)) if values else 0


def get_mission_status(mission):
    """Get mission status based on progress and phase"""
    progress = mission.get("progress_pct", 0)
    phase = mission.get("phase", "unknown")
    
    if phase == "completed":
        return "Completed"
    elif progress < 30:
        return "Behind Schedule"
    elif progress < 70:
        return "On Track"
    else:
        return "Ahead of Schedule"


def get_critical_resource_type(logistics_item):
    """Get the most critical resource type for a unit"""
    resources = {
        "ammo_pct": "Ammunition",
        "fuel_pct": "Fuel", 
        "medical_pct": "Medical",
        "food_pct": "Food & Water"
    }
    
    min_resource = min(resources.keys(), key=lambda x: logistics_item.get(x, 100))
    return resources[min_resource]


def get_lowest_resource_level(logistics_item):
    """Get the lowest resource level for a unit"""
    levels = [
        logistics_item.get("ammo_pct", 100),
        logistics_item.get("fuel_pct", 100),
        logistics_item.get("medical_pct", 100),
        logistics_item.get("food_pct", 100)
    ]
    return min(levels)


def get_resource_status(logistics_item):
    """Get resource status based on lowest level"""
    lowest = get_lowest_resource_level(logistics_item)
    
    if lowest < 20:
        return "Critical"
    elif lowest < 50:
        return "Low"
    else:
        return "Normal"


def has_critical_resources(logistics_item):
    """Check if unit has any critical resource levels"""
    return get_lowest_resource_level(logistics_item) < 30


def get_status_color(status):
    """Get color based on unit status"""
    status_colors = {
        'operational': '#28a745',
        'warning': '#ffc107',
        'critical': '#dc3545',
        'offline': '#6c757d',
        'unknown': '#17a2b8'
    }
    return status_colors.get(status.lower(), '#17a2b8')


def create_metric_card(title, value, icon_type):
    """Create a metric card component"""
    icons = {
        'heart': '❤️',
        'stress': '⚡',
        'personnel': '👥',
        'fuel': '⛽',
        'ammo': '🔫',
        'medical': '🏥',
        'food': '🍽️'
    }
    
    return html.Div([
        html.Div([
            html.Span(icons.get(icon_type, '📊'), className="metric-icon"),
            html.Div([
                html.H3(value, className="metric-value"),
                html.P(title, className="metric-title")
            ], className="metric-content")
        ], className="metric-card-inner")
    ], className="metric-card")


def create_health_charts(health_data):
    """Create health monitoring charts with Turkish labels"""
    if not health_data:
        return {}, {}, {}
    
    # Heart rate chart
    heart_rate_fig = go.Figure()
    heart_rate_fig.add_trace(go.Scatter(
        x=[d["timestamp"] for d in health_data],
        y=[d.get("heart_rate", 0) for d in health_data],
        mode="lines+markers",
        name="Kalp Atış Hızı",
        line=dict(color="#e74c3c", width=2),
        marker=dict(size=6)
    ))
    heart_rate_fig.update_layout(
        title="Kalp Atış Hızı Trendi",
        xaxis_title="Zaman",
        yaxis_title="Atış/Dakika",
        height=250,
        margin=dict(l=40, r=20, t=40, b=40),
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font={"color": "#2c3e50", "size": 12}
    )
    
    # SpO2 chart
    spo2_fig = go.Figure()
    spo2_fig.add_trace(go.Scatter(
        x=[d["timestamp"] for d in health_data],
        y=[d.get("spo2", 0) for d in health_data],
        mode="lines+markers",
        name="Oksijen Satürasyonu",
        line=dict(color="#3498db", width=2),
        marker=dict(size=6)
    ))
    spo2_fig.update_layout(
        title="Oksijen Satürasyonu (%)",
        xaxis_title="Zaman",
        yaxis_title="SpO2 (%)",
        height=250,
        margin=dict(l=40, r=20, t=40, b=40),
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font={"color": "#2c3e50", "size": 12}
    )
    
    # Stress level chart
    stress_fig = go.Figure()
    stress_fig.add_trace(go.Scatter(
        x=[d["timestamp"] for d in health_data],
        y=[d.get("stress_level", 0) for d in health_data],
        mode="lines+markers",
        name="Stres Seviyesi",
        line=dict(color="#f39c12", width=2),
        marker=dict(size=6)
    ))
    stress_fig.update_layout(
        title="Stres Seviyesi Analizi",
        xaxis_title="Zaman",
        yaxis_title="Stres Skoru (1-10)",
        height=250,
        margin=dict(l=40, r=20, t=40, b=40),
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font={"color": "#2c3e50", "size": 12}
    )
    
    return heart_rate_fig, spo2_fig, stress_fig


def create_mission_progress_chart(missions_data):
    """Create mission progress chart with Turkish labels"""
    if not missions_data:
        return {}
    
    # Group missions by status
    status_counts = {}
    for mission in missions_data:
        status = mission.get("status", "Bilinmiyor")
        status_counts[status] = status_counts.get(status, 0) + 1
    
    # Turkish status labels
    status_labels = {
        "active": "Aktif",
        "completed": "Tamamlandı", 
        "pending": "Beklemede",
        "cancelled": "İptal Edildi"
    }
    
    labels = [status_labels.get(status, status) for status in status_counts.keys()]
    values = list(status_counts.values())
    colors = ["#27ae60", "#3498db", "#f39c12", "#e74c3c"]
    
    fig = go.Figure(data=[go.Pie(
        labels=labels,
        values=values,
        hole=0.4,
        marker_colors=colors
    )])
    
    fig.update_layout(
        title="Görev Durumu Dağılımı",
        height=300,
        margin=dict(l=20, r=20, t=40, b=20),
        font={"color": "#2c3e50", "size": 12}
    )
    
    return fig


def create_resource_trends_chart(logistics_data):
    """Create resource trends chart with Turkish labels"""
    if not logistics_data:
        return {}
    
    fig = go.Figure()
    
    # Resource types with Turkish labels
    resource_types = {
        "ammunition": "Mühimmat",
        "fuel": "Yakıt", 
        "medical": "Tıbbi Malzeme",
        "food": "Yiyecek ve Su"
    }
    
    colors = ["#e74c3c", "#f39c12", "#27ae60", "#3498db"]
    
    for i, (resource_type, label) in enumerate(resource_types.items()):
        resource_data = [d for d in logistics_data if d.get("resource_type") == resource_type]
        if resource_data:
            fig.add_trace(go.Scatter(
                x=[d["timestamp"] for d in resource_data],
                y=[d.get("level_pct", 0) for d in resource_data],
                mode="lines+markers",
                name=label,
                line=dict(color=colors[i % len(colors)], width=2),
                marker=dict(size=4)
            ))
    
    fig.update_layout(
        title="Kaynak Seviyeleri Trendi",
        xaxis_title="Zaman",
        yaxis_title="Seviye (%)",
        height=300,
        margin=dict(l=40, r=20, t=40, b=40),
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font={"color": "#2c3e50", "size": 12},
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )
    
    return fig

# Utility functions

def calculate_resource_average(logistics_data, resource_type):
    """Calculate average resource level"""
    if not logistics_data:
        return 0
    
    values = [item.get(resource_type, 0) for item in logistics_data]
    return round(sum(values) / len(values)) if values else 0


def get_mission_status(mission):
    """Get mission status based on progress and phase"""
    progress = mission.get("progress_pct", 0)
    phase = mission.get("phase", "unknown")
    
    if phase == "completed":
        return "Completed"
    elif progress < 30:
        return "Behind Schedule"
    elif progress < 70:
        return "On Track"
    else:
        return "Ahead of Schedule"


def get_critical_resource_type(logistics_item):
    """Get the most critical resource type for a unit"""
    resources = {
        "ammo_pct": "Ammunition",
        "fuel_pct": "Fuel", 
        "medical_pct": "Medical",
        "food_pct": "Food & Water"
    }
    
    min_resource = min(resources.keys(), key=lambda x: logistics_item.get(x, 100))
    return resources[min_resource]


def get_lowest_resource_level(logistics_item):
    """Get the lowest resource level for a unit"""
    levels = [
        logistics_item.get("ammo_pct", 100),
        logistics_item.get("fuel_pct", 100),
        logistics_item.get("medical_pct", 100),
        logistics_item.get("food_pct", 100)
    ]
    return min(levels)


def get_resource_status(logistics_item):
    """Get resource status based on lowest level"""
    lowest = get_lowest_resource_level(logistics_item)
    
    if lowest < 20:
        return "Critical"
    elif lowest < 50:
        return "Low"
    else:
        return "Normal"


def has_critical_resources(logistics_item):
    """Check if unit has any critical resource levels"""
    return get_lowest_resource_level(logistics_item) < 30


def get_status_color(status):
    """Get color based on unit status"""
    status_colors = {
        'operational': '#28a745',
        'warning': '#ffc107',
        'critical': '#dc3545',
        'offline': '#6c757d',
        'unknown': '#17a2b8'
    }
    return status_colors.get(status.lower(), '#17a2b8')


def create_metric_card(title, value, icon_type):
    """Create a metric card component"""
    icons = {
        'heart': '❤️',
        'stress': '⚡',
        'personnel': '👥',
        'fuel': '⛽',
        'ammo': '🔫',
        'medical': '🏥',
        'food': '🍽️'
    }
    
    return html.Div([
        html.Div([
            html.Span(icons.get(icon_type, '📊'), className="metric-icon"),
            html.Div([
                html.H3(value, className="metric-value"),
                html.P(title, className="metric-title")
            ], className="metric-content")
        ], className="metric-card-inner")
    ], className="metric-card")


def create_health_charts(health_data):
    """Create health monitoring charts with Turkish labels"""
    if not health_data:
        return {}, {}, {}
    
    # Heart rate chart
    heart_rate_fig = go.Figure()
    heart_rate_fig.add_trace(go.Scatter(
        x=[d["timestamp"] for d in health_data],
        y=[d.get("heart_rate", 0) for d in health_data],
        mode="lines+markers",
        name="Kalp Atış Hızı",
        line=dict(color="#e74c3c", width=2),
        marker=dict(size=6)
    ))
    heart_rate_fig.update_layout(
        title="Kalp Atış Hızı Trendi",
        xaxis_title="Zaman",
        yaxis_title="Atış/Dakika",
        height=250,
        margin=dict(l=40, r=20, t=40, b=40),
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font={"color": "#2c3e50", "size": 12}
    )
    
    # SpO2 chart
    spo2_fig = go.Figure()
    spo2_fig.add_trace(go.Scatter(
        x=[d["timestamp"] for d in health_data],
        y=[d.get("spo2", 0) for d in health_data],
        mode="lines+markers",
        name="Oksijen Satürasyonu",
        line=dict(color="#3498db", width=2),
        marker=dict(size=6)
    ))
    spo2_fig.update_layout(
        title="Oksijen Satürasyonu (%)",
        xaxis_title="Zaman",
        yaxis_title="SpO2 (%)",
        height=250,
        margin=dict(l=40, r=20, t=40, b=40),
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font={"color": "#2c3e50", "size": 12}
    )
    
    # Stress level chart
    stress_fig = go.Figure()
    stress_fig.add_trace(go.Scatter(
        x=[d["timestamp"] for d in health_data],
        y=[d.get("stress_level", 0) for d in health_data],
        mode="lines+markers",
        name="Stres Seviyesi",
        line=dict(color="#f39c12", width=2),
        marker=dict(size=6)
    ))
    stress_fig.update_layout(
        title="Stres Seviyesi Analizi",
        xaxis_title="Zaman",
        yaxis_title="Stres Skoru (1-10)",
        height=250,
        margin=dict(l=40, r=20, t=40, b=40),
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font={"color": "#2c3e50", "size": 12}
    )
    
    return heart_rate_fig, spo2_fig, stress_fig


def create_mission_progress_chart(missions_data):
    """Create mission progress chart with Turkish labels"""
    if not missions_data:
        return {}
    
    # Group missions by status
    status_counts = {}
    for mission in missions_data:
        status = mission.get("status", "Bilinmiyor")
        status_counts[status] = status_counts.get(status, 0) + 1
    
    # Turkish status labels
    status_labels = {
        "active": "Aktif",
        "completed": "Tamamlandı", 
        "pending": "Beklemede",
        "cancelled": "İptal Edildi"
    }
    
    labels = [status_labels.get(status, status) for status in status_counts.keys()]
    values = list(status_counts.values())
    colors = ["#27ae60", "#3498db", "#f39c12", "#e74c3c"]
    
    fig = go.Figure(data=[go.Pie(
        labels=labels,
        values=values,
        hole=0.4,
        marker_colors=colors
    )])
    
    fig.update_layout(
        title="Görev Durumu Dağılımı",
        height=300,
        margin=dict(l=20, r=20, t=40, b=20),
        font={"color": "#2c3e50", "size": 12}
    )
    
    return fig


def create_resource_trends_chart(logistics_data):
    """Create resource trends chart with Turkish labels"""
    if not logistics_data:
        return {}
    
    fig = go.Figure()
    
    # Resource types with Turkish labels
    resource_types = {
        "ammunition": "Mühimmat",
        "fuel": "Yakıt", 
        "medical": "Tıbbi Malzeme",
        "food": "Yiyecek ve Su"
    }
    
    colors = ["#e74c3c", "#f39c12", "#27ae60", "#3498db"]
    
    for i, (resource_type, label) in enumerate(resource_types.items()):
        resource_data = [d for d in logistics_data if d.get("resource_type") == resource_type]
        if resource_data:
            fig.add_trace(go.Scatter(
                x=[d["timestamp"] for d in resource_data],
                y=[d.get("level_pct", 0) for d in resource_data],
                mode="lines+markers",
                name=label,
                line=dict(color=colors[i % len(colors)], width=2),
                marker=dict(size=4)
            ))
    
    fig.update_layout(
        title="Kaynak Seviyeleri Trendi",
        xaxis_title="Zaman",
        yaxis_title="Seviye (%)",
        height=300,
        margin=dict(l=40, r=20, t=40, b=40),
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font={"color": "#2c3e50", "size": 12},
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )
    
    return fig

def register_role_callbacks():
    """Register role-based layout callbacks"""
    
    # Role-based layout callbacks
    @app.callback(
        Output('commander-overview-chart', 'figure'),
        [Input('interval-component', 'n_intervals')]
    )
    def update_commander_overview(n):
        """Komutan genel durum grafiği"""
        fig = go.Figure()
        
        # Birim durumu
        categories = ['Aktif', 'Görevde', 'Hazır', 'Bakımda']
        values = [45, 32, 18, 5]
        colors = ['#4CAF50', '#2196F3', '#FF9800', '#f44336']
        
        fig.add_trace(go.Bar(
            x=categories,
            y=values,
            marker_color=colors,
            text=values,
            textposition='auto',
        name='Birim Durumu'
    ))
    
    fig.update_layout(
        title='Birim Durumu Genel Bakış',
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white'),
        xaxis=dict(color='white'),
        yaxis=dict(color='white'),
        height=200
    )
    
    return fig

    @app.callback(
        Output('commander-mission-chart', 'figure'),
        [Input('interval-component', 'n_intervals')]
    )
    def update_commander_mission(n):
        """Komutan görev durumu grafiği"""
        fig = go.Figure()
        
        # Görev durumu
        labels = ['Tamamlanan', 'Devam Eden', 'Bekleyen', 'İptal Edilen']
        values = [65, 25, 8, 2]
        colors = ['#4CAF50', '#2196F3', '#FF9800', '#f44336']
        
        fig.add_trace(go.Pie(
            labels=labels,
            values=values,
            marker_colors=colors,
            hole=0.4
        ))
        
        fig.update_layout(
            title='Görev Durumu',
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color='white'),
            height=200
        )
        
        return fig

    @app.callback(
        Output('commander-threat-chart', 'figure'),
        [Input('interval-component', 'n_intervals')]
    )
    def update_commander_threat(n):
        """Komutan tehdit seviyesi grafiği"""
        fig = go.Figure()
        
        # Son 24 saat tehdit seviyeleri
        hours = list(range(24))
        threat_levels = [2, 1, 1, 0, 0, 1, 2, 3, 4, 3, 2, 3, 4, 5, 4, 3, 2, 3, 4, 3, 2, 1, 1, 2]
        
        fig.add_trace(go.Scatter(
            x=hours,
            y=threat_levels,
            mode='lines+markers',
            line=dict(color='#f44336', width=3),
            marker=dict(size=6, color='#f44336'),
            fill='tonexty',
            name='Tehdit Seviyesi'
        ))
        
        fig.update_layout(
            title='24 Saatlik Tehdit Seviyesi',
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color='white'),
            xaxis=dict(title='Saat', color='white'),
            yaxis=dict(title='Tehdit Seviyesi', color='white'),
            height=200
        )
        
        return fig

    @app.callback(
        Output('commander-resources-chart', 'figure'),
        [Input('interval-component', 'n_intervals')]
    )
    def update_commander_resources(n):
        """Komutan kaynak durumu grafiği"""
        fig = go.Figure()
        
        # Kaynak durumu
        resources = ['Personel', 'Araç', 'Silah', 'Mühimmat', 'Yakıt', 'Yiyecek']
        current = [85, 92, 78, 65, 88, 95]
        target = [100, 100, 100, 100, 100, 100]
    
    fig.add_trace(go.Bar(
        x=resources,
        y=current,
        name='Mevcut',
        marker_color='#4CAF50'
    ))
    
    fig.add_trace(go.Bar(
        x=resources,
        y=[t-c for t, c in zip(target, current)],
        name='Eksik',
        marker_color='#f44336',
        base=current
    ))
    
    fig.update_layout(
        title='Kaynak Durumu (%)',
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white'),
        xaxis=dict(color='white'),
        yaxis=dict(color='white'),
        barmode='stack',
        height=200
    )
    
    return fig

def register_role_callbacks():
    """Rol bazlı callback'leri kaydet"""
    
    @app.callback(
        Output('commander-overview-chart', 'figure'),
        [Input('interval-component', 'n_intervals')]
    )
    def update_commander_overview(n):
        """Komutan genel bakış grafiği"""
        fig = go.Figure()
        
        # Birim durumu verileri
        categories = ['Aktif', 'Görevde', 'Hazır', 'Bakımda']
        values = [45, 32, 18, 5]
        colors = ['#4CAF50', '#2196F3', '#FF9800', '#f44336']

        fig.add_trace(go.Bar(
            x=categories,
            y=values,
            marker_color=colors,
            name='Birim Durumu'
        ))

        fig.update_layout(
            title='Birim Durumu Genel Bakış',
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color='white'),
            xaxis=dict(color='white'),
            yaxis=dict(color='white'),
            height=200
        )
        
        return fig

    @app.callback(
        Output('commander-mission-chart', 'figure'),
        [Input('interval-component', 'n_intervals')]
    )
    def update_commander_mission(n):
        """Komutan görev durumu grafiği"""
        fig = go.Figure()
        
        # Görev durumu verileri
        labels = ['Tamamlanan', 'Devam Eden', 'Bekleyen', 'İptal Edilen']
        values = [65, 25, 8, 2]
        colors = ['#4CAF50', '#2196F3', '#FF9800', '#f44336']

        fig.add_trace(go.Pie(
            labels=labels,
            values=values,
            marker_colors=colors,
            hole=0.4
        ))

        fig.update_layout(
            title='Görev Durumu Dağılımı',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='white'),
            height=200
        )
        
        return fig

    @app.callback(
        Output('commander-threat-chart', 'figure'),
        [Input('interval-component', 'n_intervals')]
    )
    def update_commander_threat(n):
        """Komutan tehdit seviyesi grafiği"""
        fig = go.Figure()
        
        # 24 saatlik tehdit seviyeleri
        hours = list(range(24))
        threat_levels = [2, 1, 1, 0, 0, 1, 2, 3, 4, 3, 2, 3, 4, 5, 4, 3, 2, 3, 4, 3, 2, 1, 1, 2]

        fig.add_trace(go.Scatter(
            x=hours,
            y=threat_levels,
            mode='lines+markers',
            name='Tehdit Seviyesi',
            line=dict(color='#f44336', width=2),
            marker=dict(size=6)
        ))

        fig.update_layout(
            title='24 Saatlik Tehdit Seviyesi',
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color='white'),
            xaxis=dict(title='Saat', color='white'),
            yaxis=dict(title='Tehdit Seviyesi', color='white'),
            height=200
        )
        
        return fig

    @app.callback(
        Output('commander-resources-chart', 'figure'),
        [Input('interval-component', 'n_intervals')]
    )
    def update_commander_resources(n):
        """Komutan kaynak durumu grafiği"""
        fig = go.Figure()
        
        # Kaynak durumu
        resources = ['Personel', 'Araç', 'Silah', 'Mühimmat', 'Yakıt', 'Yiyecek']
        current = [85, 92, 78, 65, 88, 95]
        target = [100, 100, 100, 100, 100, 100]

        fig.add_trace(go.Bar(
            x=resources,
            y=current,
            name='Mevcut',
            marker_color='#4CAF50'
        ))

        fig.add_trace(go.Bar(
            x=resources,
            y=[t-c for t, c in zip(target, current)],
            name='Eksik',
            marker_color='#f44336',
            base=current
        ))

        fig.update_layout(
            title='Kaynak Durumu (%)',
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color='white'),
            xaxis=dict(color='white'),
            yaxis=dict(color='white'),
            barmode='stack',
            height=200
        )
        
        return fig

    @app.callback(
        Output('health-history-chart', 'figure'),
        [Input('interval-component', 'n_intervals')]
    )
    def update_health_history(n):
        """Sağlık geçmişi grafiği"""
        fig = go.Figure()
        
        # Son 30 günlük sağlık verileri
        dates = pd.date_range(start='2024-01-01', periods=30, freq='D')
        healthy = [85 + i*0.5 + (i%7)*2 for i in range(30)]
        injured = [5 + (i%3) for i in range(30)]
        sick = [2 + (i%5) for i in range(30)]
        
        fig.add_trace(go.Scatter(
            x=dates,
            y=healthy,
            mode='lines+markers',
            name='Sağlıklı',
            line=dict(color='#4CAF50', width=2),
            marker=dict(size=4)
        ))
        
        fig.add_trace(go.Scatter(
            x=dates,
            y=injured,
            mode='lines+markers',
            name='Yaralı',
            line=dict(color='#FF9800', width=2),
            marker=dict(size=4)
        ))
        
        fig.add_trace(go.Scatter(
            x=dates,
            y=sick,
            mode='lines+markers',
            name='Hasta',
            line=dict(color='#f44336', width=2),
            marker=dict(size=4)
        ))
        
        fig.update_layout(
            title='30 Günlük Sağlık Geçmişi',
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color='white'),
            xaxis=dict(title='Tarih', color='white'),
            yaxis=dict(title='Kişi Sayısı', color='white'),
            height=300
        )
        
        return fig

    @app.callback(
        Output('health-incidents-chart', 'figure'),
        [Input('interval-component', 'n_intervals')]
    )
    def update_health_incidents(n):
        """Sağlık olayları grafiği"""
        fig = go.Figure()
        
        # Olay türleri
        incident_types = ['Yaralanma', 'Hastalık', 'Kaza', 'Acil Durum']
        incident_counts = [15, 8, 5, 3]
        
        fig.add_trace(go.Bar(
            x=incident_types,
            y=incident_counts,
            name='Sağlık Olayları',
            marker_color='#e74c3c'
        ))
        
        fig.update_layout(
            title='Sağlık Olayları Dağılımı',
            xaxis_title='Olay Türü',
            yaxis_title='Olay Sayısı',
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color='white'),
            xaxis=dict(color='white'),
            yaxis=dict(color='white'),
            height=300
        )
        
        return fig

    @app.callback(
        Output('analyst-time-series-chart', 'figure'),
        [Input('interval-component', 'n_intervals')]
    )
    def update_analyst_time_series(n):
        """Analist zaman serisi grafiği"""
        fig = go.Figure()
        
        # Zaman serisi verileri
        dates = pd.date_range(start='2024-01-01', periods=100, freq='H')
        values = [50 + i*0.1 + (i%24)*2 + (i%7)*5 for i in range(100)]
        
        fig.add_trace(go.Scatter(
            x=dates,
            y=values,
            mode='lines',
            name='Operasyonel Metrik',
            line=dict(color='#2196F3', width=2)
        ))
        
        # Trend çizgisi
        trend = [50 + i*0.15 for i in range(100)]
        fig.add_trace(go.Scatter(
            x=dates,
            y=trend,
            mode='lines',
            name='Trend',
            line=dict(color='#FF9800', width=2, dash='dash')
        ))
        
        fig.update_layout(
            title='Zaman Serisi Analizi',
            xaxis_title='Zaman',
            yaxis_title='Değer',
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color='white'),
            xaxis=dict(color='white'),
            yaxis=dict(color='white'),
            height=400
        )
        
        return fig

    @app.callback(
        Output('analyst-correlation-chart', 'figure'),
        [Input('interval-component', 'n_intervals')]
    )
    def update_analyst_correlation(n):
        """Analist korelasyon grafiği"""
        fig = go.Figure()
        
        # Korelasyon matrisi
        variables = ['Personel', 'Araç', 'Görev', 'Risk']
        correlation_matrix = [
            [1.0, 0.8, 0.6, -0.4],
            [0.8, 1.0, 0.7, -0.3],
            [0.6, 0.7, 1.0, -0.5],
            [-0.4, -0.3, -0.5, 1.0]
        ]
        
        fig.add_trace(go.Heatmap(
            z=correlation_matrix,
            x=variables,
            y=variables,
            colorscale='RdBu',
            zmid=0,
            text=correlation_matrix,
            texttemplate='%{text:.2f}',
            textfont={"size": 12}
        ))
        
        fig.update_layout(
            title='Değişken Korelasyon Matrisi',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='white'),
            height=400
        )
        
        return fig

    @app.callback(
        Output('analyst-prediction-chart', 'figure'),
        [Input('interval-component', 'n_intervals')]
    )
    def update_analyst_prediction(n):
        """Analist tahmin grafiği"""
        fig = go.Figure()
        
        # Geçmiş ve tahmin verileri
        dates_past = pd.date_range(start='2024-01-01', periods=30, freq='D')
        dates_future = pd.date_range(start='2024-01-31', periods=15, freq='D')
        
        past_values = [80 + i*0.5 + (i%7)*3 for i in range(30)]
        predicted_values = [110 + i*0.3 + (i%5)*2 for i in range(15)]
        
        fig.add_trace(go.Scatter(
            x=dates_past,
            y=past_values,
            mode='lines+markers',
            name='Geçmiş Veriler',
            line=dict(color='#2196F3', width=2)
        ))
        
        fig.add_trace(go.Scatter(
            x=dates_future,
            y=predicted_values,
            mode='lines+markers',
            name='Tahminler',
            line=dict(color='#FF9800', width=2, dash='dash')
        ))
        
        fig.update_layout(
            title='Operasyonel Tahmin Modeli',
            xaxis_title='Tarih',
            yaxis_title='Değer',
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color='white'),
            xaxis=dict(color='white'),
            yaxis=dict(color='white'),
            height=400
        )
        
        return fig