"""
GLTF/GLB Exporter
Exports terrain as 3D mesh in GLTF format
"""

import json
from pathlib import Path
from typing import Dict, Optional
import numpy as np

try:
    import trimesh

    TRIMESH_AVAILABLE = True
except ImportError:
    TRIMESH_AVAILABLE = False

from ..base import BaseExporter, TerrainData


class GLTFExporter(BaseExporter):
    """
    Export terrain as GLTF/GLB 3D mesh.

    GLTF is a universal 3D format supported by:
    - Blender
    - Three.js, Babylon.js
    - Unity (via plugins)
    - Unreal Engine (via plugins)
    - Web browsers (AR/VR)

    Output:
    - {name}.gltf + {name}.bin (separate files)
    - OR {name}.glb (single binary file)
    """

    def __init__(self, output_dir: Path, binary_format: bool = True):
        """
        Args:
            binary_format: If True, export as .glb, else as .gltf
        """
        super().__init__(output_dir)
        self.binary_format = binary_format

    @property
    def format_name(self) -> str:
        return "GLTF" if not self.binary_format else "GLB"

    @property
    def file_extensions(self) -> list[str]:
        return [".glb"] if self.binary_format else [".gltf", ".bin"]

    def validate(self, terrain_data: TerrainData) -> tuple[bool, Optional[str]]:
        """Validate terrain data for GLTF export"""
        if not TRIMESH_AVAILABLE:
            return False, "trimesh library not installed (pip install trimesh)"

        if terrain_data.heightmap is None:
            return False, "Heightmap data is missing"

        return True, None

    async def export(self, terrain_data: TerrainData) -> Dict[str, Path]:
        """Export terrain as GLTF mesh"""

        if not TRIMESH_AVAILABLE:
            raise ImportError("trimesh is required for GLTF export")

        output_files = {}

        # Generate 3D mesh from heightmap
        mesh = await self._generate_mesh(terrain_data)

        # Export to GLTF/GLB
        if self.binary_format:
            filename = f"{terrain_data.name}.glb"
            filepath = self.output_dir / filename
            mesh.export(filepath, file_type="glb")
            output_files["model"] = filepath
        else:
            filename = f"{terrain_data.name}.gltf"
            filepath = self.output_dir / filename
            mesh.export(filepath, file_type="gltf")
            output_files["model"] = filepath
            output_files["binary"] = self.output_dir / f"{terrain_data.name}.bin"

        # Export metadata
        metadata = self.create_metadata(terrain_data)
        metadata_path = self.output_dir / f"{terrain_data.name}_metadata.json"
        with open(metadata_path, "w") as f:
            json.dump(metadata, f, indent=2)
        output_files["metadata"] = metadata_path

        return output_files

    async def _generate_mesh(self, terrain_data: TerrainData) -> "trimesh.Trimesh":
        """Generate 3D mesh from heightmap"""

        heightmap = terrain_data.heightmap
        resolution = terrain_data.resolution

        # Calculate real-world scale
        bbox_width = terrain_data.bbox_east - terrain_data.bbox_west
        bbox_height = terrain_data.bbox_north - terrain_data.bbox_south
        center_lat = (terrain_data.bbox_north + terrain_data.bbox_south) / 2

        # Approximate meters
        width_m = bbox_width * 111000 * np.cos(np.radians(center_lat))
        height_m = bbox_height * 111000

        # Generate vertices
        x = np.linspace(0, width_m, resolution)
        y = np.linspace(0, height_m, resolution)
        X, Y = np.meshgrid(x, y)

        # Z is elevation
        Z = heightmap

        # Flatten to vertex array
        vertices = np.column_stack([X.ravel(), Y.ravel(), Z.ravel()])

        # Generate faces (triangles)
        faces = []
        for i in range(resolution - 1):
            for j in range(resolution - 1):
                # Each quad becomes 2 triangles
                v0 = i * resolution + j
                v1 = i * resolution + (j + 1)
                v2 = (i + 1) * resolution + j
                v3 = (i + 1) * resolution + (j + 1)

                faces.append([v0, v1, v2])
                faces.append([v1, v3, v2])

        faces = np.array(faces)

        # Create mesh
        mesh = trimesh.Trimesh(vertices=vertices, faces=faces)

        # Generate vertex colors based on elevation
        colors = self._generate_vertex_colors(Z.ravel(), terrain_data)
        mesh.visual.vertex_colors = colors

        return mesh

    def _generate_vertex_colors(
        self, elevations: np.ndarray, terrain_data: TerrainData
    ) -> np.ndarray:
        """Generate vertex colors based on elevation"""

        # Normalize elevations to 0-1
        e_min = elevations.min()
        e_max = elevations.max()

        if e_max == e_min:
            normalized = np.zeros_like(elevations)
        else:
            normalized = (elevations - e_min) / (e_max - e_min)

        # Simple color gradient: blue (low) -> green (mid) -> brown (high)
        colors = np.zeros((len(elevations), 4), dtype=np.uint8)

        for i, e in enumerate(normalized):
            if e < 0.33:
                # Low elevation: blue to green
                r = 0
                g = int(255 * (e / 0.33))
                b = int(255 * (1 - e / 0.33))
            elif e < 0.66:
                # Mid elevation: green to brown
                e_local = (e - 0.33) / 0.33
                r = int(139 * e_local)
                g = int(255 * (1 - e_local * 0.3))
                b = 0
            else:
                # High elevation: brown to white
                e_local = (e - 0.66) / 0.34
                r = int(139 + 116 * e_local)
                g = int(178 + 77 * e_local)
                b = int(69 + 186 * e_local)

            colors[i] = [r, g, b, 255]

        return colors

