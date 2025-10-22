"""
OpenStreetMap data extraction using direct Overpass API
"""

import logging
from typing import Dict, Any

from ..models import BoundingBox
from ..config import settings
from .direct_overpass import DirectOverpassClient

logger = logging.getLogger(__name__)


class OSMExtractor:
    """Extract and process OpenStreetMap data using direct Overpass API"""
    
    def __init__(self):
        # Use direct Overpass API client instead of osmnx
        self.client = DirectOverpassClient(timeout=60)
        
    def extract_all_data(
        self, 
        bbox: BoundingBox
    ) -> Dict[str, Any]:
        """
        Extract all relevant OSM data for the bounding box
        
        Args:
            bbox: Geographic bounding box
            
        Returns:
            Dictionary containing roads, buildings, traffic lights, etc.
        """
        logger.info(f"Extracting OSM data for bbox: north={bbox.north} south={bbox.south} east={bbox.east} west={bbox.west}")
        logger.info(f"Area: {bbox.area_km2():.2f} km²")
        
        import time
        start = time.time()
        
        logger.info("[1/5] Extracting roads...")
        roads = self.client.extract_roads(bbox)
        logger.info(f"[1/5] ✓ Roads extracted: {len(roads)} in {time.time()-start:.1f}s")
        
        logger.info("[2/5] Extracting buildings...")
        buildings = self.client.extract_buildings(bbox)
        logger.info(f"[2/5] ✓ Buildings extracted: {len(buildings)} in {time.time()-start:.1f}s")
        
        logger.info("[3/5] Extracting traffic lights...")
        traffic_lights = self.client.extract_traffic_lights(bbox)
        logger.info(f"[3/5] ✓ Traffic lights extracted: {len(traffic_lights)} in {time.time()-start:.1f}s")
        
        logger.info("[4/5] Extracting parking...")
        parking_lots = self.client.extract_parking(bbox)
        logger.info(f"[4/5] ✓ Parking lots extracted: {len(parking_lots)} in {time.time()-start:.1f}s")
        
        logger.info("[5/5] Extracting vegetation...")
        vegetation = self.client.extract_vegetation(bbox)
        logger.info(f"[5/5] ✓ Vegetation extracted: {len(vegetation)} in {time.time()-start:.1f}s")
        
        result = {
            "roads": roads,
            "buildings": buildings,
            "traffic_lights": traffic_lights,
            "parking_lots": parking_lots,
            "vegetation": vegetation
        }
        
        total_time = time.time() - start
        logger.info(f"✓ OSM extraction complete in {total_time:.1f}s: "
                   f"{len(result['roads'])} roads, "
                   f"{len(result['buildings'])} buildings, "
                   f"{len(result['traffic_lights'])} traffic lights, "
                   f"{len(result['parking_lots'])} parking lots, "
                   f"{len(result['vegetation'])} vegetation areas")
        
        return result
