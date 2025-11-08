import { useState } from "react";
import { useQuery } from "@tanstack/react-query";

interface CallGraphResponse {
  file_path: string;
  call_graph: Record<string, string[]>;
  total_functions: number;
}

interface TraceChainResponse {
  start_function: string;
  chain: Array<{
    depth: number;
    function: string;
    callees: string[];
  }>;
  max_depth_reached: boolean;
}

export function CallTracerView(): JSX.Element {
  const [filePath, setFilePath] = useState("code_map/server.py");
  const [startFunction, setStartFunction] = useState("");
  const [maxDepth, setMaxDepth] = useState(5);
  const [activeTab, setActiveTab] = useState<"analyze" | "trace">("analyze");

  // Query para analizar archivo
  const {
    data: callGraphData,
    isLoading: isLoadingGraph,
    isError: isErrorGraph,
    error: errorGraph,
    refetch: refetchGraph,
  } = useQuery<CallGraphResponse>({
    queryKey: ["call-tracer", "analyze", filePath],
    queryFn: async () => {
      const response = await fetch("/tracer/analyze", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ file_path: filePath }),
      });
      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || "Failed to analyze file");
      }
      return response.json();
    },
    enabled: false, // Solo ejecutar manualmente
  });

  // Query para trazar cadena
  const {
    data: traceData,
    isLoading: isLoadingTrace,
    isError: isErrorTrace,
    error: errorTrace,
    refetch: refetchTrace,
  } = useQuery<TraceChainResponse>({
    queryKey: ["call-tracer", "trace", filePath, startFunction, maxDepth],
    queryFn: async () => {
      const response = await fetch("/tracer/trace", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          file_path: filePath,
          start_function: startFunction,
          max_depth: maxDepth,
        }),
      });
      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || "Failed to trace chain");
      }
      return response.json();
    },
    enabled: false,
  });

  const handleAnalyze = () => {
    setActiveTab("analyze");
    refetchGraph();
  };

  const handleTrace = () => {
    if (!startFunction.trim()) {
      alert("Please enter a function name to trace");
      return;
    }
    setActiveTab("trace");
    refetchTrace();
  };

  return (
    <div className="page-layout">
      <div className="page-content">
        <div className="panel">
          <div className="panel-header">
            <h2>Call Tracer - Stage 1 MVP</h2>
            <p style={{ fontSize: "13px", color: "#7f869d", marginTop: "4px" }}>
              Trace function call chains within Python files
            </p>
          </div>

          {/* Input Section */}
          <div style={{ padding: "20px", borderBottom: "1px solid #2a2f3e" }}>
            <div style={{ marginBottom: "16px" }}>
              <label
                htmlFor="file-path"
                style={{ display: "block", marginBottom: "8px", fontWeight: 500 }}
              >
                File Path (relative to project root)
              </label>
              <input
                id="file-path"
                type="text"
                value={filePath}
                onChange={(e) => setFilePath(e.target.value)}
                placeholder="e.g., code_map/server.py"
                style={{
                  width: "100%",
                  padding: "8px 12px",
                  background: "#1e2330",
                  border: "1px solid #2a2f3e",
                  borderRadius: "4px",
                  color: "#e4e6eb",
                }}
              />
            </div>

            <div style={{ display: "flex", gap: "12px" }}>
              <button
                type="button"
                onClick={handleAnalyze}
                disabled={isLoadingGraph}
                className="primary-btn"
              >
                {isLoadingGraph ? "Analyzing..." : "Analyze Call Graph"}
              </button>

              <div style={{ flex: 1, display: "flex", gap: "8px" }}>
                <input
                  type="text"
                  value={startFunction}
                  onChange={(e) => setStartFunction(e.target.value)}
                  placeholder="Function name (e.g., create_app)"
                  style={{
                    flex: 1,
                    padding: "8px 12px",
                    background: "#1e2330",
                    border: "1px solid #2a2f3e",
                    borderRadius: "4px",
                    color: "#e4e6eb",
                  }}
                />
                <input
                  type="number"
                  value={maxDepth}
                  onChange={(e) => setMaxDepth(Number(e.target.value))}
                  min="1"
                  max="20"
                  style={{
                    width: "80px",
                    padding: "8px 12px",
                    background: "#1e2330",
                    border: "1px solid #2a2f3e",
                    borderRadius: "4px",
                    color: "#e4e6eb",
                  }}
                />
                <button
                  type="button"
                  onClick={handleTrace}
                  disabled={isLoadingTrace}
                  className="primary-btn"
                >
                  {isLoadingTrace ? "Tracing..." : "Trace Chain"}
                </button>
              </div>
            </div>
          </div>

          {/* Results Section */}
          <div style={{ padding: "20px" }}>
            {activeTab === "analyze" && (
              <>
                {isLoadingGraph && <p style={{ color: "#7f869d" }}>Analyzing file...</p>}

                {isErrorGraph && (
                  <div className="error-banner">
                    Error: {(errorGraph as Error)?.message || "Unknown error"}
                  </div>
                )}

                {callGraphData && (
                  <div>
                    <h3 style={{ marginBottom: "12px" }}>
                      Call Graph - {callGraphData.file_path}
                    </h3>
                    <p style={{ color: "#7f869d", marginBottom: "16px" }}>
                      Found {callGraphData.total_functions} functions
                    </p>

                    {Object.entries(callGraphData.call_graph).length === 0 ? (
                      <p style={{ color: "#7f869d" }}>No function calls detected</p>
                    ) : (
                      <div style={{ fontFamily: "monospace", fontSize: "13px" }}>
                        {Object.entries(callGraphData.call_graph).map(([caller, callees]) => (
                          <div
                            key={caller}
                            style={{
                              marginBottom: "12px",
                              padding: "12px",
                              background: "#1e2330",
                              borderRadius: "4px",
                              borderLeft: "3px solid #5b9bd5",
                            }}
                          >
                            <div style={{ fontWeight: 600, color: "#5b9bd5", marginBottom: "8px" }}>
                              {caller}()
                            </div>
                            {callees.length > 0 ? (
                              <div style={{ paddingLeft: "16px" }}>
                                {callees.map((callee, idx) => (
                                  <div key={idx} style={{ color: "#e4e6eb", marginBottom: "4px" }}>
                                    → {callee}()
                                  </div>
                                ))}
                              </div>
                            ) : (
                              <div style={{ paddingLeft: "16px", color: "#7f869d", fontStyle: "italic" }}>
                                (no calls detected)
                              </div>
                            )}
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                )}
              </>
            )}

            {activeTab === "trace" && (
              <>
                {isLoadingTrace && <p style={{ color: "#7f869d" }}>Tracing call chain...</p>}

                {isErrorTrace && (
                  <div className="error-banner">
                    Error: {(errorTrace as Error)?.message || "Unknown error"}
                  </div>
                )}

                {traceData && (
                  <div>
                    <h3 style={{ marginBottom: "12px" }}>
                      Call Chain from: {traceData.start_function}()
                    </h3>
                    {traceData.max_depth_reached && (
                      <p style={{ color: "#f0b429", marginBottom: "12px" }}>
                        ⚠️ Maximum depth reached. Chain may be incomplete.
                      </p>
                    )}

                    <div style={{ fontFamily: "monospace", fontSize: "13px" }}>
                      {traceData.chain.map((item, idx) => (
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
                              background: "#1e2330",
                              borderRadius: "4px",
                              borderLeft: `3px solid ${item.depth === 0 ? "#5b9bd5" : "#7f869d"}`,
                            }}
                          >
                            <div style={{ fontWeight: item.depth === 0 ? 600 : 400, color: "#5b9bd5" }}>
                              {item.function}()
                            </div>
                            {item.callees.length > 0 && (
                              <div style={{ fontSize: "11px", color: "#7f869d", marginTop: "4px" }}>
                                calls: {item.callees.join(", ")}
                              </div>
                            )}
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </>
            )}
          </div>

          {/* Stage 1 Limitations Notice */}
          <div
            style={{
              padding: "16px",
              background: "#2a2f3e",
              borderTop: "1px solid #3a3f4e",
              fontSize: "12px",
              color: "#7f869d",
            }}
          >
            <strong>Stage 1 Limitations:</strong>
            <ul style={{ marginTop: "8px", paddingLeft: "20px" }}>
              <li>Only analyzes calls within the same file (no cross-file analysis)</li>
              <li>Detects direct calls: foo(), obj.method()</li>
              <li>Does not handle imports, complex decorators, or lambdas</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
}
