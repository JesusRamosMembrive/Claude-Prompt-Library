import { useQuery } from "@tanstack/react-query";

interface CommitInfo {
  hash: string;
  author: string;
  date: string;
  message: string;
  files_changed: string[];
}

interface TimelineSummaryResponse {
  total_commits: number;
  total_files: number;
  latest_commit: CommitInfo | null;
  active_files_count: number;
}

export function useTimelineSummary() {
  return useQuery<TimelineSummaryResponse>({
    queryKey: ["timeline-summary"],
    queryFn: async () => {
      const response = await fetch("/api/timeline/matrix?limit=10");
      if (!response.ok) {
        throw new Error(`Failed to fetch timeline summary: ${response.statusText}`);
      }
      const data = await response.json();

      return {
        total_commits: data.total_commits ?? 0,
        total_files: data.total_files ?? 0,
        latest_commit: data.commits && data.commits.length > 0 ? data.commits[0] : null,
        active_files_count: data.files ? data.files.length : 0,
      };
    },
    refetchInterval: 30_000,
    staleTime: 20_000,
    retry: false,
  });
}
