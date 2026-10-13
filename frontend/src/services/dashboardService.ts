import { apiClient } from './apiClient';
import { DashboardData } from '../types/dashboard';
import { DeploymentStatusResponse, DeploymentApproveResponse, SystemHealthResponse } from '../types/governance';
import { ExplainTransactionResponse } from '../types/explain';

export const dashboardService = {
  getDashboardData: async (): Promise<DashboardData> => {
    const response = await apiClient.get<DashboardData>('/dashboard');
    return response.data;
  },
  getLogsJson: async (): Promise<any> => {
    const response = await apiClient.get<any>('/logs');
    return response.data;
  },
  getRetrainingLogText: async (): Promise<string> => {
    const response = await apiClient.get<string>('/retraining-log', { responseType: 'text' });
    return response.data;
  },
  runMonitoring: async (): Promise<void> => {
    await apiClient.post('/run-monitoring');
  },
  // SHAP Explainability API
  getExplain: async (transactionId: number = 42): Promise<ExplainTransactionResponse> => {
    const response = await apiClient.get<ExplainTransactionResponse>(`/api/explain/${Number(transactionId)}`);
    return response.data;
  },
  // HITL Governance APIs
  getDeploymentStatus: async (): Promise<DeploymentStatusResponse> => {
    const response = await apiClient.get<DeploymentStatusResponse>('/deployment/status');
    return response.data;
  },
  approveDeployment: async (reviewer?: string, notes?: string): Promise<DeploymentApproveResponse> => {
    const response = await apiClient.post<DeploymentApproveResponse>('/deployment/approve', {
      reviewer: reviewer || 'Human Compliance Officer',
      notes: notes || 'Approved via MLOps Governance Portal'
    });
    return response.data;
  },
  rejectDeployment: async (reviewer?: string, notes?: string): Promise<any> => {
    const response = await apiClient.post<any>('/deployment/reject', {
      reviewer: reviewer || 'Human Compliance Officer',
      notes: notes || 'Rejected by human reviewer'
    });
    return response.data;
  },
  // Ensemble & System Health API
  getSystemHealth: async (): Promise<SystemHealthResponse> => {
    const response = await apiClient.get<SystemHealthResponse>('/system/health');
    return response.data;
  }
};
