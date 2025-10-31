import type { UseQueryResult } from "@tanstack/react-query";

import type { StatusPayload } from "../api/types";
import { Sidebar } from "./Sidebar";
import { DetailPanel } from "./DetailPanel";
import { SearchPanel } from "./SearchPanel";
import { ActivityFeed } from "./ActivityFeed";
import { StatusPanel } from "./StatusPanel";

export function CodeMapDashboard({
  statusQuery,
}: {
  statusQuery: UseQueryResult<StatusPayload>;
}): JSX.Element {
  return (
    <div className="main-grid">
      <Sidebar />
      <DetailPanel />
      <aside className="panel inspector-panel">
        <SearchPanel />
        <StatusPanel statusQuery={statusQuery} />
        <div>
          <h2>Actividad reciente</h2>
          <ActivityFeed />
        </div>
      </aside>
    </div>
  );
}
