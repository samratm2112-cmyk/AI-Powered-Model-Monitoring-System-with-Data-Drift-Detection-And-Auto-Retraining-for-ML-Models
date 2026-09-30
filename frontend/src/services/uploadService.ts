import { apiClient } from './apiClient';

export interface CSVPreviewResponse {
  filename: string;
  row_count: number;
  column_count: number;
  columns: string[];
  preview_rows: Record<string, any>[];
  file_size_mb: number;
}

export interface ColumnStatistic {
  column: string;
  mean: number;
  std: number;
}

export interface TemplateInfoResponse {
  template_columns: string[];
  required_columns: string[];
  baseline_statistics: ColumnStatistic[];
}

export interface TransformPreviewResponse {
  preview_rows: Record<string, any>[];
  total_rows: number;
  mapped_columns: string[];
  smart_filled_columns: string[];
  mapped_count: number;
  smart_filled_count: number;
}

export interface UploadPipelineResponse {
  status: string;
  message: string;
  total_rows: number;
  mapped_columns: string[];
  smart_filled_columns: string[];
  pipeline_summary: Record<string, any> | null;
}

export const uploadService = {
  /**
   * Upload CSV and get a preview of its structure.
   */
  uploadCSVPreview: async (file: File): Promise<CSVPreviewResponse> => {
    const formData = new FormData();
    formData.append('file', file);
    const response = await apiClient.post<CSVPreviewResponse>('/upload/preview', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
      timeout: 30000,
    });
    return response.data;
  },

  /**
   * Get template column schema and baseline statistics.
   */
  getTemplateInfo: async (): Promise<TemplateInfoResponse> => {
    const response = await apiClient.get<TemplateInfoResponse>('/upload/template');
    return response.data;
  },

  /**
   * Transform uploaded CSV using column mapping and preview result.
   */
  transformCSV: async (
    file: File,
    mapping: Record<string, string | null>
  ): Promise<TransformPreviewResponse> => {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('column_mapping', JSON.stringify(mapping));
    const response = await apiClient.post<TransformPreviewResponse>('/upload/transform', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
      timeout: 30000,
    });
    return response.data;
  },

  /**
   * Transform CSV and execute the full monitoring pipeline.
   */
  executeUploadPipeline: async (
    file: File,
    mapping: Record<string, string | null>
  ): Promise<UploadPipelineResponse> => {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('column_mapping', JSON.stringify(mapping));
    const response = await apiClient.post<UploadPipelineResponse>('/upload/execute', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
      timeout: 120000, // 2-minute timeout for pipeline execution
    });
    return response.data;
  },
};
