import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { dashboardService } from '../services/dashboardService';
import { DeploymentStatusResponse, DeploymentApproveResponse } from '../types/governance';

export const useDeploymentStatus = () => {
  const queryClient = useQueryClient();

  const query = useQuery<DeploymentStatusResponse>({
    queryKey: ['deploymentStatus'],
    queryFn: dashboardService.getDeploymentStatus,
    refetchInterval: 5000, // Poll every 5 seconds for real-time human-in-the-loop alerts
    refetchOnWindowFocus: true,
  });

  const approveMutation = useMutation<DeploymentApproveResponse, Error, { reviewer?: string; notes?: string }>({
    mutationFn: ({ reviewer, notes }) => dashboardService.approveDeployment(reviewer, notes),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['deploymentStatus'] });
      queryClient.invalidateQueries({ queryKey: ['systemHealth'] });
      queryClient.invalidateQueries({ queryKey: ['dashboard'] });
    },
  });

  const rejectMutation = useMutation<any, Error, { reviewer?: string; notes?: string }>({
    mutationFn: ({ reviewer, notes }) => dashboardService.rejectDeployment(reviewer, notes),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['deploymentStatus'] });
      queryClient.invalidateQueries({ queryKey: ['dashboard'] });
    },
  });

  return {
    ...query,
    approveDeployment: approveMutation.mutateAsync,
    rejectDeployment: rejectMutation.mutateAsync,
    isApproving: approveMutation.isPending,
    isRejecting: rejectMutation.isPending,
  };
};
