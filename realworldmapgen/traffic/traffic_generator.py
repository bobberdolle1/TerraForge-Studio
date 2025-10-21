"""
Traffic route generation for AI vehicles
"""

import logging
from typing import List, Optional
import networkx as nx

from ..models import RoadSegment, TrafficRoute, BoundingBox

logger = logging.getLogger(__name__)


class TrafficGenerator:
    """Generate AI traffic routes from road network"""
    
    def __init__(self):
        pass
    
    def generate_traffic_routes(
        self,
        roads: List[RoadSegment],
        bbox: BoundingBox,
        num_routes: int = 10
    ) -> List[TrafficRoute]:
        """
        Generate traffic routes from road network
        
        Args:
            roads: List of road segments
            bbox: Map bounding box
            num_routes: Number of routes to generate
            
        Returns:
            List of traffic routes
        """
        logger.info(f"Generating {num_routes} traffic routes")
        
        if not roads:
            logger.warning("No roads provided for traffic generation")
            return []
        
        try:
            # Build graph from roads
            G = self._build_road_graph(roads)
            
            if len(G.nodes) < 2:
                logger.warning("Not enough nodes for traffic routes")
                return []
            
            routes = []
            nodes = list(G.nodes)
            
            # Generate routes between random pairs of nodes
            import random
            for i in range(min(num_routes, len(nodes) // 2)):
                try:
                    start = random.choice(nodes)
                    end = random.choice([n for n in nodes if n != start])
                    
                    # Find shortest path
                    path = nx.shortest_path(G, start, end, weight='length')
                    
                    # Convert path to waypoints
                    waypoints = []
                    total_distance = 0.0
                    
                    for node in path:
                        lat, lon = G.nodes[node]['pos']
                        waypoints.append((lat, lon))
                    
                    # Calculate total distance
                    for j in range(len(path) - 1):
                        u, v = path[j], path[j + 1]
                        if G.has_edge(u, v):
                            total_distance += G[u][v].get('length', 0)
                    
                    # Determine route type based on road types used
                    route_type = self._determine_route_type(G, path)
                    
                    route = TrafficRoute(
                        waypoints=waypoints,
                        route_type=route_type,
                        total_distance=total_distance,
                        avg_speed=self._estimate_avg_speed(route_type),
                        priority=0.5 + (i / num_routes) * 0.5
                    )
                    
                    routes.append(route)
                    logger.debug(f"Generated route {i+1}: {len(waypoints)} waypoints, {total_distance:.0f}m")
                    
                except (nx.NetworkXNoPath, nx.NodeNotFound) as e:
                    logger.debug(f"Could not generate route {i+1}: {e}")
                    continue
            
            logger.info(f"Successfully generated {len(routes)} traffic routes")
            return routes
            
        except Exception as e:
            logger.error(f"Error generating traffic routes: {e}")
            return []
    
    def _build_road_graph(self, roads: List[RoadSegment]) -> nx.DiGraph:
        """Build a directed graph from road segments"""
        G = nx.DiGraph()
        
        for road in roads:
            if len(road.geometry) < 2:
                continue
            
            # Add nodes and edges for each road segment
            for i in range(len(road.geometry) - 1):
                start = road.geometry[i]
                end = road.geometry[i + 1]
                
                # Add nodes
                G.add_node(start, pos=start)
                G.add_node(end, pos=end)
                
                # Calculate edge length
                length = self._haversine_distance(start[0], start[1], end[0], end[1])
                
                # Add edge
                G.add_edge(
                    start, end,
                    road_id=road.osm_id,
                    road_type=road.road_type,
                    length=length,
                    speed_limit=road.max_speed or 50
                )
                
                # Add reverse edge if not oneway
                if not road.oneway:
                    G.add_edge(
                        end, start,
                        road_id=road.osm_id,
                        road_type=road.road_type,
                        length=length,
                        speed_limit=road.max_speed or 50
                    )
        
        return G
    
    def _haversine_distance(
        self,
        lat1: float, lon1: float,
        lat2: float, lon2: float
    ) -> float:
        """Calculate distance between two coordinates in meters"""
        from math import radians, sin, cos, sqrt, atan2
        
        R = 6371000  # Earth radius in meters
        
        lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        
        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
        c = 2 * atan2(sqrt(a), sqrt(1-a))
        
        return R * c
    
    def _determine_route_type(self, G: nx.DiGraph, path: list) -> str:
        """Determine route type based on roads used"""
        road_types = []
        
        for i in range(len(path) - 1):
            u, v = path[i], path[i + 1]
            if G.has_edge(u, v):
                road_types.append(G[u][v].get('road_type'))
        
        # Count road type occurrences
        if not road_types:
            return "local"
        
        # Simple heuristic: use most common road type
        from collections import Counter
        most_common = Counter(road_types).most_common(1)[0][0]
        
        if hasattr(most_common, 'value'):
            type_str = most_common.value
        else:
            type_str = str(most_common)
        
        if type_str in ['motorway', 'trunk', 'primary']:
            return "primary"
        elif type_str in ['secondary', 'tertiary']:
            return "secondary"
        else:
            return "local"
    
    def _estimate_avg_speed(self, route_type: str) -> float:
        """Estimate average speed based on route type"""
        speed_map = {
            "primary": 80.0,
            "secondary": 60.0,
            "local": 40.0
        }
        return speed_map.get(route_type, 50.0)
