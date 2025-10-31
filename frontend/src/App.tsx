import { BrowserRouter, Navigate, Route, Routes } from "react-router-dom";
import { HeaderBar } from "./components/HeaderBar";
import { HomeView } from "./components/HomeView";
import { CodeMapDashboard } from "./components/CodeMapDashboard";
import { SettingsView } from "./components/SettingsView";
import { StageToolkitView } from "./components/StageToolkitView";
import { ClassGraphView } from "./components/ClassGraphView";
import { ClassUMLView } from "./components/ClassUMLView";
import { LintersView } from "./components/LintersView";
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
                  title="Stage-Aware Workspace"
                  watcherActive={watcherActive}
                  rootPath={rootPath}
                  lastFullScan={statusQuery.data?.last_full_scan}
                  filesIndexed={statusQuery.data?.files_indexed}
                />
                <HomeView statusQuery={statusQuery} />
              </>
            }
          />
          <Route
            path="/code-map"
            element={
              <>
                <HeaderBar
                  title="Code Map"
                  watcherActive={watcherActive}
                  rootPath={rootPath}
                  lastFullScan={statusQuery.data?.last_full_scan}
                  filesIndexed={statusQuery.data?.files_indexed}
                />
                <CodeMapDashboard statusQuery={statusQuery} />
              </>
            }
          />
          <Route
            path="/stage-toolkit"
            element={
              <>
                <HeaderBar
                  title="Project Stage Toolkit"
                  watcherActive={watcherActive}
                  rootPath={rootPath}
                  lastFullScan={statusQuery.data?.last_full_scan}
                  filesIndexed={statusQuery.data?.files_indexed}
                />
                <StageToolkitView />
              </>
            }
          />
          <Route
            path="/class-graph"
            element={
              <>
                <HeaderBar
                  title="Class Graph"
                  watcherActive={watcherActive}
                  rootPath={rootPath}
                  lastFullScan={statusQuery.data?.last_full_scan}
                  filesIndexed={statusQuery.data?.files_indexed}
                />
                <ClassGraphView />
              </>
            }
          />
          <Route
            path="/class-uml"
            element={
              <>
                <HeaderBar
                  title="Class UML"
                  watcherActive={watcherActive}
                  rootPath={rootPath}
                  lastFullScan={statusQuery.data?.last_full_scan}
                  filesIndexed={statusQuery.data?.files_indexed}
                />
                <ClassUMLView />
              </>
            }
          />
          <Route
            path="/linters"
            element={
              <>
                <HeaderBar
                  title="Linters & Calidad"
                  watcherActive={watcherActive}
                  rootPath={rootPath}
                  lastFullScan={statusQuery.data?.last_full_scan}
                  filesIndexed={statusQuery.data?.files_indexed}
                />
                <LintersView />
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
