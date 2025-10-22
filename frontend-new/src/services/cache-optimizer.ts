/**
 * Cache Optimization System
 * Intelligent caching with LRU eviction and size limits
 */

interface CacheEntry<T> {
  key: string;
  value: T;
  size: number;
  lastAccessed: number;
  accessCount: number;
  createdAt: number;
}

interface CacheStats {
  hits: number;
  misses: number;
  evictions: number;
  totalSize: number;
  entryCount: number;
}

export class CacheOptimizer<T = any> {
  private cache: Map<string, CacheEntry<T>> = new Map();
  private maxSize: number;
  private maxAge: number;
  private stats: CacheStats = {
    hits: 0,
    misses: 0,
    evictions: 0,
    totalSize: 0,
    entryCount: 0,
  };

  constructor(
    maxSize: number = 100 * 1024 * 1024, // 100 MB default
    maxAge: number = 3600000 // 1 hour default
  ) {
    this.maxSize = maxSize;
    this.maxAge = maxAge;
  }

  set(key: string, value: T, size?: number): void {
    const entrySize = size || this.estimateSize(value);
    
    // Evict if necessary
    while (this.stats.totalSize + entrySize > this.maxSize && this.cache.size > 0) {
      this.evictLRU();
    }

    // Remove old entry if exists
    if (this.cache.has(key)) {
      const old = this.cache.get(key)!;
      this.stats.totalSize -= old.size;
    }

    const entry: CacheEntry<T> = {
      key,
      value,
      size: entrySize,
      lastAccessed: Date.now(),
      accessCount: 0,
      createdAt: Date.now(),
    };

    this.cache.set(key, entry);
    this.stats.totalSize += entrySize;
    this.stats.entryCount = this.cache.size;
  }

  get(key: string): T | undefined {
    const entry = this.cache.get(key);

    if (!entry) {
      this.stats.misses++;
      return undefined;
    }

    // Check if expired
    if (Date.now() - entry.createdAt > this.maxAge) {
      this.delete(key);
      this.stats.misses++;
      return undefined;
    }

    // Update access info
    entry.lastAccessed = Date.now();
    entry.accessCount++;
    this.stats.hits++;

    return entry.value;
  }

  has(key: string): boolean {
    return this.cache.has(key);
  }

  delete(key: string): boolean {
    const entry = this.cache.get(key);
    if (entry) {
      this.stats.totalSize -= entry.size;
      this.stats.entryCount--;
      return this.cache.delete(key);
    }
    return false;
  }

  clear(): void {
    this.cache.clear();
    this.stats.totalSize = 0;
    this.stats.entryCount = 0;
  }

  getStats(): CacheStats {
    return { ...this.stats };
  }

  getHitRate(): number {
    const total = this.stats.hits + this.stats.misses;
    return total > 0 ? this.stats.hits / total : 0;
  }

  private evictLRU(): void {
    let oldest: CacheEntry<T> | null = null;
    let oldestKey: string | null = null;

    for (const [key, entry] of this.cache.entries()) {
      if (!oldest || entry.lastAccessed < oldest.lastAccessed) {
        oldest = entry;
        oldestKey = key;
      }
    }

    if (oldestKey) {
      this.delete(oldestKey);
      this.stats.evictions++;
    }
  }

  private estimateSize(value: T): number {
    try {
      const str = JSON.stringify(value);
      return str.length * 2; // UTF-16 encoding
    } catch {
      return 1024; // Default 1KB if can't serialize
    }
  }

  // Clean up expired entries
  cleanup(): void {
    const now = Date.now();
    for (const [key, entry] of this.cache.entries()) {
      if (now - entry.createdAt > this.maxAge) {
        this.delete(key);
      }
    }
  }

  // Get top N most accessed items
  getPopular(n: number = 10): Array<{ key: string; accessCount: number }> {
    return Array.from(this.cache.values())
      .sort((a, b) => b.accessCount - a.accessCount)
      .slice(0, n)
      .map(entry => ({
        key: entry.key,
        accessCount: entry.accessCount,
      }));
  }
}

// Global cache instance
export const terrainCache = new CacheOptimizer(100 * 1024 * 1024); // 100 MB
export const exportCache = new CacheOptimizer(50 * 1024 * 1024); // 50 MB

// Periodic cleanup
if (typeof window !== 'undefined') {
  setInterval(() => {
    terrainCache.cleanup();
    exportCache.cleanup();
  }, 300000); // Every 5 minutes
}
