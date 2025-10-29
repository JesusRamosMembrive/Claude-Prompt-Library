import { useEffect, useMemo, useState } from "react";
import {
  useMutation,
  UseQueryResult,
  useQueryClient,
} from "@tanstack/react-query";

import { updateSettings } from "../api/client";
import type { SettingsPayload } from "../api/types";
import { queryKeys } from "../api/queryKeys";
import { useActivityStore } from "../state/useActivityStore";
import { useSelectionStore } from "../state/useSelectionStore";

interface SettingsViewProps {
  onBack: () => void;
  settingsQuery: UseQueryResult<SettingsPayload>;
}

export function SettingsView({ onBack, settingsQuery }: SettingsViewProps): JSX.Element {
  const activityClear = useActivityStore((state) => state.clear);
  const queryClient = useQueryClient();

  const settings = settingsQuery.data;
  const [formRoot, setFormRoot] = useState(settings?.root_path ?? "");
  const [formDocstrings, setFormDocstrings] = useState(
    settings?.include_docstrings ?? true,
  );
  const [statusMessage, setStatusMessage] = useState<string | null>(null);

  useEffect(() => {
    if (settings) {
      setFormRoot(settings.root_path);
      setFormDocstrings(settings.include_docstrings);
    }
  }, [settings?.root_path, settings?.include_docstrings]);

  const mutation = useMutation({
    mutationFn: updateSettings,
    onSuccess: (result) => {
      queryClient.setQueryData(queryKeys.settings, result.settings);
      queryClient.invalidateQueries({ queryKey: queryKeys.tree });
      if (result.updated.includes("root_path")) {
        useSelectionStore.getState().select(undefined);
      }
      setStatusMessage(
        result.updated.length > 0
          ? `Cambios aplicados: ${result.updated.join(", ")}`
          : "No había cambios que guardar."
      );
    },
    onError: (error: unknown) => {
      const message =
        error instanceof Error ? error.message : "Error desconocido";
      setStatusMessage(`Error al guardar: ${message}`);
    },
  });

  const originalRoot = settings?.root_path ?? "";
  const originalDoc = settings?.include_docstrings ?? true;

  const isDirty = useMemo(() => {
    if (!settings) {
      return false;
    }
    return originalRoot !== formRoot.trim() || originalDoc !== formDocstrings;
  }, [settings, originalRoot, formRoot, originalDoc, formDocstrings]);

  const handleSave = () => {
    if (!settings || !isDirty || mutation.isPending) {
      return;
    }
    const payload: { root_path?: string; include_docstrings?: boolean } = {};
    const trimmedRoot = formRoot.trim();
    if (trimmedRoot && trimmedRoot !== originalRoot) {
      payload.root_path = trimmedRoot;
    }
    if (formDocstrings !== originalDoc) {
      payload.include_docstrings = formDocstrings;
    }
    if (Object.keys(payload).length === 0) {
      setStatusMessage("No hay cambios para guardar.");
      return;
    }
    setStatusMessage(null);
    mutation.mutate(payload);
  };

  const excludeDirs = settings?.exclude_dirs ?? [];

  return (
    <div className="settings-view">
      <header className="header-bar">
        <div className="header-left">
          <div className="brand-logo">⚙</div>
          <div className="brand-copy">
            <h1>Settings</h1>
            <p>Configura el workspace y preferencias de visualización.</p>
          </div>
        </div>
        <div className="header-actions">
          <button className="secondary-btn" type="button" onClick={onBack}>
            Volver al overview
          </button>
          <button
            className="primary-btn"
            type="button"
            onClick={handleSave}
            disabled={!isDirty || mutation.isPending || settingsQuery.isLoading}
          >
            {mutation.isPending ? "Guardando…" : "Guardar cambios"}
          </button>
        </div>
      </header>

      <div className="panel" style={{ gap: 12 }}>
        {settingsQuery.isLoading ? (
          <span style={{ color: "#7f869d" }}>Cargando configuración…</span>
        ) : settingsQuery.isError ? (
          <div className="error-banner">
            No se pudo cargar la configuración. {String(settingsQuery.error)}
          </div>
        ) : statusMessage ? (
          <span style={{ color: "#7dd3fc" }}>{statusMessage}</span>
        ) : (
          <span>Los cambios se aplican y persisten en el backend.</span>
        )}
        <button type="button" onClick={activityClear}>
          Limpiar actividad
        </button>
      </div>

      <div className="settings-grid">
        <section className="settings-card">
          <h2>Ruta del proyecto</h2>
          <p>Define el directorio raíz que será analizado por el backend.</p>
          <div className="setting-row">
            <div className="setting-info">
              <strong>Ruta actual</strong>
              <span>{settings?.absolute_root ?? formRoot}</span>
            </div>
            <div className="setting-controls">
              <input
                type="text"
                value={formRoot}
                onChange={(event) => setFormRoot(event.target.value)}
                disabled={settingsQuery.isLoading}
              />
              <button type="button" disabled>
                Cambiar...
              </button>
            </div>
          </div>
          <div className="setting-row">
            <div className="setting-info">
              <strong>Excluir directorios</strong>
              <span>Se ignoran durante escaneos e índices.</span>
            </div>
            <div className="settings-tags">
              {excludeDirs.map((tag) => (
                <span className="settings-tag" key={tag}>
                  {tag}
                </span>
              ))}
            </div>
          </div>
        </section>

        <section className="settings-card">
          <h2>Watcher y sincronización</h2>
          <p>Controla cómo se aplican los cambios del sistema de archivos.</p>
          <div className="toggle-row">
            <div>
              <strong>Watcher activo</strong>
              <span>
                {settings?.watcher_active
                  ? "Reescanea en cuanto se detectan eventos."
                  : "Watcher deshabilitado."}
              </span>
            </div>
            <input type="checkbox" checked={settings?.watcher_active ?? false} readOnly />
          </div>
          <div className="toggle-row">
            <div>
              <strong>Auto-rescan</strong>
              <span>Fuerza escaneos completos al detectar cambios mayores.</span>
            </div>
            <input type="checkbox" disabled />
          </div>
          <div className="toggle-row">
            <div>
              <strong>Persistir snapshots</strong>
              <span>Guarda los resultados en `.cache` para iniciar más rápido.</span>
            </div>
            <input type="checkbox" checked readOnly />
          </div>
        </section>

        <section className="settings-card">
          <h2>Visualización</h2>
          <p>Ajusta cómo se muestran los símbolos en la interfaz.</p>
          <div className="setting-row">
            <div className="setting-info">
              <strong>Modo de símbolos</strong>
              <span>Agrupación principal para el explorador.</span>
            </div>
            <div className="setting-controls">
              <select value="tree" disabled>
                <option value="tree">Carpeta → archivo → símbolo</option>
              </select>
            </div>
          </div>
          <div className="toggle-row">
            <div>
              <strong>Mostrar docstrings</strong>
              <span>
                Controla si el analizador extrae docstrings para mostrarlos en la UI.
              </span>
            </div>
            <input
              type="checkbox"
              checked={formDocstrings}
              onChange={(event) => setFormDocstrings(event.target.checked)}
              disabled={settingsQuery.isLoading}
            />
          </div>
          <div className="toggle-row">
            <div>
              <strong>Tema oscuro</strong>
              <span>Activa la paleta actual del workspace.</span>
            </div>
            <input type="checkbox" checked readOnly />
          </div>
        </section>

        <section className="settings-card">
          <h2>Próximamente</h2>
          <p>Funcionalidades en el roadmap para iteraciones futuras.</p>
          <div className="settings-tags">
            <span className="settings-tag">Integraciones</span>
            <span className="settings-tag">Perfiles</span>
            <span className="settings-tag">Alertas</span>
            <span className="settings-tag">Permisos</span>
          </div>
          <p>
            Añadiremos soporte para múltiples workspaces, reglas de exclusión por lenguaje
            y alertas configurables para eventos críticos.
          </p>
        </section>
      </div>

      <footer className="settings-footer">
        <span>Settings sincronizados con el backend</span>
        <span>Última actualización: {new Date().toLocaleString()}</span>
      </footer>
    </div>
  );
}
