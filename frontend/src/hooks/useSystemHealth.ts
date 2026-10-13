import { useQuery } from '@tanstack/react-query';
import { dashboardService } from '../services/dashboardService';
import { SystemHealthResponse } from '../types/governance';

export const useSystemHealth = () => {
  return useQuery<SystemHealthResponse>({
    queryKey: ['systemHealth'],
    queryFn: dashboardService.getSystemHealth,
    refetchInterval: 10000,
    refetchOnWindowFocus: true,
  });
};
