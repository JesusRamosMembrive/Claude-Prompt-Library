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
      <h2>Search</h2>
      <div className="search-box">
        <span role="img" aria-label="Search">
          🔍
        </span>
        <input
          type="search"
          value={term}
          onChange={(event) => setTerm(event.target.value)}
          placeholder="Search symbols (minimum 2 characters)…"
        />
      </div>

      {term.trim().length > 1 && (
        <>
          {isError && (
            <div className="error-banner">
              Search error: {(error as Error)?.message ?? "try again"}
            </div>
          )}
          {isFetching && (
            <p style={{ color: "#7f869d", fontSize: "13px" }}>Searching…</p>
          )}
          {!isFetching && results.length === 0 && (
            <p style={{ color: "#7f869d", fontSize: "13px" }}>
              No symbols match “{term}”.
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
