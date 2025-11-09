import { useQuery } from "@tanstack/react-query";

import { getLintersLatestReport } from "../api/client";
import { queryKeys } from "../api/queryKeys";

export function useLintersLatestReport() {
  return useQuery({
    queryKey: queryKeys.lintersLatest,
    queryFn: getLintersLatestReport,
    refetchInterval: 15_000,
    staleTime: 10_000,
    retry: false,
  });
}
