/**
 * Ecosystem Simulation
 * Vegetation distribution based on climate and terrain
 */

export interface VegetationType {
  id: string;
  name: string;
  minElevation: number;
  maxElevation: number;
  minTemperature: number;
  maxTemperature: number;
  minHumidity: number;
  maxHumidity: number;
  density: number;
  icon: string;
}

export interface EcosystemCell {
  x: number;
  y: number;
  elevation: number;
  slope: number;
  temperature: number;
  humidity: number;
  vegetation: VegetationType | null;
}

export const vegetationTypes: VegetationType[] = [
  {
    id: 'snow',
    name: 'Snow/Ice',
    minElevation: 3000,
    maxElevation: 9000,
    minTemperature: -50,
    maxTemperature: 0,
    minHumidity: 0,
    maxHumidity: 100,
    density: 0,
    icon: '❄️',
  },
  {
    id: 'alpine',
    name: 'Alpine Tundra',
    minElevation: 2500,
    maxElevation: 3500,
    minTemperature: -10,
    maxTemperature: 10,
    minHumidity: 30,
    maxHumidity: 100,
    density: 0.3,
    icon: '🌿',
  },
  {
    id: 'coniferous',
    name: 'Coniferous Forest',
    minElevation: 1000,
    maxElevation: 2500,
    minTemperature: -20,
    maxTemperature: 20,
    minHumidity: 40,
    maxHumidity: 100,
    density: 0.8,
    icon: '🌲',
  },
  {
    id: 'deciduous',
    name: 'Deciduous Forest',
    minElevation: 0,
    maxElevation: 1500,
    minTemperature: 0,
    maxTemperature: 30,
    minHumidity: 50,
    maxHumidity: 100,
    density: 0.7,
    icon: '🌳',
  },
  {
    id: 'grassland',
    name: 'Grassland',
    minElevation: 0,
    maxElevation: 2000,
    minTemperature: 5,
    maxTemperature: 35,
    minHumidity: 30,
    maxHumidity: 70,
    density: 0.6,
    icon: '🌾',
  },
  {
    id: 'desert',
    name: 'Desert',
    minElevation: 0,
    maxElevation: 2000,
    minTemperature: 10,
    maxTemperature: 50,
    minHumidity: 0,
    maxHumidity: 30,
    density: 0.1,
    icon: '🏜️',
  },
  {
    id: 'tropical',
    name: 'Tropical Rainforest',
    minElevation: 0,
    maxElevation: 1000,
    minTemperature: 20,
    maxTemperature: 35,
    minHumidity: 70,
    maxHumidity: 100,
    density: 0.9,
    icon: '🌴',
  },
];

export class EcosystemSimulation {
  private grid: EcosystemCell[][] = [];
  private width: number;
  private height: number;

  constructor(width: number, height: number) {
    this.width = width;
    this.height = height;
    this.initializeGrid();
  }

  private initializeGrid(): void {
    for (let y = 0; y < this.height; y++) {
      const row: EcosystemCell[] = [];
      for (let x = 0; x < this.width; x++) {
        row.push({
          x,
          y,
          elevation: 0,
          slope: 0,
          temperature: 15,
          humidity: 50,
          vegetation: null,
        });
      }
      this.grid.push(row);
    }
  }

  setTerrain(heightmap: Float32Array, width: number, height: number): void {
    for (let y = 0; y < Math.min(height, this.height); y++) {
      for (let x = 0; x < Math.min(width, this.width); x++) {
        const elevation = heightmap[y * width + x];
        const slope = this.calculateSlope(heightmap, x, y, width, height);
        
        this.grid[y][x].elevation = elevation;
        this.grid[y][x].slope = slope;
      }
    }
  }

  private calculateSlope(
    heightmap: Float32Array,
    x: number,
    y: number,
    width: number,
    height: number
  ): number {
    const current = heightmap[y * width + x];
    let maxDiff = 0;

    for (let dy = -1; dy <= 1; dy++) {
      for (let dx = -1; dx <= 1; dx++) {
        if (dx === 0 && dy === 0) continue;
        
        const nx = x + dx;
        const ny = y + dy;
        
        if (nx >= 0 && nx < width && ny >= 0 && ny < height) {
          const neighbor = heightmap[ny * width + nx];
          const diff = Math.abs(current - neighbor);
          maxDiff = Math.max(maxDiff, diff);
        }
      }
    }

    return Math.atan(maxDiff) * (180 / Math.PI);
  }

  setClimate(latitude: number, season: 'spring' | 'summer' | 'autumn' | 'winter'): void {
    const baseTemp = 30 - Math.abs(latitude) * 0.5;
    const seasonalAdjustment = {
      spring: 0,
      summer: 10,
      autumn: 0,
      winter: -10,
    }[season];

    for (let y = 0; y < this.height; y++) {
      for (let x = 0; x < this.width; x++) {
        const cell = this.grid[y][x];
        
        // Temperature decreases with elevation (6.5°C per 1000m)
        const elevationEffect = -0.0065 * cell.elevation;
        cell.temperature = baseTemp + seasonalAdjustment + elevationEffect;
        
        // Humidity based on terrain and elevation
        if (cell.elevation < 100) {
          cell.humidity = 70 + Math.random() * 20;
        } else if (cell.elevation < 1000) {
          cell.humidity = 50 + Math.random() * 30;
        } else {
          cell.humidity = 30 + Math.random() * 20;
        }
      }
    }
  }

  distributeVegetation(): void {
    for (let y = 0; y < this.height; y++) {
      for (let x = 0; x < this.width; x++) {
        const cell = this.grid[y][x];
        cell.vegetation = this.determineVegetation(cell);
      }
    }
  }

  private determineVegetation(cell: EcosystemCell): VegetationType | null {
    // Too steep for vegetation
    if (cell.slope > 45) return null;

    // Find matching vegetation types
    const suitable = vegetationTypes.filter(
      (veg) =>
        cell.elevation >= veg.minElevation &&
        cell.elevation <= veg.maxElevation &&
        cell.temperature >= veg.minTemperature &&
        cell.temperature <= veg.maxTemperature &&
        cell.humidity >= veg.minHumidity &&
        cell.humidity <= veg.maxHumidity
    );

    if (suitable.length === 0) return null;

    // Choose best match based on optimal conditions
    let best = suitable[0];
    let bestScore = 0;

    for (const veg of suitable) {
      const tempScore = 1 - Math.abs(
        (cell.temperature - (veg.minTemperature + veg.maxTemperature) / 2) /
        ((veg.maxTemperature - veg.minTemperature) / 2)
      );
      const humidityScore = 1 - Math.abs(
        (cell.humidity - (veg.minHumidity + veg.maxHumidity) / 2) /
        ((veg.maxHumidity - veg.minHumidity) / 2)
      );
      const score = tempScore * humidityScore;

      if (score > bestScore) {
        best = veg;
        bestScore = score;
      }
    }

    return best;
  }

  getVegetationMap(): Map<string, number> {
    const counts = new Map<string, number>();

    for (let y = 0; y < this.height; y++) {
      for (let x = 0; x < this.width; x++) {
        const veg = this.grid[y][x].vegetation;
        if (veg) {
          counts.set(veg.name, (counts.get(veg.name) || 0) + 1);
        }
      }
    }

    return counts;
  }

  getGrid(): EcosystemCell[][] {
    return this.grid;
  }
}

export const ecosystemSimulation = new EcosystemSimulation(100, 100);
