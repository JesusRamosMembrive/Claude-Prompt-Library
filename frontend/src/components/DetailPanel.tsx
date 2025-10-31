import { useMemo } from "react";
import { useQuery } from "@tanstack/react-query";

import { getFileSummary } from "../api/client";
import { queryKeys } from "../api/queryKeys";
import type { SymbolInfo } from "../api/types";
import { useSelectionStore } from "../state/useSelectionStore";
import { PreviewPane } from "./PreviewPane";

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
          <h3>Selecciona un archivo</h3>
          <p>
            Haz clic sobre un archivo en el árbol para ver sus clases, métodos y
            funciones. Cuando añadas docstrings aparecerán como descripción.
          </p>
        </div>
      </section>
    );
  }

  if (isPending) {
    return (
      <section className="panel">
        <p style={{ color: "#7f869d" }}>
          Cargando símbolos de <strong>{selectedPath}</strong>…
        </p>
      </section>
    );
  }

  if (isError) {
    return (
      <section className="panel">
        <div className="error-banner">
          Error al cargar <strong>{selectedPath}</strong>:{" "}
          {(error as Error)?.message ?? "intenta de nuevo"}
        </div>
      </section>
    );
  }

  if (!data) {
    return (
      <section className="panel">
        <p style={{ color: "#7f869d" }}>
          No hay información disponible para <strong>{selectedPath}</strong>.
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
            Última modificación: {modified} · {data.symbols.length} símbolos
          </div>
        </div>
        {data.errors.length > 0 && (
          <span className="badge" style={{ background: "rgba(249, 115, 22, 0.18)", color: "#f9a84b" }}>
            {data.errors.length} errores
          </span>
        )}
      </div>

      {data.errors.length > 0 && (
        <div className="error-banner">
          {data.errors.map((issue, index) => (
            <div key={`${issue.message}-${index}`}>
              {issue.message}
              {issue.lineno != null ? ` · línea ${issue.lineno}` : ""}
            </div>
          ))}
        </div>
      )}

      {grouped.classes.map(({ symbol, methods }) => (
        <article key={symbol.name} className="symbol-card">
          <div className="symbol-title">
            {symbol.name}
            <span className="symbol-meta">
              <span>línea {symbol.lineno}</span>
              <span>{methods.length} métodos</span>
            </span>
          </div>
          {symbol.docstring && (
            <p className="symbol-doc">{formatDocstring(symbol.docstring)}</p>
          )}
          <ul className="symbol-methods">
            {methods.map((method) => (
              <li key={method.name}>
                <span>
                  {method.parent}.{method.name} (línea {method.lineno})
                </span>
                {method.docstring && (
                  <span className="symbol-method-doc">
                    {formatDocstring(method.docstring)}
                  </span>
                )}
              </li>
            ))}
          </ul>
        </article>
      ))}

      {grouped.functions.map((fn) => (
        <article key={fn.name} className="symbol-card">
          <div className="symbol-title">
            {fn.name}
            <span className="symbol-meta">
              <span>línea {fn.lineno}</span>
              <span>función</span>
            </span>
          </div>
          {fn.docstring ? (
            <p className="symbol-doc">{formatDocstring(fn.docstring)}</p>
          ) : (
            <p className="symbol-doc" style={{ opacity: 0.65 }}>
              Sin docstring
            </p>
          )}
        </article>
      ))}

      {grouped.classes.length === 0 && grouped.functions.length === 0 && (
        <div className="placeholder">
          <h3>Archivo sin símbolos exportables</h3>
          <p>
            Añade funciones o clases de nivel superior para visualizarlas aquí. Los
            métodos se agrupan automáticamente bajo su clase correspondiente.
          </p>
        </div>
      )}

      {selectedPath && (
        <div className="preview-container">
          <h3 style={{ margin: "0 0 8px", color: "#7f869d", fontSize: "13px" }}>
            Previsualización
          </h3>
          <PreviewPane path={selectedPath} />
        </div>
      )}
    </section>
  );
}

function formatDocstring(docstring: string): string {
  return docstring.trim().split("\n\n")[0].replace(/\s+/g, " ");
}
