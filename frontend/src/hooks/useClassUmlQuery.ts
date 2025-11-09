import { useQuery } from "@tanstack/react-query";

import { useEffect, useRef, useMemo } from "react";
import { getClassUml, getClassUmlSvg } from "../api/client";
import { queryKeys } from "../api/queryKeys";
import type { GraphvizOptionsPayload } from "../api/types";

interface Options {
  includeExternal: boolean;
  modulePrefixes?: string[];
  edgeTypes?: string[];
  graphvizOptions?: GraphvizOptionsPayload;
  graphvizSignature?: string;
}

export function useClassUmlQuery(options: Options) {
  const { includeExternal, modulePrefixes, edgeTypes, graphvizOptions, graphvizSignature } =
    options;
  const sortedPrefixes =
    modulePrefixes && modulePrefixes.length > 0 ? [...modulePrefixes].sort() : [];
  const sortedEdgeTypes = edgeTypes && edgeTypes.length > 0 ? [...edgeTypes].sort() : [];

  const graphvizOptionsRef = useRef<GraphvizOptionsPayload | undefined>(graphvizOptions);
  useEffect(() => {
    graphvizOptionsRef.current = graphvizOptions;
  }, [graphvizOptions]);

  const queryKey = useMemo(
    () =>
      queryKeys.classUml(
        includeExternal,
        sortedPrefixes,
        sortedEdgeTypes,
        graphvizSignature ?? "",
      ),
    [includeExternal, sortedPrefixes, sortedEdgeTypes, graphvizSignature],
  );

  return useQuery({
    queryKey,
    queryFn: async () => {
      const filteredPrefixes = sortedPrefixes.length === 0 ? undefined : sortedPrefixes;
      const filteredEdgeTypes = sortedEdgeTypes.length === 0 ? undefined : sortedEdgeTypes;
      const currentGraphviz = graphvizOptionsRef.current;

      const [model, svg] = await Promise.all([
        getClassUml({
          includeExternal,
          modulePrefixes: filteredPrefixes,
          edgeTypes: filteredEdgeTypes,
          graphvizOptions: currentGraphviz,
        }),
        getClassUmlSvg({
          includeExternal,
          modulePrefixes: filteredPrefixes,
          edgeTypes: filteredEdgeTypes,
          graphvizOptions: currentGraphviz,
        }),
      ]);
      return {
        svg,
        stats: model.stats,
        classCount: model.classes.length,
        classes: model.classes,
      };
    },
    staleTime: 60_000,
  });
}

export function buildGraphvizSignature(options?: GraphvizOptionsPayload): string {
  if (!options) {
    return "";
  }
  // Sort keys to ensure consistent signature across same options
  const sortedKeys = Object.keys(options).sort();
  const sortedOptions: Record<string, unknown> = {};
  for (const key of sortedKeys) {
    sortedOptions[key] = options[key as keyof GraphvizOptionsPayload];
  }
  return JSON.stringify(sortedOptions);
}
