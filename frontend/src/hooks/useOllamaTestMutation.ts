import { useMutation } from "@tanstack/react-query";

import { testOllamaChat } from "../api/client";
import type { OllamaTestError } from "../api/client";
import type { OllamaTestPayload, OllamaTestResponse } from "../api/types";

export function useOllamaTestMutation() {
  return useMutation<OllamaTestResponse, OllamaTestError, OllamaTestPayload>({
    mutationFn: testOllamaChat,
  });
}
