import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { apiService } from "../services/api";
import type { ResearchRequest, ResearchReportResponse } from "../types/research";

/**
 * Hook to manage active research tasks.
 * Tracks loading state, errors, and invalidates history queries on success.
 */
export const useResearch = () => {
  const queryClient = useQueryClient();

  const researchMutation = useMutation<ResearchReportResponse, Error, ResearchRequest>({
    mutationFn: (data: ResearchRequest) => apiService.runResearch(data),
    onSuccess: () => {
      // Refresh the report list query cache
      queryClient.invalidateQueries({ queryKey: ["reports"] });
    },
  });

  return {
    runResearch: researchMutation.mutateAsync,
    isProcessing: researchMutation.isPending,
    error: researchMutation.error,
    report: researchMutation.data,
  };
};

/**
 * Hook to fetch the complete research report history.
 */
export const useReports = () => {
  return useQuery<ResearchReportResponse[], Error>({
    queryKey: ["reports"],
    queryFn: () => apiService.getReports(),
  });
};

/**
 * Hook to fetch a single report's details by ID.
 */
export const useReport = (id: string) => {
  return useQuery<ResearchReportResponse | null, Error>({
    queryKey: ["report", id],
    queryFn: () => apiService.getReportById(id),
    enabled: !!id,
  });
};
