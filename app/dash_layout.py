"""
MSA Dashboard - Dash Layout
Interactive dashboard layout with military situational awareness components
"""

import dash
from dash import html, dcc, dash_table
import dash_leaflet as dl
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import uuid

from core.settings import settings, RISK_COLORS, MAP_CONFIG, ROLE_CONFIGS


def create_header():
    """Create dashboard header with role indicator"""
    return html.Header([
        html.Div([
            html.Div([
                html.H1("MSA Dashboard", className="header-title"),
                html.P("Military Situational Awareness", className="header-subtitle")
            ], className="header-brand"),
            
            html.Div([
                html.Div(id="role-indicator", className="role-indicator"),
                html.Div([
                    html.Span(id="current-time", className="time-display"),
                    html.Button("Çıkış", id="logout-button", className="logout-btn")
                ], className="header-controls")
            ], className="header-info")
        ], className="header-content")
    ], className="dashboard-header")


def create_control_panel():
    """Create control panel with filters and settings"""
    return html.Div([
        html.H3("Kontrol Paneli", className="panel-title"),
        
        # Role selector
        html.Div([
            html.Label("Kullanıcı Rolü:", className="control-label"),
            dcc.Dropdown(
                id="role-selector",
                options=[
                    {"label": "Komutan", "value": "commander"},
                    {"label": "Sağlık Subayı", "value": "health_officer"},
                    {"label": "Operasyon Analisti", "value": "operations_analyst"}
                ],
                value="commander",
                className="control-dropdown"
            )
        ], className="control-group"),
        
        # Unit type filter
        html.Div([
            html.Label("Birim Tipi Filtresi:", className="control-label"),
            dcc.Dropdown(
                id="unit-type-filter",
                options=[
                    {"label": "Tüm Birimler", "value": "all"},
                    {"label": "Piyade", "value": "infantry"},
                    {"label": "Zırhlı", "value": "armor"},
                    {"label": "Topçu", "value": "artillery"},
                    {"label": "Keşif", "value": "recon"},
                    {"label": "Destek", "value": "support"},
                    {"label": "Komuta", "value": "command"}
                ],
                value="all",
                multi=True,
                className="control-dropdown"
            )
        ], className="control-group"),
        
        # Risk level filter
        html.Div([
            html.Label("Risk Seviyesi Filtresi:", className="control-label"),
            dcc.Dropdown(
                id="risk-filter",
                options=[
                    {"label": "Tüm Seviyeler", "value": "all"},
                    {"label": "Kritik (Kırmızı)", "value": "red"},
                    {"label": "Uyarı (Sarı)", "value": "amber"},
                    {"label": "Normal (Yeşil)", "value": "green"}
                ],
                value="all",
                multi=True,
                className="control-dropdown"
            )
        ], className="control-group"),
        
        # Time range selector
        html.Div([
            html.Label("Zaman Aralığı:", className="control-label"),
            dcc.Dropdown(
                id="time-range",
                options=[
                    {"label": "Son 1 Saat", "value": 1},
                    {"label": "Son 6 Saat", "value": 6},
                    {"label": "Son 24 Saat", "value": 24},
                    {"label": "Son 7 Gün", "value": 168}
                ],
                value=24,
                className="control-dropdown"
            )
        ], className="control-group"),
        
        # Auto-refresh toggle
        html.Div([
            html.Label("Otomatik Yenileme:", className="control-label"),
            dcc.Interval(
                id="interval-component",
                interval=settings.default_refresh_interval * 1000,  # milliseconds
                n_intervals=0
            ),
            html.Button("Şimdi Yenile", id="manual-refresh", className="refresh-button")
        ], className="control-group"),
        
    ], className="control-panel")


def create_map_panel():
    """Create interactive map panel with units and threats"""
    return html.Div([
        html.H3("Taktik Harita", className="panel-title"),
        
        # Map controls
        html.Div([
            html.Button("Haritayı Ortala", id="center-map-btn", className="map-control-btn"),
            html.Button("Katmanları Değiştir", id="toggle-layers-btn", className="map-control-btn"),
            html.Div([
                html.Label("Harita Stili:"),
                dcc.Dropdown(
                    id="map-style",
                    options=[
                        {"label": "OpenStreetMap", "value": "osm"},
                        {"label": "Uydu", "value": "satellite"},
                        {"label": "Arazi", "value": "terrain"}
                    ],
                    value="osm",
                    className="map-style-dropdown"
                )
            ], className="map-style-control")
        ], className="map-controls"),
        
        # Interactive map
        dl.Map([
            dl.TileLayer(
                id="tile-layer",
                url=MAP_CONFIG["tile_layer"],
                attribution=MAP_CONFIG["attribution"]
            ),
            
            # Unit markers layer
            dl.LayerGroup(id="units-layer", children=[]),
            
            # Threat markers layer
            dl.LayerGroup(id="threats-layer", children=[]),
            
            # Weather layer
            dl.LayerGroup(id="weather-layer", children=[]),
            
            # Mission areas layer
            dl.LayerGroup(id="missions-layer", children=[]),
            
        ], 
        id="tactical-map",
        center=MAP_CONFIG["map_default_center"],
        zoom=MAP_CONFIG["map_default_zoom"],
        style={"height": "500px", "width": "100%"}
        ),
        
        # Map legend
        html.Div([
            html.H4("Açıklama", className="legend-title"),
            html.Div([
                html.Div([
                    html.Div(className="legend-color", style={"background-color": RISK_COLORS["green"]}),
                    html.Span("Normal Durum", className="legend-text")
                ], className="legend-item"),
                html.Div([
                    html.Div(className="legend-color", style={"background-color": RISK_COLORS["amber"]}),
                    html.Span("Uyarı Durumu", className="legend-text")
                ], className="legend-item"),
                html.Div([
                    html.Div(className="legend-color", style={"background-color": RISK_COLORS["red"]}),
                    html.Span("Kritik Durum", className="legend-text")
                ], className="legend-item"),
            ], className="legend-items")
        ], className="map-legend")
        
    ], className="map-panel")


def create_health_panel():
    """Create health monitoring panel"""
    return html.Div([
        html.H3("Sağlık İzleme", className="panel-title"),
        
        # Health summary cards
        html.Div([
            html.Div([
                html.H4("Kritik Sağlık", className="metric-title"),
                html.H2(id="critical-health-count", className="metric-value critical"),
                html.P("Birim", className="metric-unit")
            ], className="health-card critical"),
            
            html.Div([
                html.H4("Uyarı Sağlık", className="metric-title"),
                html.H2(id="warning-health-count", className="metric-value warning"),
                html.P("Birim", className="metric-unit")
            ], className="health-card warning"),
            
            html.Div([
                html.H4("Normal Sağlık", className="metric-title"),
                html.H2(id="normal-health-count", className="metric-value normal"),
                html.P("Birim", className="metric-unit")
            ], className="health-card normal"),
        ], className="health-summary"),
        
        # Health metrics charts
        html.Div([
            html.Div([
                dcc.Graph(id="heart-rate-chart", className="health-chart")
            ], className="chart-container"),
            
            html.Div([
                dcc.Graph(id="spo2-chart", className="health-chart")
            ], className="chart-container"),
            
            html.Div([
                dcc.Graph(id="stress-chart", className="health-chart")
            ], className="chart-container"),
        ], className="health-charts"),
        
        # Health alerts table
        html.Div([
            html.H4("Sağlık Uyarıları", className="table-title"),
            dash_table.DataTable(
                id="health-alerts-table",
                columns=[
                    {"name": "Birim", "id": "unit_id"},
                    {"name": "Uyarı", "id": "alert_type"},
                    {"name": "Önem", "id": "severity"},
                    {"name": "Zaman", "id": "timestamp"},
                    {"name": "Durum", "id": "status"}
                ],
                style_cell={"textAlign": "left"},
                style_data_conditional=[
                    {
                        "if": {"filter_query": "{severity} = critical"},
                        "backgroundColor": "#ffebee",
                        "color": "black",
                    },
                    {
                        "if": {"filter_query": "{severity} = warning"},
                        "backgroundColor": "#fff8e1",
                        "color": "black",
                    }
                ],
                page_size=10
            )
        ], className="health-alerts")
        
    ], className="health-panel")


def create_mission_panel():
    """Create mission status panel"""
    return html.Div([
        html.H3("Görev Durumu", className="panel-title"),
        
        # Mission overview cards
        html.Div([
            html.Div([
                html.H4("Aktif Görevler", className="metric-title"),
                html.H2(id="active-missions-count", className="metric-value"),
                html.P("Görev", className="metric-unit")
            ], className="mission-card"),
            
            html.Div([
                html.H4("Tamamlanma Oranı", className="metric-title"),
                html.H2(id="mission-completion-rate", className="metric-value"),
                html.P("%", className="metric-unit")
            ], className="mission-card"),
            
            html.Div([
                html.H4("Kritik Hedefler", className="metric-title"),
                html.H2(id="critical-objectives-count", className="metric-value critical"),
                html.P("Hedef", className="metric-unit")
            ], className="mission-card"),
        ], className="mission-summary"),
        
        # Mission progress chart
        html.Div([
            dcc.Graph(id="mission-progress-chart", className="mission-chart")
        ], className="mission-progress"),
        
        # Mission timeline
        html.Div([
            html.H4("Görev Zaman Çizelgesi", className="table-title"),
            dash_table.DataTable(
                id="mission-timeline-table",
                columns=[
                    {"name": "Görev", "id": "name"},
                    {"name": "Aşama", "id": "phase"},
                    {"name": "İlerleme", "id": "progress_pct"},
                    {"name": "Durum", "id": "status"},
                    {"name": "Tahmini Bitiş", "id": "estimated_end_time"}
                ],
                style_cell={"textAlign": "left"},
                page_size=8
            )
        ], className="mission-timeline")
        
    ], className="mission-panel")


def create_alerts_panel():
    """Create alerts and notifications panel"""
    return html.Div([
        html.H3("Uyarı Konsolu", className="panel-title"),
        
        # Alert summary
        html.Div([
            html.Div([
                html.H4("Acil Durum", className="alert-level-title"),
                html.H2(id="emergency-alerts-count", className="alert-count emergency"),
            ], className="alert-summary-card emergency"),
            
            html.Div([
                html.H4("Kritik", className="alert-level-title"),
                html.H2(id="critical-alerts-count", className="alert-count critical"),
            ], className="alert-summary-card critical"),
            
            html.Div([
                html.H4("Uyarı", className="alert-level-title"),
                html.H2(id="warning-alerts-count", className="alert-count warning"),
            ], className="alert-summary-card warning"),
            
            html.Div([
                html.H4("Bilgi", className="alert-level-title"),
                html.H2(id="info-alerts-count", className="alert-count info"),
            ], className="alert-summary-card info"),
        ], className="alert-summary"),
        
        # Active alerts list
        html.Div([
            html.H4("Aktif Uyarılar", className="alerts-title"),
            html.Div(id="active-alerts-list", className="alerts-list")
        ], className="active-alerts"),
        
        # Alert actions
        html.Div([
            html.Button("Tümünü Onayla", id="ack-all-btn", className="alert-action-btn"),
            html.Button("Çözülenleri Temizle", id="clear-resolved-btn", className="alert-action-btn"),
            html.Button("Günlük Dışa Aktar", id="export-log-btn", className="alert-action-btn"),
        ], className="alert-actions")
        
    ], className="alerts-panel")


def create_logistics_panel():
    """Create logistics status panel"""
    return html.Div([
        html.H3("Lojistik Durumu", className="panel-title"),
        
        # Resource overview
        html.Div([
            html.Div([
                html.H4("Mühimmat", className="resource-title"),
                dcc.Graph(id="ammo-gauge", className="resource-gauge")
            ], className="resource-card"),
            
            html.Div([
                html.H4("Yakıt", className="resource-title"),
                dcc.Graph(id="fuel-gauge", className="resource-gauge")
            ], className="resource-card"),
            
            html.Div([
                html.H4("Tıbbi Malzeme", className="resource-title"),
                dcc.Graph(id="medical-gauge", className="resource-gauge")
            ], className="resource-card"),
            
            html.Div([
                html.H4("Yiyecek ve Su", className="resource-title"),
                dcc.Graph(id="food-gauge", className="resource-gauge")
            ], className="resource-card"),
        ], className="logistics-overview"),
        
        # Resource trends chart
        html.Div([
            dcc.Graph(id="resource-trends-chart", className="logistics-chart")
        ], className="resource-trends"),
        
        # Critical supplies table
        html.Div([
            html.H4("Kritik Malzemeler", className="table-title"),
            dash_table.DataTable(
                id="critical-supplies-table",
                columns=[
                    {"name": "Birim", "id": "unit_id"},
                    {"name": "Kaynak", "id": "resource_type"},
                    {"name": "Seviye", "id": "level_pct"},
                    {"name": "Durum", "id": "status"},
                    {"name": "Son Güncelleme", "id": "timestamp"}
                ],
                style_cell={"textAlign": "left"},
                style_data_conditional=[
                    {
                        "if": {"filter_query": "{level_pct} < 20"},
                        "backgroundColor": "#ffebee",
                        "color": "black",
                    },
                    {
                        "if": {"filter_query": "{level_pct} < 50 && {level_pct} >= 20"},
                        "backgroundColor": "#fff8e1",
                        "color": "black",
                    }
                ],
                page_size=10
            )
        ], className="critical-supplies")
        
    ], className="logistics-panel")


def create_commander_layout():
    """Create commander-specific layout with 2x2 large cards"""
    return html.Div([
        # Commander header
        html.Div([
            html.H2("Komutan Kontrol Paneli", className="commander-title"),
            html.P("Operasyonel Durum Özeti", className="commander-subtitle")
        ], className="commander-header"),
        
        # 2x2 Grid of large cards
        html.Div([
            # Row 1
            html.Div([
                # Operational Status Card
                html.Div([
                    html.H3("Operasyonel Durum", className="card-title"),
                    html.Div([
                        html.Div([
                            html.H2(id="total-units-count", className="metric-value"),
                            html.P("Toplam Birim", className="metric-label")
                        ], className="metric-item"),
                        html.Div([
                            html.H2(id="active-missions-count", className="metric-value"),
                            html.P("Aktif Görev", className="metric-label")
                        ], className="metric-item"),
                        html.Div([
                            html.H2(id="threat-level", className="metric-value"),
                            html.P("Tehdit Seviyesi", className="metric-label")
                        ], className="metric-item")
                    ], className="metrics-grid"),
                    dcc.Graph(id="operational-overview-chart", className="card-chart")
                ], className="commander-card operational-card"),
                
                # Resource Status Card
                html.Div([
                    html.H3("Kaynak Durumu", className="card-title"),
                    html.Div([
                        dcc.Graph(id="commander-resource-chart", className="card-chart-full")
                    ], className="chart-container")
                ], className="commander-card resource-card")
            ], className="commander-row"),
            
            # Row 2
            html.Div([
                # Mission Control Card
                html.Div([
                    html.H3("Görev Kontrolü", className="card-title"),
                    html.Div([
                        dcc.Graph(id="mission-status-pie", className="card-chart"),
                        html.Div([
                            html.Button("Yeni Görev", className="action-btn primary"),
                            html.Button("Görev Güncelle", className="action-btn secondary"),
                            html.Button("Acil Durum", className="action-btn danger")
                        ], className="action-buttons")
                    ], className="mission-control-content")
                ], className="commander-card mission-card"),
                
                # Intelligence Card
                html.Div([
                    html.H3("İstihbarat Özeti", className="card-title"),
                    html.Div([
                        html.Div(id="intelligence-alerts", className="intelligence-content"),
                        dcc.Graph(id="threat-analysis-chart", className="card-chart")
                    ], className="intelligence-container")
                ], className="commander-card intelligence-card")
            ], className="commander-row")
        ], className="commander-grid")
    ], className="commander-layout")


def create_health_officer_layout():
    """Create health officer-specific layout with health history charts"""
    return html.Div([
        # Health Officer header
        html.Div([
            html.H2("Sağlık Subayı Paneli", className="health-title"),
            html.P("Personel Sağlık İzleme ve Geçmiş Analizi", className="health-subtitle")
        ], className="health-header"),
        
        # Health metrics overview
        html.Div([
            html.Div([
                html.H4("Aktif Personel", className="health-metric-title"),
                html.H2(id="active-personnel-count", className="health-metric-value")
            ], className="health-metric-card"),
            html.Div([
                html.H4("Sağlık Uyarıları", className="health-metric-title"),
                html.H2(id="health-alerts-count", className="health-metric-value")
            ], className="health-metric-card"),
            html.Div([
                html.H4("Tıbbi Müdahale", className="health-metric-title"),
                html.H2(id="medical-interventions-count", className="health-metric-value")
            ], className="health-metric-card"),
            html.Div([
                html.H4("Ortalama Fitness", className="health-metric-title"),
                html.H2(id="average-fitness-score", className="health-metric-value")
            ], className="health-metric-card")
        ], className="health-metrics-overview"),
        
        # Health history charts
        html.Div([
            # Vital signs trends
            html.Div([
                html.H3("Vital Bulgular Geçmişi", className="chart-title"),
                dcc.Graph(id="vital-signs-history", className="health-chart")
            ], className="health-chart-container"),
            
            # Health incidents timeline
            html.Div([
                html.H3("Sağlık Olayları Zaman Çizelgesi", className="chart-title"),
                dcc.Graph(id="health-incidents-timeline", className="health-chart")
            ], className="health-chart-container")
        ], className="health-charts-row"),
        
        html.Div([
            # Medical supply usage
            html.Div([
                html.H3("Tıbbi Malzeme Kullanımı", className="chart-title"),
                dcc.Graph(id="medical-supply-usage", className="health-chart")
            ], className="health-chart-container"),
            
            # Personnel fitness trends
            html.Div([
                html.H3("Personel Fitness Trendleri", className="chart-title"),
                dcc.Graph(id="fitness-trends", className="health-chart")
            ], className="health-chart-container")
        ], className="health-charts-row"),
        
        # Detailed health table
        html.Div([
            html.H3("Detaylı Sağlık Raporu", className="table-title"),
            dash_table.DataTable(
                id="detailed-health-table",
                columns=[
                    {"name": "Personel ID", "id": "personnel_id"},
                    {"name": "İsim", "id": "name"},
                    {"name": "Kalp Atışı", "id": "heart_rate"},
                    {"name": "Oksijen", "id": "oxygen_saturation"},
                    {"name": "Stres", "id": "stress_level"},
                    {"name": "Son Kontrol", "id": "last_check"},
                    {"name": "Durum", "id": "status"}
                ],
                style_cell={"textAlign": "left"},
                page_size=10,
                sort_action="native",
                filter_action="native"
            )
        ], className="health-table-container")
    ], className="health-officer-layout")


def create_analyst_layout():
    """Create analyst-specific layout with time series analysis"""
    return html.Div([
        # Analyst header
        html.Div([
            html.H2("Operasyon Analisti Paneli", className="analyst-title"),
            html.P("Zaman Serisi Analizi ve Trend Değerlendirmesi", className="analyst-subtitle")
        ], className="analyst-header"),
        
        # Analysis controls
        html.Div([
            html.Div([
                html.Label("Analiz Periyodu:", className="control-label"),
                dcc.Dropdown(
                    id="analysis-period-dropdown",
                    options=[
                        {"label": "Son 1 Saat", "value": "1h"},
                        {"label": "Son 6 Saat", "value": "6h"},
                        {"label": "Son 24 Saat", "value": "24h"},
                        {"label": "Son 7 Gün", "value": "7d"},
                        {"label": "Son 30 Gün", "value": "30d"}
                    ],
                    value="24h",
                    className="analysis-dropdown"
                )
            ], className="analysis-control"),
            html.Div([
                html.Label("Metrik Türü:", className="control-label"),
                dcc.Dropdown(
                    id="metric-type-dropdown",
                    options=[
                        {"label": "Operasyonel Metrikler", "value": "operational"},
                        {"label": "Sağlık Metrikleri", "value": "health"},
                        {"label": "Lojistik Metrikleri", "value": "logistics"},
                        {"label": "Güvenlik Metrikleri", "value": "security"}
                    ],
                    value="operational",
                    className="analysis-dropdown"
                )
            ], className="analysis-control"),
            html.Div([
                html.Button("Analizi Yenile", id="refresh-analysis-btn", className="analysis-btn"),
                html.Button("Rapor Oluştur", id="generate-report-btn", className="analysis-btn")
            ], className="analysis-actions")
        ], className="analysis-controls"),
        
        # Time series charts
        html.Div([
            # Main trend analysis
            html.Div([
                html.H3("Ana Trend Analizi", className="chart-title"),
                dcc.Graph(id="main-trend-analysis", className="analyst-chart-large")
            ], className="analyst-chart-container-large"),
            
            # Correlation analysis
            html.Div([
                html.H3("Korelasyon Analizi", className="chart-title"),
                dcc.Graph(id="correlation-analysis", className="analyst-chart")
            ], className="analyst-chart-container"),
            
            # Anomaly detection
            html.Div([
                html.H3("Anomali Tespiti", className="chart-title"),
                dcc.Graph(id="anomaly-detection", className="analyst-chart")
            ], className="analyst-chart-container")
        ], className="analyst-charts-row"),
        
        html.Div([
            # Predictive analysis
            html.Div([
                html.H3("Tahmin Analizi", className="chart-title"),
                dcc.Graph(id="predictive-analysis", className="analyst-chart")
            ], className="analyst-chart-container"),
            
            # Performance metrics
            html.Div([
                html.H3("Performans Metrikleri", className="chart-title"),
                dcc.Graph(id="performance-metrics", className="analyst-chart")
            ], className="analyst-chart-container"),
            
            # Statistical summary
            html.Div([
                html.H3("İstatistiksel Özet", className="chart-title"),
                html.Div(id="statistical-summary", className="stats-container")
            ], className="analyst-stats-container")
        ], className="analyst-charts-row"),
        
        # Analysis results table
        html.Div([
            html.H3("Analiz Sonuçları", className="table-title"),
            dash_table.DataTable(
                id="analysis-results-table",
                columns=[
                    {"name": "Zaman", "id": "timestamp"},
                    {"name": "Metrik", "id": "metric"},
                    {"name": "Değer", "id": "value"},
                    {"name": "Trend", "id": "trend"},
                    {"name": "Anomali", "id": "anomaly"},
                    {"name": "Güven Aralığı", "id": "confidence"}
                ],
                style_cell={"textAlign": "left"},
                page_size=15,
                sort_action="native",
                filter_action="native"
            )
        ], className="analyst-table-container")
    ], className="analyst-layout")


def create_dashboard_layout():
    """Create the main dashboard layout with role-based content"""
    return html.Div([
        # Authentication modal
        create_login_modal(),
        
        # Session storage for authentication
        dcc.Store(id='session-store', storage_type='session'),
        dcc.Store(id='user-role-store', storage_type='session'),
        
        # Header
        create_header(),
        
        # Role-based content container
        html.Div(id="role-based-content", className="role-content-container"),
        
        # Footer
        html.Footer([
            html.P("MSA Dashboard © 2024 - Military Situational Awareness System", 
                   className="footer-text")
        ], className="dashboard-footer"),
        
        # Data stores
        dcc.Store(id='units-data-store'),
        dcc.Store(id='health-data-store'),
        dcc.Store(id='weather-data-store'),
        dcc.Store(id='threats-data-store'),
        dcc.Store(id='alerts-data-store'),
        dcc.Store(id='missions-data-store'),
        
        # Hidden divs for storing data
        html.Div(id="units-data", style={"display": "none"}),
        html.Div(id="health-data", style={"display": "none"}),
        html.Div(id="alerts-data", style={"display": "none"}),
        html.Div(id="missions-data", style={"display": "none"}),
        html.Div(id="logistics-data", style={"display": "none"}),
        html.Div(id="current-role", children="commander", style={"display": "none"}),
        
        # Refresh interval
        dcc.Interval(
            id='data-refresh-interval',
            interval=5000,  # 5 seconds
            n_intervals=0
        )
        
    ], className="dashboard-container")


def create_login_modal():
    """Create authentication modal"""
    return dbc.Modal([
        dbc.ModalHeader(dbc.ModalTitle("MSA Dashboard - Authentication")),
        dbc.ModalBody([
            dbc.Row([
                dbc.Col([
                    html.H5("Login to Military Situational Awareness Dashboard", className="text-center mb-4"),
                    dbc.InputGroup([
                        dbc.InputGroupText("👤"),
                        dbc.Input(
                            id="username-input",
                            placeholder="Username",
                            type="text",
                            value=""
                        )
                    ], className="mb-3"),
                    dbc.InputGroup([
                        dbc.InputGroupText("🔒"),
                        dbc.Input(
                            id="password-input",
                            placeholder="Password",
                            type="password",
                            value=""
                        )
                    ], className="mb-3"),
                    html.Div(id="login-error", className="text-danger mb-3"),
                    dbc.Button(
                        "Login",
                        id="login-button",
                        color="primary",
                        className="w-100 mb-3"
                    ),
                    html.Hr(),
                    html.Small([
                        "Demo Credentials:",
                        html.Br(),
                        "Commander: admin/admin123",
                        html.Br(),
                        "Health Officer: health/health123",
                        html.Br(),
                        "Operations Analyst: ops/ops123"
                    ], className="text-muted")
                ], width=12)
            ])
        ])
    ], id="login-modal", is_open=True, backdrop="static", keyboard=False)


# Helper functions for creating chart components
def create_gauge_chart(value, title, color_threshold=None):
    """Create a gauge chart for metrics"""
    if color_threshold is None:
        color_threshold = {"low": 30, "medium": 70}
    
    # Determine color based on value
    if value < color_threshold["low"]:
        color = RISK_COLORS["red"]
    elif value < color_threshold["medium"]:
        color = RISK_COLORS["amber"]
    else:
        color = RISK_COLORS["green"]
    
    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=value,
        domain={"x": [0, 1], "y": [0, 1]},
        title={"text": title},
        gauge={
            "axis": {"range": [None, 100]},
            "bar": {"color": color},
            "steps": [
                {"range": [0, color_threshold["low"]], "color": "lightgray"},
                {"range": [color_threshold["low"], color_threshold["medium"]], "color": "gray"}
            ],
            "threshold": {
                "line": {"color": "red", "width": 4},
                "thickness": 0.75,
                "value": 90
            }
        }
    ))
    
    fig.update_layout(
        height=200,
        margin=dict(l=20, r=20, t=40, b=20),
        font={"color": "white", "family": "Arial"}
    )
    
    return fig


def create_time_series_chart(data, title, y_axis_title):
    """Create a time series chart"""
    fig = go.Figure()
    
    if data:
        fig.add_trace(go.Scatter(
            x=[d["timestamp"] for d in data],
            y=[d["value"] for d in data],
            mode="lines+markers",
            name=title,
            line=dict(color=RISK_COLORS["green"], width=2)
        ))
    
    fig.update_layout(
        title=title,
        xaxis_title="Time",
        yaxis_title=y_axis_title,
        height=300,
        margin=dict(l=40, r=20, t=40, b=40),
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font={"color": "white"}
    )
    
    return fig