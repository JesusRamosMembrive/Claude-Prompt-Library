# API FastAPI: especificación inicial

## Objetivos
- Exponer la información del motor (`SymbolIndex`, `ProjectScanner`, `SnapshotStore`, `ChangeScheduler`) mediante un API HTTP accesible por la UI React.
- Permitir que la UI consulte el estado actual (árbol de archivos, detalle de un archivo, búsqueda).
- Proveer un canal para recibir notificaciones de cambios en caliente (SSE inicialmente, con posibilidad de WebSocket más adelante).
- Ofrecer endpoints de diagnóstico (`/health`) y la capacidad de iniciar rescaneos manuales si fuese necesario.

## Endpoints iniciales

### `GET /health`
- **Respuesta**: `{ "status": "ok" }`
- Verifica que el servicio está operativo. Útil para supervisión.

### `GET /tree`
- **Descripción**: Devuelve la jerarquía carpeta → archivo → símbolos.
- **Query params**:
  - `refresh` (bool, opcional): si es `true`, fuerza un escaneo completo antes de responder.
- **Respuesta**:
  ```json
  {
    "root": {
      "name": "project",
      "path": "relative/path",
      "is_dir": true,
      "children": [...],
      "symbols": []  // solo para nodos de archivo
    }
  }
  ```
- Se serializa `ProjectTreeNode` de forma recursiva. Forzamos rutas relativas al root definido.
- Si el árbol es grande, considerar paginación/lazy loading en el frontend; la API entrega el árbol completo por ahora.

### `GET /files/{path}`
- **Descripción**: Devuelve el resumen de un archivo concreto.
- **Path param**: `path` relativo al root. Se normaliza y valida que permanezca dentro del root.
- **Respuesta**:
  ```json
  {
    "path": "pkg/module.py",
    "modified_at": "2024-05-01T12:34:56Z",
    "symbols": [
      { "name": "foo", "kind": "function", "lineno": 10, "parent": null }
    ],
    "errors": [
      { "message": "...", "lineno": 20, "col_offset": 4 }
    ]
  }
  ```
- Si el archivo no existe en el índice, se responde 404.

### `GET /search`
- **Query params**:
  - `q`: string requerido, texto a buscar (case-insensitive) en nombres de símbolos.
- **Respuesta**:
  ```json
  {
    "results": [
      {
        "name": "MyClass",
        "kind": "class",
        "path": "pkg/module.py",
        "lineno": 12,
        "parent": null
      }
    ]
  }
  ```
- Puede incluir paginación futura (`limit`/`offset`), por ahora devolvemos todos.

### `GET /events`
- **Descripción**: Stream SSE con notificaciones de cambios (`event: update`, `data: {"updated":[...], "deleted":[...]}`).
- **Notas**:
  - Se conecta a un `asyncio.Queue` alimentado por el loop que drena `ChangeScheduler`.
  - Mantiene la conexión abierta, envía `: keepalive` cada N segundos para evitar timeouts.
  - En una fase posterior se evaluará WebSocket; se diseña para permitir ambos.

### `POST /rescan`
- **Descripción**: Fuerza un escaneo completo, actualiza índice y snapshot, retorna resumen `{ "files": N }`.
- **Uso**: Herramienta administrativa/manual; podría requerir autenticación básica en futuro.

### `GET /status` *(nuevo)*
- **Descripción**: Devuelve información resumida del motor para mostrar en UI y diagnosticar estados.
- **Respuesta**:
  ```json
  {
    "root_path": "relative/path",
    "absolute_root": "/abs/path",
    "watcher_active": true,
    "include_docstrings": true,
    "last_full_scan": "2025-02-14T12:34:56Z",
    "last_event_batch": "2025-02-14T12:35:12Z",
    "files_indexed": 128,
    "symbols_indexed": 642,
    "pending_events": 0
  }
  ```
- `last_full_scan`: se actualiza cuando `perform_full_scan` termina correctamente.
- `last_event_batch`: timestamp del último batch aplicado por `ChangeScheduler`.
- `files_indexed` y `symbols_indexed`: recuento rápido (`len(index.get_all())` y suma de símbolos).
- `pending_events`: tamaño actual de la cola de eventos SSE (para detectar cuellos de botella).
- Uso previsto: alimentar badge del header, mostrar tooltips y permitir diagnósticos rápidos.

### `GET /preview`
- **Descripción**: Devuelve el contenido bruto de un archivo para previsualización (especialmente HTML).
- **Parámetros**:
  - `path` (query): ruta relativa al root. Se valida que apunte a un archivo existente.
- **Comportamiento**:
  - Para HTML devuelve `Content-Type: text/html; charset=utf-8`. Se recomienda que la UI lo renderice en `iframe` con `sandbox` para evitar scripts.
  - Para otras extensiones se puede devolver como texto plano (future work).
- **Errores**:
  - 404 si la ruta no existe o está fuera del root.

## Gestión del root y dependencias
- La ruta raíz se pasa vía configuración (env var `CODE_MAP_ROOT` o archivo `.env`) o se gestiona en memoria cuando la UI la establece.
- Para este MVP, se lanza el backend apuntando a un root fijo; más adelante añadimos endpoint/config para cambiarlo en caliente.
- Se utilizarán dependencias de FastAPI para inyectar `AppState` con referencias a `ProjectScanner`, `SymbolIndex`, `ChangeScheduler`, `SnapshotStore` y la cola de eventos SSE.

## Serialización
- Crear utilidades en `code_map/api/schemas.py` (Pydantic) para garantizar formatos consistentes.
- `modified_at` se serializa a ISO8601 en UTC.
- Las rutas se envían relativas al root para evitar exponer caminos absolutos del host.

## Concurrencia y loop de cambios
- Un task en background (al arrancar la app) ejecuta:
  1. `scanner.hydrate_index_from_snapshot(index)`
  2. `scanner.scan_and_update_index(index, persist=True)`
  3. `watcher.start()` si está disponible.
  4. Loop `while True`: `await scheduler_async.drain()` utilizando `asyncio.to_thread` para no bloquear.
- Por simplicidad inicial, implementaremos `ChangeScheduler` en sync y un wrapper asíncrono que hace `await asyncio.sleep(interval)` + `scheduler.drain(force=True)` en un hilo.
- Notificaciones se empujan a `asyncio.Queue` consumida por `/events`.

## Seguridad y límites
- No se implementa autenticación de momento (proyecto local). Documentar que el servicio debe correr en red de confianza.
- Añadir límites de tamaño de respuesta (gzip activado por uvicorn/gunicorn) más adelante si el árbol es muy grande.

## Pruebas
- Usar `TestClient` de FastAPI para validar `GET /health`, `/tree`, `/files/{path}`, `/search`.
- Inyectar una instancia de `AppState` con index prellenado mediante fixtures para aislar tests sin un watcher real.
