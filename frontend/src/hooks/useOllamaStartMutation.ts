import { useMutation } from "@tanstack/react-query";

import { startOllama } from "../api/client";
import type { OllamaStartPayload, OllamaStartResponse } from "../api/types";

export function useOllamaStartMutation() {
  return useMutation<OllamaStartResponse, Error, OllamaStartPayload>({
    mutationFn: startOllama,
  });
}
