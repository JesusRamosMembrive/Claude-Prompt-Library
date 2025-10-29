import { useEffect } from "react";
import { useQueryClient } from "@tanstack/react-query";

import { getEventsUrl } from "../api/client";
import { queryKeys } from "../api/queryKeys";
import type { ChangeNotification } from "../api/types";
import { useActivityStore } from "../state/useActivityStore";

export function useEventStream(): void {
  const queryClient = useQueryClient();
  const pushActivity = useActivityStore((state) => state.push);

  useEffect(() => {
    const url = getEventsUrl();
    const eventSource = new EventSource(url);

    const handleUpdate = (event: MessageEvent<string>) => {
      try {
        const payload = JSON.parse(event.data) as ChangeNotification;
        queryClient.invalidateQueries({ queryKey: queryKeys.tree });

        payload.updated?.forEach((path) => {
          queryClient.invalidateQueries({ queryKey: queryKeys.file(path) });
        });

        payload.deleted?.forEach((path) => {
          queryClient.removeQueries({ queryKey: queryKeys.file(path) });
        });

        const timestamp = Date.now();
        const activityRecords = [
          ...(payload.updated ?? []).map((path) => ({
            path,
            type: "updated" as const,
            timestamp,
          })),
          ...(payload.deleted ?? []).map((path) => ({
            path,
            type: "deleted" as const,
            timestamp,
          })),
        ];
        pushActivity(activityRecords);
      } catch (error) {
        console.warn("Failed to parse update event", error);
      }
    };

    eventSource.addEventListener("update", handleUpdate as EventListener);
    eventSource.onerror = () => {
      console.warn("EventSource connection lost, retrying…");
    };

    return () => {
      eventSource.removeEventListener("update", handleUpdate as EventListener);
      eventSource.close();
    };
  }, [pushActivity, queryClient]);
}
