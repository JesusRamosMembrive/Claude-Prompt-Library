import { BrowserRouter, Navigate, Route, Routes } from "react-router-dom";
import { HeaderBar } from "./components/HeaderBar";
import { Dashboard } from "./components/Dashboard";
import { SettingsView } from "./components/SettingsView";
import { useEventStream } from "./hooks/useEventStream";
import { useSettingsQuery } from "./hooks/useSettingsQuery";
import { useStatusQuery } from "./hooks/useStatusQuery";
import "./styles/index.css";

export function App(): JSX.Element {
  const settingsQuery = useSettingsQuery();
  const statusQuery = useStatusQuery();
  useEventStream();

  const rootPath = statusQuery.data?.root_path ?? settingsQuery.data?.root_path ?? "";
  const watcherActive = statusQuery.data?.watcher_active ?? false;

  return (
    <BrowserRouter>
      <div className="app-root">
        <Routes>
          <Route
            path="/"
            element={
              <>
                <HeaderBar
                  watcherActive={watcherActive}
                  rootPath={rootPath}
                  lastFullScan={statusQuery.data?.last_full_scan}
                  filesIndexed={statusQuery.data?.files_indexed}
                />
                <Dashboard statusQuery={statusQuery} />
              </>
            }
          />
          <Route path="/settings" element={<SettingsView settingsQuery={settingsQuery} />} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </div>
    </BrowserRouter>
  );
}
