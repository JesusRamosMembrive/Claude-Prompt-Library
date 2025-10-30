import { useQuery } from "@tanstack/react-query";

import { getClassGraph } from "../api/client";
import { queryKeys } from "../api/queryKeys";

export interface ClassGraphQueryOptions {
  includeExternal: boolean;
  edgeTypes: string[];
}

export function useClassGraphQuery(options: ClassGraphQueryOptions) {
  const { includeExternal, edgeTypes } = options;
  return useQuery({
    queryKey: queryKeys.classGraph(includeExternal, edgeTypes),
    queryFn: () =>
      getClassGraph({
        includeExternal,
        edgeTypes,
      }),
    staleTime: 60_000,
  });
}
