import { useEffect } from "react";
import { useQueryClient } from "@tanstack/react-query";

import { getEventsUrl } from "../api/client";
import { queryKeys } from "../api/queryKeys";
import type { ChangeNotification } from "../api/types";
import { useActivityStore } from "../state/useActivityStore";

/**
 * Hook para manejar el stream de eventos SSE del servidor.
 *
 * Establece y mantiene una conexión EventSource para recibir notificaciones
 * de cambios en el proyecto en tiempo real. Invalida queries de React Query
 * y actualiza el store de actividad automáticamente.
 *
 * Returns:
 *     void (side-effects only)
 *
 * Side Effects:
 *     - Invalida queryKeys.tree cuando hay cambios
 *     - Invalida queryKeys.file(path) para archivos actualizados
 *     - Invalida queryKeys.preview(path) para archivos actualizados
 *     - Remueve queries de archivos eliminados
 *     - Añade registros al store de actividad
 *
 * Notes:
 *     - Conexión se establece en mount, se cierra en unmount
 *     - EventSource reconecta automáticamente en errores
 *     - Warnings en console si falla el parseo de eventos
 *     - Único listener: "update" event con ChangeNotification payload
 *
 * Usage:
 *     // En App.tsx o layout principal
 *     useEventStream();
 */
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
          queryClient.invalidateQueries({ queryKey: queryKeys.preview(path) });
        });

        payload.deleted?.forEach((path) => {
          queryClient.removeQueries({ queryKey: queryKeys.file(path) });
          queryClient.removeQueries({ queryKey: queryKeys.preview(path) });
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
