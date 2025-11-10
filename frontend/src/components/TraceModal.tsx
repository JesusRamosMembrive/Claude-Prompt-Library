import { useQuery } from "@tanstack/react-query";

interface CallChain {
  depth: number;
  qualified_name: string;
  callees: string[];
  file_path: string;
  function_name: string;
}

interface TraceChainResponse {
  start_function: string;
  chain: CallChain[];
  max_depth_reached: boolean;
  total_depth: number;
}

interface TraceModalProps {
  qualifiedName: string;
  onClose: () => void;
}

export function TraceModal({ qualifiedName, onClose }: TraceModalProps): JSX.Element {
  const { data, isLoading, isError, error } = useQuery<TraceChainResponse>({
    queryKey: ["trace", qualifiedName],
    queryFn: async () => {
      const response = await fetch("/api/tracer/trace-cross-file", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          start_function: qualifiedName,
          max_depth: 10,
        }),
      });
      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || "Failed to trace function");
      }
      return response.json();
    },
  });

  return (
    <div
      style={{
        position: "fixed",
        top: 0,
        left: 0,
        right: 0,
        bottom: 0,
        background: "rgba(0, 0, 0, 0.7)",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        zIndex: 1000,
      }}
      onClick={onClose}
    >
      <div
        style={{
          background: "#1e2330",
          borderRadius: "8px",
          padding: "24px",
          maxWidth: "800px",
          maxHeight: "80vh",
          overflow: "auto",
          border: "1px solid #2a2f3e",
          boxShadow: "0 8px 32px rgba(0, 0, 0, 0.5)",
        }}
        onClick={(e) => e.stopPropagation()}
      >
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "20px" }}>
          <h2 style={{ margin: 0, fontSize: "18px" }}>Call Trace</h2>
          <button
            onClick={onClose}
            style={{
              background: "transparent",
              border: "none",
              color: "#7f869d",
              fontSize: "24px",
              cursor: "pointer",
              padding: "0 8px",
            }}
          >
            ×
          </button>
        </div>

        {isLoading && <p style={{ color: "#7f869d" }}>Tracing call chain...</p>}

        {isError && (
          <div className="error-banner">
            Error: {(error as Error)?.message || "Unknown error"}
          </div>
        )}

        {data && (
          <div>
            <h3 style={{ marginBottom: "12px", fontSize: "16px" }}>
              From: {data.start_function}
            </h3>
            <div style={{ display: "flex", gap: "20px", marginBottom: "12px", fontSize: "13px" }}>
              <p style={{ color: "#7f869d" }}>
                Total depth: <strong>{data.total_depth}</strong>
              </p>
              <p style={{ color: "#7f869d" }}>
                Functions traced: <strong>{data.chain.length}</strong>
              </p>
            </div>
            {data.max_depth_reached && (
              <p style={{ color: "#f0b429", marginBottom: "12px", fontSize: "13px" }}>
                ⚠️ Maximum depth reached. Chain may be incomplete.
              </p>
            )}

            <div style={{ fontFamily: "monospace", fontSize: "13px" }}>
              {data.chain.map((item, idx) => (
                <div
                  key={idx}
                  style={{
                    marginBottom: "8px",
                    paddingLeft: `${item.depth * 24}px`,
                  }}
                >
                  <div
                    style={{
                      padding: "8px 12px",
                      background: "#252b3a",
                      borderRadius: "4px",
                      borderLeft: `3px solid ${item.depth === 0 ? "#5b9bd5" : "#7f869d"}`,
                    }}
                  >
                    <div style={{ fontWeight: item.depth === 0 ? 600 : 400, color: "#5b9bd5" }}>
                      {item.qualified_name}
                    </div>
                    <div style={{ fontSize: "11px", color: "#7f869d", marginTop: "2px" }}>
                      📁 {item.file_path}
                    </div>
                    {item.callees.length > 0 && (
                      <div style={{ fontSize: "11px", color: "#7f869d", marginTop: "4px" }}>
                        calls: {item.callees.slice(0, 5).join(", ")}
                        {item.callees.length > 5 && ` (+${item.callees.length - 5} more)`}
                      </div>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
