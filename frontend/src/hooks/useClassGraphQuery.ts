import { useQuery } from "@tanstack/react-query";

import { getClassGraph } from "../api/client";
import { queryKeys } from "../api/queryKeys";

export interface ClassGraphQueryOptions {
  includeExternal: boolean;
  edgeTypes: string[];
  modulePrefixes?: string[];
}

export function useClassGraphQuery(options: ClassGraphQueryOptions) {
  const { includeExternal, edgeTypes, modulePrefixes } = options;
  return useQuery({
    queryKey: queryKeys.classGraph(includeExternal, edgeTypes, modulePrefixes),
    queryFn: () =>
      getClassGraph({
        includeExternal,
        edgeTypes,
        modulePrefixes,
      }),
    staleTime: 60_000,
  });
}
