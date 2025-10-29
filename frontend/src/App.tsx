import { useState } from "react";
import { HeaderBar } from "./components/HeaderBar";
import { Dashboard } from "./components/Dashboard";
import { SettingsView } from "./components/SettingsView";
import { useAppQueries } from "./hooks/useAppQueries";
import { useEventStream } from "./hooks/useEventStream";
import "./styles/index.css";

export function App(): JSX.Element {
  const [view, setView] = useState<"dashboard" | "settings">("dashboard");
  const { settingsQuery, statusQuery, summary } = useAppQueries();
  useEventStream();

  return (
    <div className="app-root">
      {view === "dashboard" ? (
        <>
          <HeaderBar
            onOpenSettings={() => setView("settings")}
            watcherActive={summary.watcherActive}
            rootPath={summary.rootPath}
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
