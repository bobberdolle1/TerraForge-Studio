"""
TerraForge Studio - Unified Terrain Generator
Main orchestrator for terrain generation with multi-source and multi-format support
"""

import logging
import asyncio
from typing import Optional, Dict, Any, List
from pathlib import Path
import uuid
import numpy as np

from ..models import (
    MapGenerationRequest,
    GenerationStatus,
    ExportFormat,
    ElevationSource,
    BoundingBox,
)
from ..config import settings
from .sources.base import BoundingBox as SourceBBox, DataSourceConfig
from .sources import (
    SentinelHubSource,
    OpenTopographySource,
    AzureMapsSource,
    EarthEngineSource,
    OSMSource,
)
from ..exporters.base import TerrainData
from ..exporters import (
    Unreal5HeightmapExporter,
    Unreal5WeightmapExporter,
    UnityTerrainExporter,
    GLTFExporter,
    GeoTIFFExporter,
)

logger = logging.getLogger(__name__)


class TerraForgeGenerator:
    """
    Main terrain generation orchestrator for TerraForge Studio.

    Coordinates:
    1. Data acquisition from multiple sources
    2. Terrain processing and analysis
    3. Export to multiple game engine formats
    """

    def __init__(self):
        """Initialize generator with data sources and exporters"""

        # Initialize data sources
        self.sources = self._initialize_sources()

        # Task tracking
        self.active_tasks: Dict[str, GenerationStatus] = {}

        logger.info("TerraForge Generator initialized")
        logger.info(f"Available sources: {list(self.sources.keys())}")

    def _initialize_sources(self) -> Dict[str, Any]:
        """Initialize all available data sources"""

        sources = {}

        # Sentinel Hub (Imagery)
        if getattr(settings, "sentinelhub_enabled", False):
            config = DataSourceConfig(
                enabled=True,
                api_key=getattr(settings, "sentinelhub_client_id", None),
                api_secret=getattr(settings, "sentinelhub_client_secret", None),
            )
            sources["sentinelhub"] = SentinelHubSource(config)

        # OpenTopography (High-res DEMs)
        if getattr(settings, "opentopography_enabled", False):
            config = DataSourceConfig(
                enabled=True,
                api_key=getattr(settings, "opentopography_api_key", None),
            )
            sources["opentopography"] = OpenTopographySource(config)

        # Azure Maps (Vector + Elevation)
        if getattr(settings, "azure_maps_enabled", False):
            config = DataSourceConfig(
                enabled=True,
                api_key=getattr(settings, "azure_maps_subscription_key", None),
            )
            sources["azure_maps"] = AzureMapsSource(config)

        # Google Earth Engine (Advanced analysis)
        if getattr(settings, "google_earth_engine_enabled", False):
            config = DataSourceConfig(
                enabled=True,
                custom_params={
                    "service_account": getattr(
                        settings, "google_earth_engine_service_account", None
                    ),
                    "private_key_path": getattr(
                        settings, "google_earth_engine_private_key_path", None
                    ),
                },
            )
            sources["earth_engine"] = EarthEngineSource(config)

        # OpenStreetMap (always available)
        config = DataSourceConfig(enabled=True)
        sources["osm"] = OSMSource(config)

        return sources

    async def generate_terrain(
        self, request: MapGenerationRequest, task_id: Optional[str] = None
    ) -> GenerationStatus:
        """
        Generate terrain from request.

        Args:
            request: Terrain generation request
            task_id: Optional task ID

        Returns:
            Generation status
        """
        if task_id is None:
            task_id = str(uuid.uuid4())

        # Create status tracker
        status = GenerationStatus(
            task_id=task_id, status="processing", progress=0.0, current_step="Initializing"
        )
        self.active_tasks[task_id] = status

        try:
            logger.info(f"Starting terrain generation: '{request.name}' (task: {task_id})")

            # Validate area
            area_km2 = request.bbox.area_km2()
            max_area = getattr(settings, "max_area_km2", 100.0)
            if area_km2 > max_area:
                raise ValueError(f"Area too large: {area_km2:.2f} km² (max: {max_area} km²)")

            # Convert bbox
            bbox = self._convert_bbox(request.bbox)

            # Step 1: Acquire elevation data
            status.current_step = "Acquiring elevation data"
            status.progress = 10.0
            logger.info("Step 1/6: Acquiring elevation data")

            elevation_data = await self._get_elevation_data(
                bbox, request.resolution, request.elevation_source
            )

            if elevation_data is None:
                raise ValueError("Failed to acquire elevation data from any source")

            # Step 2: Get vector data (roads, buildings)
            if request.enable_roads or request.enable_buildings:
                status.current_step = "Extracting vector features"
                status.progress = 30.0
                logger.info("Step 2/6: Extracting vector data")

                vector_data = await self._get_vector_data(bbox, request)
            else:
                vector_data = None

            # Step 3: Generate weightmaps (if enabled)
            weightmaps = None
            if request.enable_weightmaps:
                status.current_step = "Generating material weightmaps"
                status.progress = 50.0
                logger.info("Step 3/6: Generating weightmaps")

                weightmaps = await self._generate_weightmaps(elevation_data)

            # Step 4: Create terrain data structure
            status.current_step = "Preparing terrain data"
            status.progress = 60.0
            logger.info("Step 4/6: Preparing terrain data")

            terrain_data = TerrainData(
                heightmap=elevation_data,
                resolution=request.resolution,
                bbox_north=request.bbox.north,
                bbox_south=request.bbox.south,
                bbox_east=request.bbox.east,
                bbox_west=request.bbox.west,
                name=request.name,
                weightmaps=weightmaps,
                roads=vector_data.get("roads") if vector_data else None,
                buildings=vector_data.get("buildings") if vector_data else None,
            )

            # Step 5: Export to requested formats
            status.current_step = "Exporting terrain"
            status.progress = 70.0
            logger.info("Step 5/6: Exporting to formats")

            output_dir = Path(getattr(settings, "output_dir", "output")) / request.name
            output_dir.mkdir(parents=True, exist_ok=True)

            export_results = await self._export_terrain(
                terrain_data, request.export_formats, output_dir
            )

            # Step 6: Package results
            status.current_step = "Finalizing"
            status.progress = 95.0
            logger.info("Step 6/6: Finalizing")

            # Create result summary
            result = {
                "terrain_name": request.name,
                "resolution": request.resolution,
                "area_km2": area_km2,
                "elevation_range": {
                    "min": float(np.min(elevation_data)),
                    "max": float(np.max(elevation_data)),
                },
                "exports": export_results,
                "output_directory": str(output_dir),
            }

            # Mark complete
            status.status = "completed"
            status.progress = 100.0
            status.current_step = "Complete"
            status.result = result

            logger.info(f"Terrain generation completed: {request.name}")

            return status

        except Exception as e:
            logger.error(f"Terrain generation failed: {e}", exc_info=True)
            status.status = "failed"
            status.error = str(e)
            return status

    async def _get_elevation_data(
        self, bbox: SourceBBox, resolution: int, source_priority: ElevationSource
    ) -> Optional[np.ndarray]:
        """
        Acquire elevation data from best available source.

        Args:
            bbox: Bounding box
            resolution: Target resolution
            source_priority: Preferred source

        Returns:
            Elevation data array or None
        """

        # Define source priority
        if source_priority == ElevationSource.AUTO:
            # Try sources in order of quality
            priority = ["opentopography", "azure_maps", "srtm"]
        else:
            priority = [source_priority.value]

        # Try each source
        for source_name in priority:
            if source_name not in self.sources:
                continue

            source = self.sources[source_name]

            try:
                if not await source.is_available():
                    logger.info(f"Source {source_name} not available, skipping")
                    continue

                logger.info(f"Trying elevation source: {source_name}")
                elevation = await source.get_elevation_data(bbox, resolution)

                if elevation is not None:
                    logger.info(f"Successfully acquired elevation from {source_name}")
                    return elevation

            except Exception as e:
                logger.warning(f"Failed to get elevation from {source_name}: {e}")
                continue

        # Fallback: Generate synthetic terrain (for testing)
        logger.warning("All elevation sources failed, generating synthetic terrain")
        return self._generate_synthetic_terrain(resolution)

    async def _get_vector_data(
        self, bbox: SourceBBox, request: MapGenerationRequest
    ) -> Optional[Dict[str, Any]]:
        """Get vector data (roads, buildings) from OSM or Azure Maps"""

        feature_types = []
        if request.enable_roads:
            feature_types.append("roads")
        if request.enable_buildings:
            feature_types.append("buildings")

        # Try OSM first (free and always available)
        if "osm" in self.sources:
            try:
                osm = self.sources["osm"]
                vector_data = await osm.get_vector_data(bbox, feature_types)
                if vector_data:
                    return self._organize_vector_data(vector_data)
            except Exception as e:
                logger.warning(f"OSM vector data failed: {e}")

        # Try Azure Maps as fallback
        if "azure_maps" in self.sources:
            try:
                azure = self.sources["azure_maps"]
                if await azure.is_available():
                    vector_data = await azure.get_vector_data(bbox, feature_types)
                    if vector_data:
                        return self._organize_vector_data(vector_data)
            except Exception as e:
                logger.warning(f"Azure Maps vector data failed: {e}")

        return None

    async def _generate_weightmaps(
        self, elevation: np.ndarray
    ) -> Dict[str, np.ndarray]:
        """
        Generate material weightmaps from elevation and slope.

        Returns dict with keys: rock, grass, dirt, sand
        """

        # Calculate slope
        dy, dx = np.gradient(elevation)
        slope = np.degrees(np.arctan(np.sqrt(dx**2 + dy**2)))

        # Normalize height
        height_norm = (elevation - elevation.min()) / (elevation.max() - elevation.min() + 1e-6)

        # Initialize weightmaps
        rock = np.clip((slope - 30) / 30, 0, 1)  # Steep slopes
        sand = (1 - height_norm) * (1 - np.clip(slope / 15, 0, 1))  # Low + flat
        grass = (1 - np.abs(height_norm - 0.5) * 2) * (
            1 - np.clip(slope / 20, 0, 1)
        )  # Mid + gentle
        dirt = np.clip(1 - (rock + grass + sand), 0, 1)  # Fill remainder

        # Normalize
        total = rock + grass + dirt + sand
        total = np.maximum(total, 0.001)

        return {
            "rock": (rock / total).astype(np.float32),
            "grass": (grass / total).astype(np.float32),
            "dirt": (dirt / total).astype(np.float32),
            "sand": (sand / total).astype(np.float32),
        }

    async def _export_terrain(
        self, terrain_data: TerrainData, formats: List[ExportFormat], output_dir: Path
    ) -> Dict[str, Any]:
        """Export terrain to requested formats"""

        results = {}

        # Handle "all" format
        if ExportFormat.ALL in formats:
            formats = [
                ExportFormat.UNREAL5,
                ExportFormat.UNITY,
                ExportFormat.GLTF,
                ExportFormat.GEOTIFF,
            ]

        for fmt in formats:
            try:
                if fmt == ExportFormat.UNREAL5:
                    # Export UE5 heightmap
                    ue5_dir = output_dir / "unreal5"
                    ue5_dir.mkdir(exist_ok=True)

                    heightmap_exp = Unreal5HeightmapExporter(ue5_dir)
                    heightmap_files = await heightmap_exp.export(terrain_data)

                    # Export weightmaps if available
                    if terrain_data.weightmaps:
                        weightmap_exp = Unreal5WeightmapExporter(ue5_dir)
                        weightmap_files = await weightmap_exp.export(terrain_data)
                        heightmap_files.update(weightmap_files)

                    results["unreal5"] = {"files": heightmap_files, "directory": str(ue5_dir)}

                elif fmt == ExportFormat.UNITY:
                    unity_dir = output_dir / "unity"
                    unity_dir.mkdir(exist_ok=True)

                    exporter = UnityTerrainExporter(unity_dir)
                    files = await exporter.export(terrain_data)

                    results["unity"] = {"files": files, "directory": str(unity_dir)}

                elif fmt == ExportFormat.GLTF:
                    gltf_dir = output_dir / "gltf"
                    gltf_dir.mkdir(exist_ok=True)

                    exporter = GLTFExporter(gltf_dir, binary_format=True)
                    files = await exporter.export(terrain_data)

                    results["gltf"] = {"files": files, "directory": str(gltf_dir)}

                elif fmt == ExportFormat.GEOTIFF:
                    geotiff_dir = output_dir / "geotiff"
                    geotiff_dir.mkdir(exist_ok=True)

                    exporter = GeoTIFFExporter(geotiff_dir)
                    files = await exporter.export(terrain_data)

                    results["geotiff"] = {"files": files, "directory": str(geotiff_dir)}

                logger.info(f"Successfully exported to {fmt.value}")

            except Exception as e:
                logger.error(f"Failed to export to {fmt.value}: {e}")
                results[fmt.value] = {"error": str(e)}

        return results

    def _convert_bbox(self, bbox: BoundingBox) -> SourceBBox:
        """Convert API bbox to source bbox"""
        return SourceBBox(
            north=bbox.north, south=bbox.south, east=bbox.east, west=bbox.west
        )

    def _organize_vector_data(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """Organize raw vector data by type"""

        organized = {"roads": [], "buildings": [], "poi": []}

        if "features" in raw_data:
            for feature in raw_data["features"]:
                ftype = feature.get("properties", {}).get("type", "")

                if ftype == "road":
                    organized["roads"].append(feature)
                elif ftype == "building":
                    organized["buildings"].append(feature)
                elif ftype == "poi":
                    organized["poi"].append(feature)

        return organized

    def _generate_synthetic_terrain(self, resolution: int) -> np.ndarray:
        """Generate synthetic terrain for testing (Perlin-like noise)"""

        logger.warning("Generating synthetic terrain - not real world data!")

        # Simple procedural terrain
        x = np.linspace(0, 8 * np.pi, resolution)
        y = np.linspace(0, 8 * np.pi, resolution)
        X, Y = np.meshgrid(x, y)

        # Combine multiple frequencies
        Z = (
            np.sin(X) * np.cos(Y) * 100
            + np.sin(2 * X) * np.cos(2 * Y) * 50
            + np.sin(4 * X) * np.cos(4 * Y) * 25
        )

        # Add some random noise
        Z += np.random.randn(resolution, resolution) * 10

        # Shift to positive values
        Z = Z - Z.min() + 100

        return Z.astype(np.float32)

    def get_task_status(self, task_id: str) -> Optional[GenerationStatus]:
        """Get status of a generation task"""
        return self.active_tasks.get(task_id)

    def list_tasks(self) -> List[GenerationStatus]:
        """List all tracked tasks"""
        return list(self.active_tasks.values())

