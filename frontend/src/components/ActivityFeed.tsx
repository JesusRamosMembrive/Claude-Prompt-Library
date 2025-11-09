import { useMemo } from "react";
import { useActivityStore } from "../state/useActivityStore";

function formatTimeAgo(timestamp: number): string {
  const now = Date.now();
  const diff = Math.max(0, now - timestamp);
  const seconds = Math.floor(diff / 1000);
  if (seconds < 60) {
    return `${seconds}s`;
  }
  const minutes = Math.floor(seconds / 60);
  if (minutes < 60) {
    return `${minutes}m`;
  }
  const hours = Math.floor(minutes / 60);
  if (hours < 24) {
    return `${hours}h`;
  }
  const days = Math.floor(hours / 24);
  return `${days}d`;
}

export function ActivityFeed(): JSX.Element {
  const items = useActivityStore((state) => state.items);

  const empty = items.length === 0;
  const groups = useMemo(() => items.slice(0, 10), [items]);

  if (empty) {
    return (
      <p style={{ color: "#7f869d", fontSize: "13px" }}>
        No activity recorded yet. Modify `.py` files to see events detected by the watcher.
      </p>
    );
  }

  return (
    <ul className="activity-list">
      {groups.map((item) => (
        <li
          key={item.id}
          className={`activity-item ${item.type === "deleted" ? "deleted" : ""}`}
        >
          <span>
            {item.type === "deleted" ? "🗑 Deleted" : "📝 Updated"} ·{" "}
            <strong>{item.path}</strong>
          </span>
          <span className="activity-time">{formatTimeAgo(item.timestamp)}</span>
        </li>
      ))}
    </ul>
  );
}
