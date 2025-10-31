import { useQuery } from "@tanstack/react-query";

import { getSettings } from "../api/client";
import { queryKeys } from "../api/queryKeys";

export function useSettingsQuery() {
  return useQuery({
    queryKey: queryKeys.settings,
    queryFn: getSettings,
    staleTime: 30_000,
  });
}
