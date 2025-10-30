import { useMemo, useState } from "react";
import ForceGraph2D from "react-force-graph-2d";
import type { GraphData } from "react-force-graph-2d";

import { useClassGraphQuery } from "../hooks/useClassGraphQuery";
import type { ClassGraphEdge, ClassGraphNode, ClassGraphResponse } from "../api/types";

const EDGE_OPTIONS: { value: "inherits" | "instantiates"; label: string }[] = [
  { value: "inherits", label: "Herencias" },
  { value: "instantiates", label: "Instancias" },
];

export function ClassGraphView(): JSX.Element {
  const [includeExternal, setIncludeExternal] = useState(true);
  const [edgeTypes, setEdgeTypes] = useState<("inherits" | "instantiates")[]>([
    "inherits",
    "instantiates",
  ]);
  const [moduleFilter, setModuleFilter] = useState("");
  const [nodeLimit, setNodeLimit] = useState(300);

  const query = useClassGraphQuery({
    includeExternal,
    edgeTypes,
  });

  const data = query.data;

  const { graph, internalEdges, externalEdges, nodeCount, edgeCount } = useMemo(
    () => buildGraphData(data, { moduleFilter, nodeLimit, includeExternal }),
    [data, moduleFilter, nodeLimit, includeExternal],
  );

  const toggleEdgeType = (value: "inherits" | "instantiates") => {
    setEdgeTypes((prev) =>
      prev.includes(value) ? prev.filter((item) => item !== value) : [...prev, value],
    );
  };

  return (
    <div className="class-graph-view">
      <section className="class-graph-controls">
        <div className="control-block">
          <h2>Relaciones incluidas</h2>
          <div className="control-row">
            {EDGE_OPTIONS.map((option) => (
              <label key={option.value} className="control-checkbox">
                <input
                  type="checkbox"
                  checked={edgeTypes.includes(option.value)}
                  onChange={() => toggleEdgeType(option.value)}
                />
                <span>{option.label}</span>
              </label>
            ))}
          </div>
        </div>

        <div className="control-block">
          <h2>Referencias externas</h2>
          <label className="control-checkbox">
            <input
              type="checkbox"
              checked={includeExternal}
              onChange={() => setIncludeExternal((prev) => !prev)}
            />
            <span>Mostrar nodos/aristas externas al proyecto</span>
          </label>
        </div>

        <div className="control-block">
          <h2>Filtro por módulo</h2>
          <input
            type="text"
            className="input-text"
            placeholder="Ej: code_map."
            value={moduleFilter}
            onChange={(event) => setModuleFilter(event.target.value)}
          />
        </div>

        <div className="control-block">
          <h2>Límite de nodos</h2>
          <div className="control-row">
            <input
              type="range"
              min={50}
              max={1000}
              step={50}
              value={nodeLimit}
              onChange={(event) => setNodeLimit(Number(event.target.value))}
            />
            <span>{nodeLimit}</span>
          </div>
        </div>

        <button
          className="secondary-btn"
          type="button"
          onClick={() => query.refetch()}
          disabled={query.isFetching}
        >
          {query.isFetching ? "Actualizando…" : "Actualizar grafo"}
        </button>
      </section>

      <section className="class-graph-summary">
        {query.isLoading ? (
          <p className="summary-info">Generando grafo…</p>
        ) : query.isError ? (
          <p className="summary-error">
            No se pudo obtener el grafo. {String(query.error)}
          </p>
        ) : data ? (
          <>
            <div className="summary-cards">
              <article>
                <h3>Nodos (filtrados)</h3>
                <p>{nodeCount.toLocaleString("es-ES")}</p>
                <span className="summary-sub">
                  Total: {data.stats.nodes.toLocaleString("es-ES")}
                </span>
              </article>
              <article>
                <h3>Aristas (filtradas)</h3>
                <p>{edgeCount.toLocaleString("es-ES")}</p>
                <span className="summary-sub">
                  Total: {data.stats.edges.toLocaleString("es-ES")}
                </span>
              </article>
              <article>
                <h3>Aristas internas</h3>
                <p>{internalEdges.length.toLocaleString("es-ES")}</p>
              </article>
              <article>
                <h3>Aristas externas</h3>
                <p>{externalEdges.length.toLocaleString("es-ES")}</p>
              </article>
            </div>

            <div className="edge-lists">
              <EdgeList
                title="Relaciones internas destacadas"
                edges={internalEdges.slice(0, 20)}
                nodes={graph.nodes}
              />
              {includeExternal ? (
                <EdgeList
                  title="Relaciones externas destacadas"
                  edges={externalEdges.slice(0, 20)}
                  nodes={graph.nodes}
                />
              ) : null}
            </div>

            <div className="class-graph-canvas">
              {graph.nodes.length === 0 ? (
                <p className="summary-info">No hay datos para los filtros seleccionados.</p>
              ) : (
                <ForceGraph2D
                  graphData={graph}
                  cooldownTime={1500}
                  linkColor={(link) => (link as GraphLink).internal ? "#38bdf8" : "#f97316"}
                  linkDirectionalParticles={2}
                  linkDirectionalParticleSpeed={0.002}
                  nodeLabel={(node) => {
                    const n = node as GraphNode;
                    const scope = n.external ? "Fuera del proyecto" : n.module;
                    return `${n.name}\n${scope}`;
                  }}
                  nodeCanvasObject={(node, ctx, globalScale) => renderNode(node as GraphNode, ctx, globalScale)}
                  nodePointerAreaPaint={(node, color, ctx) => renderNode(node as GraphNode, ctx, 1, color)}
                />
              )}
            </div>
          </>
        ) : null}
      </section>
    </div>
  );
}

function EdgeList({
  title,
  edges,
  nodes,
}: {
  title: string;
  edges: ClassGraphEdge[];
  nodes: ClassGraphNode[];
}): JSX.Element {
  const nodeMap = useMemo(() => {
    const map = new Map<string, ClassGraphNode>();
    nodes.forEach((node) => map.set(node.id, node));
    return map;
  }, [nodes]);

  return (
    <div className="edge-list">
      <h3>{title}</h3>
      {edges.length === 0 ? (
        <p className="summary-info">Sin resultados para los filtros seleccionados.</p>
      ) : (
        <ul>
          {edges.map((edge, index) => {
            const source = nodeMap.get(edge.source);
            const target = nodeMap.get(edge.target);
            return (
              <li key={`${edge.source}-${edge.target}-${index}`}>
                <span className={`edge-type edge-type-${edge.type}`}>
                  {edge.type === "inherits" ? "Hereda" : "Instancia"}
                </span>
                <span className="edge-source">{source?.name ?? edge.source}</span>
                <span className="edge-arrow">→</span>
                <span className="edge-target">
                  {edge.internal ? target?.name ?? edge.target : edge.raw_target}
                </span>
              </li>
            );
          })}
        </ul>
      )}
    </div>
  );
}

type GraphNode = ClassGraphNode & {
  x?: number;
  y?: number;
  vx?: number;
  vy?: number;
  val?: number;
  external?: boolean;
};

type GraphLink = ClassGraphEdge & {
  source: string;
  target: string;
  value?: number;
};

interface ForceGraphData extends GraphData {
  nodes: GraphNode[];
  links: GraphLink[];
}

interface FilteredGraphResult {
  graph: ForceGraphData;
  internalEdges: ClassGraphEdge[];
  externalEdges: ClassGraphEdge[];
  nodeCount: number;
  edgeCount: number;
}

function buildGraphData(
  data: ClassGraphResponse | undefined,
  options: { moduleFilter: string; nodeLimit: number; includeExternal: boolean },
): FilteredGraphResult {
  if (!data) {
    return {
      graph: { nodes: [], links: [] },
      internalEdges: [],
      externalEdges: [],
      nodeCount: 0,
      edgeCount: 0,
    };
  }

  const filterText = options.moduleFilter.trim().toLowerCase();
  const sortedNodes = [...data.nodes].sort((a, b) =>
    a.module.localeCompare(b.module) || a.name.localeCompare(b.name),
  );

  let candidateNodes = sortedNodes;
  if (filterText) {
    candidateNodes = sortedNodes.filter(
      (node) =>
        node.module.toLowerCase().includes(filterText) ||
        node.name.toLowerCase().includes(filterText),
    );
  }
  if (candidateNodes.length === 0) {
    if (filterText) {
      return {
        graph: { nodes: [], links: [] },
        internalEdges: [],
        externalEdges: [],
        nodeCount: 0,
        edgeCount: 0,
      };
    }
    candidateNodes = sortedNodes;
  }

  const limit = Math.max(1, options.nodeLimit);
  const limitedNodes = candidateNodes.slice(0, limit);

  const nodeMap = new Map<string, GraphNode>();
  const nodes: GraphNode[] = [];

  for (const baseNode of limitedNodes) {
    const graphNode: GraphNode = { ...baseNode, val: 4, external: false };
    nodeMap.set(graphNode.id, graphNode);
    nodes.push(graphNode);
  }

  const allowedSources = new Set(nodeMap.keys());
  const links: GraphLink[] = [];
  const internalEdges: ClassGraphEdge[] = [];
  const externalEdges: ClassGraphEdge[] = [];

  // TODO: mover este filtrado al backend para evitar transferir grafos enormes.
  for (const edge of data.edges) {
    if (!allowedSources.has(edge.source)) {
      continue;
    }

    const targetAllowed = nodeMap.has(edge.target);

    if (!targetAllowed) {
      if (edge.internal || !options.includeExternal) {
        continue;
      }
      if (!nodeMap.has(edge.target)) {
        const externalNode: GraphNode = {
          id: edge.target,
          name: edge.raw_target ?? edge.target,
          module: "external",
          file: edge.target,
          external: true,
          val: 2,
        };
        nodeMap.set(edge.target, externalNode);
        nodes.push(externalNode);
      }
    }

    if (!edge.internal && !options.includeExternal) {
      continue;
    }

    const link: GraphLink = { ...edge };
    links.push(link);

    if (edge.internal) {
      internalEdges.push(edge);
    } else if (options.includeExternal) {
      externalEdges.push(edge);
    }
  }

  return {
    graph: { nodes, links },
    internalEdges,
    externalEdges,
    nodeCount: nodes.length,
    edgeCount: links.length,
  };
}

function renderNode(node: GraphNode, ctx: CanvasRenderingContext2D, globalScale: number, fillStyle?: string) {
  if (typeof node.x !== "number" || typeof node.y !== "number") {
    return;
  }
  const label = node.name;
  const fontSize = 12 / globalScale;
  ctx.font = `${fontSize}px Inter`;
  const textWidth = ctx.measureText(label).width;
  const padding = fontSize * 0.4;
  const backgroundSize = textWidth + padding * 2;

  const background = node.external ? "rgba(190, 24, 93, 0.45)" : "rgba(15, 23, 42, 0.85)";
  ctx.fillStyle = fillStyle ?? background;
  ctx.fillRect(node.x! - backgroundSize / 2, node.y! - fontSize, backgroundSize, fontSize * 1.6);

  ctx.textAlign = "center";
  ctx.textBaseline = "middle";
  ctx.fillStyle = "#e2e8f0";
  ctx.fillText(label, node.x!, node.y!);
}
