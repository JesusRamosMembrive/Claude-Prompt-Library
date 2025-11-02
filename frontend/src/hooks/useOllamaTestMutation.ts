import { useMutation } from "@tanstack/react-query";

import { OllamaTestError, testOllamaChat } from "../api/client";
import type { OllamaTestPayload, OllamaTestResponse } from "../api/types";

export function useOllamaTestMutation() {
  return useMutation<OllamaTestResponse, OllamaTestError, OllamaTestPayload>({
    mutationFn: testOllamaChat,
  });
}
