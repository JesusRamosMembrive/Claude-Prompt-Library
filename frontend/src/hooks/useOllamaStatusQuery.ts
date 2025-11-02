import { useQuery } from "@tanstack/react-query";

import { getOllamaStatus } from "../api/client";
import type { OllamaStatusPayload } from "../api/types";

const OLLAMA_STATUS_QUERY_KEY = ["ollama-status"];

export function useOllamaStatusQuery() {
  return useQuery<OllamaStatusPayload, Error>({
    queryKey: OLLAMA_STATUS_QUERY_KEY,
    queryFn: getOllamaStatus,
    staleTime: 30_000,
  });
}
