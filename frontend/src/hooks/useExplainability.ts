import { useQuery } from '@tanstack/react-query';
import { dashboardService } from '../services/dashboardService';
import { ExplainTransactionResponse } from '../types/explain';

export const useExplainability = (transactionId: number = 42) => {
  const numericId = Number(transactionId);
  return useQuery<ExplainTransactionResponse>({
    queryKey: ['explainTransaction', numericId],
    queryFn: () => dashboardService.getExplain(numericId),
    staleTime: 0,
  });
};
