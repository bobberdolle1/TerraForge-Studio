/**
 * TerraForge Studio - TypeScript Types
 */

export interface BoundingBox {
  north: number;
  south: number;
  east: number;
  west: number;
}

// Helper function for BoundingBox
export function calculateArea(bbox: BoundingBox): number {
  // Approximate area in km² (simplified calculation)
  const latDiff = Math.abs(bbox.north - bbox.south);
  const lonDiff = Math.abs(bbox.east - bbox.west);
  const avgLat = (bbox.north + bbox.south) / 2;
  
  // 1 degree latitude ≈ 111 km
  // 1 degree longitude ≈ 111 km * cos(latitude)
  const kmLat = latDiff * 111;
  const kmLon = lonDiff * 111 * Math.cos(avgLat * Math.PI / 180);
  
  return kmLat * kmLon;
}

export type ExportFormat = 'unreal5' | 'unity' | 'gltf' | 'geotiff' | 'obj' | 'all' | 'ue5' | 'raw16' | 'kml';
export type ElevationSource = 'srtm' | 'opentopography' | 'sentinelhub' | 'azure_maps' | 'auto' | 'sentinel';

export interface TerrainGenerationRequest {
  bbox: BoundingBox;
  name: string;
  resolution?: number;
  export_formats: ExportFormat[];
  elevation_source: ElevationSource;
  enable_ai_analysis?: boolean;
  enable_roads?: boolean;
  enable_buildings?: boolean;
  enable_vegetation?: boolean;
  enable_water_bodies?: boolean;
  enable_weightmaps?: boolean;
  enable_3d_preview?: boolean;
}

export interface GenerationStatus {
  task_id: string;
  status: 'pending' | 'processing' | 'completed' | 'failed';
  progress: number;
  current_step: string;
  message?: string;
  error?: string;
  download_url?: string;
  thumbnail_base64?: string;
  result?: {
    terrain_name: string;
    resolution: number;
    area_km2: number;
    elevation_range: {
      min: number;
      max: number;
    };
    exports: Record<string, any>;
    output_directory: string;
    thumbnail?: string;
    thumbnail_base64?: string;
  };
}

export interface DataSource {
  name: string;
  resolution: string;
  coverage: string;
  cost: string;
  available: boolean;
  requires_api_key: boolean;
}

export interface ExportFormatInfo {
  name: string;
  description: string;
  files: string[];
  valid_resolutions: number[] | string;
  supports_weightmaps: boolean;
  supports_roads: boolean;
  supports_buildings: boolean;
}

export interface HealthStatus {
  status: string;
  version: string;
  data_sources: {
    available: string[];
    total: number;
  };
  settings: {
    max_area_km2: number;
    default_resolution: number;
  };
}

export interface SourcesResponse {
  elevation: Record<string, DataSource>;
  imagery: Record<string, DataSource>;
  vector: Record<string, DataSource>;
}

export interface FormatsResponse {
  formats: Record<string, ExportFormatInfo>;
}

