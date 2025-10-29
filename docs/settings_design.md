# Configuración y persistencia de Settings

## Objetivo
Permitir que la aplicación exponga y actualice opciones de configuración mediante la API, con almacenamiento persistente para que sobrevivan reinicios.

## Alcances iniciales
- **Ruta raíz** (`root_path`): directorio que analiza el motor. Cambiarla reinicia watcher/escáner y fuerza un rescan completo.
- **Exclusiones** (`exclude_dirs`): lista de carpetas a ignorar. **Editable** desde la UI; debemos persistirla y aplicarla tanto en el escáner como en el watcher.
- **Docstrings** (`include_docstrings`): booleano que controla si el analizador captura docstrings.

## Almacenamiento
- Archivo JSON en `<root>/.cache/code-map-settings.json` con estructura:
  ```json
  {
    "version": 1,
    "root_path": "/abs/path",
    "exclude_dirs": [".venv", "__pycache__", "node_modules"],
    "include_docstrings": true
  }
  ```
- Al iniciar la app se carga el archivo; si no existe, se crea con los valores por defecto de `DEFAULT_EXCLUDED_DIRS`.
- Cuando se actualiza la configuración (`PUT /settings`), se valida y se sobrescribe el archivo.

## API
### `GET /settings`
Devuelve la configuración actual + flags de runtime. Ejemplo:
```json
{
  "root_path": "src",
  "absolute_root": "/home/user/project/src",
  "exclude_dirs": [".venv", "__pycache__"],
  "include_docstrings": true,
  "watcher_active": true
}
```

### `PUT /settings`
Cuerpo permitido:
```json
{
  "root_path": "/otro/path",        // opcional
  "include_docstrings": true|false,   // opcional
  "exclude_dirs": [".venv", "build"] // opcional
}
```
- Campos omitidos no se modifican.
- Validaciones:
  - `root_path`: debe existir y ser directorio.
  - `exclude_dirs`: lista de cadenas; se normaliza eliminando vacíos, duplicados y espacios. Los defaults (`DEFAULT_EXCLUDED_DIRS`) se conservan (no se eliminan).
  - No se permiten rutas absolutas fuera del root para exclusiones.
- Respuesta `200`:
```json
{
  "updated": ["root_path", "exclude_dirs"],
  "settings": { ... }  // igual que GET
}
```
- Respuesta `400`: validación fallida.

## Backend
1. `AppSettings` ya soporta `exclude_dirs`. Debemos permitir que `with_updates` reciba la lista nueva, normalice y combine con defaults.
2. `AppState.update_settings` debe detectar cambios en `exclude_dirs`, reconstruir scanner/index/watcher y persistir.
3. El watcher (`WatcherService`) ya recibe `exclude_dirs`; tras actualizar debemos reiniciarlo.
4. `settings.to_payload()` y `load_settings` deben garantizar que la lista devuelta está ordenada/normalizada.

## Frontend
- A partir de `GET /settings`, poblar controles que permitan añadir y quitar exclusiones.
- Al `PUT /settings`, refrescar `settings` y `status`, limpiar selección y forzar `tree` cuando haya cambios.
