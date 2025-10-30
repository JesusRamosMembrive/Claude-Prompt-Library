import { useQuery } from "@tanstack/react-query";

import { getStageStatus } from "../api/client";
import { queryKeys } from "../api/queryKeys";

export function useStageStatusQuery() {
  return useQuery({
    queryKey: queryKeys.stageStatus,
    queryFn: getStageStatus,
    staleTime: 60_000,
    refetchOnWindowFocus: false,
  });
}
