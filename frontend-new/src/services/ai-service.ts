/**
 * AI Service - Smart Recommendations
 * Basic ML-powered features for terrain generation
 */

interface LocationHistory {
  bbox: { north: number; south: number; east: number; west: number };
  timestamp: number;
  success: boolean;
}

export class AIService {
  private history: LocationHistory[] = [];

  recordGeneration(bbox: any, success: boolean) {
    this.history.push({
      bbox,
      timestamp: Date.now(),
      success,
    });
    
    // Keep only last 100 entries
    if (this.history.length > 100) {
      this.history = this.history.slice(-100);
    }
  }

  getRecommendations(): Array<{ name: string; bbox: any; score: number }> {
    // Simple recommendation based on successful generations
    const successfulAreas = this.history.filter(h => h.success);
    
    return [
      {
        name: 'Similar to your recent success',
        bbox: successfulAreas[successfulAreas.length - 1]?.bbox,
        score: 0.9,
      },
    ].filter(r => r.bbox);
  }
}

export const aiService = new AIService();
