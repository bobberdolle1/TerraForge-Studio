"""
AI-optimized traffic route generation
"""

import logging
from typing import List, Dict, Any, Optional
import networkx as nx
import numpy as np

from ..models import RoadSegment, TrafficRoute
from ..ai import OllamaClient

logger = logging.getLogger(__name__)


class TrafficGenerator:
    """Generate traffic routes using AI optimization"""
    
    def __init__(self, ollama_client: Optional[OllamaClient] = None):
        self.ollama = ollama_client or OllamaClient()
    
    async def generate_traffic_routes(
        self,
        roads: List[RoadSegment],
        ai_analysis: Optional[Dict[str, Any]] = None
    ) -> List[TrafficRoute]:
        """
        Generate optimized traffic routes
        
        Args:
            roads: List of road segments
            ai_analysis: AI terrain analysis results
            
        Returns:
            List of traffic routes
        """
        logger.info(f"Generating traffic routes for {len(roads)} road segments")
        
        if not roads:
            return []
        
        # Build road network graph
        G = self._build_road_graph(roads)
        
        # Identify key nodes (intersections, highway entrances, etc.)
        key_nodes = self._identify_key_nodes(G, roads)
        
        # Generate routes between key nodes
        routes = []
        
        if ai_analysis and self.ollama:
            # Use AI to optimize route selection
            routes = await self._ai_optimized_routes(G, key_nodes, roads, ai_analysis)
        else:
            # Use heuristic-based route generation
            routes = self._heuristic_routes(G, key_nodes, roads)
        
        logger.info(f"Generated {len(routes)} traffic routes")
        return routes
    
    def _build_road_graph(self, roads: List[RoadSegment]) -> nx.Graph:
        """Build network graph from road segments"""
        G = nx.Graph()
        
        for road in roads:
            if len(road.geometry) < 2:
                continue
            
            # Add nodes and edges
            for i in range(len(road.geometry) - 1):
                start = road.geometry[i]
                end = road.geometry[i + 1]
                
                # Calculate edge weight (distance)
                distance = self._haversine_distance(start, end)
                
                # Add edge with road properties
                G.add_edge(
                    start, end,
                    weight=distance,
                    road_type=road.road_type.value,
                    lanes=road.lanes,
                    max_speed=road.max_speed or 50,
                    road_id=road.osm_id
                )
        
        return G
    
    def _identify_key_nodes(
        self,
        G: nx.Graph,
        roads: List[RoadSegment]
    ) -> List[tuple]:
        """Identify important nodes (intersections, highway entrances)"""
        key_nodes = []
        
        # Nodes with degree > 2 are intersections
        for node in G.nodes():
            degree = G.degree(node)
            if degree > 2:  # Intersection
                key_nodes.append(node)
        
        # If too few key nodes, add some random endpoints
        if len(key_nodes) < 10:
            endpoints = [node for node in G.nodes() if G.degree(node) == 1]
            if endpoints:
                additional = min(10 - len(key_nodes), len(endpoints))
                key_nodes.extend(np.random.choice(endpoints, additional, replace=False))
        
        return key_nodes
    
    async def _ai_optimized_routes(
        self,
        G: nx.Graph,
        key_nodes: List[tuple],
        roads: List[RoadSegment],
        ai_analysis: Dict[str, Any]
    ) -> List[TrafficRoute]:
        """Use AI to optimize route selection"""
        routes = []
        
        try:
            # Prepare context for AI
            prompt = f"""
            Optimize traffic route generation for a map with the following characteristics:
            - Terrain type: {ai_analysis.get('terrain_type', 'urban')}
            - Building density: {ai_analysis.get('building_density', 0.5)}
            - Road density: {ai_analysis.get('road_density', 0.5)}
            - Number of road segments: {len(roads)}
            - Number of key intersections: {len(key_nodes)}
            
            Provide recommendations for:
            1. Number of primary traffic routes (main corridors)
            2. Number of secondary routes (local circulation)
            3. Traffic density multiplier (0.5-2.0)
            4. Preferred route characteristics (prefer highways, avoid residential, etc.)
            
            Return JSON with: primary_routes, secondary_routes, traffic_density, prefer_highways
            """
            
            ollama_available = await self.ollama.check_health()
            
            if ollama_available:
                response = await self.ollama.generate(
                    model=self.ollama.coder_model,
                    prompt=prompt,
                    format="json"
                )
                
                import json
                try:
                    optimization = json.loads(response)
                    
                    num_primary = optimization.get('primary_routes', 5)
                    num_secondary = optimization.get('secondary_routes', 10)
                    prefer_highways = optimization.get('prefer_highways', True)
                    
                    # Generate routes based on AI recommendations
                    routes.extend(
                        self._generate_routes(
                            G, key_nodes, num_primary,
                            route_type='primary',
                            prefer_highways=prefer_highways
                        )
                    )
                    routes.extend(
                        self._generate_routes(
                            G, key_nodes, num_secondary,
                            route_type='secondary',
                            prefer_highways=False
                        )
                    )
                    
                    logger.info(f"AI-optimized: {num_primary} primary, {num_secondary} secondary routes")
                    return routes
                    
                except json.JSONDecodeError:
                    logger.warning("Failed to parse AI response, using heuristics")
                    
        except Exception as e:
            logger.error(f"AI optimization failed: {e}")
        
        # Fallback to heuristic
        return self._heuristic_routes(G, key_nodes, roads)
    
    def _heuristic_routes(
        self,
        G: nx.Graph,
        key_nodes: List[tuple],
        roads: List[RoadSegment]
    ) -> List[TrafficRoute]:
        """Generate routes using heuristic methods"""
        # Generate 5 primary and 10 secondary routes
        routes = []
        routes.extend(self._generate_routes(G, key_nodes, 5, 'primary'))
        routes.extend(self._generate_routes(G, key_nodes, 10, 'secondary'))
        return routes
    
    def _generate_routes(
        self,
        G: nx.Graph,
        key_nodes: List[tuple],
        count: int,
        route_type: str = 'primary',
        prefer_highways: bool = True
    ) -> List[TrafficRoute]:
        """Generate specific number of routes"""
        routes = []
        
        if len(key_nodes) < 2:
            return routes
        
        for _ in range(count):
            # Select random start and end nodes
            start, end = np.random.choice(key_nodes, 2, replace=False)
            
            try:
                # Find shortest path
                if prefer_highways:
                    # Prefer highways by modifying edge weights
                    path = nx.shortest_path(G, start, end, weight='weight')
                else:
                    path = nx.shortest_path(G, start, end)
                
                if len(path) > 1:
                    # Calculate route properties
                    total_distance = sum(
                        G[path[i]][path[i+1]]['weight']
                        for i in range(len(path) - 1)
                    )
                    
                    avg_speed = np.mean([
                        G[path[i]][path[i+1]].get('max_speed', 50)
                        for i in range(len(path) - 1)
                    ])
                    
                    routes.append(TrafficRoute(
                        waypoints=path,
                        route_type=route_type,
                        total_distance=total_distance,
                        avg_speed=avg_speed,
                        priority=1.0 if route_type == 'primary' else 0.5
                    ))
                    
            except nx.NetworkXNoPath:
                continue
        
        return routes
    
    def _haversine_distance(
        self,
        coord1: tuple,
        coord2: tuple
    ) -> float:
        """Calculate distance between two coordinates in meters"""
        lat1, lon1 = coord1
        lat2, lon2 = coord2
        
        R = 6371000  # Earth radius in meters
        
        phi1 = np.radians(lat1)
        phi2 = np.radians(lat2)
        delta_phi = np.radians(lat2 - lat1)
        delta_lambda = np.radians(lon2 - lon1)
        
        a = np.sin(delta_phi/2)**2 + np.cos(phi1) * np.cos(phi2) * np.sin(delta_lambda/2)**2
        c = 2 * np.arctan2(np.sqrt(a), np.sqrt(1-a))
        
        return R * c
