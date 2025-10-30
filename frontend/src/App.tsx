import { BrowserRouter, Navigate, Route, Routes } from "react-router-dom";
import { HeaderBar } from "./components/HeaderBar";
import { Dashboard } from "./components/Dashboard";
import { SettingsView } from "./components/SettingsView";
import { useAppQueries } from "./hooks/useAppQueries";
import { useEventStream } from "./hooks/useEventStream";
import "./styles/index.css";

export function App(): JSX.Element {
  const { settingsQuery, statusQuery, summary } = useAppQueries();
  useEventStream();

  return (
    <BrowserRouter>
      <div className="app-root">
        <Routes>
          <Route
            path="/"
            element={
              <>
                <HeaderBar
                  watcherActive={summary.watcherActive}
                  rootPath={summary.rootPath}
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
