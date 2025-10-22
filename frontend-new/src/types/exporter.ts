/**
 * Exporter System Types
 * Support for multiple game engines and formats
 */

export type ExporterFormat = 
  | 'godot'
  | 'unity'
  | 'unreal'
  | 'cryengine'
  | 'gltf'
  | 'usdz'
  | 'geotiff'
  | 'png'
  | 'raw';

export type ExporterCategory = 
  | 'game-engine'
  | 'ar-vr'
  | 'gis'
  | 'image'
  | 'custom';

export interface ExporterConfig {
  format: ExporterFormat;
  category: ExporterCategory;
  name: string;
  description: string;
  icon?: string;
  version: string;
  fileExtension: string;
  mimeType: string;
  options: ExporterOption[];
  supports: {
    heightmap: boolean;
    texture: boolean;
    mesh: boolean;
    metadata: boolean;
  };
}

export interface ExporterOption {
  id: string;
  name: string;
  type: 'number' | 'string' | 'boolean' | 'select' | 'range';
  description: string;
  defaultValue: any;
  required?: boolean;
  min?: number;
  max?: number;
  options?: Array<{ label: string; value: any }>;
  unit?: string;
}

export interface ExportRequest {
  format: ExporterFormat;
  bbox: {
    north: number;
    south: number;
    east: number;
    west: number;
  };
  resolution: number;
  options: Record<string, any>;
}

export interface ExportResult {
  id: string;
  format: ExporterFormat;
  status: 'pending' | 'processing' | 'completed' | 'failed';
  progress?: number;
  downloadUrl?: string;
  fileSize?: number;
  createdAt: number;
  completedAt?: number;
  error?: string;
  metadata?: Record<string, any>;
}

export interface CustomExporter {
  id: string;
  name: string;
  description: string;
  author: string;
  version: string;
  category: ExporterCategory;
  config: ExporterConfig;
  execute: (request: ExportRequest) => Promise<ExportResult>;
  validate?: (request: ExportRequest) => boolean | string;
}
