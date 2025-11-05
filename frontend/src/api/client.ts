import type {
  FileSummary,
  ProjectTreeNode,
  SettingsPayload,
  SettingsUpdatePayload,
  StatusPayload,
  SymbolInfo,
  StageStatusPayload,
  StageInitPayload,
  StageInitResponse,
  BrowseDirectoryResponse,
  UMLDiagramResponse,
  LintersReportRecord,
  LintersReportListItem,
  LintersNotificationEntry,
  OllamaStatusPayload,
  OllamaStartPayload,
  OllamaStartResponse,
  OllamaTestPayload,
  OllamaTestResponse,
  OllamaTestErrorDetail,
  OllamaInsightEntry,
  OllamaInsightsResponse,
  OllamaInsightsClearResponse,
} from "./types";

const API_BASE = import.meta.env.VITE_API_BASE_URL
  ? String(import.meta.env.VITE_API_BASE_URL).replace(/\/$/, "")
  : null;
const API_PREFIX = API_BASE ? "" : "/api";

/**
 * Construye la URL completa para una llamada a la API.
 *
 * Args:
 *     path: Ruta relativa del endpoint (debe empezar con '/')
 *
 * Returns:
 *     URL completa combinando base URL, prefijo y path
 *
 * Notes:
 *     - Usa VITE_API_BASE_URL si está configurado (producción)
 *     - Fallback a '/api' prefix para desarrollo local
 *     - Remueve trailing slash de la base URL
 */
const buildUrl = (path: string): string =>
  `${API_BASE ?? ""}${API_PREFIX}${path}`;

/**
 * Realiza una petición HTTP y parsea la respuesta como JSON.
 *
 * Wrapper genérico sobre fetch() que:
 * - Añade headers JSON automáticamente
 * - Maneja errores HTTP con mensajes descriptivos
 * - Parsea respuesta como tipo genérico T
 *
 * Args:
 *     path: Ruta relativa del endpoint
 *     init: Opciones adicionales de fetch (method, body, headers, etc.)
 *
 * Returns:
 *     Promise con datos parseados del tipo T
 *
 * Raises:
 *     Error: Si response.ok es false, con mensaje de status y detalle
 *
 * Notes:
 *     - Content-Type: application/json se añade por defecto
 *     - Headers personalizados pueden sobrescribir defaults
 *     - Error detail extrae response.text() si está disponible
 */
async function fetchJson<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(buildUrl(path), {
    headers: {
      "Content-Type": "application/json",
      ...(init?.headers ?? {}),
    },
    ...init,
  });

  if (!response.ok) {
    const detail = await response.text().catch(() => response.statusText);
    throw new Error(
      `API request failed (${response.status}): ${detail || "Unknown error"}`
    );
  }

  return (await response.json()) as T;
}

async function fetchJsonNullable<T>(
  path: string,
  init?: RequestInit
): Promise<T | null> {
  const response = await fetch(buildUrl(path), {
    headers: {
      "Content-Type": "application/json",
      ...(init?.headers ?? {}),
    },
    ...init,
  });

  if (response.status === 404) {
    return null;
  }

  if (!response.ok) {
    const detail = await response.text().catch(() => response.statusText);
    throw new Error(
      `API request failed (${response.status}): ${detail || "Unknown error"}`
    );
  }

  if (response.status === 204) {
    return null;
  }

  return (await response.json()) as T;
}

export class OllamaTestError extends Error {
  status: number;
  detail?: OllamaTestErrorDetail;

  constructor(message: string, status: number, detail?: OllamaTestErrorDetail) {
    super(message);
    this.status = status;
    this.detail = detail;
  }
}

/**
 * Obtiene el árbol completo del proyecto.
 *
 * Returns:
 *     Promise con la estructura jerárquica del proyecto (carpetas y archivos)
 *
 * Notes:
 *     - Endpoint: GET /api/tree
 *     - Incluye metadata de archivos y símbolos
 *     - Estructura recursiva ProjectTreeNode
 */
export function getTree(): Promise<ProjectTreeNode> {
  return fetchJson<ProjectTreeNode>("/tree");
}

/**
 * Obtiene el resumen de análisis de un archivo específico.
 *
 * Args:
 *     path: Ruta del archivo (relativa a root del proyecto)
 *
 * Returns:
 *     Promise con símbolos, errores y metadata del archivo
 *
 * Notes:
 *     - Endpoint: GET /api/files/{path}
 *     - Path se encoda automáticamente (espacios, caracteres especiales)
 *     - Incluye funciones, clases, métodos detectados
 */
export function getFileSummary(path: string): Promise<FileSummary> {
  const encoded = encodeURIComponent(path);
  return fetchJson<FileSummary>(`/files/${encoded}`);
}

/**
 * Busca símbolos en todo el proyecto.
 *
 * Args:
 *     term: Término de búsqueda (nombre de función, clase, método)
 *
 * Returns:
 *     Promise con lista de símbolos que coinciden con el término
 *
 * Notes:
 *     - Endpoint: GET /api/search?q={term}
 *     - Búsqueda parcial (substring matching)
 *     - Resultados incluyen path y ubicación de cada símbolo
 */
export function searchSymbols(term: string): Promise<{ results: SymbolInfo[] }> {
  const params = new URLSearchParams({ q: term });
  return fetchJson(`/search?${params.toString()}`);
}

/**
 * Dispara un rescaneo manual del proyecto.
 *
 * Returns:
 *     Promise con número de archivos procesados
 *
 * Notes:
 *     - Endpoint: POST /api/rescan
 *     - Fuerza actualización completa del índice
 *     - Útil después de cambios masivos (git checkout, etc.)
 */
export function triggerRescan(): Promise<{ files: number }> {
  return fetchJson<{ files: number }>("/rescan", {
    method: "POST",
  });
}

/**
 * Obtiene la URL del stream de eventos SSE.
 *
 * Returns:
 *     URL completa del endpoint de eventos
 *
 * Notes:
 *     - Endpoint: GET /api/events (Server-Sent Events)
 *     - Usado por useEventStream hook
 *     - Mantiene conexión persistente para notificaciones en tiempo real
 */
export function getEventsUrl(): string {
  return buildUrl("/events");
}

export type { ChangeNotification } from "./types";

/**
 * Obtiene la configuración actual del proyecto.
 *
 * Returns:
 *     Promise con settings actuales (root, excludes, docstrings, etc.)
 *
 * Notes:
 *     - Endpoint: GET /api/settings
 *     - Incluye tanto configuración persistente como runtime
 *     - Usado por formulario de configuración
 */
export function getSettings(): Promise<SettingsPayload> {
  return fetchJson<SettingsPayload>("/settings");
}

/**
 * Actualiza la configuración del proyecto.
 *
 * Args:
 *     payload: Objeto con campos a actualizar (parcial)
 *
 * Returns:
 *     Promise con lista de campos actualizados y settings completos
 *
 * Notes:
 *     - Endpoint: PUT /api/settings
 *     - Update parcial: solo enviar campos a modificar
 *     - Algunos cambios requieren rescaneo (root, excludes)
 *     - Respuesta incluye settings completos actualizados
 */
export function updateSettings(payload: SettingsUpdatePayload): Promise<{
  updated: string[];
  settings: SettingsPayload;
}> {
  return fetchJson("/settings", {
    method: "PUT",
    body: JSON.stringify(payload),
  });
}

/**
 * Solicita al backend un cuadro de diálogo nativo para seleccionar directorio.
 */
export function browseForRoot(): Promise<BrowseDirectoryResponse> {
  return fetchJson("/settings/browse", {
    method: "POST",
  });
}

/**
 * Obtiene el estado Stage-Aware del proyecto.
 */
export function getStageStatus(): Promise<StageStatusPayload> {
  return fetchJson<StageStatusPayload>("/stage/status");
}

/**
 * Obtiene el estado del servidor Ollama (instalación, servicio y modelos).
 */
export function getOllamaStatus(): Promise<OllamaStatusPayload> {
  return fetchJson<OllamaStatusPayload>("/integrations/ollama/status");
}

/**
 * Solicita al backend iniciar el servidor Ollama.
 */
export async function startOllama(payload: OllamaStartPayload): Promise<OllamaStartResponse> {
  const response = await fetch(buildUrl("/integrations/ollama/start"), {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(payload),
  });

  if (!response.ok) {
    let detailMessage = `No se pudo iniciar Ollama (${response.status})`;
    const body = await response.text().catch(() => "");
    if (body) {
      try {
        const parsed = JSON.parse(body);
        const candidate = (parsed && parsed.detail) ?? parsed;
        if (candidate && typeof candidate === "object" && candidate.message) {
          detailMessage = String(candidate.message);
        }
      } catch {
        // sin acción, mantenemos mensaje genérico
      }
    }
    throw new Error(detailMessage);
  }

  return (await response.json()) as OllamaStartResponse;
}

/**
 * Ejecuta una petición de chat simple contra Ollama para comprobar conectividad.
 */
export async function testOllamaChat(payload: OllamaTestPayload): Promise<OllamaTestResponse> {
  const response = await fetch(buildUrl("/integrations/ollama/test"), {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(payload),
  });

  const bodyText = await response.text().catch(() => "");

  if (!response.ok) {
    let detail: OllamaTestErrorDetail | undefined;
    if (bodyText) {
      try {
        const parsed = JSON.parse(bodyText);
        const candidate = (parsed && parsed.detail) ?? parsed;
        if (candidate && typeof candidate === "object") {
          detail = candidate as OllamaTestErrorDetail;
        }
      } catch {
        // Ignorar errores de parseo, enviamos mensaje genérico.
      }
    }

    const message =
      detail?.message ?? `Ollama test request failed (${response.status})`;
    throw new OllamaTestError(message, response.status, detail);
  }

  if (!bodyText) {
    throw new OllamaTestError("Respuesta vacía de Ollama.", response.status);
  }

  try {
    return JSON.parse(bodyText) as OllamaTestResponse;
  } catch {
    throw new OllamaTestError(
      "Respuesta inválida del servidor al parsear JSON.",
      response.status
    );
  }
}

/**
 * Recupera el historial reciente de insights generados con Ollama.
 */
export function getOllamaInsights(limit = 20): Promise<OllamaInsightEntry[]> {
  const params = new URLSearchParams({ limit: String(limit) });
  return fetchJson(`/integrations/ollama/insights?${params.toString()}`);
}

export function triggerOllamaInsights(payload?: {
  model?: string;
  timeout_seconds?: number;
  focus?: string;
}): Promise<OllamaInsightsResponse> {
  const bodyPayload = payload
    ? {
        ...payload,
        focus:
          payload.focus && payload.focus.trim()
            ? payload.focus.trim().toLowerCase()
            : undefined,
      }
    : {};
  return fetchJson("/integrations/ollama/analyze", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(bodyPayload),
  });
}

export function clearOllamaInsights(): Promise<OllamaInsightsClearResponse> {
  return fetchJson("/integrations/ollama/insights", {
    method: "DELETE",
  });
}

/**
 * Ejecuta init_project.py sobre el proyecto actual con los agentes seleccionados.
 */
export function initializeStageToolkit(payload: StageInitPayload): Promise<StageInitResponse> {
  return fetchJson<StageInitResponse>("/stage/init", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export function getClassUml(options?: {
  includeExternal?: boolean;
  modulePrefixes?: string[];
  edgeTypes?: string[];
}): Promise<UMLDiagramResponse> {
  const params = new URLSearchParams();
  if (options?.includeExternal) {
    params.set("include_external", "true");
  }
  if (options?.modulePrefixes) {
    options.modulePrefixes.forEach((prefix) => {
      if (prefix.trim()) {
        params.append("module_prefix", prefix.trim());
      }
    });
  }
  if (options?.edgeTypes) {
    options.edgeTypes.forEach((type) => {
      params.append("edge_types", type);
    });
  }
  const query = params.toString();
  return fetchJson(`/graph/uml${query ? `?${query}` : ""}`);
}

export async function getClassUmlSvg(options?: {
  includeExternal?: boolean;
  modulePrefixes?: string[];
  edgeTypes?: string[];
}): Promise<string> {
  const params = new URLSearchParams();
  if (options?.includeExternal) {
    params.set("include_external", "true");
  }
  if (options?.modulePrefixes) {
    options.modulePrefixes.forEach((prefix) => {
      const trimmed = prefix.trim();
      if (trimmed) {
        params.append("module_prefix", trimmed);
      }
    });
  }
  if (options?.edgeTypes) {
    options.edgeTypes.forEach((type) => {
      params.append("edge_types", type);
    });
  }
  const query = params.toString();
  const response = await fetch(buildUrl(`/graph/uml/svg${query ? `?${query}` : ""}`));
  if (!response.ok) {
    const detail = await response.text().catch(() => response.statusText);
    throw new Error(`API request failed (${response.status}): ${detail || "Unknown error"}`);
  }
  return await response.text();
}

/**
 * Obtiene el estado actual del analizador.
 *
 * Returns:
 *     Promise con información de estado (archivos indexados, errores, etc.)
 *
 * Notes:
 *     - Endpoint: GET /api/status
 *     - Útil para monitoreo y diagnóstico
 *     - Incluye contadores y métricas de rendimiento
 */
export function getStatus(): Promise<StatusPayload> {
  return fetchJson<StatusPayload>("/status");
}

export async function getPreview(path: string): Promise<{ content: string; contentType: string }> {
  const response = await fetch(buildUrl(`/preview?path=${encodeURIComponent(path)}`));
  if (!response.ok) {
    const detail = await response.text().catch(() => response.statusText);
    throw new Error(`Preview request failed (${response.status}): ${detail || "Unknown error"}`);
  }
  const content = await response.text();
  const contentType = response.headers.get("Content-Type") ?? "text/plain";
  return { content, contentType };
}

export function getLintersLatestReport(): Promise<LintersReportRecord | null> {
  return fetchJsonNullable<LintersReportRecord>("/linters/reports/latest");
}

export function getLintersReports(
  limit = 20,
  offset = 0
): Promise<LintersReportListItem[]> {
  const params = new URLSearchParams({
    limit: String(limit),
    offset: String(offset),
  });
  return fetchJson<LintersReportListItem[]>(`/linters/reports?${params.toString()}`);
}

export function getLintersNotifications(
  limit = 50,
  unreadOnly = false
): Promise<LintersNotificationEntry[]> {
  const params = new URLSearchParams({
    limit: String(limit),
    unread_only: unreadOnly ? "true" : "false",
  });
  return fetchJson<LintersNotificationEntry[]>(
    `/linters/notifications?${params.toString()}`
  );
}

export async function markNotificationAsRead(
  notificationId: number,
  read = true
): Promise<void> {
  const query = read ? "" : "?read=false";
  await fetchJsonNullable<void>(
    `/linters/notifications/${notificationId}/read${query}`,
    { method: "POST" }
  );
}
