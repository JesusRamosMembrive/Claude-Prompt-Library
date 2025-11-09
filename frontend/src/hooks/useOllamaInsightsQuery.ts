import { useQuery } from "@tanstack/react-query";

import { getOllamaInsights } from "../api/client";
import { queryKeys } from "../api/queryKeys";

export function useOllamaInsightsQuery(limit = 10) {
  return useQuery({
    queryKey: queryKeys.ollamaInsights(limit),
    queryFn: () => getOllamaInsights(limit),
    staleTime: 60_000,
  });
}
