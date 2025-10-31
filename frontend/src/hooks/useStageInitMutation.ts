import { useMutation, useQueryClient } from "@tanstack/react-query";

import { initializeStageToolkit } from "../api/client";
import type { StageInitPayload, StageInitResponse } from "../api/types";
import { queryKeys } from "../api/queryKeys";

export function useStageInitMutation() {
  const queryClient = useQueryClient();

  return useMutation<StageInitResponse, Error, StageInitPayload>({
    mutationFn: initializeStageToolkit,
    onSuccess: (result) => {
      queryClient.setQueryData(queryKeys.stageStatus, result.status);
    },
  });
}
