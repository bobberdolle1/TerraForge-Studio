"""
TerraForge Studio - Unified Terrain Generator
Main orchestrator for terrain generation with multi-source and multi-format support
"""

from __future__ import annotations

import logging
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import numpy as np

from ..config import settings
from ..exporters import (
    GeoTIFFExporter,
    GLTFExporter,
    UnityTerrainExporter,
    Unreal5HeightmapExporter,
    Unreal5WeightmapExporter,
)
from ..exporters.base import TerrainData
from ..models import (
    BoundingBox,
    ElevationProvenance,
    ElevationSource,
    ExportFormat,
    ExportResult,
    GenerationResult,
    GenerationStatus,
    MapGenerationRequest,
    TaskStatus,
)
from .cache_manager import get_cache_manager
from .plugin_system import get_plugin_registry
from .sources import (
    AzureMapsSource,
    EarthEngineSource,
    OpenTopographySource,
    OSMSource,
    SentinelHubSource,
    SRTMSource,
)
from .sources.base import BoundingBox as SourceBBox
from .sources.base import DataSourceConfig
from .thumbnail_generator import generate_thumbnail

logger = logging.getLogger(__name__)

#: Formats covered by ``ExportFormat.ALL``.
_ALL_FORMATS: Tuple[ExportFormat, ...] = (
    ExportFormat.UNREAL5,
    ExportFormat.UNITY,
    ExportFormat.GLTF,
    ExportFormat.GEOTIFF,
)


def _utcnow() -> str:
    return datetime.now(timezone.utc).isoformat()


class TerrainGenerationError(RuntimeError):
    """Raised when a generation cannot produce any usable output."""


class TerraForgeGenerator:
    """
    Main terrain generation orchestrator for TerraForge Studio.

    Coordinates:
    1. Data acquisition from multiple sources
    2. Terrain processing and analysis
    3. Export to multiple game engine formats
    """

    def __init__(self) -> None:
        """Initialize generator with data sources and exporters"""

        self.sources = self._initialize_sources()

        self.cache_manager = get_cache_manager(str(settings.cache_dir))

        self.plugin_registry = get_plugin_registry()
        self.plugin_registry.load_from_directory(Path(settings.plugin_dir))

        # Task tracking
        self.active_tasks: Dict[str, GenerationStatus] = {}

        logger.info("TerraForge Generator initialized")
        logger.info("Available sources: %s", list(self.sources.keys()))
        logger.info("Cache directory: %s", settings.cache_dir)
        logger.info("Plugins loaded: %d", len(self.plugin_registry.list_plugins()))

    # ------------------------------------------------------------------
    # Sources
    # ------------------------------------------------------------------
    def _initialize_sources(self) -> Dict[str, Any]:
        """Initialize all available data sources."""

        sources: Dict[str, Any] = {}

        # SRTM via open terrain tiles: free, global, no API key. This is the
        # default elevation provider and the reason generation works offline of
        # any paid account.
        if settings.srtm_enabled:
            sources["srtm"] = SRTMSource(
                DataSourceConfig(enabled=True, timeout=settings.srtm_timeout),
                tile_url=settings.srtm_tile_url,
                cache_dir=settings.cache_dir if settings.srtm_tile_cache_enabled else None,
                max_zoom=settings.srtm_max_zoom,
                max_tiles=settings.srtm_max_tiles,
                concurrency=settings.srtm_concurrency,
                user_agent=settings.osm_user_agent,
            )

        if settings.sentinelhub_enabled:
            sources["sentinelhub"] = SentinelHubSource(
                DataSourceConfig(
                    enabled=True,
                    api_key=settings.sentinelhub_client_id,
                    api_secret=settings.sentinelhub_client_secret,
                )
            )

        if settings.opentopography_enabled:
            sources["opentopography"] = OpenTopographySource(
                DataSourceConfig(enabled=True, api_key=settings.opentopography_api_key)
            )

        if settings.azure_maps_enabled:
            sources["azure_maps"] = AzureMapsSource(
                DataSourceConfig(enabled=True, api_key=settings.azure_maps_subscription_key)
            )

        if settings.google_earth_engine_enabled:
            sources["earth_engine"] = EarthEngineSource(
                DataSourceConfig(
                    enabled=True,
                    custom_params={
                        "service_account": settings.google_earth_engine_service_account,
                        "private_key_path": settings.google_earth_engine_private_key_path,
                    },
                )
            )

        if settings.osm_enabled:
            sources["osm"] = OSMSource(DataSourceConfig(enabled=True, timeout=settings.osm_timeout))

        return sources

    # ------------------------------------------------------------------
    # Task lifecycle
    # ------------------------------------------------------------------
    def create_task(self, request: MapGenerationRequest) -> GenerationStatus:
        """Register a queued task so its status is visible before work starts."""
        task_id = str(uuid.uuid4())
        status = GenerationStatus(
            task_id=task_id,
            status=TaskStatus.PENDING,
            progress=0.0,
            current_step="Queued for processing",
            message=f"Map generation for '{request.name}' has been queued",
            created_at=_utcnow(),
            updated_at=_utcnow(),
        )
        self.active_tasks[task_id] = status
        return status

    def get_task_status(self, task_id: str) -> Optional[GenerationStatus]:
        """Get status of a generation task"""
        return self.active_tasks.get(task_id)

    def list_tasks(self) -> List[GenerationStatus]:
        """List all tracked tasks, newest first."""
        return sorted(
            self.active_tasks.values(),
            key=lambda task: task.created_at or "",
            reverse=True,
        )

    def _advance(self, status: GenerationStatus, step: str, progress: float) -> None:
        """Record progress on a task and log the transition."""
        status.current_step = step
        status.progress = progress
        status.updated_at = _utcnow()
        logger.info("[%s] %.0f%% - %s", status.task_id[:8], progress, step)

    # ------------------------------------------------------------------
    # Generation
    # ------------------------------------------------------------------
    async def generate_terrain(
        self, request: MapGenerationRequest, task_id: Optional[str] = None
    ) -> GenerationStatus:
        """
        Generate terrain from request.

        Args:
            request: Terrain generation request
            task_id: Task ID of an already-registered task; a new one is
                created when omitted.

        Returns:
            Generation status. Failures are reported through the returned
            status object rather than raised, so background tasks always leave
            a readable state behind.
        """
        status = self.active_tasks.get(task_id) if task_id else None
        if status is None:
            status = self.create_task(request)
            task_id = status.task_id

        status.status = TaskStatus.PROCESSING
        started = time.perf_counter()
        self._emit_event(
            "generation.started",
            {"task_id": task_id, "name": request.name, "resolution": request.resolution},
        )

        try:
            logger.info("Starting terrain generation: '%s' (task: %s)", request.name, task_id)

            area_km2 = request.bbox.area_km2()
            if area_km2 > settings.max_area_km2:
                raise TerrainGenerationError(
                    f"Area too large: {area_km2:.2f} km² (max: {settings.max_area_km2} km²)"
                )

            bbox = self._convert_bbox(request.bbox)
            output_dir = settings.output_dir / request.name
            output_dir.mkdir(parents=True, exist_ok=True)

            # --- Step 1: elevation ---------------------------------------
            self._advance(status, "Acquiring elevation data", 10.0)
            elevation_data, provenance = await self._get_elevation_data(
                bbox, request.resolution, request.elevation_source
            )

            if elevation_data is None:
                raise TerrainGenerationError(
                    "Failed to acquire elevation data from any configured source. "
                    "Check network connectivity or enable a data source in .env"
                )

            if provenance.synthetic:
                status.add_warning(
                    "Elevation data is procedurally generated, not real-world measurements. "
                    "Every configured elevation source was unavailable."
                )

            # --- Step 2: vector features ---------------------------------
            vector_data = None
            if request.enable_roads or request.enable_buildings:
                self._advance(status, "Extracting vector features", 30.0)
                vector_data = await self._get_vector_data(bbox, request)
                if vector_data is None:
                    status.add_warning(
                        "No vector data (roads/buildings) could be retrieved for this area."
                    )

            # --- Step 3: weightmaps --------------------------------------
            weightmaps = None
            if request.enable_weightmaps:
                self._advance(status, "Generating material weightmaps", 50.0)
                weightmaps = self._generate_weightmaps(elevation_data)

            # --- Step 4: assemble ----------------------------------------
            self._advance(status, "Preparing terrain data", 60.0)
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

            # --- Step 5: export ------------------------------------------
            self._advance(status, "Exporting terrain", 70.0)
            exports = await self._export_terrain(
                terrain_data, request.export_formats, output_dir
            )

            successful = [export for export in exports if export.success]
            if not successful:
                reasons = "; ".join(
                    f"{export.format}: {export.error}" for export in exports if export.error
                )
                raise TerrainGenerationError(f"All exports failed ({reasons})")

            for export in exports:
                if not export.success:
                    status.add_warning(f"Export to {export.format} failed: {export.error}")

            # --- Step 6: finalize ----------------------------------------
            self._advance(status, "Generating preview", 92.0)
            thumbnail_path, thumbnail_b64 = self._generate_thumbnail(elevation_data, output_dir)
            if thumbnail_path is None:
                status.add_warning("Preview thumbnail could not be generated.")

            result = GenerationResult(
                terrain_name=request.name,
                resolution=request.resolution,
                area_km2=round(area_km2, 4),
                bbox=request.bbox,
                elevation=provenance,
                exports=exports,
                output_directory=str(output_dir),
                thumbnail_path=str(thumbnail_path) if thumbnail_path else None,
                thumbnail_base64=thumbnail_b64,
                duration_seconds=round(time.perf_counter() - started, 3),
            )

            status.result = result
            status.status = TaskStatus.COMPLETED
            status.download_url = f"/api/maps/{request.name}/download/zip"
            self._advance(status, "Complete", 100.0)
            status.message = (
                f"Generated '{request.name}' in {result.duration_seconds:.1f}s "
                f"({len(successful)}/{len(exports)} formats exported)"
            )

            logger.info("Terrain generation completed: %s", request.name)
            self._emit_event(
                "generation.completed",
                {
                    "task_id": task_id,
                    "name": request.name,
                    "duration_seconds": result.duration_seconds,
                    "elevation_source": provenance.source,
                    "synthetic": provenance.synthetic,
                    "formats": [export.format for export in successful],
                    "download_url": status.download_url,
                },
            )
            return status

        except Exception as exc:
            logger.error("Terrain generation failed: %s", exc, exc_info=True)
            status.status = TaskStatus.FAILED
            status.error = str(exc)
            status.updated_at = _utcnow()
            status.message = f"Generation of '{request.name}' failed"
            self._emit_event(
                "generation.failed",
                {"task_id": task_id, "name": request.name, "error": str(exc)},
            )
            return status

    @staticmethod
    def _emit_event(name: str, data: Dict[str, Any]) -> None:
        """Notify webhook subscribers; never let a subscriber break generation."""
        try:
            from ..api.webhook_routes import emit

            emit(name, data)
        except Exception as exc:  # noqa: BLE001
            logger.debug("Could not emit webhook event %s: %s", name, exc)

    # ------------------------------------------------------------------
    # Elevation
    # ------------------------------------------------------------------
    def _elevation_priority(self, requested: ElevationSource) -> List[str]:
        """Resolve the ordered list of source names to try for a request."""
        if requested != ElevationSource.AUTO:
            # Always keep the free source as a last resort behind an explicit choice.
            priority = [requested.value]
            if "srtm" in self.sources and requested.value != "srtm":
                priority.append("srtm")
            return priority

        priority = [name for name in settings.elevation_source_priority if name in self.sources]
        if "srtm" in self.sources and "srtm" not in priority:
            priority.append("srtm")
        return priority

    async def _get_elevation_data(
        self, bbox: SourceBBox, resolution: int, source_priority: ElevationSource
    ) -> Tuple[Optional[np.ndarray], ElevationProvenance]:
        """
        Acquire elevation data from the best available source.

        Returns the elevation array together with provenance describing which
        source produced it and whether it is real or synthetic.
        """
        priority = self._elevation_priority(source_priority)
        if not priority:
            logger.warning("No elevation sources are configured")

        for source_name in priority:
            source = self.sources.get(source_name)
            if source is None:
                continue

            try:
                if not await source.is_available():
                    logger.info("Source %s not available, skipping", source_name)
                    continue

                logger.info("Trying elevation source: %s", source_name)
                elevation = await source.get_elevation_data(bbox, resolution)

                if elevation is not None and np.isfinite(elevation).any():
                    logger.info("Acquired elevation from %s", source_name)
                    return elevation, ElevationProvenance(
                        source=source_name,
                        synthetic=False,
                        min_elevation_m=float(np.nanmin(elevation)),
                        max_elevation_m=float(np.nanmax(elevation)),
                    )

            except Exception as exc:
                logger.warning("Failed to get elevation from %s: %s", source_name, exc)
                continue

        if not settings.allow_synthetic_fallback:
            return None, ElevationProvenance(source="none", synthetic=True)

        logger.warning("All elevation sources failed - generating synthetic terrain")
        synthetic = self._generate_synthetic_terrain(resolution)
        return synthetic, ElevationProvenance(
            source="synthetic",
            synthetic=True,
            min_elevation_m=float(synthetic.min()),
            max_elevation_m=float(synthetic.max()),
        )

    # ------------------------------------------------------------------
    # Vector data
    # ------------------------------------------------------------------
    async def _get_vector_data(
        self, bbox: SourceBBox, request: MapGenerationRequest
    ) -> Optional[Dict[str, Any]]:
        """Get vector data (roads, buildings) from OSM or Azure Maps"""

        feature_types = []
        if request.enable_roads:
            feature_types.append("roads")
        if request.enable_buildings:
            feature_types.append("buildings")

        for source_name in ("osm", "azure_maps"):
            source = self.sources.get(source_name)
            if source is None:
                continue
            try:
                if not await source.is_available():
                    continue
                vector_data = await source.get_vector_data(bbox, feature_types)
                if vector_data:
                    return self._organize_vector_data(vector_data)
            except Exception as exc:
                logger.warning("%s vector data failed: %s", source_name, exc)

        return None

    @staticmethod
    def _organize_vector_data(raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """Organize raw vector data by type"""

        organized: Dict[str, List[Any]] = {"roads": [], "buildings": [], "poi": []}

        for feature in raw_data.get("features", []):
            ftype = feature.get("properties", {}).get("type", "")
            if ftype == "road":
                organized["roads"].append(feature)
            elif ftype == "building":
                organized["buildings"].append(feature)
            elif ftype == "poi":
                organized["poi"].append(feature)

        return organized

    # ------------------------------------------------------------------
    # Derived layers
    # ------------------------------------------------------------------
    @staticmethod
    def _generate_weightmaps(elevation: np.ndarray) -> Dict[str, np.ndarray]:
        """
        Generate material weightmaps from elevation and slope.

        Returns normalized layers that sum to 1 per pixel, keyed
        ``rock`` / ``grass`` / ``dirt`` / ``sand``.
        """
        clean = np.nan_to_num(elevation, nan=float(np.nanmean(elevation)) if np.isfinite(elevation).any() else 0.0)

        dy, dx = np.gradient(clean)
        slope = np.degrees(np.arctan(np.sqrt(dx**2 + dy**2)))

        span = float(clean.max() - clean.min())
        height_norm = (clean - clean.min()) / span if span > 1e-6 else np.zeros_like(clean)

        rock = np.clip((slope - 30) / 30, 0, 1)  # steep slopes
        sand = (1 - height_norm) * (1 - np.clip(slope / 15, 0, 1))  # low and flat
        grass = (1 - np.abs(height_norm - 0.5) * 2) * (1 - np.clip(slope / 20, 0, 1))
        grass = np.clip(grass, 0, 1)
        dirt = np.clip(1 - (rock + grass + sand), 0, 1)  # fill remainder

        total = np.maximum(rock + grass + dirt + sand, 1e-3)

        return {
            "rock": (rock / total).astype(np.float32),
            "grass": (grass / total).astype(np.float32),
            "dirt": (dirt / total).astype(np.float32),
            "sand": (sand / total).astype(np.float32),
        }

    @staticmethod
    def _generate_thumbnail(
        elevation: np.ndarray, output_dir: Path
    ) -> Tuple[Optional[Path], Optional[str]]:
        """Render a preview image; failures are non-fatal."""
        try:
            thumbnail_path = output_dir / "thumbnail.png"
            thumbnail_b64 = generate_thumbnail(elevation, thumbnail_path, size=(400, 300))
            if thumbnail_b64:
                return thumbnail_path, thumbnail_b64
        except Exception as exc:
            logger.warning("Failed to generate thumbnail: %s", exc)
        return None, None

    # ------------------------------------------------------------------
    # Export
    # ------------------------------------------------------------------
    async def _export_terrain(
        self, terrain_data: TerrainData, formats: List[ExportFormat], output_dir: Path
    ) -> List[ExportResult]:
        """
        Export terrain to the requested formats.

        Each format is attempted independently; one failing exporter never
        prevents the others from producing output.
        """
        targets: List[ExportFormat] = []
        for fmt in formats:
            if fmt == ExportFormat.ALL:
                targets.extend(_ALL_FORMATS)
            else:
                targets.append(fmt)

        seen: set = set()
        ordered = [fmt for fmt in targets if not (fmt in seen or seen.add(fmt))]

        results: List[ExportResult] = []
        for fmt in ordered:
            target_dir = output_dir / fmt.value
            try:
                files, directory = await self._run_exporter(fmt, terrain_data, output_dir)
                results.append(
                    ExportResult(
                        format=fmt.value,
                        success=True,
                        directory=str(directory),
                        files={key: str(path) for key, path in files.items()},
                    )
                )
                logger.info("Successfully exported to %s", fmt.value)
            except Exception as exc:
                logger.error("Failed to export to %s: %s", fmt.value, exc)
                results.append(ExportResult(format=fmt.value, success=False, error=str(exc)))
                # Remove the directory the exporter created before failing, so
                # /api/maps does not advertise a format that produced no files.
                self._remove_if_empty(target_dir)

        return results

    @staticmethod
    def _remove_if_empty(directory: Path) -> None:
        """Delete a directory when it exists and contains nothing."""
        try:
            if directory.is_dir() and not any(directory.iterdir()):
                directory.rmdir()
        except OSError as exc:
            logger.debug("Could not remove empty directory %s: %s", directory, exc)

    async def _run_exporter(
        self, fmt: ExportFormat, terrain_data: TerrainData, output_dir: Path
    ) -> Tuple[Dict[str, Path], Path]:
        """Dispatch to the exporter for a single format."""
        if fmt == ExportFormat.UNREAL5:
            target = output_dir / "unreal5"
            target.mkdir(parents=True, exist_ok=True)

            files = await Unreal5HeightmapExporter(
                target, export_format=settings.ue5_heightmap_format
            ).export(terrain_data)

            if terrain_data.weightmaps and settings.ue5_export_weightmaps:
                files.update(await Unreal5WeightmapExporter(target).export(terrain_data))
            return files, target

        if fmt == ExportFormat.UNITY:
            target = output_dir / "unity"
            target.mkdir(parents=True, exist_ok=True)
            return await UnityTerrainExporter(target).export(terrain_data), target

        if fmt == ExportFormat.GLTF:
            target = output_dir / "gltf"
            target.mkdir(parents=True, exist_ok=True)
            exporter = GLTFExporter(
                target,
                binary_format=True,
                max_mesh_resolution=settings.gltf_max_mesh_resolution,
            )
            return await exporter.export(terrain_data), target

        if fmt == ExportFormat.GEOTIFF:
            target = output_dir / "geotiff"
            target.mkdir(parents=True, exist_ok=True)
            return await GeoTIFFExporter(target).export(terrain_data), target

        raise ValueError(f"Unsupported export format: {fmt.value}")

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------
    @staticmethod
    def _convert_bbox(bbox: BoundingBox) -> SourceBBox:
        """Convert API bbox to source bbox"""
        return SourceBBox(north=bbox.north, south=bbox.south, east=bbox.east, west=bbox.west)

    @staticmethod
    def _generate_synthetic_terrain(resolution: int) -> np.ndarray:
        """
        Generate procedural terrain used only when every real source failed.

        Results are always flagged as synthetic in the provenance so callers
        never mistake them for measured elevation.
        """
        logger.warning("Generating synthetic terrain - this is NOT real world data")

        axis = np.linspace(0, 8 * np.pi, resolution)
        grid_x, grid_y = np.meshgrid(axis, axis)

        heights = (
            np.sin(grid_x) * np.cos(grid_y) * 100
            + np.sin(2 * grid_x) * np.cos(2 * grid_y) * 50
            + np.sin(4 * grid_x) * np.cos(4 * grid_y) * 25
        )
        # Deterministic noise keeps repeated runs reproducible and cacheable.
        rng = np.random.default_rng(seed=resolution)
        heights += rng.standard_normal((resolution, resolution)) * 10

        return (heights - heights.min() + 100).astype(np.float32)
