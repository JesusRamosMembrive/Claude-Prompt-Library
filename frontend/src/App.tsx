import { useState } from "react";
import { useQuery } from "@tanstack/react-query";

import { getSettings, getStatus } from "./api/client";
import { queryKeys } from "./api/queryKeys";
import { HeaderBar } from "./components/HeaderBar";
import { Dashboard } from "./components/Dashboard";
import { SettingsView } from "./components/SettingsView";
import { useEventStream } from "./hooks/useEventStream";
import "./styles.css";

export function App(): JSX.Element {
  const [view, setView] = useState<"dashboard" | "settings">("dashboard");
  const settingsQuery = useQuery({
    queryKey: queryKeys.settings,
    queryFn: getSettings,
    staleTime: 30_000,
  });
  const statusQuery = useQuery({
    queryKey: queryKeys.status,
    queryFn: getStatus,
    refetchInterval: 10_000,
    staleTime: 5_000,
  });
  useEventStream();

  const watcherActive = statusQuery.data?.watcher_active ?? true;
  const rootPath = statusQuery.data?.root_path ?? settingsQuery.data?.root_path;

  return (
    <div className="app-root">
      {view === "dashboard" ? (
        <>
          <HeaderBar
            onOpenSettings={() => setView("settings")}
            watcherActive={watcherActive}
            rootPath={rootPath}
            lastFullScan={statusQuery.data?.last_full_scan}
            filesIndexed={statusQuery.data?.files_indexed}
          />
          <Dashboard statusQuery={statusQuery} />
        </>
      ) : (
        <SettingsView
          onBack={() => setView("dashboard")}
          settingsQuery={settingsQuery}
        />
      )}
    </div>
  );
}
