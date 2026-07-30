import { apiClient } from './apiClient';
import { DashboardData } from '../types/dashboard';

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
  }
};
