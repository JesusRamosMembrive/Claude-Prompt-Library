import { useMemo, useState } from "react";
import { useQuery } from "@tanstack/react-query";

import { getFileSummary } from "../api/client";
import { queryKeys } from "../api/queryKeys";
import type { SymbolInfo } from "../api/types";
import { useSelectionStore } from "../state/useSelectionStore";
import { PreviewPane } from "./PreviewPane";
import { TraceModal } from "./TraceModal";

interface ClassWithMethods {
  symbol: SymbolInfo;
  methods: SymbolInfo[];
}

interface GroupedSymbols {
  classes: ClassWithMethods[];
  functions: SymbolInfo[];
}

export function DetailPanel(): JSX.Element {
  const selectedPath = useSelectionStore((state) => state.selectedPath);
  const [traceTarget, setTraceTarget] = useState<string | null>(null);

  const { data, isPending, isError, error } = useQuery({
    queryKey: queryKeys.file(selectedPath ?? ""),
    queryFn: () => getFileSummary(selectedPath!),
    enabled: Boolean(selectedPath),
  });

  const grouped = useMemo<GroupedSymbols>(() => {
    if (!data) {
      return { classes: [], functions: [] };
    }

    const classSymbols = data.symbols.filter((symbol) => symbol.kind === "class");
    const methodSymbols = data.symbols.filter((symbol) => symbol.kind === "method");
    const functionSymbols = data.symbols.filter(
      (symbol) => symbol.kind === "function"
    );

    const methodsMap = new Map<string, SymbolInfo[]>();
    for (const method of methodSymbols) {
      if (!method.parent) {
        continue;
      }
      const list = methodsMap.get(method.parent) ?? [];
      list.push(method);
      methodsMap.set(method.parent, list);
    }

    return {
      classes: classSymbols.map((cls) => ({
        symbol: cls,
        methods: (methodsMap.get(cls.name) ?? []).sort(
          (a, b) => a.lineno - b.lineno
        ),
      })),
      functions: functionSymbols.sort((a, b) => a.lineno - b.lineno),
    };
  }, [data]);

  if (!selectedPath) {
    return (
      <section className="panel">
        <div className="placeholder">
          <h3>Select a file</h3>
          <p>
            Click a file in the tree to see its classes, methods, and functions. Any docstrings you
            add will appear as descriptions.
          </p>
        </div>
      </section>
    );
  }

  if (isPending) {
    return (
      <section className="panel">
        <p style={{ color: "#7f869d" }}>
          Loading symbols for <strong>{selectedPath}</strong>…
        </p>
      </section>
    );
  }

  if (isError) {
    return (
      <section className="panel">
        <div className="error-banner">
          Error loading <strong>{selectedPath}</strong>:{" "}
          {(error as Error)?.message ?? "try again"}
        </div>
      </section>
    );
  }

  if (!data) {
    return (
      <section className="panel">
        <p style={{ color: "#7f869d" }}>
          No information available for <strong>{selectedPath}</strong>.
        </p>
      </section>
    );
  }

  const modified =
    data.modified_at != null ? new Date(data.modified_at).toLocaleString() : "—";

  return (
    <section className="panel">
      <div className="detail-header">
        <div>
          <h2>{selectedPath}</h2>
          <div className="detail-meta">
            Last modified: {modified} · {data.symbols.length} symbols
          </div>
        </div>
        {data.errors.length > 0 && (
          <span className="badge" style={{ background: "rgba(249, 115, 22, 0.18)", color: "#f9a84b" }}>
            {data.errors.length} errors
          </span>
        )}
      </div>

      {data.errors.length > 0 && (
        <div className="error-banner">
          {data.errors.map((issue, index) => (
            <div key={`${issue.message}-${index}`}>
              {issue.message}
              {issue.lineno != null ? ` · line ${issue.lineno}` : ""}
            </div>
          ))}
        </div>
      )}

      {grouped.classes.map(({ symbol, methods }) => (
        <article key={symbol.name} className="symbol-card">
          <div className="symbol-title">
            {symbol.name}
            <span className="symbol-meta">
              <span>line {symbol.lineno}</span>
              <span>{methods.length} methods</span>
            </span>
          </div>
          {symbol.docstring && (
            <p className="symbol-doc">{formatDocstring(symbol.docstring)}</p>
          )}
          <ul className="symbol-methods">
            {methods.map((method) => (
              <li key={method.name}>
                <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", gap: "8px" }}>
                  <div style={{ flex: 1 }}>
                    <span>
                      {method.parent}.{method.name} (line {method.lineno})
                    </span>
                    {method.docstring && (
                      <span className="symbol-method-doc">
                        {formatDocstring(method.docstring)}
                      </span>
                    )}
                  </div>
                  <button
                    onClick={() => setTraceTarget(`${selectedPath}::${method.parent}.${method.name}`)}
                    style={{
                      padding: "2px 8px",
                      fontSize: "11px",
                      background: "#5b9bd5",
                      color: "#fff",
                      border: "none",
                      borderRadius: "3px",
                      cursor: "pointer",
                      flexShrink: 0,
                    }}
                    title="Trace method calls"
                  >
                    Trace
                  </button>
                </div>
              </li>
            ))}
          </ul>
        </article>
      ))}

      {grouped.functions.map((fn) => (
        <article key={fn.name} className="symbol-card">
          <div className="symbol-title">
            <div style={{ display: "flex", alignItems: "center", gap: "8px", flex: 1 }}>
              {fn.name}
              <button
                onClick={() => setTraceTarget(`${selectedPath}::${fn.name}`)}
                style={{
                  padding: "2px 8px",
                  fontSize: "11px",
                  background: "#5b9bd5",
                  color: "#fff",
                  border: "none",
                  borderRadius: "3px",
                  cursor: "pointer",
                }}
                title="Trace function calls"
              >
                Trace
              </button>
            </div>
            <span className="symbol-meta">
              <span>line {fn.lineno}</span>
              <span>function</span>
            </span>
          </div>
          {fn.docstring ? (
            <p className="symbol-doc">{formatDocstring(fn.docstring)}</p>
          ) : (
            <p className="symbol-doc" style={{ opacity: 0.65 }}>
              No docstring
            </p>
          )}
        </article>
      ))}

      {grouped.classes.length === 0 && grouped.functions.length === 0 && (
        <div className="placeholder">
          <h3>File without exportable symbols</h3>
          <p>
            Add top-level functions or classes to visualize them here. Methods are automatically
            grouped under their class.
          </p>
        </div>
      )}

      {selectedPath && (
        <div className="preview-container">
          <h3 className="preview-title">Preview</h3>
          <PreviewPane path={selectedPath} />
        </div>
      )}

      {traceTarget && (
        <TraceModal
          qualifiedName={traceTarget}
          onClose={() => setTraceTarget(null)}
        />
      )}
    </section>
  );
}

function formatDocstring(docstring: string): string {
  return docstring.trim().split("\n\n")[0].replace(/\s+/g, " ");
}
