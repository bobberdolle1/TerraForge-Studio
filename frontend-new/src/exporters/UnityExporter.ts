import type { ExporterConfig, ExportRequest, ExportResult } from '../types/exporter';

/**
 * Unity Engine Exporter
 * Exports terrain data in Unity-compatible format
 * Supports: Terrain Asset, RAW heightmap, Texture arrays
 */

export const UnityExporterConfig: ExporterConfig = {
  format: 'unity',
  category: 'game-engine',
  name: 'Unity Engine',
  description: 'Export terrain for Unity with Terrain Asset support',
  version: '1.0.0',
  fileExtension: '.raw',
  mimeType: 'application/octet-stream',
  supports: {
    heightmap: true,
    texture: true,
    mesh: false,
    metadata: true,
  },
  options: [
    {
      id: 'heightmapResolution',
      name: 'Heightmap Resolution',
      type: 'select',
      description: 'Terrain heightmap resolution (must be 2^n + 1)',
      defaultValue: 513,
      options: [
        { label: '257 x 257', value: 257 },
        { label: '513 x 513', value: 513 },
        { label: '1025 x 1025', value: 1025 },
        { label: '2049 x 2049', value: 2049 },
      ],
    },
    {
      id: 'heightScale',
      name: 'Height Scale',
      type: 'number',
      description: 'Unity terrain height (in meters)',
      defaultValue: 600,
      min: 1,
      max: 10000,
      unit: 'm',
    },
    {
      id: 'bitDepth',
      name: 'Bit Depth',
      type: 'select',
      description: 'RAW file bit depth',
      defaultValue: 16,
      options: [
        { label: '8-bit', value: 8 },
        { label: '16-bit', value: 16 },
      ],
    },
    {
      id: 'byteOrder',
      name: 'Byte Order',
      type: 'select',
      description: 'Endianness for 16-bit RAW',
      defaultValue: 'windows',
      options: [
        { label: 'Windows (Little Endian)', value: 'windows' },
        { label: 'Mac (Big Endian)', value: 'mac' },
      ],
    },
    {
      id: 'exportSplatmap',
      name: 'Export Splatmap',
      type: 'boolean',
      description: 'Generate texture splatmap for terrain layers',
      defaultValue: false,
    },
  ],
};

export class UnityExporter {
  async export(request: ExportRequest): Promise<ExportResult> {
    const startTime = Date.now();
    
    try {
      if (!this.validate(request)) {
        throw new Error('Invalid export request');
      }

      const rawData = this.generateRAWHeightmap(request);

      const result: ExportResult = {
        id: `unity-${Date.now()}`,
        format: 'unity',
        status: 'completed',
        progress: 100,
        fileSize: rawData.byteLength,
        createdAt: startTime,
        completedAt: Date.now(),
        metadata: {
          resolution: request.options.heightmapResolution || 513,
          heightScale: request.options.heightScale || 600,
          bitDepth: request.options.bitDepth || 16,
          byteOrder: request.options.byteOrder || 'windows',
        },
      };

      return result;
    } catch (error) {
      return {
        id: `unity-${Date.now()}`,
        format: 'unity',
        status: 'failed',
        createdAt: startTime,
        error: error instanceof Error ? error.message : 'Unknown error',
      };
    }
  }

  validate(request: ExportRequest): boolean {
    if (!request.bbox) return false;
    
    const resolution = request.options.heightmapResolution || 513;
    // Unity requires 2^n + 1 resolution
    const validResolutions = [33, 65, 129, 257, 513, 1025, 2049, 4097];
    if (!validResolutions.includes(resolution)) {
      return false;
    }
    
    return true;
  }

  private generateRAWHeightmap(request: ExportRequest): ArrayBuffer {
    const resolution = request.options.heightmapResolution || 513;
    const bitDepth = request.options.bitDepth || 16;
    const byteOrder = request.options.byteOrder || 'windows';
    
    const totalPixels = resolution * resolution;
    const buffer = new ArrayBuffer(totalPixels * (bitDepth / 8));
    
    if (bitDepth === 16) {
      const view = new DataView(buffer);
      const littleEndian = byteOrder === 'windows';
      
      // Generate placeholder heightmap data
      for (let i = 0; i < totalPixels; i++) {
        // This would be replaced with actual terrain data
        const height = Math.floor(Math.random() * 65535);
        view.setUint16(i * 2, height, littleEndian);
      }
    } else {
      const view = new Uint8Array(buffer);
      for (let i = 0; i < totalPixels; i++) {
        view[i] = Math.floor(Math.random() * 255);
      }
    }
    
    return buffer;
  }
}

export default new UnityExporter();
