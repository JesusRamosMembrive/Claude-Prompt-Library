import { useMemo } from "react";
import { useQuery } from "@tanstack/react-query";

import { getSettings, getStatus } from "../api/client";
import { queryKeys } from "../api/queryKeys";

export function useAppQueries() {
  const settingsQuery = useQuery({
    queryKey: queryKeys.settings,
    queryFn: getSettings,
    staleTime: 30_000,
  });

  const statusQuery = useQuery({
    queryKey: queryKeys.status,
    queryFn: getStatus,
    refetchInterval: 10_000,
    staleTime: 5_000,
  });

  const summary = useMemo(() => {
    const rootPath = statusQuery.data?.root_path ?? settingsQuery.data?.root_path ?? "";
    const watcherActive = statusQuery.data?.watcher_active ?? false;
    const includeDocstrings =
      settingsQuery.data?.include_docstrings ?? statusQuery.data?.include_docstrings ?? true;
    return {
      rootPath,
      watcherActive,
      includeDocstrings,
    };
  }, [settingsQuery.data, statusQuery.data]);

  return {
    settingsQuery,
    statusQuery,
    summary,
  };
}
