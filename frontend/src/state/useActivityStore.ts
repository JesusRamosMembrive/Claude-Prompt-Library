import { create } from "zustand";

/**
 * Tipo de actividad en el feed.
 *
 * - "updated": Archivo fue modificado o creado
 * - "deleted": Archivo fue eliminado
 */
type ActivityType = "updated" | "deleted";

/**
 * Registro individual de actividad en el proyecto.
 *
 * Attributes:
 *     id: Identificador único generado (type-path-timestamp-index)
 *     path: Ruta del archivo afectado
 *     type: Tipo de cambio ("updated" o "deleted")
 *     timestamp: Marca de tiempo UNIX (milisegundos)
 *
 * Notes:
 *     - id se genera automáticamente en push()
 *     - timestamp común para batch de cambios
 *     - Usado en ActivityFeed component
 */
export interface ActivityRecord {
  id: string;
  path: string;
  type: ActivityType;
  timestamp: number;
}

/**
 * Estado del store de actividad.
 *
 * Attributes:
 *     items: Lista de registros de actividad (máximo MAX_ITEMS)
 *     push: Añade nuevos registros al inicio de la lista
 *     clear: Limpia todos los registros
 */
interface ActivityState {
  items: ActivityRecord[];
  push: (records: Omit<ActivityRecord, "id">[]) => void;
  clear: () => void;
}

/**
 * Número máximo de items en el feed de actividad.
 *
 * Limita el uso de memoria y mantiene el feed manejable.
 * Items más antiguos se descartan automáticamente.
 */
const MAX_ITEMS = 20;

/**
 * Store global de actividad del proyecto (Zustand).
 *
 * Mantiene un feed de cambios recientes (archivos actualizados/eliminados)
 * provenientes del EventStream. Limita automáticamente a MAX_ITEMS.
 *
 * Returns:
 *     Hook con estado y acciones del store
 *
 * Usage:
 *     const { items, push, clear } = useActivityStore();
 *     push([{ path: "file.py", type: "updated", timestamp: Date.now() }]);
 *
 * Notes:
 *     - Store singleton (compartido por todos los componentes)
 *     - IDs se generan automáticamente con timestamp + index
 *     - Nuevos items se añaden al inicio (orden cronológico inverso)
 *     - Lista se trunca a MAX_ITEMS automáticamente
 */
export const useActivityStore = create<ActivityState>((set) => ({
  items: [],

  /**
   * Añade registros de actividad al inicio del feed.
   *
   * Args:
   *     records: Array de registros sin ID (será generado automáticamente)
   *
   * Notes:
   *     - No-op si records está vacío
   *     - IDs generados: `${type}-${path}-${timestamp}-${index}`
   *     - Timestamp común para todo el batch
   *     - Lista truncada a MAX_ITEMS después de añadir
   *     - Nuevos items aparecen primero (prepend)
   */
  push(records) {
    if (records.length === 0) {
      return;
    }
    set((state) => {
      const timestamp = Date.now();
      const next = [
        ...records.map((record, index) => ({
          ...record,
          id: `${record.type}-${record.path}-${timestamp}-${index}`,
        })),
        ...state.items,
      ].slice(0, MAX_ITEMS);
      return { items: next };
    });
  },

  /**
   * Limpia todos los registros de actividad.
   *
   * Notes:
   *     - Útil para resetear el feed
   *     - No hay confirmación (acción inmediata)
   */
  clear() {
    set({ items: [] });
  },
}));
