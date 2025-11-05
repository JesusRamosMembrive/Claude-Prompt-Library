import {
  forwardRef,
  useCallback,
  useEffect,
  useImperativeHandle,
  useMemo,
  useRef,
  useState,
} from "react";
import type { PointerEvent as ReactPointerEvent } from "react";

import { useClassUmlQuery } from "../hooks/useClassUmlQuery";
import type { UMLClass } from "../api/types";

const DEFAULT_PREFIXES = "";
const UML_ZOOM_MIN = 0.05;
const UML_ZOOM_MAX = 4;
const UML_ZOOM_STEP = 0.05;

interface UmlSvgHandle {
  setZoom: (value: number) => void;
  resetView: () => void;
}

interface UmlViewState {
  zoom: number;
}

export function ClassUMLView(): JSX.Element {
  const [includeExternal, setIncludeExternal] = useState(false);
  const [prefixInput, setPrefixInput] = useState(DEFAULT_PREFIXES);
  const [zoom, setZoom] = useState(1);
  const svgHandleRef = useRef<UmlSvgHandle | null>(null);
  const [selectedClassId, setSelectedClassId] = useState<string | null>(null);
  const [searchTerm, setSearchTerm] = useState("");

  // Edge type filters - default to inheritance + association only (no clutter)
  const [edgeTypes, setEdgeTypes] = useState<Set<string>>(
    new Set(["inheritance", "association"])
  );

  const toggleEdgeType = useCallback((type: string) => {
    setEdgeTypes((prev) => {
      const next = new Set(prev);
      if (next.has(type)) {
        next.delete(type);
      } else {
        next.add(type);
      }
      return next;
    });
  }, []);

  const handleCanvasStateChange = useCallback((state: UmlViewState) => {
    setZoom((prev) => (Math.abs(prev - state.zoom) < 0.001 ? prev : state.zoom));
  }, []);

  const modulePrefixes = useMemo(
    () =>
      prefixInput
        .split(",")
        .map((item) => item.trim())
        .filter(Boolean),
    [prefixInput],
  );

  const edgeTypesArray = useMemo(() => Array.from(edgeTypes), [edgeTypes]);

  const query = useClassUmlQuery({
    includeExternal,
    modulePrefixes,
    edgeTypes: edgeTypesArray,
  });
  const data = query.data;
  const classCount = data?.classCount ?? 0;
  const svgMarkup = data?.svg ?? null;
  const stats = data?.stats;
  const classes = data?.classes ?? [];

  const selectedClass = useMemo(() => {
    if (!selectedClassId) return null;
    return classes.find((c) => c.id === selectedClassId) ?? null;
  }, [selectedClassId, classes]);

  // Filter classes based on search term
  const filteredClasses = useMemo(() => {
    if (!searchTerm.trim()) return [];
    const term = searchTerm.toLowerCase();
    return classes.filter(
      (c) =>
        c.name.toLowerCase().includes(term) ||
        c.module.toLowerCase().includes(term) ||
        c.file.toLowerCase().includes(term)
    );
  }, [searchTerm, classes]);

  const handleSearchSelect = useCallback((classId: string) => {
    setSelectedClassId(classId);
    setSearchTerm(""); // Clear search after selection
  }, []);

  // Handle keyboard events for accessibility
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      // Close panel on Escape key
      if (e.key === "Escape" && selectedClassId) {
        setSelectedClassId(null);
      }
    };

    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [selectedClassId]);

  return (
    <div className="uml-view">
      <section className="uml-search-section" aria-label="Búsqueda de clases">
        <div className="uml-search-container">
          <label htmlFor="uml-search" className="sr-only">
            Buscar clase
          </label>
          <input
            id="uml-search"
            type="text"
            className="uml-search-input"
            placeholder="Buscar clase por nombre, módulo o archivo..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            aria-label="Buscar clase por nombre, módulo o archivo"
            aria-autocomplete="list"
            aria-controls={filteredClasses.length > 0 ? "uml-search-results" : undefined}
            aria-expanded={filteredClasses.length > 0}
          />
          {filteredClasses.length > 0 && (
            <div id="uml-search-results" className="uml-search-results" role="listbox">
              {filteredClasses.slice(0, 10).map((cls) => (
                <button
                  key={cls.id}
                  type="button"
                  className="uml-search-result-item"
                  onClick={() => handleSearchSelect(cls.id)}
                  role="option"
                  aria-label={`Seleccionar clase ${cls.name} del módulo ${cls.module}`}
                >
                  <div className="search-result-name">{cls.name}</div>
                  <div className="search-result-path">{cls.module}</div>
                </button>
              ))}
              {filteredClasses.length > 10 && (
                <div className="uml-search-more">
                  +{filteredClasses.length - 10} resultados más
                </div>
              )}
            </div>
          )}
        </div>
      </section>

      <section className="uml-controls">
        <div className="control-block">
          <h2>Prefijos de módulo</h2>
          <input
            type="text"
            className="input-text"
            value={prefixInput}
            onChange={(event) => setPrefixInput(event.target.value)}
            placeholder="Ej: api, src"
          />
        </div>

        <label className="control-checkbox">
          <input
            type="checkbox"
            checked={includeExternal}
            onChange={() => setIncludeExternal((prev) => !prev)}
          />
          <span>Incluir clases externas</span>
        </label>

        <div className="control-block">
          <h2>Tipos de relaciones</h2>
          <div className="control-row">
            <label className="control-checkbox">
              <input
                type="checkbox"
                checked={edgeTypes.has("inheritance")}
                onChange={() => toggleEdgeType("inheritance")}
              />
              <span style={{ color: "#60a5fa" }}>Herencia</span>
            </label>
            <label className="control-checkbox">
              <input
                type="checkbox"
                checked={edgeTypes.has("association")}
                onChange={() => toggleEdgeType("association")}
              />
              <span style={{ color: "#f97316" }}>Asociación</span>
            </label>
            <label className="control-checkbox">
              <input
                type="checkbox"
                checked={edgeTypes.has("instantiation")}
                onChange={() => toggleEdgeType("instantiation")}
              />
              <span style={{ color: "#10b981" }}>Instanciación</span>
            </label>
            <label className="control-checkbox">
              <input
                type="checkbox"
                checked={edgeTypes.has("reference")}
                onChange={() => toggleEdgeType("reference")}
              />
              <span style={{ color: "#a855f7" }}>Referencias</span>
            </label>
          </div>
        </div>

        <div className="uml-zoom-control">
          <label htmlFor="uml-zoom-slider">Zoom</label>
          <input
            id="uml-zoom-slider"
            type="range"
            min={UML_ZOOM_MIN}
            max={UML_ZOOM_MAX}
            step={UML_ZOOM_STEP}
            value={zoom}
            onChange={(event) => {
              const value = clamp(Number(event.target.value), UML_ZOOM_MIN, UML_ZOOM_MAX);
              setZoom(value);
              svgHandleRef.current?.setZoom(value);
            }}
          />
          <div className="uml-zoom-indicator">
            <span>{Math.round(zoom * 100)}%</span>
            <button
              type="button"
              className="link-btn"
              onClick={() => {
                svgHandleRef.current?.resetView();
                setZoom(1);
              }}
              disabled={!svgMarkup}
            >
              Reset
            </button>
          </div>
        </div>

        <button
          className="secondary-btn"
          type="button"
          onClick={() => query.refetch()}
          disabled={query.isFetching}
        >
          {query.isFetching ? "Actualizando…" : "Regenerar"}
        </button>
      </section>

      {!query.isLoading && !query.isError && classCount > 0 && (
        <section className="uml-legend" aria-label="Leyenda de relaciones">
          <h3>Leyenda</h3>
          <div className="legend-items">
            <div className="legend-item">
              <svg width="40" height="20" viewBox="0 0 40 20">
                <line
                  x1="0"
                  y1="10"
                  x2="40"
                  y2="10"
                  stroke="#60a5fa"
                  strokeWidth="2"
                  markerEnd="url(#arrow-inheritance)"
                />
                <defs>
                  <marker
                    id="arrow-inheritance"
                    markerWidth="10"
                    markerHeight="10"
                    refX="9"
                    refY="3"
                    orient="auto"
                  >
                    <path d="M0,0 L0,6 L9,3 z" fill="#60a5fa" />
                  </marker>
                </defs>
              </svg>
              <span>Herencia (extends)</span>
            </div>
            <div className="legend-item">
              <svg width="40" height="20" viewBox="0 0 40 20">
                <line
                  x1="0"
                  y1="10"
                  x2="40"
                  y2="10"
                  stroke="#f97316"
                  strokeWidth="2"
                  strokeDasharray="5,3"
                />
              </svg>
              <span>Asociación (uses)</span>
            </div>
            <div className="legend-item">
              <svg width="40" height="20" viewBox="0 0 40 20">
                <line
                  x1="0"
                  y1="10"
                  x2="40"
                  y2="10"
                  stroke="#10b981"
                  strokeWidth="2"
                  strokeDasharray="5,3"
                />
              </svg>
              <span>Instanciación (creates)</span>
            </div>
            <div className="legend-item">
              <svg width="40" height="20" viewBox="0 0 40 20">
                <line
                  x1="0"
                  y1="10"
                  x2="40"
                  y2="10"
                  stroke="#a855f7"
                  strokeWidth="1.5"
                  strokeDasharray="2,2"
                />
              </svg>
              <span>Referencias (refers)</span>
            </div>
          </div>
        </section>
      )}

      {stats && !query.isLoading && !query.isError && (
        <section className="uml-stats" aria-label="Resumen del modelo UML">
          <div className="uml-stat">
            <span className="uml-stat-label">Clases</span>
            <strong className="uml-stat-value">{stats.classes ?? classCount}</strong>
          </div>
          <div className="uml-stat">
            <span className="uml-stat-label">Herencias</span>
            <strong className="uml-stat-value" style={{ color: "#60a5fa" }}>
              {stats.inheritance_edges ?? 0}
            </strong>
          </div>
          <div className="uml-stat">
            <span className="uml-stat-label">Asociaciones</span>
            <strong className="uml-stat-value" style={{ color: "#f97316" }}>
              {stats.association_edges ?? 0}
            </strong>
          </div>
          <div className="uml-stat">
            <span className="uml-stat-label">Instanciaciones</span>
            <strong className="uml-stat-value" style={{ color: "#10b981" }}>
              {stats.instantiation_edges ?? 0}
            </strong>
          </div>
          <div className="uml-stat">
            <span className="uml-stat-label">Referencias</span>
            <strong className="uml-stat-value" style={{ color: "#a855f7" }}>
              {stats.reference_edges ?? 0}
            </strong>
          </div>
        </section>
      )}

      <section className="uml-canvas" aria-live="polite" aria-busy={query.isLoading}>
        {query.isLoading ? (
          <div className="uml-loading" role="status">
            <div className="uml-spinner" aria-hidden="true"></div>
            <p className="summary-info">Calculando modelo UML…</p>
          </div>
        ) : query.isError ? (
          <p className="summary-error" role="alert">
            No se pudo generar el modelo: {String(query.error)}
          </p>
        ) : classCount === 0 ? (
          <p className="summary-info">No hay clases para los filtros seleccionados.</p>
        ) : svgMarkup ? (
          <>
            <UmlSvgContainer
              ref={svgHandleRef}
              svg={svgMarkup}
              onStateChange={handleCanvasStateChange}
              onNodeClick={setSelectedClassId}
              selectedNodeId={selectedClassId}
            />
            {selectedClass && (
              <ClassDetailsPanel
                classInfo={selectedClass}
                onClose={() => setSelectedClassId(null)}
              />
            )}
          </>
        ) : (
          <p className="summary-info">El backend no devolvió un diagrama válido.</p>
        )}
      </section>
    </div>
  );
}

interface ClassDetailsPanelProps {
  classInfo: UMLClass;
  onClose: () => void;
}

function ClassDetailsPanel({ classInfo, onClose }: ClassDetailsPanelProps): JSX.Element {
  const panelRef = useRef<HTMLElement>(null);

  // Auto-focus panel when opened for accessibility
  useEffect(() => {
    panelRef.current?.focus();
  }, []);

  return (
    <aside
      ref={panelRef}
      className="class-details-panel"
      role="dialog"
      aria-modal="true"
      aria-labelledby="class-details-title"
      tabIndex={-1}
    >
      <header className="class-details-header">
        <h2 id="class-details-title">{classInfo.name}</h2>
        <button
          type="button"
          className="link-btn"
          onClick={onClose}
          aria-label="Cerrar panel de detalles"
          title="Cerrar (Esc)"
        >
          ✕
        </button>
      </header>

      <div className="class-details-body">
        <section className="class-details-section">
          <h3>Información</h3>
          <dl>
            <dt>Módulo</dt>
            <dd>{classInfo.module}</dd>
            <dt>Archivo</dt>
            <dd>{classInfo.file}</dd>
            {classInfo.bases.length > 0 && (
              <>
                <dt>Hereda de</dt>
                <dd>{classInfo.bases.join(", ")}</dd>
              </>
            )}
          </dl>
        </section>

        {classInfo.attributes.length > 0 && (
          <section className="class-details-section">
            <h3>Atributos ({classInfo.attributes.length})</h3>
            <ul className="class-members-list">
              {classInfo.attributes.map((attr, idx) => (
                <li key={idx}>
                  <code className="member-name">{attr.name}</code>
                  {attr.type && <span className="member-type">: {attr.type}</span>}
                  {attr.optional && <span className="member-optional"> (opcional)</span>}
                </li>
              ))}
            </ul>
          </section>
        )}

        {classInfo.methods.length > 0 && (
          <section className="class-details-section">
            <h3>Métodos ({classInfo.methods.length})</h3>
            <ul className="class-members-list">
              {classInfo.methods.map((method, idx) => (
                <li key={idx}>
                  <code className="member-name">{method.name}</code>
                  <code className="member-signature">
                    ({method.parameters.join(", ")})
                    {method.returns && ` → ${method.returns}`}
                  </code>
                </li>
              ))}
            </ul>
          </section>
        )}

        {classInfo.associations.length > 0 && (
          <section className="class-details-section">
            <h3>Asociaciones ({classInfo.associations.length})</h3>
            <ul className="class-associations-list">
              {classInfo.associations.map((assoc, idx) => (
                <li key={idx}>
                  <code>{assoc}</code>
                </li>
              ))}
            </ul>
          </section>
        )}
      </div>
    </aside>
  );
}

interface UmlSvgContainerProps {
  svg: string;
  onStateChange?: (state: UmlViewState) => void;
  onNodeClick?: (classId: string) => void;
  selectedNodeId?: string | null;
}

const MIN_ZOOM = UML_ZOOM_MIN;
const MAX_ZOOM = UML_ZOOM_MAX;

const clamp = (value: number, min: number, max: number) => Math.min(max, Math.max(min, value));

const initialOffset = { x: 0, y: 0 };

const UmlSvgContainer = forwardRef<UmlSvgHandle, UmlSvgContainerProps>(function UmlSvgContainer(
  { svg, onStateChange, onNodeClick, selectedNodeId },
  ref,
) {
  const containerRef = useRef<HTMLDivElement | null>(null);
  const [zoom, setZoomState] = useState(1);
  const [offset, setOffsetState] = useState(initialOffset);
  const [contentOrigin, setContentOrigin] = useState<{ x: number; y: number }>({ x: 0, y: 0 });
  const panState = useRef<{
    pointerId: number;
    startX: number;
    startY: number;
    originX: number;
    originY: number;
  } | null>(null);
  const fitState = useRef<
    | {
        zoom: number;
        offset: { x: number; y: number };
        origin: { x: number; y: number };
      }
    | null
  >(null);
  const zoomRef = useRef(1);
  const [isPanning, setIsPanning] = useState(false);

  const content = useMemo(() => ({ __html: svg }), [svg]);

  useEffect(() => {
    zoomRef.current = zoom;
  }, [zoom]);

  const applyZoom = useCallback(
    (targetZoom: number, anchor?: { x: number; y: number }) => {
      const container = containerRef.current;
      if (!container) {
        return;
      }
      const rect = container.getBoundingClientRect();
      setZoomState((prevZoom) => {
        const base = prevZoom === 0 ? 1 : prevZoom;
        const clamped = clamp(targetZoom, MIN_ZOOM, MAX_ZOOM);
        const scale = clamped / base;
        setOffsetState((prevOffset) => {
          const pivotX = anchor?.x ?? rect.width / 2;
          const pivotY = anchor?.y ?? rect.height / 2;
          const nextOffset = {
            x: pivotX - (pivotX - prevOffset.x) * scale,
            y: pivotY - (pivotY - prevOffset.y) * scale,
          };
          return nextOffset;
        });
        return clamped;
      });
    },
    [],
  );

  const updateFitState = useCallback(() => {
    const container = containerRef.current;
    const svgElement = container?.querySelector("svg");
    if (!container || !svgElement) {
      return;
    }

    const containerRect = container.getBoundingClientRect();
    if (containerRect.width === 0 || containerRect.height === 0) {
      return;
    }
    const view = svgElement.viewBox?.baseVal;
    const rawWidth =
      view?.width || parseSvgDimension(svgElement.getAttribute("width")) || 0;
    const rawHeight =
      view?.height || parseSvgDimension(svgElement.getAttribute("height")) || 0;
    let bbox: DOMRect | null = null;
    try {
      const candidate = svgElement.getBBox();
      if (Number.isFinite(candidate.x) && Number.isFinite(candidate.y)) {
        bbox = candidate;
      }
    } catch {
      bbox = null;
    }
    const contentWidth = bbox?.width && bbox.width > 0 ? bbox.width : rawWidth;
    const contentHeight = bbox?.height && bbox.height > 0 ? bbox.height : rawHeight;
    if (!contentWidth || !contentHeight) {
      return;
    }
    const desiredZoom = 1;
    const fitZoom = clamp(desiredZoom, MIN_ZOOM, MAX_ZOOM);
    const scaledWidth = contentWidth * fitZoom;
    const scaledHeight = contentHeight * fitZoom;
    const offsetX = containerRect.width / 2 - scaledWidth / 2;
    const offsetY = containerRect.height / 2 - scaledHeight / 2;
    const origin = {
      x: bbox?.x ?? 0,
      y: bbox?.y ?? 0,
    };
    const next = {
      zoom: fitZoom,
      offset: {
        x: Number.isFinite(offsetX) ? offsetX : initialOffset.x,
        y: Number.isFinite(offsetY) ? offsetY : initialOffset.y,
      },
      origin,
    };
    fitState.current = next;
    zoomRef.current = next.zoom;
    setZoomState(next.zoom);
    setOffsetState(next.offset);
    setContentOrigin(origin);
    panState.current = null;
    setIsPanning(false);
    onStateChange?.({ zoom: next.zoom });
  }, [onStateChange]);

  useEffect(() => {
    const frame = requestAnimationFrame(updateFitState);
    return () => cancelAnimationFrame(frame);
  }, [svg, updateFitState]);

  // Handle node clicks and highlighting
  useEffect(() => {
    const container = containerRef.current;
    if (!container || !onNodeClick) {
      return;
    }

    const handleClick = (event: MouseEvent) => {
      // Find if we clicked on a node or its children
      let target = event.target as Element | null;
      let nodeElement: Element | null = null;

      // Walk up the DOM tree to find the .node element
      while (target && target !== container) {
        if (target.classList?.contains("node")) {
          nodeElement = target;
          break;
        }
        target = target.parentElement;
      }

      if (nodeElement) {
        // Extract class ID from the <title> element
        const titleElement = nodeElement.querySelector("title");
        if (titleElement) {
          const classId = titleElement.textContent?.trim();
          if (classId) {
            onNodeClick(classId);
          }
        }
      }
    };

    container.addEventListener("click", handleClick);
    return () => container.removeEventListener("click", handleClick);
  }, [onNodeClick]);

  // Apply highlighting to selected node
  useEffect(() => {
    const container = containerRef.current;
    if (!container) {
      return;
    }

    // Remove previous highlights
    const previousHighlights = container.querySelectorAll(".node.highlighted");
    previousHighlights.forEach((node) => node.classList.remove("highlighted"));

    if (!selectedNodeId) {
      return;
    }

    // Find and highlight the selected node
    const nodes = container.querySelectorAll(".node");
    nodes.forEach((node) => {
      const title = node.querySelector("title");
      if (title?.textContent?.trim() === selectedNodeId) {
        node.classList.add("highlighted");
      }
    });
  }, [selectedNodeId, svg]);

  useEffect(() => {
    onStateChange?.({ zoom });
  }, [zoom, onStateChange]);

  useEffect(() => {
    const container = containerRef.current;
    if (!container) {
      return;
    }
    const handler = (event: WheelEvent) => {
      if (!event.ctrlKey) {
        event.preventDefault();
      }
      const delta = event.deltaY;
      const factor = delta < 0 ? 1.1 : 0.9;
      const rect = container.getBoundingClientRect();
      const anchor = {
        x: event.clientX - rect.left,
        y: event.clientY - rect.top,
      };
      applyZoom(zoomRef.current * factor, anchor);
    };
    container.addEventListener("wheel", handler, { passive: false });
    return () => container.removeEventListener("wheel", handler);
  }, [applyZoom]);

  const handlePointerDown = useCallback((event: ReactPointerEvent<HTMLDivElement>) => {
    if (event.pointerType === "mouse" && event.button !== 0) {
      return;
    }
    event.preventDefault();
    if (!containerRef.current) {
      return;
    }
    containerRef.current.setPointerCapture(event.pointerId);
    panState.current = {
      pointerId: event.pointerId,
      startX: event.clientX,
      startY: event.clientY,
      originX: offset.x,
      originY: offset.y,
    };
    setIsPanning(true);
  }, [offset]);

  const handlePointerMove = useCallback((event: ReactPointerEvent<HTMLDivElement>) => {
    const state = panState.current;
    if (!state || state.pointerId !== event.pointerId) {
      return;
    }
    event.preventDefault();
    const dx = event.clientX - state.startX;
    const dy = event.clientY - state.startY;
    setOffsetState({
      x: state.originX + dx,
      y: state.originY + dy,
    });
  }, []);

  const endPan = useCallback((event: ReactPointerEvent<HTMLDivElement>) => {
    if (panState.current?.pointerId === event.pointerId) {
      containerRef.current?.releasePointerCapture(event.pointerId);
      panState.current = null;
      setIsPanning(false);
    }
  }, []);

  useImperativeHandle(
    ref,
    () => ({
      setZoom: (value: number) => {
        const container = containerRef.current;
        if (!container) {
          return;
        }
        const rect = container.getBoundingClientRect();
        applyZoom(value, { x: rect.width / 2, y: rect.height / 2 });
      },
      resetView: () => {
        if (!fitState.current) {
          updateFitState();
        } else {
          setZoomState(fitState.current.zoom);
          setOffsetState(fitState.current.offset);
          setContentOrigin(fitState.current.origin);
          panState.current = null;
          setIsPanning(false);
          onStateChange?.({ zoom: fitState.current.zoom });
        }
      },
    }),
    [applyZoom, onStateChange, updateFitState],
  );

  return (
    <div
      ref={containerRef}
      className="uml-svg"
      onPointerDown={handlePointerDown}
      onPointerMove={handlePointerMove}
      onPointerUp={endPan}
      onPointerLeave={endPan}
      style={{ cursor: isPanning ? "grabbing" : "grab" }}
    >
      <div
        className="uml-svg-inner"
        style={{
          transform: `translate(${offset.x}px, ${offset.y}px) scale(${zoom}) translate(${-contentOrigin.x}px, ${-contentOrigin.y}px)`,
          transformOrigin: "top left",
        }}
        dangerouslySetInnerHTML={content}
      />
    </div>
  );
});

function parseSvgDimension(raw: string | null): number | null {
  if (!raw) {
    return null;
  }
  const match = raw.trim().match(/^([0-9]+(?:\.[0-9]+)?)\s*(pt|px)?$/i);
  if (!match) {
    return null;
  }
  const value = parseFloat(match[1]);
  const unit = match[2]?.toLowerCase();
  if (!Number.isFinite(value)) {
    return null;
  }
  if (unit === "pt") {
    return value * (96 / 72);
  }
  return value;
}
