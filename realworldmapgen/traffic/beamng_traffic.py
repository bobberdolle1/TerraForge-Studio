"""
BeamNG.drive specific traffic system generation
"""

import logging
from typing import List, Dict, Any
import json
from pathlib import Path

from ..models import TrafficRoute, TrafficLight, ParkingLot

logger = logging.getLogger(__name__)


class BeamNGTrafficSystem:
    """Generate BeamNG.drive traffic system"""
    
    def __init__(self):
        pass
    
    def export_traffic_system(
        self,
        routes: List[TrafficRoute],
        traffic_lights: List[TrafficLight],
        parking_lots: List[ParkingLot],
        output_path: Path
    ) -> Path:
        """
        Export complete traffic system for BeamNG.drive
        
        Args:
            routes: Traffic routes
            traffic_lights: Traffic light placements
            parking_lots: Parking lot areas
            output_path: Output file path
            
        Returns:
            Path to exported file
        """
        logger.info("Exporting BeamNG traffic system")
        
        traffic_data = {
            "version": 2,
            "traffic": {
                "enabled": True,
                "density": 0.5,
                "routes": self._export_routes(routes),
                "spawnPoints": self._generate_spawn_points(routes),
                "aiSettings": {
                    "aggressiveness": 0.5,
                    "speedVariation": 0.2,
                    "laneChangeFrequency": 0.3,
                    "obeyTrafficLights": True
                }
            },
            "trafficLights": self._export_traffic_lights(traffic_lights),
            "parking": self._export_parking(parking_lots)
        }
        
        with open(output_path, 'w') as f:
            json.dump(traffic_data, f, indent=2)
        
        logger.info(f"Traffic system exported to {output_path}")
        return output_path
    
    def _export_routes(self, routes: List[TrafficRoute]) -> List[Dict[str, Any]]:
        """Export traffic routes"""
        exported = []
        
        for i, route in enumerate(routes):
            exported.append({
                "id": f"route_{i}",
                "waypoints": [
                    {"lat": lat, "lon": lon}
                    for lat, lon in route.waypoints
                ],
                "type": route.route_type,
                "priority": route.priority,
                "avgSpeed": route.avg_speed,
                "totalDistance": route.total_distance
            })
        
        return exported
    
    def _generate_spawn_points(
        self,
        routes: List[TrafficRoute],
        points_per_route: int = 3
    ) -> List[Dict[str, Any]]:
        """Generate vehicle spawn points from routes"""
        spawn_points = []
        
        for i, route in enumerate(routes):
            if len(route.waypoints) < points_per_route:
                continue
            
            # Distribute spawn points along route
            step = len(route.waypoints) // points_per_route
            
            for j in range(points_per_route):
                idx = min(j * step, len(route.waypoints) - 1)
                lat, lon = route.waypoints[idx]
                
                spawn_points.append({
                    "id": f"spawn_{i}_{j}",
                    "position": {"lat": lat, "lon": lon},
                    "routeId": f"route_{i}",
                    "vehicleType": self._select_vehicle_type(route.route_type),
                    "spawnProbability": 0.7
                })
        
        return spawn_points
    
    def _export_traffic_lights(
        self,
        traffic_lights: List[TrafficLight]
    ) -> List[Dict[str, Any]]:
        """Export traffic lights"""
        exported = []
        
        for i, light in enumerate(traffic_lights):
            exported.append({
                "id": light.osm_id or f"light_{i}",
                "position": {
                    "lat": light.position[0],
                    "lon": light.position[1]
                },
                "direction": light.direction or 0,
                "cycleTime": 30.0,
                "phases": [
                    {"duration": 15, "state": "green"},
                    {"duration": 3, "state": "yellow"},
                    {"duration": 15, "state": "red"},
                    {"duration": 3, "state": "yellow"}
                ]
            })
        
        return exported
    
    def _export_parking(
        self,
        parking_lots: List[ParkingLot]
    ) -> List[Dict[str, Any]]:
        """Export parking lots"""
        exported = []
        
        for lot in parking_lots:
            # Calculate center
            lats = [coord[0] for coord in lot.geometry]
            lons = [coord[1] for coord in lot.geometry]
            center_lat = sum(lats) / len(lats)
            center_lon = sum(lons) / len(lons)
            
            exported.append({
                "id": lot.osm_id,
                "center": {
                    "lat": center_lat,
                    "lon": center_lon
                },
                "boundary": [
                    {"lat": lat, "lon": lon}
                    for lat, lon in lot.geometry
                ],
                "capacity": lot.capacity or 20,
                "type": lot.parking_type,
                "surface": lot.surface or "asphalt",
                "parkingSpots": self._generate_parking_spots(lot)
            })
        
        return exported
    
    def _generate_parking_spots(
        self,
        parking_lot: ParkingLot
    ) -> List[Dict[str, Any]]:
        """Generate individual parking spots within a lot"""
        # Simple grid-based parking spot generation
        # In production, this would be more sophisticated
        
        capacity = parking_lot.capacity or 20
        spots = []
        
        # Use lot center for simplicity
        lats = [coord[0] for coord in parking_lot.geometry]
        lons = [coord[1] for coord in parking_lot.geometry]
        center_lat = sum(lats) / len(lats)
        center_lon = sum(lons) / len(lons)
        
        # Create spots in a grid around center
        import math
        rows = int(math.sqrt(capacity))
        cols = capacity // rows
        
        offset = 0.00002  # Roughly 2 meters
        
        for row in range(rows):
            for col in range(cols):
                spot_lat = center_lat + (row - rows/2) * offset
                spot_lon = center_lon + (col - cols/2) * offset
                
                spots.append({
                    "position": {"lat": spot_lat, "lon": spot_lon},
                    "rotation": 0,
                    "occupied": False
                })
        
        return spots
    
    def _select_vehicle_type(self, route_type: str) -> str:
        """Select appropriate vehicle type for route"""
        vehicle_map = {
            "primary": "sedan",
            "secondary": "sedan",
            "local": "sedan"
        }
        return vehicle_map.get(route_type, "sedan")
