"""
BeamNG.drive traffic system integration
"""

import logging
from typing import List, Dict, Any, Optional
import math

from ..models import RoadSegment, TrafficRoute
from ..ai import OllamaClient

logger = logging.getLogger(__name__)


class BeamNGTrafficIntegrator:
    """Integrate traffic routes with BeamNG.drive traffic system"""
    
    def __init__(self, ollama_client: Optional[OllamaClient] = None):
        self.ollama = ollama_client or OllamaClient()
    
    async def generate_traffic_config(
        self,
        roads: List[RoadSegment],
        traffic_routes: List[TrafficRoute],
        ai_analysis: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Generate complete BeamNG.drive traffic configuration
        
        Args:
            roads: Road network
            traffic_routes: Generated traffic routes
            ai_analysis: Optional AI terrain analysis
            
        Returns:
            BeamNG traffic config dictionary
        """
        logger.info("Generating BeamNG.drive traffic configuration")
        
        # Determine traffic density based on terrain type
        traffic_density = self._calculate_traffic_density(ai_analysis)
        
        # Generate spawn points
        spawn_points = self._generate_spawn_points(roads, traffic_routes)
        
        # Generate AI vehicle behaviors
        ai_behaviors = await self._generate_ai_behaviors(traffic_routes, ai_analysis)
        
        # Traffic groups (different vehicle types)
        traffic_groups = self._create_traffic_groups(traffic_density)
        
        # Traffic signals timing
        signal_timings = self._generate_signal_timings(ai_analysis)
        
        return {
            "version": "1.0",
            "traffic_density": traffic_density,
            "spawn_points": spawn_points,
            "ai_behaviors": ai_behaviors,
            "traffic_groups": traffic_groups,
            "signal_timings": signal_timings,
            "routes": [self._route_to_beamng(route, i) for i, route in enumerate(traffic_routes)]
        }
    
    def _calculate_traffic_density(
        self,
        ai_analysis: Optional[Dict[str, Any]]
    ) -> float:
        """Calculate appropriate traffic density"""
        if not ai_analysis:
            return 0.5
        
        terrain_type = ai_analysis.get('terrain_type', 'mixed')
        road_density = ai_analysis.get('road_density', 0.5)
        building_density = ai_analysis.get('building_density', 0.5)
        
        # Urban areas have higher traffic
        if terrain_type == 'urban':
            return min(0.9, road_density * 1.2)
        elif terrain_type == 'suburban':
            return min(0.7, road_density * 1.0)
        elif terrain_type == 'rural':
            return min(0.3, road_density * 0.5)
        else:
            return 0.5
    
    def _generate_spawn_points(
        self,
        roads: List[RoadSegment],
        routes: List[TrafficRoute]
    ) -> List[Dict[str, Any]]:
        """Generate vehicle spawn points along routes"""
        spawn_points = []
        
        for i, route in enumerate(routes):
            if len(route.waypoints) < 2:
                continue
            
            # More spawns for primary routes
            spawn_count = 3 if route.route_type == 'primary' else 1
            
            for j in range(spawn_count):
                spawn_points.append({
                    "id": f"spawn_{i}_{j}",
                    "position": list(route.waypoints[0]),
                    "direction": self._calculate_direction(
                        route.waypoints[0],
                        route.waypoints[1]
                    ),
                    "route_id": f"route_{i}",
                    "spawn_probability": route.priority,
                    "vehicle_types": ["sedan", "hatchback", "suv"]
                })
        
        logger.info(f"Generated {len(spawn_points)} spawn points")
        return spawn_points
    
    async def _generate_ai_behaviors(
        self,
        routes: List[TrafficRoute],
        ai_analysis: Optional[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Generate AI driving behaviors using Qwen3-Coder"""
        
        # Default behaviors for different scenarios
        default_behaviors = [
            {
                "name": "city_driver",
                "description": "Cautious urban driving",
                "aggression": 0.3,
                "speed_multiplier": 0.9,
                "lane_change_frequency": 0.5,
                "follow_distance_meters": 3.0,
                "obey_traffic_lights": True
            },
            {
                "name": "highway_driver",
                "description": "Fast highway cruising",
                "aggression": 0.5,
                "speed_multiplier": 1.0,
                "lane_change_frequency": 0.7,
                "follow_distance_meters": 5.0,
                "obey_traffic_lights": True
            },
            {
                "name": "careful_driver",
                "description": "Very cautious defensive driving",
                "aggression": 0.1,
                "speed_multiplier": 0.7,
                "lane_change_frequency": 0.2,
                "follow_distance_meters": 6.0,
                "obey_traffic_lights": True
            },
            {
                "name": "aggressive_driver",
                "description": "Fast and assertive",
                "aggression": 0.8,
                "speed_multiplier": 1.15,
                "lane_change_frequency": 0.9,
                "follow_distance_meters": 2.5,
                "obey_traffic_lights": False
            }
        ]
        
        # Try to optimize with AI
        if ai_analysis and self.ollama:
            try:
                ollama_available = await self.ollama.check_health()
                if ollama_available:
                    prompt = f"""
                    Optimize AI driver behaviors for BeamNG.drive traffic simulation.
                    
                    Context:
                    - Terrain: {ai_analysis.get('terrain_type', 'mixed')}
                    - Road density: {ai_analysis.get('road_density', 0.5)}
                    - Building density: {ai_analysis.get('building_density', 0.5)}
                    - Routes: {len(routes)} ({sum(1 for r in routes if r.route_type == 'primary')} primary)
                    
                    Generate 4-6 behavior profiles optimized for this environment.
                    Each behavior should have:
                    - name: string
                    - description: string
                    - aggression: 0.0-1.0 (low=cautious, high=aggressive)
                    - speed_multiplier: 0.5-1.3
                    - lane_change_frequency: 0.0-1.0
                    - follow_distance_meters: 2.0-10.0
                    - obey_traffic_lights: boolean
                    
                    Return JSON array.
                    """
                    
                    response = await self.ollama.generate(
                        model=self.ollama.coder_model,
                        prompt=prompt,
                        format="json"
                    )
                    
                    import json
                    behaviors = json.loads(response)
                    logger.info(f"AI-optimized {len(behaviors)} traffic behaviors")
                    return behaviors
                    
            except Exception as e:
                logger.warning(f"AI behavior generation failed: {e}")
        
        return default_behaviors
    
    def _create_traffic_groups(
        self,
        density: float
    ) -> List[Dict[str, Any]]:
        """Create traffic groups with vehicle types and spawning rules"""
        return [
            {
                "name": "passenger_cars",
                "vehicles": ["sedan", "hatchback", "coupe", "suv"],
                "weight": 0.65,
                "density_multiplier": density,
                "preferred_routes": ["primary", "secondary"]
            },
            {
                "name": "commercial",
                "vehicles": ["van", "pickup", "delivery"],
                "weight": 0.25,
                "density_multiplier": density * 0.6,
                "preferred_routes": ["primary", "secondary", "service"]
            },
            {
                "name": "heavy",
                "vehicles": ["truck", "semi"],
                "weight": 0.10,
                "density_multiplier": density * 0.4,
                "preferred_routes": ["primary"]
            }
        ]
    
    def _generate_signal_timings(
        self,
        ai_analysis: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Generate traffic light timing configurations"""
        # Adjust timings based on traffic density
        base_green = 30  # seconds
        base_yellow = 3
        
        if ai_analysis:
            density = ai_analysis.get('road_density', 0.5)
            # Higher density = longer green times
            base_green = int(30 + (density * 20))
        
        return {
            "default_cycle": {
                "green_time": base_green,
                "yellow_time": base_yellow,
                "red_time": 2,
                "all_red_time": 1
            },
            "pedestrian_crossing": {
                "walk_time": 15,
                "clearance_time": 10
            }
        }
    
    def _route_to_beamng(
        self,
        route: TrafficRoute,
        route_id: int
    ) -> Dict[str, Any]:
        """Convert TrafficRoute to BeamNG format"""
        return {
            "id": f"route_{route_id}",
            "type": route.route_type,
            "waypoints": [
                {
                    "position": list(wp),
                    "speed_limit": route.avg_speed
                }
                for wp in route.waypoints
            ],
            "priority": route.priority,
            "distance_meters": route.total_distance,
            "allow_vehicles": ["all"] if route.route_type == "primary" else ["light", "medium"]
        }
    
    def _calculate_direction(
        self,
        point1: tuple,
        point2: tuple
    ) -> float:
        """Calculate heading direction between two points in degrees"""
        dx = point2[1] - point1[1]  # longitude
        dy = point2[0] - point1[0]  # latitude
        return math.degrees(math.atan2(dy, dx))
