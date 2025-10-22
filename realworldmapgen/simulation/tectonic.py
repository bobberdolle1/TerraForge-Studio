"""
Tectonic Plate Simulation
Simulates plate tectonics for realistic terrain generation
"""

import numpy as np
from typing import List, Tuple
from dataclasses import dataclass


@dataclass
class TectonicPlate:
    """Represents a tectonic plate"""
    id: int
    center: Tuple[float, float]
    velocity: Tuple[float, float]  # Movement direction and speed
    elevation: float
    density: float  # Oceanic (high) vs Continental (low)
    rotation: float  # Angular velocity


class TectonicSimulation:
    """Simulates tectonic plate movements"""
    
    def __init__(self, width: int, height: int, num_plates: int = 8):
        self.width = width
        self.height = height
        self.num_plates = num_plates
        self.plates: List[TectonicPlate] = []
        self.plate_map = np.zeros((height, width), dtype=int)
        self.elevation_map = np.zeros((height, width), dtype=float)
        
        self._initialize_plates()
    
    def _initialize_plates(self):
        """Initialize tectonic plates with random positions"""
        for i in range(self.num_plates):
            # Random plate center
            center = (
                np.random.rand() * self.width,
                np.random.rand() * self.height
            )
            
            # Random velocity
            angle = np.random.rand() * 2 * np.pi
            speed = np.random.rand() * 0.5
            velocity = (
                np.cos(angle) * speed,
                np.sin(angle) * speed
            )
            
            # Random elevation (continental vs oceanic)
            is_continental = np.random.rand() > 0.4
            elevation = np.random.rand() * 1000 if is_continental else -np.random.rand() * 500
            density = 2.7 if is_continental else 3.0  # g/cm³
            
            rotation = (np.random.rand() - 0.5) * 0.01
            
            plate = TectonicPlate(
                id=i,
                center=center,
                velocity=velocity,
                elevation=elevation,
                density=density,
                rotation=rotation
            )
            self.plates.append(plate)
        
        self._assign_cells_to_plates()
    
    def _assign_cells_to_plates(self):
        """Assign each cell to nearest plate"""
        for y in range(self.height):
            for x in range(self.width):
                min_dist = float('inf')
                nearest_plate = 0
                
                for plate in self.plates:
                    dx = x - plate.center[0]
                    dy = y - plate.center[1]
                    dist = np.sqrt(dx**2 + dy**2)
                    
                    if dist < min_dist:
                        min_dist = dist
                        nearest_plate = plate.id
                
                self.plate_map[y, x] = nearest_plate
                self.elevation_map[y, x] = self.plates[nearest_plate].elevation
    
    def simulate_step(self, dt: float = 1.0):
        """Simulate one time step of plate tectonics"""
        # Move plates
        for plate in self.plates:
            plate.center = (
                (plate.center[0] + plate.velocity[0] * dt) % self.width,
                (plate.center[1] + plate.velocity[1] * dt) % self.height
            )
        
        # Reassign cells
        self._assign_cells_to_plates()
        
        # Simulate plate interactions at boundaries
        self._simulate_boundaries()
    
    def _simulate_boundaries(self):
        """Simulate mountain building and subduction at plate boundaries"""
        boundary_map = np.zeros((self.height, self.width), dtype=bool)
        
        # Find boundaries
        for y in range(1, self.height - 1):
            for x in range(1, self.width - 1):
                current_plate = self.plate_map[y, x]
                
                # Check if neighbor has different plate
                is_boundary = False
                for dy in [-1, 0, 1]:
                    for dx in [-1, 0, 1]:
                        if dx == 0 and dy == 0:
                            continue
                        neighbor_plate = self.plate_map[y + dy, x + dx]
                        if neighbor_plate != current_plate:
                            is_boundary = True
                            break
                    if is_boundary:
                        break
                
                if is_boundary:
                    boundary_map[y, x] = True
                    self._apply_boundary_effect(x, y)
    
    def _apply_boundary_effect(self, x: int, y: int):
        """Apply tectonic effects at plate boundaries"""
        current_plate = self.plates[self.plate_map[y, x]]
        
        # Find neighboring plates
        neighbor_plates = set()
        for dy in [-1, 0, 1]:
            for dx in [-1, 0, 1]:
                if dx == 0 and dy == 0:
                    continue
                nx, ny = x + dx, y + dy
                if 0 <= nx < self.width and 0 <= ny < self.height:
                    neighbor_id = self.plate_map[ny, nx]
                    if neighbor_id != current_plate.id:
                        neighbor_plates.add(neighbor_id)
        
        for neighbor_id in neighbor_plates:
            neighbor_plate = self.plates[neighbor_id]
            
            # Calculate relative velocity
            rel_vx = current_plate.velocity[0] - neighbor_plate.velocity[0]
            rel_vy = current_plate.velocity[1] - neighbor_plate.velocity[1]
            rel_speed = np.sqrt(rel_vx**2 + rel_vy**2)
            
            if rel_speed < 0.1:
                continue
            
            # Determine boundary type
            if current_plate.density < neighbor_plate.density:
                # Continental-oceanic: mountain building
                self.elevation_map[y, x] += rel_speed * 50
            elif current_plate.density > neighbor_plate.density:
                # Oceanic-continental: subduction
                self.elevation_map[y, x] -= rel_speed * 20
            else:
                # Same type: uplift or rift
                dot_product = rel_vx * (neighbor_plate.center[0] - current_plate.center[0]) + \
                             rel_vy * (neighbor_plate.center[1] - current_plate.center[1])
                
                if dot_product > 0:
                    # Convergent: uplift
                    self.elevation_map[y, x] += rel_speed * 30
                else:
                    # Divergent: rift valley
                    self.elevation_map[y, x] -= rel_speed * 15
    
    def simulate(self, steps: int = 100, dt: float = 1.0):
        """Run simulation for multiple steps"""
        for _ in range(steps):
            self.simulate_step(dt)
    
    def get_elevation_map(self) -> np.ndarray:
        """Get final elevation map"""
        # Smooth the elevation map
        from scipy.ndimage import gaussian_filter
        smoothed = gaussian_filter(self.elevation_map, sigma=2.0)
        return smoothed
    
    def get_plate_map(self) -> np.ndarray:
        """Get plate boundary map"""
        return self.plate_map
    
    def get_boundary_map(self) -> np.ndarray:
        """Get plate boundaries as binary map"""
        boundary_map = np.zeros((self.height, self.width), dtype=bool)
        
        for y in range(1, self.height - 1):
            for x in range(1, self.width - 1):
                current_plate = self.plate_map[y, x]
                for dy in [-1, 0, 1]:
                    for dx in [-1, 0, 1]:
                        if dx == 0 and dy == 0:
                            continue
                        neighbor_plate = self.plate_map[y + dy, x + dx]
                        if neighbor_plate != current_plate:
                            boundary_map[y, x] = True
                            break
        
        return boundary_map


def generate_tectonic_terrain(
    width: int = 512,
    height: int = 512,
    num_plates: int = 8,
    simulation_steps: int = 100
) -> np.ndarray:
    """
    Generate terrain using tectonic simulation
    
    Args:
        width: Width of terrain
        height: Height of terrain
        num_plates: Number of tectonic plates
        simulation_steps: Number of simulation steps
    
    Returns:
        Elevation map as 2D numpy array
    """
    sim = TectonicSimulation(width, height, num_plates)
    sim.simulate(simulation_steps)
    return sim.get_elevation_map()
