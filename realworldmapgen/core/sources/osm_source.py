"""
OpenStreetMap Data Source
Free vector data (roads, buildings, land use)
"""

from typing import Optional, Dict, Any
import numpy as np

try:
    import osmnx as ox
    import geopandas as gpd

    OSMNX_AVAILABLE = True
except ImportError:
    OSMNX_AVAILABLE = False

from .base import (
    BaseDataSource,
    DataSourceType,
    DataSourceCapability,
    BoundingBox,
    DataSourceConfig,
)


class OSMSource(BaseDataSource):
    """
    OpenStreetMap data source.

    Provides:
    - Road networks with detailed attributes
    - Building footprints
    - Land use polygons
    - Points of interest

    Free and open source, no API key required.
    """

    def __init__(self, config: DataSourceConfig):
        super().__init__(config)
        if OSMNX_AVAILABLE:
            # Configure osmnx settings
            ox.settings.use_cache = config.cache_enabled
            ox.settings.timeout = config.timeout

    @property
    def name(self) -> str:
        return "OpenStreetMap"

    @property
    def source_type(self) -> DataSourceType:
        return DataSourceType.VECTOR

    @property
    def capabilities(self) -> list[DataSourceCapability]:
        return [
            DataSourceCapability.VECTOR_ROADS,
            DataSourceCapability.VECTOR_BUILDINGS,
            DataSourceCapability.VECTOR_LANDUSE,
            DataSourceCapability.VECTOR_POI,
        ]

    async def is_available(self) -> bool:
        """OSM is always available (no API key needed)"""
        if not OSMNX_AVAILABLE:
            return False
        return self.config.enabled

    async def get_elevation_data(
        self,
        bbox: BoundingBox,
        resolution: int,
        dem_type: str = "dem",
    ) -> Optional[np.ndarray]:
        """OpenStreetMap does not provide elevation data"""
        return None

    async def get_imagery_data(
        self,
        bbox: BoundingBox,
        resolution: int,
        bands: list[str] = None,
    ) -> Optional[np.ndarray]:
        """OpenStreetMap does not provide imagery data"""
        return None

    async def get_vector_data(
        self,
        bbox: BoundingBox,
        feature_types: list[str] = None,
    ) -> Optional[Dict[str, Any]]:
        """
        Retrieve vector data from OpenStreetMap.

        Args:
            bbox: Geographic bounding box
            feature_types: Types of features to retrieve
                Options: 'roads', 'buildings', 'landuse', 'poi'

        Returns:
            GeoJSON-like dictionary with features
        """
        if not await self.is_available():
            return None

        feature_types = feature_types or ["roads", "buildings"]
        cache_key = self._get_cache_key(
            bbox, "vector", feature_types="_".join(feature_types)
        )
        cached = self._get_cached(cache_key)
        if cached is not None:
            return cached

        try:
            result = {"type": "FeatureCollection", "features": []}

            # Convert bbox to format for osmnx
            north, south, east, west = bbox.north, bbox.south, bbox.east, bbox.west

            # Retrieve roads
            if "roads" in feature_types:
                try:
                    G = ox.graph_from_bbox(
                        north, south, east, west, network_type="all", simplify=True
                    )
                    # Convert graph to GeoDataFrame
                    edges = ox.graph_to_gdfs(G, nodes=False, edges=True)

                    for idx, row in edges.iterrows():
                        feature = {
                            "type": "Feature",
                            "geometry": row.geometry.__geo_interface__,
                            "properties": {
                                "type": "road",
                                "highway": row.get("highway", ""),
                                "name": row.get("name", ""),
                                "lanes": row.get("lanes", ""),
                                "maxspeed": row.get("maxspeed", ""),
                                "surface": row.get("surface", ""),
                                "width": row.get("width", ""),
                            },
                        }
                        result["features"].append(feature)
                except Exception as e:
                    print(f"OSM roads retrieval failed: {e}")

            # Retrieve buildings
            if "buildings" in feature_types:
                try:
                    tags = {"building": True}
                    buildings = ox.features_from_bbox(north, south, east, west, tags)

                    for idx, row in buildings.iterrows():
                        feature = {
                            "type": "Feature",
                            "geometry": row.geometry.__geo_interface__,
                            "properties": {
                                "type": "building",
                                "building": row.get("building", ""),
                                "name": row.get("name", ""),
                                "height": row.get("height", ""),
                                "levels": row.get("building:levels", ""),
                            },
                        }
                        result["features"].append(feature)
                except Exception as e:
                    print(f"OSM buildings retrieval failed: {e}")

            # Retrieve land use
            if "landuse" in feature_types:
                try:
                    tags = {"landuse": True}
                    landuse = ox.features_from_bbox(north, south, east, west, tags)

                    for idx, row in landuse.iterrows():
                        feature = {
                            "type": "Feature",
                            "geometry": row.geometry.__geo_interface__,
                            "properties": {
                                "type": "landuse",
                                "landuse": row.get("landuse", ""),
                                "name": row.get("name", ""),
                            },
                        }
                        result["features"].append(feature)
                except Exception as e:
                    print(f"OSM landuse retrieval failed: {e}")

            # Retrieve POI
            if "poi" in feature_types:
                try:
                    tags = {"amenity": True, "shop": True, "tourism": True}
                    poi = ox.features_from_bbox(north, south, east, west, tags)

                    for idx, row in poi.iterrows():
                        feature = {
                            "type": "Feature",
                            "geometry": row.geometry.__geo_interface__,
                            "properties": {
                                "type": "poi",
                                "amenity": row.get("amenity", ""),
                                "shop": row.get("shop", ""),
                                "tourism": row.get("tourism", ""),
                                "name": row.get("name", ""),
                            },
                        }
                        result["features"].append(feature)
                except Exception as e:
                    print(f"OSM POI retrieval failed: {e}")

            self._set_cached(cache_key, result)
            return result

        except Exception as e:
            print(f"OSM vector data retrieval failed: {e}")
            return None

