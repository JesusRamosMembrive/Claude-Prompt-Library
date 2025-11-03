import { useMemo, useState } from "react";
import { useQuery } from "@tanstack/react-query";
import clsx from "clsx";

import { getTree } from "../api/client";
import { queryKeys } from "../api/queryKeys";
import type { ProjectTreeNode } from "../api/types";
import { useSelectionStore } from "../state/useSelectionStore";

const DIRECTORY_ICONS = ["📂", "📁"];
const FILE_ICON = "📄";

export function Sidebar(): JSX.Element {
  const [filter, setFilter] = useState("");
  const clearSelection = useSelectionStore((state) => state.clearSelection);
  const selectedPath = useSelectionStore((state) => state.selectedPath);

  const { data, isLoading, isError, error } = useQuery({
    queryKey: queryKeys.tree,
    queryFn: getTree,
  });

  const nodes = useMemo(() => {
    const term = filter.trim().toLowerCase();
    const children = data?.children ?? [];
    if (!term) {
      return children;
    }
    return filterTree(children, term);
  }, [data, filter]);

  return (
    <aside className="panel">
      <div className="panel-header">
        <h2>Proyecto</h2>
        {selectedPath && (
          <button type="button" onClick={clearSelection}>
            Limpiar selección
          </button>
        )}
      </div>

      <div className="search-box">
        <span role="img" aria-label="Filtrar">
          🔎
        </span>
        <input
          type="search"
          placeholder="Filtrar archivos…"
          value={filter}
          onChange={(event) => setFilter(event.target.value)}
        />
      </div>

      {isLoading && <p style={{ color: "#7f869d" }}>Cargando estructura…</p>}

      {isError && (
        <div className="error-banner">
          Error al cargar el árbol:{" "}
          {(error as Error)?.message ?? "intenta recargar la página"}
        </div>
      )}

      {!isLoading && !isError && nodes.length === 0 && (
        <p style={{ color: "#7f869d", fontSize: "13px" }}>
          {filter
            ? `No hay resultados para “${filter}”.`
            : "No se detectaron archivos Python. Añade `.py` al directorio raíz para comenzar."}
        </p>
      )}

      <ul className="tree-list">
        {nodes.map((node) => (
          <TreeNodeItem key={`${node.path}-${node.name}`} node={node} depth={0} />
        ))}
      </ul>
    </aside>
  );
}

function TreeNodeItem({
  node,
  depth,
}: {
  node: ProjectTreeNode;
  depth: number;
}): JSX.Element {
  const selectedPath = useSelectionStore((state) => state.selectedPath);
  const selectPath = useSelectionStore((state) => state.selectPath);
  const [expanded, setExpanded] = useState(true);

  const isDirectory = node.is_dir;
  const isActive = !isDirectory && selectedPath === node.path;
  const symbolCount = node.symbols?.length ?? 0;

  const handleClick = () => {
    if (isDirectory) {
      setExpanded((value) => !value);
    } else {
      selectPath(node.path);
    }
  };

  const icon = isDirectory ? DIRECTORY_ICONS[expanded ? 0 : 1] : FILE_ICON;

  return (
    <li>
      <div
        className={clsx("tree-node", { active: isActive })}
        style={{ paddingLeft: depth * 14 + 12 }}
        role="button"
        tabIndex={0}
        onClick={handleClick}
        onKeyDown={(event) => {
          if (event.key === "Enter" || event.key === " ") {
            event.preventDefault();
            handleClick();
          }
        }}
      >
        <span>
          <span aria-hidden="true">{icon}</span>
          <span>{node.name}</span>
        </span>
        {isDirectory ? (
          <span className="badge">{node.children?.length ?? 0}</span>
        ) : symbolCount > 0 ? (
          <span className="badge">{symbolCount} símbolos</span>
        ) : null}
      </div>
      {isDirectory && expanded && node.children?.length ? (
        <ul className="tree-children">
          {node.children.map((child) => (
            <TreeNodeItem
              key={`${child.path}-${child.name}`}
              node={child}
              depth={depth + 1}
            />
          ))}
        </ul>
      ) : null}
    </li>
  );
}

function filterTree(nodes: ProjectTreeNode[], term: string): ProjectTreeNode[] {
  const matcher = (value: string) => value.toLowerCase().includes(term);

  const walk = (node: ProjectTreeNode): ProjectTreeNode | null => {
    if (!node.children?.length) {
      return matcher(node.name) ? node : null;
    }

    const filteredChildren = node.children
      .map(walk)
      .filter((child): child is ProjectTreeNode => child !== null);

    if (filteredChildren.length > 0 || matcher(node.name)) {
      return { ...node, children: filteredChildren };
    }
    return null;
  };

  return nodes
    .map(walk)
    .filter((node): node is ProjectTreeNode => node !== null);
}
