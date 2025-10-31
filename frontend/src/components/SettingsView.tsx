import { useEffect, useMemo, useState } from "react";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import type { UseQueryResult } from "@tanstack/react-query";
import { useNavigate } from "react-router-dom";

import { browseForRoot, updateSettings } from "../api/client";
import type { SettingsPayload, SettingsUpdatePayload } from "../api/types";
import { queryKeys } from "../api/queryKeys";
import { DEFAULT_EXCLUDED_DIRS } from "../config/defaultExcludes";
import { useActivityStore } from "../state/useActivityStore";
import { useSelectionStore } from "../state/useSelectionStore";
import { DocstringsSection } from "./settings/DocstringsSection";
import { ExcludeDirsSection } from "./settings/ExcludeDirsSection";
import { RootPathSection } from "./settings/RootPathSection";
import { WatcherSection } from "./settings/WatcherSection";

interface SettingsViewProps {
  settingsQuery: UseQueryResult<SettingsPayload>;
}

const DEFAULT_EXCLUDES_LOWER = new Set(DEFAULT_EXCLUDED_DIRS.map((dir) => dir.toLowerCase()));

function extractCustomExcludes(list?: string[]): string[] {
  if (!list) {
    return [];
  }
  return list.filter((dir) => !DEFAULT_EXCLUDES_LOWER.has(dir.toLowerCase()));
}

function sortExcludes(list: string[]): string[] {
  return [...list].sort((a, b) => a.localeCompare(b));
}

export function SettingsView({ settingsQuery }: SettingsViewProps): JSX.Element {
  const activityClear = useActivityStore((state) => state.clear);
  const queryClient = useQueryClient();
  const navigate = useNavigate();

  const settings = settingsQuery.data;
  const originalRoot = settings?.root_path ?? "";
  const originalDoc = settings?.include_docstrings ?? true;
  const originalCustomExcludes = useMemo(
    () => sortExcludes(extractCustomExcludes(settings?.exclude_dirs)),
    [settings?.exclude_dirs],
  );

  const [formRoot, setFormRoot] = useState(originalRoot);
  const [formDocstrings, setFormDocstrings] = useState(originalDoc);
  const [customExcludes, setCustomExcludes] = useState<string[]>(originalCustomExcludes);
  const [statusMessage, setStatusMessage] = useState<string | null>(null);

  useEffect(() => {
    if (!settings) {
      return;
    }
    setFormRoot(settings.root_path);
    setFormDocstrings(settings.include_docstrings);
    setCustomExcludes(sortExcludes(extractCustomExcludes(settings.exclude_dirs)));
  }, [settings]);

  const mutation = useMutation({
    mutationFn: updateSettings,
    onSuccess: (result) => {
      queryClient.setQueryData(queryKeys.settings, result.settings);
      queryClient.invalidateQueries({ queryKey: queryKeys.tree });
      queryClient.invalidateQueries({ queryKey: queryKeys.status });
      queryClient.invalidateQueries({ queryKey: queryKeys.stageStatus });
      if (result.updated.includes("root_path")) {
        useSelectionStore.getState().clearSelection();
      }
      setCustomExcludes(sortExcludes(extractCustomExcludes(result.settings.exclude_dirs)));
      setStatusMessage(
        result.updated.length > 0
          ? `Cambios aplicados: ${result.updated.join(", ")}`
          : "No había cambios que guardar.",
      );
    },
    onError: (error: unknown) => {
      const message = error instanceof Error ? error.message : "Error desconocido";
      setStatusMessage(`Error al guardar: ${message}`);
    },
  });

  const excludesChanged = useMemo(() => {
    if (!settings) {
      return false;
    }
    if (originalCustomExcludes.length !== customExcludes.length) {
      return true;
    }
    return originalCustomExcludes.some((dir, index) => dir !== customExcludes[index]);
  }, [settings, originalCustomExcludes, customExcludes]);

  const isDirty = useMemo(() => {
    if (!settings) {
      return false;
    }
    if (originalRoot !== formRoot.trim()) {
      return true;
    }
    if (originalDoc !== formDocstrings) {
      return true;
    }
    return excludesChanged;
  }, [settings, originalRoot, formRoot, originalDoc, formDocstrings, excludesChanged]);

  const handleSave = () => {
    if (!settings || !isDirty || mutation.isPending) {
      return;
    }

    const payload: SettingsUpdatePayload = {};
    const trimmedRoot = formRoot.trim();

    if (trimmedRoot && trimmedRoot !== originalRoot) {
      payload.root_path = trimmedRoot;
    }

    if (formDocstrings !== originalDoc) {
      payload.include_docstrings = formDocstrings;
    }

    if (excludesChanged) {
      payload.exclude_dirs = customExcludes;
    }

    if (Object.keys(payload).length === 0) {
      setStatusMessage("No hay cambios para guardar.");
      return;
    }

    setStatusMessage(null);
    mutation.mutate(payload);
  };

  const handleAddExclude = (value: string) => {
    const trimmed = value.trim();
    if (!trimmed) {
      return { ok: false, error: "Escribe un nombre de directorio válido." };
    }

    if (/[\\/]/.test(trimmed)) {
      return { ok: false, error: "Usa solo nombres de directorio, sin rutas ni separadores." };
    }

    const lowered = trimmed.toLowerCase();
    if (DEFAULT_EXCLUDES_LOWER.has(lowered)) {
      return { ok: false, error: "Ese directorio ya se excluye por defecto." };
    }

    if (customExcludes.some((dir) => dir.toLowerCase() === lowered)) {
      return { ok: false, error: "Ese directorio ya está en tus exclusiones." };
    }

    setCustomExcludes((prev) => sortExcludes([...prev, trimmed]));
    return { ok: true };
  };

  const handleRemoveExclude = (value: string) => {
    setCustomExcludes((prev) => prev.filter((dir) => dir !== value));
  };

  const statusTone = statusMessage?.toLowerCase().startsWith("error") ? "error" : "info";
  const isLoading = settingsQuery.isLoading;
  const isMutating = mutation.isPending;
  const browseMutation = useMutation({
    mutationFn: browseForRoot,
    onSuccess: (response) => {
      setFormRoot(response.path);
      setStatusMessage(`Directorio seleccionado: ${response.path}`);
    },
    onError: (error: unknown) => {
      const message = error instanceof Error ? error.message : "No se pudo abrir el diálogo";
      setStatusMessage(`Error al seleccionar directorio: ${message}`);
    },
  });

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
          <button className="secondary-btn" type="button" onClick={() => navigate("/")}>
            Volver al overview
          </button>
          <button
            className="primary-btn"
            type="button"
            onClick={handleSave}
            disabled={!isDirty || isMutating || isLoading}
          >
            {isMutating ? "Guardando…" : "Guardar cambios"}
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
          <span
            style={{
              color: statusTone === "error" ? "#f97316" : "#7dd3fc",
            }}
          >
            {statusMessage}
          </span>
        ) : (
          <span>Los cambios se aplican y persisten en el backend.</span>
        )}
        <button type="button" onClick={activityClear}>
          Limpiar actividad
        </button>
      </div>

      <div className="settings-grid">
        <RootPathSection
          absoluteRoot={settings?.absolute_root}
          rootValue={formRoot}
          disabled={isLoading || browseMutation.isPending}
          onRootChange={setFormRoot}
          onBrowse={() => browseMutation.mutate()}
          browseDisabled={browseMutation.isPending || isMutating || isLoading}
        />

        <ExcludeDirsSection
          defaultDirs={DEFAULT_EXCLUDED_DIRS}
          customDirs={customExcludes}
          disabled={isLoading || isMutating}
          onAdd={handleAddExclude}
          onRemove={handleRemoveExclude}
        />

        <WatcherSection watcherActive={settings?.watcher_active} />

        <DocstringsSection
          includeDocstrings={formDocstrings}
          disabled={isLoading}
          onToggleDocstrings={setFormDocstrings}
        />

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
