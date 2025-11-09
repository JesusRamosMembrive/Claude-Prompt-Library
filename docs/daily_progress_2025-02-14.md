# Diario de progreso – 2025-02-14

## Resumen general
Hoy avanzamos tanto en la arquitectura backend como en la definición visual del frontend:

- Consolidamos el motor de análisis Python (AST, caché JSON, índice en memoria).
- Añadimos el watcher con `watchdog`, scheduler con debounce y API FastAPI completa (incluido SSE y rescan).
- Diseñamos y prototipamos en HTML una UI dark/minimalista, con vistas separadas para Dashboard y Settings.

## Backend
### Lo implementado
- **Análisis y caché**: `ProjectScanner`, `FileAnalyzer`, `SymbolIndex`, `SnapshotStore` funcionando y cubiertos por tests.
- **Actualización incremental**: `ChangeScheduler` + `WatcherService`, métodos de batch en el scanner.
- **FastAPI**: Rutas `/health`, `/tree`, `/files/{path}`, `/search`, `/events` (SSE) y `/rescan`; app creada con `create_app` y `AppState`.
- **Tests**: Suite de Pytest verificando extracción de símbolos, persistencia, scheduler y endpoints (con TestClient y lifespan).
- **Dependencias**: Instalado `fastapi` y ajustado `pytest` con `.venv/bin/python -m pytest`.
- **Insights Ollama**: Configuración persistente para activar/desactivar, elegir modelo, frecuencia y foco de análisis (general, refactors, issues, duplicación, testing).

### Pendiente
- Empaquetar comando de arranque (uvicorn) + scripts (p.ej. `make dev`).
- Validar watcher en ejecución real: escribir tests de integración o script manual.
- Manejar fallback si `watchdog` no existe (degradar a no-watcher con aviso).
- Documentar variables/config (root, docstrings, auto-rescan) y añadir README/API docs.
- Preparar endpoints para estado/config (p.ej. `GET/PUT /settings`) para futura UI settings.

## Frontend/UI
### Lo realizado
- Mockup HTML (`docs/ui_mockup.html`) con:
  - Dashboard: header, árbol de archivos, panel de símbolos con docstrings, panel de filtros/actividad.
  - Settings: tarjetas para ruta, watcher, visualización, “próximamente”; navegación “Settings ↔ Overview”.
  - Tema oscuro, tipografía Inter, iconografía placeholders.
- Interacciones básicas: botones con JS inline para alternar vistas y sincronizar campos.
- Eliminación de símbolos específicos de macOS en atajos y ajuste de layout responsive.

### Trabajo pendiente
- Trasladar el mockup a React/Vite siguiendo componentes (sidebar, detail panel, settings layout).
- Implementar API client (tree, file, search, SSE) y estado (React Query/Zustand).
- Integrar Settings con backend real (persistencia de configuración).
- Añadir soporte para docstrings extendidos, estados de error y mensajes en UI.
- Diseñar/implementar modal de búsqueda global (`Ctrl+K`).

## Próximos pasos sugeridos
1. Preparar scripts de arranque del backend (`uvicorn code_map.server:app --reload`), revisar logs del watcher y asegurar persistencia en `.code-map`.
2. Documentar la API y configuración en README o /docs (cómo cambiar la raíz con el CLI, ajustar docstrings, etc.).
3. Iniciar implementación de frontend real (setup Vite, componentes base, integrar árbol con `/tree`).
4. Plan para almacenar Settings (archivo YAML o endpoint en backend).

Guardamos todo el trabajo en esta sesión; mañana continuar con backend runbook y comenzar port a React.
