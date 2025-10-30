import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { searchSymbols } from "../api/client";
import { queryKeys } from "../api/queryKeys";
import { useSelectionStore } from "../state/useSelectionStore";

export function SearchPanel(): JSX.Element {
  const [term, setTerm] = useState("");
  const selectPath = useSelectionStore((state) => state.selectPath);
  const clearSelection = useSelectionStore((state) => state.clearSelection);

  const { data, isFetching, isError, error } = useQuery({
    queryKey: queryKeys.search(term),
    queryFn: () => searchSymbols(term),
    enabled: term.trim().length > 1,
  });

  const results = data?.results ?? [];

  return (
    <div>
      <h2>Búsqueda</h2>
      <div className="search-box">
        <span role="img" aria-label="Buscar">
          🔍
        </span>
        <input
          type="search"
          value={term}
          onChange={(event) => setTerm(event.target.value)}
          placeholder="Buscar símbolos (mínimo 2 caracteres)…"
        />
      </div>

      {term.trim().length > 1 && (
        <>
          {isError && (
            <div className="error-banner">
              Error al buscar: {(error as Error)?.message ?? "intenta de nuevo"}
            </div>
          )}
          {isFetching && (
            <p style={{ color: "#7f869d", fontSize: "13px" }}>Buscando…</p>
          )}
          {!isFetching && results.length === 0 && (
            <p style={{ color: "#7f869d", fontSize: "13px" }}>
              No se encontraron símbolos que coincidan con “{term}”.
            </p>
          )}
          {!isFetching && results.length > 0 && (
            <ul className="search-results">
              {results.slice(0, 8).map((symbol) => (
                <li
                  key={`${symbol.path}-${symbol.name}-${symbol.kind}`}
                  className="search-item"
                  onClick={() => {
                    if (symbol.path) {
                      selectPath(symbol.path);
                    } else {
                      clearSelection();
                    }
                  }}
                  onKeyDown={(event) => {
                    if (event.key === "Enter" || event.key === " ") {
                      event.preventDefault();
                      if (symbol.path) {
                        selectPath(symbol.path);
                      } else {
                        clearSelection();
                      }
                    }
                  }}
                  role="button"
                  tabIndex={0}
                >
                  <strong>{symbol.name}</strong>
                  <span>
                    {symbol.kind} · {symbol.path ?? ""}
                  </span>
                  {symbol.docstring && (
                    <span style={{ color: "#9aa3c3" }}>
                      {symbol.docstring.trim().split("\n", 1)[0]}
                    </span>
                  )}
                </li>
              ))}
            </ul>
          )}
        </>
      )}
    </div>
  );
}
