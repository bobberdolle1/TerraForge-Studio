/**
 * Animation System
 * Spring physics and smooth transitions
 */

export interface SpringConfig {
  stiffness: number;
  damping: number;
  mass: number;
}

export class SpringAnimation {
  private position: number = 0;
  private velocity: number = 0;
  private target: number = 0;
  private config: SpringConfig;

  constructor(config: SpringConfig = { stiffness: 170, damping: 26, mass: 1 }) {
    this.config = config;
  }

  setTarget(target: number): void {
    this.target = target;
  }

  step(deltaTime: number): number {
    const springForce = -this.config.stiffness * (this.position - this.target);
    const dampingForce = -this.config.damping * this.velocity;
    const acceleration = (springForce + dampingForce) / this.config.mass;

    this.velocity += acceleration * deltaTime;
    this.position += this.velocity * deltaTime;

    return this.position;
  }

  isAtRest(): boolean {
    return Math.abs(this.velocity) < 0.01 && Math.abs(this.position - this.target) < 0.01;
  }

  reset(position: number = 0): void {
    this.position = position;
    this.velocity = 0;
    this.target = position;
  }
}

export const easing = {
  // Robert Penner's easing functions
  linear: (t: number) => t,
  
  easeInQuad: (t: number) => t * t,
  easeOutQuad: (t: number) => t * (2 - t),
  easeInOutQuad: (t: number) => (t < 0.5 ? 2 * t * t : -1 + (4 - 2 * t) * t),
  
  easeInCubic: (t: number) => t * t * t,
  easeOutCubic: (t: number) => --t * t * t + 1,
  easeInOutCubic: (t: number) =>
    t < 0.5 ? 4 * t * t * t : (t - 1) * (2 * t - 2) * (2 * t - 2) + 1,
  
  easeInExpo: (t: number) => (t === 0 ? 0 : Math.pow(2, 10 * (t - 1))),
  easeOutExpo: (t: number) => (t === 1 ? 1 : -Math.pow(2, -10 * t) + 1),
  
  easeInElastic: (t: number) => {
    const p = 0.3;
    return t === 0 || t === 1
      ? t
      : -Math.pow(2, 10 * (t - 1)) * Math.sin(((t - 1.1) * 2 * Math.PI) / p);
  },
  easeOutElastic: (t: number) => {
    const p = 0.3;
    return t === 0 || t === 1
      ? t
      : Math.pow(2, -10 * t) * Math.sin(((t - 0.1) * 2 * Math.PI) / p) + 1;
  },
  
  easeInBack: (t: number) => {
    const s = 1.70158;
    return t * t * ((s + 1) * t - s);
  },
  easeOutBack: (t: number) => {
    const s = 1.70158;
    return --t * t * ((s + 1) * t + s) + 1;
  },
  
  easeInBounce: (t: number) => 1 - easing.easeOutBounce(1 - t),
  easeOutBounce: (t: number) => {
    if (t < 1 / 2.75) {
      return 7.5625 * t * t;
    } else if (t < 2 / 2.75) {
      return 7.5625 * (t -= 1.5 / 2.75) * t + 0.75;
    } else if (t < 2.5 / 2.75) {
      return 7.5625 * (t -= 2.25 / 2.75) * t + 0.9375;
    } else {
      return 7.5625 * (t -= 2.625 / 2.75) * t + 0.984375;
    }
  },
};

export function animate(
  from: number,
  to: number,
  duration: number,
  easingFn: (t: number) => number = easing.easeOutCubic,
  onUpdate: (value: number) => void,
  onComplete?: () => void
): () => void {
  const startTime = performance.now();
  let rafId: number;

  const step = (currentTime: number) => {
    const elapsed = currentTime - startTime;
    const progress = Math.min(elapsed / duration, 1);
    const easedProgress = easingFn(progress);
    const value = from + (to - from) * easedProgress;

    onUpdate(value);

    if (progress < 1) {
      rafId = requestAnimationFrame(step);
    } else if (onComplete) {
      onComplete();
    }
  };

  rafId = requestAnimationFrame(step);

  return () => cancelAnimationFrame(rafId);
}

// Presets
export const springPresets = {
  default: { stiffness: 170, damping: 26, mass: 1 },
  gentle: { stiffness: 120, damping: 14, mass: 1 },
  wobbly: { stiffness: 180, damping: 12, mass: 1 },
  stiff: { stiffness: 210, damping: 20, mass: 1 },
  slow: { stiffness: 280, damping: 60, mass: 1 },
  molasses: { stiffness: 280, damping: 120, mass: 1 },
};
