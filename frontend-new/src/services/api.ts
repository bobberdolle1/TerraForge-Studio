/**
 * TerraForge Studio - API Service
 */

import axios from 'axios';
import type {
  TerrainGenerationRequest,
  GenerationStatus,
  HealthStatus,
  SourcesResponse,
  FormatsResponse,
} from '@/types';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const terraforgeApi = {
  // Health check
  getHealth: async (): Promise<HealthStatus> => {
    const response = await api.get<HealthStatus>('/api/health');
    return response.data;
  },

  // Get available data sources
  getSources: async (): Promise<SourcesResponse> => {
    const response = await api.get<SourcesResponse>('/api/sources');
    return response.data;
  },

  // Get available export formats
  getFormats: async (): Promise<FormatsResponse> => {
    const response = await api.get<FormatsResponse>('/api/formats');
    return response.data;
  },

  // Generate terrain
  generateTerrain: async (request: TerrainGenerationRequest): Promise<GenerationStatus> => {
    const response = await api.post<GenerationStatus>('/api/generate', request);
    return response.data;
  },

  // Get generation status
  getStatus: async (taskId: string): Promise<GenerationStatus> => {
    const response = await api.get<GenerationStatus>(`/api/status/${taskId}`);
    return response.data;
  },

  // List all tasks
  listTasks: async (): Promise<GenerationStatus[]> => {
    const response = await api.get<GenerationStatus[]>('/api/tasks');
    return response.data;
  },

  // Download exported file
  downloadFile: (taskId: string, filename: string): string => {
    return `${API_BASE_URL}/api/download/${taskId}/${filename}`;
  },
};

export default terraforgeApi;

