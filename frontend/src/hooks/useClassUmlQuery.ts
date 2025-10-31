import { useQuery } from "@tanstack/react-query";

import { getClassUml, getClassUmlSvg } from "../api/client";
import { queryKeys } from "../api/queryKeys";

interface Options {
  includeExternal: boolean;
  modulePrefixes?: string[];
}

export function useClassUmlQuery(options: Options) {
  const { includeExternal, modulePrefixes } = options;
  const sortedPrefixes = modulePrefixes && modulePrefixes.length > 0 ? [...modulePrefixes].sort() : [];
  return useQuery({
    queryKey: queryKeys.classUml(includeExternal, sortedPrefixes),
    queryFn: async () => {
      const filteredPrefixes = sortedPrefixes.length === 0 ? undefined : sortedPrefixes;
      const [model, svg] = await Promise.all([
        getClassUml({
          includeExternal,
          modulePrefixes: filteredPrefixes,
        }),
        getClassUmlSvg({
          includeExternal,
          modulePrefixes: filteredPrefixes,
        }),
      ]);
      return {
        svg,
        stats: model.stats,
        classCount: model.classes.length,
      };
    },
    staleTime: 60_000,
  });
}
