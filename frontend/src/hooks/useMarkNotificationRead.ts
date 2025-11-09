import { useMutation, useQueryClient } from "@tanstack/react-query";

import { markNotificationAsRead } from "../api/client";
import { queryKeys } from "../api/queryKeys";

interface MarkNotificationArgs {
  id: number;
  read?: boolean;
}

export function useMarkNotificationRead() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ id, read = true }: MarkNotificationArgs) =>
      markNotificationAsRead(id, read),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.lintersNotifications(false) });
      queryClient.invalidateQueries({ queryKey: queryKeys.lintersNotifications(true) });
      queryClient.invalidateQueries({ queryKey: queryKeys.lintersLatest });
      queryClient.invalidateQueries({
        predicate: (query) => Array.isArray(query.queryKey) && query.queryKey[0] === "linters",
      });
    },
  });
}
