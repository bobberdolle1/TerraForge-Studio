/**
 * TerraForge Studio - TypeScript Types
 */

export interface BoundingBox {
  north: number;
  south: number;
  east: number;
  west: number;
}

export type ExportFormat = 'unreal5' | 'unity' | 'gltf' | 'geotiff' | 'obj' | 'all';
export type ElevationSource = 'srtm' | 'opentopography' | 'sentinelhub' | 'azure_maps' | 'auto';

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

