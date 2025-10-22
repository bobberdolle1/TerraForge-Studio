/**
 * Particle Effects System
 * Weather effects: rain, snow, dust, wind
 */

export interface Particle {
  x: number;
  y: number;
  z: number;
  vx: number;
  vy: number;
  vz: number;
  life: number;
  maxLife: number;
  size: number;
  opacity: number;
  color: string;
}

export class ParticleSystem {
  private particles: Particle[] = [];
  private maxParticles: number;
  private emissionRate: number;
  private gravity: number;

  constructor(maxParticles: number = 1000, emissionRate: number = 10) {
    this.maxParticles = maxParticles;
    this.emissionRate = emissionRate;
    this.gravity = -9.8;
  }

  emit(count: number, config: Partial<Particle>): void {
    for (let i = 0; i < count && this.particles.length < this.maxParticles; i++) {
      this.particles.push({
        x: config.x ?? 0,
        y: config.y ?? 10,
        z: config.z ?? 0,
        vx: config.vx ?? (Math.random() - 0.5) * 2,
        vy: config.vy ?? -5,
        vz: config.vz ?? (Math.random() - 0.5) * 2,
        life: 1.0,
        maxLife: config.maxLife ?? 5.0,
        size: config.size ?? 0.1,
        opacity: config.opacity ?? 1.0,
        color: config.color ?? '#ffffff',
      });
    }
  }

  update(deltaTime: number): void {
    for (let i = this.particles.length - 1; i >= 0; i--) {
      const p = this.particles[i];

      // Update velocity
      p.vy += this.gravity * deltaTime;

      // Update position
      p.x += p.vx * deltaTime;
      p.y += p.vy * deltaTime;
      p.z += p.vz * deltaTime;

      // Update life
      p.life -= deltaTime / p.maxLife;
      p.opacity = p.life;

      // Remove dead particles
      if (p.life <= 0 || p.y < 0) {
        this.particles.splice(i, 1);
      }
    }
  }

  getParticles(): Particle[] {
    return this.particles;
  }

  clear(): void {
    this.particles = [];
  }
}

export class RainEffect {
  private system: ParticleSystem;

  constructor() {
    this.system = new ParticleSystem(2000, 50);
  }

  update(deltaTime: number, intensity: number = 1.0): void {
    // Emit new raindrops
    const emitCount = Math.floor(intensity * 20);
    for (let i = 0; i < emitCount; i++) {
      this.system.emit(1, {
        x: (Math.random() - 0.5) * 50,
        y: 20,
        z: (Math.random() - 0.5) * 50,
        vx: 0,
        vy: -15 - Math.random() * 5,
        vz: 0,
        size: 0.05,
        maxLife: 2.0,
        color: '#6ba3d4',
      });
    }

    this.system.update(deltaTime);
  }

  getParticles(): Particle[] {
    return this.system.getParticles();
  }
}

export class SnowEffect {
  private system: ParticleSystem;

  constructor() {
    this.system = new ParticleSystem(1500, 30);
  }

  update(deltaTime: number, intensity: number = 1.0): void {
    const emitCount = Math.floor(intensity * 10);
    for (let i = 0; i < emitCount; i++) {
      this.system.emit(1, {
        x: (Math.random() - 0.5) * 50,
        y: 20,
        z: (Math.random() - 0.5) * 50,
        vx: (Math.random() - 0.5) * 2,
        vy: -2 - Math.random() * 2,
        vz: (Math.random() - 0.5) * 2,
        size: 0.1 + Math.random() * 0.1,
        maxLife: 8.0,
        color: '#ffffff',
      });
    }

    this.system.update(deltaTime);
  }

  getParticles(): Particle[] {
    return this.system.getParticles();
  }
}

export class DustEffect {
  private system: ParticleSystem;

  constructor() {
    this.system = new ParticleSystem(500, 10);
  }

  update(deltaTime: number, windSpeed: number = 5.0): void {
    const emitCount = Math.floor(windSpeed / 5);
    for (let i = 0; i < emitCount; i++) {
      this.system.emit(1, {
        x: -25 + Math.random() * 2,
        y: Math.random() * 5,
        z: (Math.random() - 0.5) * 50,
        vx: windSpeed + Math.random() * 2,
        vy: (Math.random() - 0.5) * 2,
        vz: (Math.random() - 0.5) * 2,
        size: 0.2 + Math.random() * 0.2,
        maxLife: 3.0,
        color: '#c9a87d',
        opacity: 0.5,
      });
    }

    this.system.update(deltaTime);
  }

  getParticles(): Particle[] {
    return this.system.getParticles();
  }
}

// Weather manager
export class WeatherEffects {
  private rain: RainEffect;
  private snow: SnowEffect;
  private dust: DustEffect;
  private currentEffect: 'none' | 'rain' | 'snow' | 'dust' = 'none';

  constructor() {
    this.rain = new RainEffect();
    this.snow = new SnowEffect();
    this.dust = new DustEffect();
  }

  setEffect(effect: 'none' | 'rain' | 'snow' | 'dust'): void {
    this.currentEffect = effect;
  }

  update(deltaTime: number, intensity: number = 1.0): void {
    switch (this.currentEffect) {
      case 'rain':
        this.rain.update(deltaTime, intensity);
        break;
      case 'snow':
        this.snow.update(deltaTime, intensity);
        break;
      case 'dust':
        this.dust.update(deltaTime, intensity * 10);
        break;
    }
  }

  getActiveParticles(): Particle[] {
    switch (this.currentEffect) {
      case 'rain':
        return this.rain.getParticles();
      case 'snow':
        return this.snow.getParticles();
      case 'dust':
        return this.dust.getParticles();
      default:
        return [];
    }
  }
}

export const weatherEffects = new WeatherEffects();
