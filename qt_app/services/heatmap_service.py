"""
Heatmap Service - Generates threat density heatmaps and route data
"""

import random
import math
from datetime import datetime, timedelta
from typing import List, Dict, Tuple, Any
from dataclasses import dataclass


@dataclass
class HeatmapPoint:
    """Represents a point in the heatmap with coordinates and intensity"""
    lat: float
    lng: float
    intensity: float
    
    def to_list(self) -> List[float]:
        """Convert to list format for Leaflet.heat"""
        return [self.lat, self.lng, self.intensity]


@dataclass
class RoutePoint:
    """Represents a point in a route"""
    lat: float
    lng: float
    timestamp: datetime = None
    
    def to_list(self) -> List[float]:
        """Convert to list format for Leaflet polyline"""
        return [self.lat, self.lng]


@dataclass
class Route:
    """Represents a complete route with styling"""
    coordinates: List[List[float]]
    color: str = '#007acc'
    weight: int = 3
    opacity: float = 0.7
    dashed: bool = False
    popup: str = None
    tooltip: str = None
    unit_id: str = None
    route_type: str = 'movement'  # movement, patrol, mission


@dataclass
class ThreatZone:
    """Represents a threat zone"""
    zone_type: str  # 'circle' or 'polygon'
    coordinates: List[List[float]] = None  # For polygon
    lat: float = None  # For circle
    lng: float = None  # For circle
    radius: float = None  # For circle
    color: str = '#ff0000'
    fillColor: str = None
    fillOpacity: float = 0.3
    popup: str = None
    tooltip: str = None
    threat_level: str = 'medium'  # low, medium, high, critical


class HeatmapService:
    """Service for generating heatmap and route visualization data"""
    
    def __init__(self):
        self.ankara_center = (39.9334, 32.8597)
        self.threat_history = []
        self.unit_routes = {}
        
    def generate_threat_heatmap(self, alerts_data: List[Dict], time_window_hours: int = 24) -> List[List[float]]:
        """Generate heatmap data from alerts and threat intelligence"""
        heatmap_points = []
        
        # Current time for filtering
        current_time = datetime.now()
        cutoff_time = current_time - timedelta(hours=time_window_hours)
        
        # Process alerts data
        for alert in alerts_data:
            try:
                # Get coordinates
                lat = float(alert.get('lat', 0))
                lng = float(alert.get('lng', 0))
                
                if lat == 0 or lng == 0:
                    continue
                
                # Calculate intensity based on severity and recency
                severity = alert.get('severity', 'medium').lower()
                intensity_map = {
                    'low': 0.3,
                    'medium': 0.6,
                    'high': 0.8,
                    'critical': 1.0
                }
                base_intensity = intensity_map.get(severity, 0.5)
                
                # Add time decay factor
                alert_time = datetime.fromisoformat(alert.get('timestamp', current_time.isoformat()))
                if alert_time >= cutoff_time:
                    time_factor = 1.0 - ((current_time - alert_time).total_seconds() / (time_window_hours * 3600))
                    intensity = base_intensity * max(0.1, time_factor)
                    
                    heatmap_points.append([lat, lng, intensity])
                
            except (ValueError, TypeError) as e:
                print(f"Error processing alert for heatmap: {e}")
                continue
        
        # Add simulated threat intelligence points
        heatmap_points.extend(self._generate_simulated_threats())
        
        return heatmap_points
    
    def _generate_simulated_threats(self) -> List[List[float]]:
        """Generate simulated threat points for demonstration"""
        threats = []
        
        # High-risk areas around Ankara
        high_risk_zones = [
            (39.9500, 32.8800, 0.9),  # North area
            (39.9100, 32.8400, 0.8),  # South area
            (39.9400, 32.9000, 0.7),  # East area
            (39.9200, 32.8200, 0.6),  # West area
        ]
        
        for base_lat, base_lng, base_intensity in high_risk_zones:
            # Add multiple points around each high-risk zone
            for _ in range(random.randint(3, 8)):
                # Random offset within ~2km radius
                lat_offset = random.uniform(-0.02, 0.02)
                lng_offset = random.uniform(-0.02, 0.02)
                
                lat = base_lat + lat_offset
                lng = base_lng + lng_offset
                intensity = base_intensity * random.uniform(0.5, 1.0)
                
                threats.append([lat, lng, intensity])
        
        return threats
    
    def generate_unit_routes(self, units_data: List[Dict]) -> List[Route]:
        """Generate route data for unit movements"""
        routes = []
        
        for unit in units_data:
            unit_id = unit.get('id', '')
            unit_type = unit.get('type', 'infantry')
            current_lat = float(unit.get('lat', 0))
            current_lng = float(unit.get('lng', 0))
            
            if current_lat == 0 or current_lng == 0:
                continue
            
            # Generate route based on unit type and mission
            route = self._generate_unit_route(unit_id, unit_type, current_lat, current_lng)
            if route:
                routes.append(route)
        
        return routes
    
    def _generate_unit_route(self, unit_id: str, unit_type: str, current_lat: float, current_lng: float) -> Route:
        """Generate a route for a specific unit"""
        # Route colors by unit type
        color_map = {
            'infantry': '#00ff00',
            'armor': '#ff8800',
            'air': '#0088ff',
            'naval': '#0044aa',
            'special': '#ff0088'
        }
        
        color = color_map.get(unit_type, '#007acc')
        
        # Generate waypoints for the route
        waypoints = [[current_lat, current_lng]]
        
        # Add 3-5 waypoints for patrol/mission route
        num_waypoints = random.randint(3, 5)
        
        for i in range(num_waypoints):
            # Generate next waypoint within reasonable distance
            if unit_type == 'air':
                # Air units can move further
                lat_offset = random.uniform(-0.05, 0.05)
                lng_offset = random.uniform(-0.05, 0.05)
            else:
                # Ground units move shorter distances
                lat_offset = random.uniform(-0.02, 0.02)
                lng_offset = random.uniform(-0.02, 0.02)
            
            next_lat = current_lat + lat_offset
            next_lng = current_lng + lng_offset
            waypoints.append([next_lat, next_lng])
            
            # Update current position for next waypoint
            current_lat, current_lng = next_lat, next_lng
        
        # Create route object
        route = Route(
            coordinates=waypoints,
            color=color,
            weight=3 if unit_type != 'air' else 2,
            opacity=0.7,
            dashed=unit_type == 'special',
            popup=f"Unit {unit_id} - {unit_type.title()} Route",
            tooltip=f"{unit_type.title()} Unit {unit_id}",
            unit_id=unit_id,
            route_type='patrol'
        )
        
        return route
    
    def generate_threat_zones(self) -> List[ThreatZone]:
        """Generate threat zones for the map"""
        zones = []
        
        # Critical threat zones (circles)
        critical_zones = [
            (39.9600, 32.8900, 1500, 'critical'),  # North critical zone
            (39.9000, 32.8300, 1200, 'high'),      # South high-risk zone
        ]
        
        for lat, lng, radius, threat_level in critical_zones:
            color_map = {
                'low': '#ffff00',
                'medium': '#ff8800',
                'high': '#ff4400',
                'critical': '#ff0000'
            }
            
            zone = ThreatZone(
                zone_type='circle',
                lat=lat,
                lng=lng,
                radius=radius,
                color=color_map[threat_level],
                fillColor=color_map[threat_level],
                fillOpacity=0.2 if threat_level == 'critical' else 0.15,
                popup=f"{threat_level.title()} Threat Zone",
                tooltip=f"{threat_level.title()} Risk Area",
                threat_level=threat_level
            )
            zones.append(zone)
        
        # Polygon threat zones
        polygon_zone = ThreatZone(
            zone_type='polygon',
            coordinates=[
                [39.9450, 32.8750],
                [39.9480, 32.8800],
                [39.9460, 32.8850],
                [39.9420, 32.8820],
                [39.9430, 32.8770]
            ],
            color='#ff6600',
            fillColor='#ff6600',
            fillOpacity=0.25,
            popup="Restricted Airspace",
            tooltip="No-Fly Zone",
            threat_level='medium'
        )
        zones.append(polygon_zone)
        
        return zones
    
    def update_threat_history(self, new_threats: List[Dict]):
        """Update threat history for better heatmap generation"""
        current_time = datetime.now()
        
        # Add new threats to history
        for threat in new_threats:
            threat['timestamp'] = current_time
            self.threat_history.append(threat)
        
        # Clean old threats (older than 7 days)
        cutoff_time = current_time - timedelta(days=7)
        self.threat_history = [
            threat for threat in self.threat_history 
            if threat.get('timestamp', current_time) >= cutoff_time
        ]
    
    def get_heatmap_statistics(self, heatmap_data: List[List[float]]) -> Dict[str, Any]:
        """Get statistics about the current heatmap"""
        if not heatmap_data:
            return {
                'total_points': 0,
                'max_intensity': 0,
                'avg_intensity': 0,
                'high_risk_points': 0
            }
        
        intensities = [point[2] for point in heatmap_data]
        
        return {
            'total_points': len(heatmap_data),
            'max_intensity': max(intensities),
            'avg_intensity': sum(intensities) / len(intensities),
            'high_risk_points': len([i for i in intensities if i >= 0.7])
        }


# Global service instance
_heatmap_service = None

def get_heatmap_service() -> HeatmapService:
    """Get the global heatmap service instance"""
    global _heatmap_service
    if _heatmap_service is None:
        _heatmap_service = HeatmapService()
    return _heatmap_service