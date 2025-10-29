# Configuración y persistencia de Settings

## Objetivo
Permitir que la aplicación exponga y actualice opciones de configuración (p. ej. ruta raíz, exclusiones, docstrings) mediante la API, con almacenamiento persistente para que sobrevivan reinicios.

## Alcances iniciales
- **Ruta raíz** (`root_path`): directorio que analiza el motor. Cambiar esta opción debería propagar un reescaneo completo y reiniciar el watcher.
- **Exclusiones** (`exclude_dirs`): lista de carpetas a ignorar (por defecto `.venv`, `__pycache__`, etc.). De momento solo lectura; edición futura.
- **Docstrings** (`include_docstrings`): booleano que controla si el analizador captura docstrings.
- Opciones futuras: auto-rescan, tema, persistencia de snapshots, integraciones.

## Almacenamiento propuesto
- Crear archivo `settings.json` en `<root>/.cache/code-map-settings.json`. Razones:
  - ya existe `.cache` para snapshots; mantenemos contexto del proyecto en el mismo lugar.
  - se reutiliza al cambiar de workspace (cada root tiene su configuración).
- Estructura mínima:
  ```json
  {
    "version": 1,
    "root_path": "/abs/path",
    "exclude_dirs": [".venv", "__pycache__", "node_modules"],
    "include_docstrings": true
  }
  ```
- El backend cargará este archivo en `AppState` durante `startup`. Si no existe, se crea con valores por defecto/saneados.
- Cuando el cliente haga `PUT /settings`, se valida el payload (p. ej. rutas dentro del workspace, booleans), se actualiza el archivo, y (según cambios):
  - Cambia `root_path`: se detiene watcher, se reinician `ProjectScanner`, `SymbolIndex`, se rehace snapshot.
  - Cambia `include_docstrings`: se actualiza flag y se fuerza un rescan completo para reflejar docstrings según nuevo estado.

## Endpoints API detallados

### `GET /settings`
**Respuesta 200**
```json
{
  "root_path": "relative/path",
  "absolute_root": "/abs/path",
  "exclude_dirs": ["..."],
  "include_docstrings": true,
  "watcher_active": true
}
```
- `watcher_active`: bandera para UI (depende de `WatcherService.is_running`).
- `absolute_root`: opcional para mostrar al usuario, pero UI puede usar `root_path` relativo.

### `PUT /settings`
**Body esperado**
```json
{
  "root_path": "/nuevo/path",         // opcional
  "include_docstrings": true|false    // opcional
}
```
- Cualquier campo ausente se ignora.
- Validaciones:
  - `root_path` debe existir, ser directorio, y (opcional) estar dentro de una lista permitida. Para esta iteración, permitimos cualquier ruta legible por el backend.
  - Evitar que root cambie a un directorio vacío por accidente (avisar si no se detectan `.py` tras el rescan).
- **Respuesta 200**:
  ```json
  {
    "updated": ["root_path", "include_docstrings"],
    "settings": { ... }  // mismos campos que GET
  }
  ```
- **Respuesta 400**: validación fallida (p. ej. ruta inválida).

## Integración backend
1. Añadir un dataclass `AppSettings` (atributos: `root_path`, `exclude_dirs`, `include_docstrings`).
2. Incorporar `AppState.settings: AppSettings` y métodos:
   - `load_settings()`
   - `save_settings()`
   - `apply_settings(new_settings: AppSettings)` (maneja reinicios/rescan).
3. Ajustar `AppState.startup()` para cargar `settings` antes de crear `ProjectScanner` (o recrearlos tras cargar).
4. Añadir rutas en `api.routes` (`GET/PUT /settings`), usando Pydantic para esquemas.

## Integración frontend
- Consumir `GET /settings` al entrar a la vista de Settings.
- Permitir editar `include_docstrings` (toggle) y `root_path` (input/desplegable). Por ahora:
  - `root_path` como texto editable con botón “Cambiar…”.
  - `include_docstrings` como checkbox que lanza `PUT /settings`.
- Mostrar feedback (spinner, éxito/error) y sincronizar con `useSelectionStore`/`useActivityStore` cuando se cambian rutas (posiblemente limpiar selección).

## Consideraciones
- Cambiar `root_path` supone reconfigurar watcher, planner y snapshot. Debemos asegurar cambios atómicos:
  1. Detener watcher.
  2. Limpiar índice.
  3. Actualizar configuración.
  4. Ejecutar `scan_and_update_index`.
  5. Arrancar watcher de nuevo.
- Manejar errores: si el rescan falla (p. ej. permisos), revertir a la configuración anterior y devolver 500 con detalle.
- Logging: registrar cambios de settings (`logger.info("Settings updated: root=%s, include_docstrings=%s", ...)`).

---

Con este diseño, el siguiente paso es implementar el módulo de persistencia (lectura/escritura de `AppSettings`) y los endpoints mencionados para exponerlo al frontend.
