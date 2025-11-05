import { useQuery } from "@tanstack/react-query";

import { getClassUml, getClassUmlSvg } from "../api/client";
import { queryKeys } from "../api/queryKeys";

interface Options {
  includeExternal: boolean;
  modulePrefixes?: string[];
  edgeTypes?: string[];
}

export function useClassUmlQuery(options: Options) {
  const { includeExternal, modulePrefixes, edgeTypes } = options;
  const sortedPrefixes = modulePrefixes && modulePrefixes.length > 0 ? [...modulePrefixes].sort() : [];
  const sortedEdgeTypes = edgeTypes && edgeTypes.length > 0 ? [...edgeTypes].sort() : [];

  return useQuery({
    queryKey: queryKeys.classUml(includeExternal, sortedPrefixes, sortedEdgeTypes),
    queryFn: async () => {
      const filteredPrefixes = sortedPrefixes.length === 0 ? undefined : sortedPrefixes;
      const filteredEdgeTypes = sortedEdgeTypes.length === 0 ? undefined : sortedEdgeTypes;

      const [model, svg] = await Promise.all([
        getClassUml({
          includeExternal,
          modulePrefixes: filteredPrefixes,
          edgeTypes: filteredEdgeTypes,
        }),
        getClassUmlSvg({
          includeExternal,
          modulePrefixes: filteredPrefixes,
          edgeTypes: filteredEdgeTypes,
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
