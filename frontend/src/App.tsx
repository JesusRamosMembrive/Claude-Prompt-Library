import { useState, useMemo } from "react";
import { useQuery } from "@tanstack/react-query";

import { getSettings } from "./api/client";
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
  useEventStream();

  const watcherActive = settingsQuery.data?.watcher_active ?? true;
  const rootPath = settingsQuery.data?.root_path;

  return (
    <div className="app-root">
      {view === "dashboard" ? (
        <>
          <HeaderBar
            onOpenSettings={() => setView("settings")}
            watcherActive={watcherActive}
            rootPath={rootPath}
          />
          <Dashboard />
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
