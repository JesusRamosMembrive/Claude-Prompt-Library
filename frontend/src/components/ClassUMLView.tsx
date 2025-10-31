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

  const query = useClassUmlQuery({ includeExternal, modulePrefixes });
  const data = query.data;
  const classCount = data?.classCount ?? 0;
  const svgMarkup = data?.svg ?? null;
  const stats = data?.stats;

  return (
    <div className="uml-view">
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

      {stats && !query.isLoading && !query.isError && (
        <section className="uml-stats" aria-label="Resumen del modelo UML">
          <div className="uml-stat">
            <span className="uml-stat-label">Clases</span>
            <strong className="uml-stat-value">{stats.classes ?? classCount}</strong>
          </div>
          <div className="uml-stat">
            <span className="uml-stat-label">Herencias</span>
            <strong className="uml-stat-value">{stats.inheritance_edges ?? 0}</strong>
          </div>
          <div className="uml-stat">
            <span className="uml-stat-label">Asociaciones</span>
            <strong className="uml-stat-value">{stats.association_edges ?? 0}</strong>
          </div>
        </section>
      )}

      <section className="uml-canvas">
        {query.isLoading ? (
          <p className="summary-info">Calculando modelo UML…</p>
        ) : query.isError ? (
          <p className="summary-error">No se pudo generar el modelo: {String(query.error)}</p>
        ) : classCount === 0 ? (
          <p className="summary-info">No hay clases para los filtros seleccionados.</p>
        ) : svgMarkup ? (
          <UmlSvgContainer ref={svgHandleRef} svg={svgMarkup} onStateChange={handleCanvasStateChange} />
        ) : (
          <p className="summary-info">El backend no devolvió un diagrama válido.</p>
        )}
      </section>
    </div>
  );
}

interface UmlSvgContainerProps {
  svg: string;
  onStateChange?: (state: UmlViewState) => void;
}

const MIN_ZOOM = UML_ZOOM_MIN;
const MAX_ZOOM = UML_ZOOM_MAX;

const clamp = (value: number, min: number, max: number) => Math.min(max, Math.max(min, value));

const initialOffset = { x: 0, y: 0 };

const UmlSvgContainer = forwardRef<UmlSvgHandle, UmlSvgContainerProps>(function UmlSvgContainer(
  { svg, onStateChange },
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
    const fitsHorizontally = scaledWidth <= containerRect.width;
    const fitsVertically = scaledHeight <= containerRect.height;
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
