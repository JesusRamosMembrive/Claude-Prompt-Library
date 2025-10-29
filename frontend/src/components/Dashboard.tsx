import { Sidebar } from "./Sidebar";
import { DetailPanel } from "./DetailPanel";
import { SearchPanel } from "./SearchPanel";
import { ActivityFeed } from "./ActivityFeed";

export function Dashboard(): JSX.Element {
  return (
    <div className="main-grid">
      <Sidebar />
      <DetailPanel />
      <aside className="panel inspector-panel">
        <SearchPanel />
        <div>
          <h2>Actividad reciente</h2>
          <ActivityFeed />
        </div>
      </aside>
    </div>
  );
}
