import { useQuery } from "@tanstack/react-query";

import { getLintersNotifications } from "../api/client";
import { queryKeys } from "../api/queryKeys";

export function useLintersNotifications(unreadOnly = false, limit = 50) {
  return useQuery({
    queryKey: queryKeys.lintersNotifications(unreadOnly),
    queryFn: () => getLintersNotifications(limit, unreadOnly),
    staleTime: unreadOnly ? 5_000 : 15_000,
  });
}
