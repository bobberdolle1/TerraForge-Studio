import type { ExporterConfig, ExporterFormat, CustomExporter } from '../types/exporter';
import { GodotExporterConfig } from './GodotExporter';
import { UnityExporterConfig } from './UnityExporter';
import { UnrealExporterConfig } from './UnrealExporter';

/**
 * Exporter Registry
 * Central registry for all available exporters
 */

class ExporterRegistry {
  private exporters: Map<ExporterFormat, ExporterConfig> = new Map();
  private customExporters: Map<string, CustomExporter> = new Map();

  constructor() {
    this.registerDefaultExporters();
  }

  private registerDefaultExporters() {
    // Register built-in exporters
    this.register(GodotExporterConfig);
    this.register(UnityExporterConfig);
    this.register(UnrealExporterConfig);
    
    // Additional exporters can be registered here
    // this.register(CryEngineExporterConfig);
    // this.register(GLTFExporterConfig);
  }

  register(config: ExporterConfig) {
    this.exporters.set(config.format, config);
  }

  registerCustom(exporter: CustomExporter) {
    this.customExporters.set(exporter.id, exporter);
  }

  unregister(format: ExporterFormat) {
    this.exporters.delete(format);
  }

  unregisterCustom(id: string) {
    this.customExporters.delete(id);
  }

  get(format: ExporterFormat): ExporterConfig | undefined {
    return this.exporters.get(format);
  }

  getCustom(id: string): CustomExporter | undefined {
    return this.customExporters.get(id);
  }

  getAll(): ExporterConfig[] {
    return Array.from(this.exporters.values());
  }

  getAllCustom(): CustomExporter[] {
    return Array.from(this.customExporters.values());
  }

  getByCategory(category: string): ExporterConfig[] {
    return this.getAll().filter((e) => e.category === category);
  }

  isSupported(format: ExporterFormat): boolean {
    return this.exporters.has(format);
  }

  getFormats(): ExporterFormat[] {
    return Array.from(this.exporters.keys());
  }
}

export const exporterRegistry = new ExporterRegistry();
export default exporterRegistry;
