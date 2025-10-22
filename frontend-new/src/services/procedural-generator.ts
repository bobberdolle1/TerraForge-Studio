/**
 * Procedural Terrain Generation System
 * Perlin noise, fractal algorithms, erosion simulation
 */

export class PerlinNoise {
  private permutation: number[];

  constructor(seed: number = Math.random()) {
    this.permutation = this.generatePermutation(seed);
  }

  private generatePermutation(seed: number): number[] {
    const p = [];
    for (let i = 0; i < 256; i++) {
      p[i] = i;
    }
    
    // Fisher-Yates shuffle with seed
    let random = seed;
    for (let i = 255; i > 0; i--) {
      random = (random * 9301 + 49297) % 233280;
      const j = Math.floor((random / 233280) * (i + 1));
      [p[i], p[j]] = [p[j], p[i]];
    }
    
    return [...p, ...p];
  }

  private fade(t: number): number {
    return t * t * t * (t * (t * 6 - 15) + 10);
  }

  private lerp(a: number, b: number, t: number): number {
    return a + t * (b - a);
  }

  private grad(hash: number, x: number, y: number): number {
    const h = hash & 3;
    const u = h < 2 ? x : y;
    const v = h < 2 ? y : x;
    return ((h & 1) === 0 ? u : -u) + ((h & 2) === 0 ? v : -v);
  }

  noise(x: number, y: number): number {
    const X = Math.floor(x) & 255;
    const Y = Math.floor(y) & 255;
    
    x -= Math.floor(x);
    y -= Math.floor(y);
    
    const u = this.fade(x);
    const v = this.fade(y);
    
    const a = this.permutation[X] + Y;
    const b = this.permutation[X + 1] + Y;
    
    return this.lerp(
      this.lerp(
        this.grad(this.permutation[a], x, y),
        this.grad(this.permutation[b], x - 1, y),
        u
      ),
      this.lerp(
        this.grad(this.permutation[a + 1], x, y - 1),
        this.grad(this.permutation[b + 1], x - 1, y - 1),
        u
      ),
      v
    );
  }
}

export class FractalNoise {
  private perlin: PerlinNoise;

  constructor(seed?: number) {
    this.perlin = new PerlinNoise(seed);
  }

  fractal(
    x: number,
    y: number,
    octaves: number = 4,
    persistence: number = 0.5,
    lacunarity: number = 2.0
  ): number {
    let total = 0;
    let frequency = 1;
    let amplitude = 1;
    let maxValue = 0;

    for (let i = 0; i < octaves; i++) {
      total += this.perlin.noise(x * frequency, y * frequency) * amplitude;
      maxValue += amplitude;
      amplitude *= persistence;
      frequency *= lacunarity;
    }

    return total / maxValue;
  }
}

export class TerrainGenerator {
  private fractal: FractalNoise;

  constructor(seed?: number) {
    this.fractal = new FractalNoise(seed);
  }

  generateHeightmap(
    width: number,
    height: number,
    options: {
      scale?: number;
      octaves?: number;
      persistence?: number;
      lacunarity?: number;
      heightMultiplier?: number;
    } = {}
  ): Float32Array {
    const {
      scale = 100,
      octaves = 4,
      persistence = 0.5,
      lacunarity = 2.0,
      heightMultiplier = 100,
    } = options;

    const heightmap = new Float32Array(width * height);

    for (let y = 0; y < height; y++) {
      for (let x = 0; x < width; x++) {
        const nx = x / scale;
        const ny = y / scale;
        
        const elevation = this.fractal.fractal(nx, ny, octaves, persistence, lacunarity);
        heightmap[y * width + x] = elevation * heightMultiplier;
      }
    }

    return heightmap;
  }

  applyErosion(heightmap: Float32Array, width: number, height: number, iterations: number = 1000): void {
    for (let i = 0; i < iterations; i++) {
      const x = Math.floor(Math.random() * width);
      const y = Math.floor(Math.random() * height);
      
      this.simulateDroplet(heightmap, width, height, x, y);
    }
  }

  private simulateDroplet(
    heightmap: Float32Array,
    width: number,
    height: number,
    startX: number,
    startY: number
  ): void {
    let x = startX;
    let y = startY;
    let sediment = 0;
    const capacity = 4;
    const deposition = 0.3;
    const erosion = 0.3;

    for (let i = 0; i < 30; i++) {
      const idx = y * width + x;
      const currentHeight = heightmap[idx];
      
      // Find lowest neighbor
      let lowestX = x;
      let lowestY = y;
      let lowestHeight = currentHeight;
      
      for (let dy = -1; dy <= 1; dy++) {
        for (let dx = -1; dx <= 1; dx++) {
          const nx = x + dx;
          const ny = y + dy;
          
          if (nx >= 0 && nx < width && ny >= 0 && ny < height) {
            const neighborHeight = heightmap[ny * width + nx];
            if (neighborHeight < lowestHeight) {
              lowestX = nx;
              lowestY = ny;
              lowestHeight = neighborHeight;
            }
          }
        }
      }
      
      // If stuck, deposit and stop
      if (lowestX === x && lowestY === y) {
        heightmap[idx] += sediment * deposition;
        break;
      }
      
      // Erode
      const heightDiff = currentHeight - lowestHeight;
      const erodeAmount = Math.min(heightDiff, erosion);
      heightmap[idx] -= erodeAmount;
      sediment += erodeAmount;
      
      // Deposit
      if (sediment > capacity) {
        const depositAmount = (sediment - capacity) * deposition;
        heightmap[idx] += depositAmount;
        sediment -= depositAmount;
      }
      
      // Move to lowest neighbor
      x = lowestX;
      y = lowestY;
    }
  }

  applyThermalErosion(heightmap: Float32Array, width: number, height: number, iterations: number = 10): void {
    const talusAngle = 0.5; // Threshold for material movement
    
    for (let iter = 0; iter < iterations; iter++) {
      const diffs = new Float32Array(width * height);
      
      for (let y = 1; y < height - 1; y++) {
        for (let x = 1; x < width - 1; x++) {
          const idx = y * width + x;
          const currentHeight = heightmap[idx];
          let maxDiff = 0;
          
          // Check all neighbors
          for (let dy = -1; dy <= 1; dy++) {
            for (let dx = -1; dx <= 1; dx++) {
              if (dx === 0 && dy === 0) continue;
              
              const neighborIdx = (y + dy) * width + (x + dx);
              const diff = currentHeight - heightmap[neighborIdx];
              
              if (diff > talusAngle) {
                maxDiff = Math.max(maxDiff, diff);
              }
            }
          }
          
          diffs[idx] = maxDiff * 0.5;
        }
      }
      
      // Apply changes
      for (let i = 0; i < heightmap.length; i++) {
        heightmap[i] -= diffs[i];
      }
    }
  }
}

export const terrainGenerator = new TerrainGenerator();
