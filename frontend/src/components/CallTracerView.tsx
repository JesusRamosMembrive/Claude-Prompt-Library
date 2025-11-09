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

// Stage 2: Cross-file interfaces
interface CrossFileCallGraphResponse {
  call_graph: Record<string, string[]>;
  entry_points: string[];
  total_functions: number;
  analyzed_files: string[];
}

interface CrossFileCallChain {
  depth: number;
  qualified_name: string;
  callees: string[];
  file_path: string;
  function_name: string;
}

interface TraceCrossFileResponse {
  start_function: string;
  chain: CrossFileCallChain[];
  max_depth_reached: boolean;
  total_depth: number;
}

type AnalysisMode = "single-file" | "cross-file";

export function CallTracerView(): JSX.Element {
  const [filePath, setFilePath] = useState("code_map/server.py");
  const [startFunction, setStartFunction] = useState("");
  const [maxDepth, setMaxDepth] = useState(5);
  const [activeTab, setActiveTab] = useState<"analyze" | "trace">("analyze");
  const [analysisMode, setAnalysisMode] = useState<AnalysisMode>("cross-file");
  const [recursive, setRecursive] = useState(true);
  const [maxFiles, setMaxFiles] = useState(50);

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

  // Stage 2: Query para análisis cross-file
  const {
    data: crossFileGraphData,
    isLoading: isLoadingCrossGraph,
    isError: isErrorCrossGraph,
    error: errorCrossGraph,
    refetch: refetchCrossGraph,
  } = useQuery<CrossFileCallGraphResponse>({
    queryKey: ["call-tracer", "analyze-cross-file", filePath, recursive, maxFiles],
    queryFn: async () => {
      const response = await fetch("/tracer/analyze-cross-file", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          file_path: filePath,
          recursive,
          max_files: maxFiles,
        }),
      });
      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || "Failed to analyze cross-file");
      }
      return response.json();
    },
    enabled: false,
  });

  // Stage 2: Query para trace cross-file
  const {
    data: crossFileTraceData,
    isLoading: isLoadingCrossTrace,
    isError: isErrorCrossTrace,
    error: errorCrossTrace,
    refetch: refetchCrossTrace,
  } = useQuery<TraceCrossFileResponse>({
    queryKey: ["call-tracer", "trace-cross-file", startFunction, maxDepth],
    queryFn: async () => {
      const response = await fetch("/tracer/trace-cross-file", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          start_function: startFunction,
          max_depth: maxDepth,
        }),
      });
      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || "Failed to trace cross-file");
      }
      return response.json();
    },
    enabled: false,
  });

  const handleAnalyze = () => {
    setActiveTab("analyze");
    if (analysisMode === "single-file") {
      refetchGraph();
    } else {
      refetchCrossGraph();
    }
  };

  const handleTrace = () => {
    if (!startFunction.trim()) {
      alert("Please enter a function name to trace");
      return;
    }
    setActiveTab("trace");
    if (analysisMode === "single-file") {
      refetchTrace();
    } else {
      refetchCrossTrace();
    }
  };

  return (
    <div className="page-layout">
      <div className="page-content">
        <div className="panel">
          <div className="panel-header">
            <h2>Call Tracer - Stage 2</h2>
            <p style={{ fontSize: "13px", color: "#7f869d", marginTop: "4px" }}>
              Trace function call chains with cross-file analysis
            </p>
          </div>

          {/* Mode Toggle */}
          <div style={{ padding: "20px", borderBottom: "1px solid #2a2f3e", background: "#1a1e2a" }}>
            <label style={{ display: "block", marginBottom: "12px", fontWeight: 500 }}>
              Analysis Mode
            </label>
            <div style={{ display: "flex", gap: "12px" }}>
              <button
                type="button"
                onClick={() => setAnalysisMode("single-file")}
                className={analysisMode === "single-file" ? "primary-btn" : "secondary-btn"}
                style={{ flex: 1 }}
              >
                Stage 1: Single-File
              </button>
              <button
                type="button"
                onClick={() => setAnalysisMode("cross-file")}
                className={analysisMode === "cross-file" ? "primary-btn" : "secondary-btn"}
                style={{ flex: 1 }}
              >
                Stage 2: Cross-File
              </button>
            </div>
            {analysisMode === "cross-file" && (
              <div style={{ marginTop: "12px", display: "flex", gap: "12px", alignItems: "center" }}>
                <label style={{ display: "flex", alignItems: "center", gap: "8px" }}>
                  <input
                    type="checkbox"
                    checked={recursive}
                    onChange={(e) => setRecursive(e.target.checked)}
                  />
                  <span style={{ fontSize: "13px" }}>Recursive (follow imports)</span>
                </label>
                <label style={{ display: "flex", alignItems: "center", gap: "8px" }}>
                  <span style={{ fontSize: "13px" }}>Max files:</span>
                  <input
                    type="number"
                    value={maxFiles}
                    onChange={(e) => setMaxFiles(Number(e.target.value))}
                    min="1"
                    max="200"
                    style={{
                      width: "70px",
                      padding: "4px 8px",
                      background: "#1e2330",
                      border: "1px solid #2a2f3e",
                      borderRadius: "4px",
                      color: "#e4e6eb",
                    }}
                  />
                </label>
              </div>
            )}
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
                  placeholder={
                    analysisMode === "cross-file"
                      ? "Qualified name (e.g., code_map/server.py::create_app)"
                      : "Function name (e.g., create_app)"
                  }
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
                {/* Stage 1: Single-file */}
                {analysisMode === "single-file" && (
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

                {/* Stage 2: Cross-file */}
                {analysisMode === "cross-file" && (
                  <>
                    {isLoadingCrossGraph && <p style={{ color: "#7f869d" }}>Analyzing cross-file dependencies...</p>}

                    {isErrorCrossGraph && (
                      <div className="error-banner">
                        Error: {(errorCrossGraph as Error)?.message || "Unknown error"}
                      </div>
                    )}

                    {crossFileGraphData && (
                      <div>
                        <h3 style={{ marginBottom: "12px" }}>Cross-File Call Graph</h3>
                        <div style={{ display: "flex", gap: "20px", marginBottom: "16px", fontSize: "13px" }}>
                          <p style={{ color: "#7f869d" }}>
                            <strong>{crossFileGraphData.total_functions}</strong> functions
                          </p>
                          <p style={{ color: "#7f869d" }}>
                            <strong>{crossFileGraphData.analyzed_files.length}</strong> files analyzed
                          </p>
                          <p style={{ color: "#7f869d" }}>
                            <strong>{crossFileGraphData.entry_points.length}</strong> entry points
                          </p>
                        </div>

                        {/* Entry Points */}
                        {crossFileGraphData.entry_points.length > 0 && (
                          <div style={{ marginBottom: "20px" }}>
                            <h4 style={{ marginBottom: "8px", color: "#f0b429" }}>Entry Points (not called by anyone):</h4>
                            <div style={{ fontFamily: "monospace", fontSize: "12px", paddingLeft: "12px" }}>
                              {crossFileGraphData.entry_points.map((ep, idx) => (
                                <div key={idx} style={{ color: "#7f869d", marginBottom: "4px" }}>
                                  • {ep}
                                </div>
                              ))}
                            </div>
                          </div>
                        )}

                        {/* Call Graph */}
                        {Object.entries(crossFileGraphData.call_graph).length === 0 ? (
                          <p style={{ color: "#7f869d" }}>No function calls detected</p>
                        ) : (
                          <div style={{ fontFamily: "monospace", fontSize: "13px" }}>
                            {Object.entries(crossFileGraphData.call_graph).map(([caller, callees]) => (
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
                                  {caller}
                                </div>
                                {callees.length > 0 ? (
                                  <div style={{ paddingLeft: "16px" }}>
                                    {callees.map((callee, idx) => (
                                      <div key={idx} style={{ color: "#e4e6eb", marginBottom: "4px" }}>
                                        → {callee}
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

                        {/* Analyzed Files */}
                        <details style={{ marginTop: "20px", fontSize: "13px" }}>
                          <summary style={{ cursor: "pointer", color: "#7f869d" }}>
                            Analyzed Files ({crossFileGraphData.analyzed_files.length})
                          </summary>
                          <div style={{ marginTop: "8px", paddingLeft: "12px", fontFamily: "monospace", fontSize: "12px" }}>
                            {crossFileGraphData.analyzed_files.map((file, idx) => (
                              <div key={idx} style={{ color: "#7f869d", marginBottom: "2px" }}>
                                {file}
                              </div>
                            ))}
                          </div>
                        </details>
                      </div>
                    )}
                  </>
                )}
              </>
            )}

            {activeTab === "trace" && (
              <>
                {/* Stage 1: Single-file trace */}
                {analysisMode === "single-file" && (
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

                {/* Stage 2: Cross-file trace */}
                {analysisMode === "cross-file" && (
                  <>
                    {isLoadingCrossTrace && <p style={{ color: "#7f869d" }}>Tracing cross-file call chain...</p>}

                    {isErrorCrossTrace && (
                      <div className="error-banner">
                        Error: {(errorCrossTrace as Error)?.message || "Unknown error"}
                      </div>
                    )}

                    {crossFileTraceData && (
                      <div>
                        <h3 style={{ marginBottom: "12px" }}>
                          Cross-File Call Chain from: {crossFileTraceData.start_function}
                        </h3>
                        <div style={{ display: "flex", gap: "20px", marginBottom: "12px", fontSize: "13px" }}>
                          <p style={{ color: "#7f869d" }}>
                            Total depth: <strong>{crossFileTraceData.total_depth}</strong>
                          </p>
                          <p style={{ color: "#7f869d" }}>
                            Functions traced: <strong>{crossFileTraceData.chain.length}</strong>
                          </p>
                        </div>
                        {crossFileTraceData.max_depth_reached && (
                          <p style={{ color: "#f0b429", marginBottom: "12px" }}>
                            ⚠️ Maximum depth reached. Chain may be incomplete.
                          </p>
                        )}

                        <div style={{ fontFamily: "monospace", fontSize: "13px" }}>
                          {crossFileTraceData.chain.map((item, idx) => (
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
                  </>
                )}
              </>
            )}
          </div>

          {/* Capabilities & Limitations */}
          <div
            style={{
              padding: "16px",
              background: "#2a2f3e",
              borderTop: "1px solid #3a3f4e",
              fontSize: "12px",
              color: "#7f869d",
            }}
          >
            {analysisMode === "single-file" ? (
              <>
                <strong>Stage 1 Limitations:</strong>
                <ul style={{ marginTop: "8px", paddingLeft: "20px" }}>
                  <li>Only analyzes calls within the same file (no cross-file analysis)</li>
                  <li>Detects direct calls: foo(), obj.method()</li>
                  <li>Does not handle imports, complex decorators, or lambdas</li>
                </ul>
              </>
            ) : (
              <>
                <strong>Stage 2 Capabilities:</strong>
                <ul style={{ marginTop: "8px", paddingLeft: "20px" }}>
                  <li>✅ Follows imports between files (absolute and relative)</li>
                  <li>✅ Resolves cross-file function calls</li>
                  <li>✅ Detects entry points (functions not called by anyone)</li>
                  <li>✅ Caches analysis per file (MD5-based)</li>
                  <li>✅ Detects class methods and attributes</li>
                </ul>
                <strong style={{ display: "block", marginTop: "12px" }}>Known Limitations:</strong>
                <ul style={{ marginTop: "8px", paddingLeft: "20px" }}>
                  <li>Does not handle dynamic imports or decorators</li>
                  <li>May not resolve all external library calls</li>
                  <li>Lambdas and closures not fully supported</li>
                </ul>
              </>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
