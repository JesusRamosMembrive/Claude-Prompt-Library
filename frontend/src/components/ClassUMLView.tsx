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

import { useClassUmlQuery, buildGraphvizSignature } from "../hooks/useClassUmlQuery";
import type { GraphvizOptionsPayload, UMLClass } from "../api/types";

const DEFAULT_PREFIXES = "";
const UML_ZOOM_MIN = 0.05;
const UML_ZOOM_MAX = 4;
const UML_ZOOM_STEP = 0.05;

type GraphvizFormState = {
  layoutEngine: string;
  rankdir: string;
  splines: string;
  nodesep: string;
  ranksep: string;
  pad: string;
  margin: string;
  bgcolor: string;
  graphFontname: string;
  graphFontsize: string;
  nodeShape: string;
  nodeStyle: string;
  nodeFillcolor: string;
  nodeColor: string;
  nodeFontcolor: string;
  nodeFontname: string;
  nodeFontsize: string;
  nodeWidth: string;
  nodeHeight: string;
  nodeMarginX: string;
  nodeMarginY: string;
  edgeColor: string;
  edgeFontname: string;
  edgeFontsize: string;
  edgePenwidth: string;
  inheritanceStyle: string;
  inheritanceColor: string;
  associationColor: string;
  instantiationColor: string;
  referenceColor: string;
  inheritanceArrowhead: string;
  associationArrowhead: string;
  instantiationArrowhead: string;
  referenceArrowhead: string;
  associationStyle: string;
  instantiationStyle: string;
  referenceStyle: string;
};

const DEFAULT_GRAPHVIZ_FORM: GraphvizFormState = {
  layoutEngine: "dot",
  rankdir: "LR",
  splines: "true",
  nodesep: "0.6",
  ranksep: "1.1",
  pad: "0.3",
  margin: "0",
  bgcolor: "#0b1120",
  graphFontname: "Inter",
  graphFontsize: "11",
  nodeShape: "box",
  nodeStyle: "rounded,filled",
  nodeFillcolor: "#111827",
  nodeColor: "#1f2937",
  nodeFontcolor: "#e2e8f0",
  nodeFontname: "Inter",
  nodeFontsize: "11",
  nodeWidth: "1.6",
  nodeHeight: "0.6",
  nodeMarginX: "0.12",
  nodeMarginY: "0.06",
  edgeColor: "#475569",
  edgeFontname: "Inter",
  edgeFontsize: "9",
  edgePenwidth: "1",
  inheritanceStyle: "solid",
  inheritanceColor: "#60a5fa",
  associationColor: "#f97316",
  instantiationColor: "#10b981",
  referenceColor: "#a855f7",
  inheritanceArrowhead: "empty",
  associationArrowhead: "normal",
  instantiationArrowhead: "diamond",
  referenceArrowhead: "vee",
  associationStyle: "dashed",
  instantiationStyle: "dashed",
  referenceStyle: "dotted",
};

const GRAPHVIZ_LAYOUT_ENGINES = ["dot", "neato", "fdp", "sfdp", "circo", "twopi"];
const GRAPHVIZ_RANKDIRS = ["LR", "RL", "TB", "BT"];
const GRAPHVIZ_SPLINES = ["true", "false", "polyline", "line", "spline", "curved", "ortho"];
const GRAPHVIZ_NODE_SHAPES = ["box", "rect", "ellipse", "record", "plaintext", "component", "cylinder", "tab"];
const GRAPHVIZ_ARROWHEADS = ["normal", "empty", "vee", "diamond", "dot", "obox"];
const GRAPHVIZ_EDGE_STYLES = ["solid", "dashed", "dotted", "bold", "invis"];
const RELATION_META = [
  {
    key: "inheritance",
    label: "Inheritance",
    helper: "Extends",
    colorKey: "inheritanceColor",
    arrowKey: "inheritanceArrowhead",
    styleKey: "inheritanceStyle",
  },
  {
    key: "association",
    label: "Association",
    helper: "Uses",
    colorKey: "associationColor",
    arrowKey: "associationArrowhead",
    styleKey: "associationStyle",
  },
  {
    key: "instantiation",
    label: "Instantiation",
    helper: "Creates",
    colorKey: "instantiationColor",
    arrowKey: "instantiationArrowhead",
    styleKey: "instantiationStyle",
  },
  {
    key: "reference",
    label: "Reference",
    helper: "Type hints",
    colorKey: "referenceColor",
    arrowKey: "referenceArrowhead",
    styleKey: "referenceStyle",
  },
] as const satisfies ReadonlyArray<{
  key: "inheritance" | "association" | "instantiation" | "reference";
  label: string;
  helper: string;
  colorKey: keyof GraphvizFormState;
  arrowKey: keyof GraphvizFormState;
  styleKey: keyof GraphvizFormState;
}>;

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
  const [graphvizForm, setGraphvizForm] = useState<GraphvizFormState>(() => ({
    ...DEFAULT_GRAPHVIZ_FORM,
  }));
  const [isGraphvizSidebarOpen, setIsGraphvizSidebarOpen] = useState(true);

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
  const graphvizOptions = useMemo(() => graphvizFormToPayload(graphvizForm), [graphvizForm]);
  const graphvizSignature = useMemo(
    () => buildGraphvizSignature(graphvizOptions),
    [graphvizOptions],
  );

  const query = useClassUmlQuery({
    includeExternal,
    modulePrefixes,
    edgeTypes: edgeTypesArray,
    graphvizOptions,
    graphvizSignature,
  });
  const data = query.data;
  const classCount = data?.classCount ?? 0;
  const svgMarkup = data?.svg ?? null;
  const stats = data?.stats;
  const classes = useMemo(() => data?.classes ?? [], [data?.classes]);

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

  const handleGraphvizInputChange = useCallback(
    (key: keyof GraphvizFormState, value: string) => {
      setGraphvizForm((prev) => ({ ...prev, [key]: value }));
    },
    [],
  );

  const resetGraphvizOptions = useCallback(() => {
    setGraphvizForm({ ...DEFAULT_GRAPHVIZ_FORM });
  }, []);

  return (
    <div className={`uml-view ${isGraphvizSidebarOpen ? "sidebar-open" : ""}`}>
      <div className="uml-content">
      <section className="uml-search-section" aria-label="Class search">
        <div className="uml-search-container">
          <label htmlFor="uml-search" className="sr-only">
            Search class
          </label>
          <input
            id="uml-search"
            type="text"
            className="uml-search-input"
            placeholder="Search class by name, module, or file..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            aria-label="Search class by name, module, or file"
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
                  aria-label={`Select class ${cls.name} from module ${cls.module}`}
                >
                  <div className="search-result-name">{cls.name}</div>
                  <div className="search-result-path">{cls.module}</div>
                </button>
              ))}
              {filteredClasses.length > 10 && (
                <div className="uml-search-more">
                  +{filteredClasses.length - 10} more results
                </div>
              )}
            </div>
          )}
        </div>
      </section>

      <section className="uml-controls">
        <div className="control-block">
          <h2>Module prefixes</h2>
          <input
            type="text"
            className="uml-filter-input"
            value={prefixInput}
            onChange={(event) => setPrefixInput(event.target.value)}
            placeholder="E.g. api, src"
            aria-label="Filter by module prefixes (comma separated)"
          />
        </div>

        <label className="control-checkbox">
          <input
            type="checkbox"
            checked={includeExternal}
            onChange={() => setIncludeExternal((prev) => !prev)}
          />
          <span>Include external classes</span>
        </label>

        <div className="control-block">
          <h2>Relationship types</h2>
          <div className="control-row">
            <label className="control-checkbox">
              <input
                type="checkbox"
                checked={edgeTypes.has("inheritance")}
                onChange={() => toggleEdgeType("inheritance")}
              />
              <span style={{ color: "#60a5fa" }}>Inheritance</span>
            </label>
            <label className="control-checkbox">
              <input
                type="checkbox"
                checked={edgeTypes.has("association")}
                onChange={() => toggleEdgeType("association")}
              />
              <span style={{ color: "#f97316" }}>Association</span>
            </label>
            <label className="control-checkbox">
              <input
                type="checkbox"
                checked={edgeTypes.has("instantiation")}
                onChange={() => toggleEdgeType("instantiation")}
              />
              <span style={{ color: "#10b981" }}>Instantiation</span>
            </label>
            <label className="control-checkbox">
              <input
                type="checkbox"
                checked={edgeTypes.has("reference")}
                onChange={() => toggleEdgeType("reference")}
              />
              <span style={{ color: "#a855f7" }}>References</span>
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
          {query.isFetching ? "Refreshing…" : "Regenerate"}
        </button>

        <button
          className="secondary-btn"
          type="button"
          onClick={() => setIsGraphvizSidebarOpen((prev) => !prev)}
          aria-label={isGraphvizSidebarOpen ? "Hide Graphviz options" : "Show Graphviz options"}
        >
          {isGraphvizSidebarOpen ? "Hide Options" : "Show Options"}
        </button>
      </section>

      {!query.isLoading && !query.isError && classCount > 0 && (
        <section className="uml-legend" aria-label="Relationship legend">
          <h3>Legend</h3>
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
              <span>Inheritance (extends)</span>
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
              <span>Association (uses)</span>
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
              <span>Instantiation (creates)</span>
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
              <span>References (refers)</span>
            </div>
          </div>
        </section>
      )}

      {stats && !query.isLoading && !query.isError && (
        <section className="uml-stats" aria-label="UML model summary">
          <div className="uml-stat">
            <span className="uml-stat-label">Classes</span>
            <strong className="uml-stat-value">{stats.classes ?? classCount}</strong>
          </div>
          <div className="uml-stat">
            <span className="uml-stat-label">Inheritance</span>
            <strong className="uml-stat-value" style={{ color: "#60a5fa" }}>
              {stats.inheritance_edges ?? 0}
            </strong>
          </div>
          <div className="uml-stat">
            <span className="uml-stat-label">Associations</span>
            <strong className="uml-stat-value" style={{ color: "#f97316" }}>
              {stats.association_edges ?? 0}
            </strong>
          </div>
          <div className="uml-stat">
            <span className="uml-stat-label">Instantiations</span>
            <strong className="uml-stat-value" style={{ color: "#10b981" }}>
              {stats.instantiation_edges ?? 0}
            </strong>
          </div>
          <div className="uml-stat">
            <span className="uml-stat-label">References</span>
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
            <p className="summary-info">Generating UML model…</p>
          </div>
        ) : query.isError ? (
          <p className="summary-error" role="alert">
            Could not generate the model: {String(query.error)}
          </p>
        ) : classCount === 0 ? (
          <p className="summary-info">No classes match the selected filters.</p>
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
          <p className="summary-info">The backend did not return a valid diagram.</p>
        )}
      </section>
      </div>
      {isGraphvizSidebarOpen && (
        <aside
          className="graphviz-sidebar"
          role="dialog"
          aria-label="Graphviz layout and styling options"
          aria-modal="false"
        >
          <div className="graphviz-header">
            <div>
              <h2>Graphviz layout & styling</h2>
              <p>
                Adjust the rendering engine, spacing, palette, and edge styles before regenerating
                the SVG.
              </p>
            </div>
            <button type="button" className="link-btn" onClick={resetGraphvizOptions}>
              Reset styling
            </button>
          </div>

          <div className="graphviz-groups">
            <div className="graphviz-group">
              <h3>Layout</h3>
              <div className="graphviz-grid">
                <label className="graphviz-field">
                  <span>Engine</span>
                  <select
                    value={graphvizForm.layoutEngine}
                    onChange={(event) => handleGraphvizInputChange("layoutEngine", event.target.value)}
                  >
                    {GRAPHVIZ_LAYOUT_ENGINES.map((engine) => (
                      <option key={engine} value={engine}>
                        {engine.toUpperCase()}
                      </option>
                    ))}
                  </select>
                </label>

                <label className="graphviz-field">
                  <span>Rank direction</span>
                  <select
                    value={graphvizForm.rankdir}
                    onChange={(event) => handleGraphvizInputChange("rankdir", event.target.value)}
                  >
                    {GRAPHVIZ_RANKDIRS.map((dir) => (
                      <option key={dir} value={dir}>
                        {dir}
                      </option>
                    ))}
                  </select>
                </label>

                <label className="graphviz-field">
                  <span>Splines</span>
                  <select
                    value={graphvizForm.splines}
                    onChange={(event) => handleGraphvizInputChange("splines", event.target.value)}
                  >
                    {GRAPHVIZ_SPLINES.map((mode) => (
                      <option key={mode} value={mode}>
                        {mode}
                      </option>
                    ))}
                  </select>
                </label>

                <label className="graphviz-field">
                  <span>Node spacing</span>
                  <input
                    type="number"
                    min={0.1}
                    max={5}
                    step={0.1}
                    value={graphvizForm.nodesep}
                    onChange={(event) => handleGraphvizInputChange("nodesep", event.target.value)}
                  />
                </label>

                <label className="graphviz-field">
                  <span>Rank spacing</span>
                  <input
                    type="number"
                    min={0.4}
                    max={8}
                    step={0.1}
                    value={graphvizForm.ranksep}
                    onChange={(event) => handleGraphvizInputChange("ranksep", event.target.value)}
                  />
                </label>

                <label className="graphviz-field">
                  <span>Padding</span>
                  <input
                    type="number"
                    min={0}
                    max={5}
                    step={0.1}
                    value={graphvizForm.pad}
                    onChange={(event) => handleGraphvizInputChange("pad", event.target.value)}
                  />
                </label>

                <label className="graphviz-field">
                  <span>Margin</span>
                  <input
                    type="number"
                    min={0}
                    max={5}
                    step={0.1}
                    value={graphvizForm.margin}
                    onChange={(event) => handleGraphvizInputChange("margin", event.target.value)}
                  />
                </label>

                <label className="graphviz-field">
                  <span>Background</span>
                  <div className="graphviz-color-input">
                    <input
                      type="color"
                      value={graphvizForm.bgcolor}
                      aria-label="Pick background color"
                      onChange={(event) => handleGraphvizInputChange("bgcolor", event.target.value)}
                    />
                    <input
                      type="text"
                      value={graphvizForm.bgcolor}
                      onChange={(event) => handleGraphvizInputChange("bgcolor", event.target.value)}
                    />
                  </div>
                </label>

                <label className="graphviz-field">
                  <span>Graph font</span>
                  <input
                    type="text"
                    value={graphvizForm.graphFontname}
                    onChange={(event) => handleGraphvizInputChange("graphFontname", event.target.value)}
                  />
                </label>

                <label className="graphviz-field">
                  <span>Graph font size</span>
                  <input
                    type="number"
                    min={6}
                    max={32}
                    step={1}
                    value={graphvizForm.graphFontsize}
                    onChange={(event) => handleGraphvizInputChange("graphFontsize", event.target.value)}
                  />
                </label>
              </div>
            </div>

            <div className="graphviz-group">
              <h3>Nodes</h3>
              <div className="graphviz-grid">
                <label className="graphviz-field">
                  <span>Shape</span>
                  <select
                    value={graphvizForm.nodeShape}
                    onChange={(event) => handleGraphvizInputChange("nodeShape", event.target.value)}
                  >
                    {GRAPHVIZ_NODE_SHAPES.map((shape) => (
                      <option key={shape} value={shape}>
                        {shape}
                      </option>
                    ))}
                  </select>
                </label>

                <label className="graphviz-field">
                  <span>Style</span>
                  <input
                    type="text"
                    value={graphvizForm.nodeStyle}
                    onChange={(event) => handleGraphvizInputChange("nodeStyle", event.target.value)}
                    placeholder="rounded,filled"
                  />
                </label>

                <label className="graphviz-field">
                  <span>Fill</span>
                  <div className="graphviz-color-input">
                    <input
                      type="color"
                      value={graphvizForm.nodeFillcolor}
                      aria-label="Pick node fill color"
                      onChange={(event) =>
                        handleGraphvizInputChange("nodeFillcolor", event.target.value)
                      }
                    />
                    <input
                      type="text"
                      value={graphvizForm.nodeFillcolor}
                      onChange={(event) =>
                        handleGraphvizInputChange("nodeFillcolor", event.target.value)
                      }
                    />
                  </div>
                </label>

                <label className="graphviz-field">
                  <span>Border</span>
                  <div className="graphviz-color-input">
                    <input
                      type="color"
                      value={graphvizForm.nodeColor}
                      aria-label="Pick node border color"
                      onChange={(event) => handleGraphvizInputChange("nodeColor", event.target.value)}
                    />
                    <input
                      type="text"
                      value={graphvizForm.nodeColor}
                      onChange={(event) => handleGraphvizInputChange("nodeColor", event.target.value)}
                    />
                  </div>
                </label>

                <label className="graphviz-field">
                  <span>Text color</span>
                  <div className="graphviz-color-input">
                    <input
                      type="color"
                      value={graphvizForm.nodeFontcolor}
                      aria-label="Pick node text color"
                      onChange={(event) =>
                        handleGraphvizInputChange("nodeFontcolor", event.target.value)
                      }
                    />
                    <input
                      type="text"
                      value={graphvizForm.nodeFontcolor}
                      onChange={(event) =>
                        handleGraphvizInputChange("nodeFontcolor", event.target.value)
                      }
                    />
                  </div>
                </label>

                <label className="graphviz-field">
                  <span>Node font</span>
                  <input
                    type="text"
                    value={graphvizForm.nodeFontname}
                    onChange={(event) => handleGraphvizInputChange("nodeFontname", event.target.value)}
                  />
                </label>

                <label className="graphviz-field">
                  <span>Node font size</span>
                  <input
                    type="number"
                    min={6}
                    max={32}
                    step={1}
                    value={graphvizForm.nodeFontsize}
                    onChange={(event) => handleGraphvizInputChange("nodeFontsize", event.target.value)}
                  />
                </label>

                <label className="graphviz-field">
                  <span>Min width</span>
                  <input
                    type="number"
                    min={0.2}
                    max={6}
                    step={0.1}
                    value={graphvizForm.nodeWidth}
                    onChange={(event) => handleGraphvizInputChange("nodeWidth", event.target.value)}
                  />
                </label>

                <label className="graphviz-field">
                  <span>Min height</span>
                  <input
                    type="number"
                    min={0.2}
                    max={6}
                    step={0.1}
                    value={graphvizForm.nodeHeight}
                    onChange={(event) => handleGraphvizInputChange("nodeHeight", event.target.value)}
                  />
                </label>

                <label className="graphviz-field">
                  <span>Margin X</span>
                  <input
                    type="number"
                    min={0.02}
                    max={1}
                    step={0.01}
                    value={graphvizForm.nodeMarginX}
                    onChange={(event) => handleGraphvizInputChange("nodeMarginX", event.target.value)}
                  />
                </label>

                <label className="graphviz-field">
                  <span>Margin Y</span>
                  <input
                    type="number"
                    min={0.02}
                    max={1}
                    step={0.01}
                    value={graphvizForm.nodeMarginY}
                    onChange={(event) => handleGraphvizInputChange("nodeMarginY", event.target.value)}
                  />
                </label>
              </div>
            </div>

            <div className="graphviz-group">
              <h3>Edges & relationships</h3>
              <div className="graphviz-grid">
                <label className="graphviz-field">
                  <span>Default edge color</span>
                  <div className="graphviz-color-input">
                    <input
                      type="color"
                      value={graphvizForm.edgeColor}
                      aria-label="Pick edge color"
                      onChange={(event) => handleGraphvizInputChange("edgeColor", event.target.value)}
                    />
                    <input
                      type="text"
                      value={graphvizForm.edgeColor}
                      onChange={(event) => handleGraphvizInputChange("edgeColor", event.target.value)}
                    />
                  </div>
                </label>

                <label className="graphviz-field">
                  <span>Edge font</span>
                  <input
                    type="text"
                    value={graphvizForm.edgeFontname}
                    onChange={(event) => handleGraphvizInputChange("edgeFontname", event.target.value)}
                  />
                </label>

                <label className="graphviz-field">
                  <span>Edge font size</span>
                  <input
                    type="number"
                    min={6}
                    max={24}
                    step={1}
                    value={graphvizForm.edgeFontsize}
                    onChange={(event) => handleGraphvizInputChange("edgeFontsize", event.target.value)}
                  />
                </label>

                <label className="graphviz-field">
                  <span>Stroke width</span>
                  <input
                    type="number"
                    min={0.5}
                    max={4}
                    step={0.1}
                    value={graphvizForm.edgePenwidth}
                    onChange={(event) => handleGraphvizInputChange("edgePenwidth", event.target.value)}
                  />
                </label>
              </div>

              <div className="graphviz-relations">
                {RELATION_META.map(({ key, label, helper, colorKey, arrowKey, styleKey }) => (
                  <div key={key} className="graphviz-relation-row">
                    <div className="graphviz-relation-label">
                      <span>{label}</span>
                      <small>{helper}</small>
                    </div>
                    <div className="graphviz-relation-controls">
                      <label>
                        <span>Color</span>
                        <div className="graphviz-color-input">
                          <input
                            type="color"
                            value={graphvizForm[colorKey]}
                            aria-label={`Pick ${label} color`}
                            onChange={(event) =>
                              handleGraphvizInputChange(colorKey, event.target.value)
                            }
                          />
                          <input
                            type="text"
                            value={graphvizForm[colorKey]}
                            onChange={(event) =>
                              handleGraphvizInputChange(colorKey, event.target.value)
                            }
                          />
                        </div>
                      </label>

                      <label>
                        <span>Arrowhead</span>
                        <select
                          value={graphvizForm[arrowKey]}
                          onChange={(event) =>
                            handleGraphvizInputChange(arrowKey, event.target.value)
                          }
                        >
                          {GRAPHVIZ_ARROWHEADS.map((arrow) => (
                            <option key={arrow} value={arrow}>
                              {arrow}
                            </option>
                          ))}
                        </select>
                      </label>

                      <label>
                        <span>Line style</span>
                        <select
                          value={graphvizForm[styleKey]}
                          onChange={(event) =>
                            handleGraphvizInputChange(styleKey, event.target.value)
                          }
                        >
                          {GRAPHVIZ_EDGE_STYLES.map((style) => (
                            <option key={style} value={style}>
                              {style}
                            </option>
                          ))}
                        </select>
                      </label>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </aside>
      )}
    </div>
  );
}

function graphvizFormToPayload(form: GraphvizFormState): GraphvizOptionsPayload {
  return {
    layoutEngine: form.layoutEngine,
    rankdir: form.rankdir,
    splines: form.splines,
    nodesep: toNumber(form.nodesep),
    ranksep: toNumber(form.ranksep),
    pad: toNumber(form.pad),
    margin: toNumber(form.margin),
    bgcolor: form.bgcolor,
    graphFontname: form.graphFontname,
    graphFontsize: toNumber(form.graphFontsize),
    nodeShape: form.nodeShape,
    nodeStyle: form.nodeStyle,
    nodeFillcolor: form.nodeFillcolor,
    nodeColor: form.nodeColor,
    nodeFontcolor: form.nodeFontcolor,
    nodeFontname: form.nodeFontname,
    nodeFontsize: toNumber(form.nodeFontsize),
    nodeWidth: toNumber(form.nodeWidth),
    nodeHeight: toNumber(form.nodeHeight),
    nodeMarginX: toNumber(form.nodeMarginX),
    nodeMarginY: toNumber(form.nodeMarginY),
    edgeColor: form.edgeColor,
    edgeFontname: form.edgeFontname,
    edgeFontsize: toNumber(form.edgeFontsize),
    edgePenwidth: toNumber(form.edgePenwidth),
    inheritanceStyle: form.inheritanceStyle,
    inheritanceColor: form.inheritanceColor,
    associationColor: form.associationColor,
    instantiationColor: form.instantiationColor,
    referenceColor: form.referenceColor,
    inheritanceArrowhead: form.inheritanceArrowhead,
    associationArrowhead: form.associationArrowhead,
    instantiationArrowhead: form.instantiationArrowhead,
    referenceArrowhead: form.referenceArrowhead,
    associationStyle: form.associationStyle,
    instantiationStyle: form.instantiationStyle,
    referenceStyle: form.referenceStyle,
  };
}

function toNumber(value: string): number | undefined {
  if (!value.trim()) {
    return undefined;
  }
  const parsed = Number(value);
  return Number.isFinite(parsed) ? parsed : undefined;
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
          aria-label="Close details panel"
          title="Close (Esc)"
        >
          ✕
        </button>
      </header>

      <div className="class-details-body">
        <section className="class-details-section">
          <h3>Information</h3>
          <dl>
            <dt>Module</dt>
            <dd>{classInfo.module}</dd>
            <dt>File</dt>
            <dd>{classInfo.file}</dd>
            {classInfo.bases.length > 0 && (
              <>
                <dt>Inherits from</dt>
                <dd>{classInfo.bases.join(", ")}</dd>
              </>
            )}
          </dl>
        </section>

        {classInfo.attributes.length > 0 && (
          <section className="class-details-section">
            <h3>Attributes ({classInfo.attributes.length})</h3>
            <ul className="class-members-list">
              {classInfo.attributes.map((attr, idx) => (
                <li key={idx}>
                  <code className="member-name">{attr.name}</code>
                  {attr.type && <span className="member-type">: {attr.type}</span>}
                  {attr.optional && <span className="member-optional"> (optional)</span>}
                </li>
              ))}
            </ul>
          </section>
        )}

        {classInfo.methods.length > 0 && (
          <section className="class-details-section">
            <h3>Methods ({classInfo.methods.length})</h3>
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
            <h3>Associations ({classInfo.associations.length})</h3>
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
