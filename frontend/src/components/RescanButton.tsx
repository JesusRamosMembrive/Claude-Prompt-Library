import { useMutation, useQueryClient } from "@tanstack/react-query";

import { triggerRescan } from "../api/client";
import { queryKeys } from "../api/queryKeys";

export function RescanButton(): JSX.Element {
  const queryClient = useQueryClient();
  const mutation = useMutation({
    mutationFn: triggerRescan,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.tree });
    },
  });

  return (
    <button
      className="primary-btn"
      type="button"
      onClick={() => mutation.mutate()}
      disabled={mutation.isPending}
      aria-live="polite"
    >
      {mutation.isPending ? "Re-escaneando…" : "Re-escaneo manual"}
    </button>
  );
}
