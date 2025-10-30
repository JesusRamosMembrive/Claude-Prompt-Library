import { useQuery } from "@tanstack/react-query";

import { getStatus } from "../api/client";
import { queryKeys } from "../api/queryKeys";

export function useStatusQuery() {
  return useQuery({
    queryKey: queryKeys.status,
    queryFn: getStatus,
    refetchInterval: 10_000,
    staleTime: 5_000,
  });
}
