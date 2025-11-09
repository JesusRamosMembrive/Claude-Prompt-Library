import { useQuery } from "@tanstack/react-query";

import { getLintersReports } from "../api/client";
import { queryKeys } from "../api/queryKeys";

export function useLintersReports(limit = 20, offset = 0) {
  return useQuery({
    queryKey: queryKeys.lintersReports(limit, offset),
    queryFn: () => getLintersReports(limit, offset),
    staleTime: 30_000,
  });
}
