import { useQuery } from '@tanstack/react-query';
import { dashboardService } from '../services/dashboardService';

export const useDashboardData = () => {
  return useQuery({
    queryKey: ['dashboardData'],
    queryFn: dashboardService.getDashboardData,
    refetchInterval: 15000,
    staleTime: 5000,
  });
};
