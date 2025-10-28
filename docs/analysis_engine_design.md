# Motor de análisis: diseño inicial

## Objetivos y responsabilidades
- Escanear todos los archivos `.py` dentro de una ruta raíz definida por el usuario desde la UI.
- Respetar una lista de exclusiones por defecto (`__pycache__`, `.venv`, carpetas ocultas comunes, configurables a futuro).
- Obtener símbolos de primer nivel (funciones libres) y símbolos declarados dentro de clases (métodos) con su metadata esencial.
- Servir datos estructurados listos para API/UI sin lógica de presentación.
- Mantener un estado consistente y actualizado gracias a un watcher activo que reprocese archivos modificados.

## Suposiciones iniciales
- El proyecto se encuentra en un filesystem accesible para el backend (no remoto).
- El código Python es compatible con la versión del intérprete que ejecuta el analizador.
- Cuando un archivo tiene errores de sintaxis, se registrará el problema y se continuará con el resto, marcando el archivo como inválido.
- No se requiere información sobre docstrings ni anotaciones de tipos en esta iteración, pero la arquitectura debe permitir añadirlos.
- Los resultados sólo se consumen desde la UI, no hay exportación externa.

## Arquitectura propuesta

### Componentes principales
- `ProjectScanner`: coordina recorridos completos a partir de una ruta raíz, aplicando reglas de exclusión. Produce una colección de descriptores de archivo.
- `FileAnalyzer`: encapsula la lógica basada en `ast` para extraer símbolos de un archivo individual. Recibe rutas y devuelve un objeto `FileSummary`.
- `SymbolIndex`: almacena los resultados en memoria (y opcionalmente en disco) para consumo rápido por la API. Ofrece métodos para consultar por ruta, por símbolo y para construir la jerarquía carpeta → archivo → símbolos.
- `ChangeScheduler`: orquesta reanálisis incremental cuando el watcher emite eventos. Gestiona una cola simple de archivos pendientes y evita duplicados.

### Interfaces clave
- `FileSummary` (dataclass):
  - `path`: `Path`
  - `symbols`: lista de `SymbolInfo`
  - `errors`: lista de incidencias (vacía si el parseo fue exitoso)
  - `modified_at`: `datetime`
- `SymbolInfo` (dataclass):
  - `name`: `str`
  - `kind`: `Literal["function","class","method"]`
  - `parent`: `Optional[str]` (para métodos)
  - `lineno`: `int`
- `ProjectScanner.scan(root: Path) -> list[FileSummary]`
- `FileAnalyzer.parse(path: Path) -> FileSummary`
- `SymbolIndex.update(files: Iterable[FileSummary])`
- `SymbolIndex.get_tree() -> ProjectTree`
- `SymbolIndex.get_file(path: Path) -> FileSummary`
- `SymbolIndex.search(term: str) -> list[SymbolInfo]`

### Flujo general
1. La UI envía la ruta raíz al backend.
2. El backend inicializa `ProjectScanner` con esa ruta, exclusiones y referencias a `FileAnalyzer` y `SymbolIndex`.
3. Se ejecuta un escaneo completo:
   - `ProjectScanner` recorre recursivamente con `Path.rglob("*.py")`, filtrando excluidos.
   - Para cada archivo válido, invoca `FileAnalyzer.parse`.
   - Los resultados se entregan a `SymbolIndex` para que construya el árbol y los índices auxiliares.
4. La API expone los datos a la UI.
5. El watcher alimenta `ChangeScheduler`, que vuelve a llamar a `FileAnalyzer` y refresca las entradas impactadas en `SymbolIndex`.

## Actualizaciones incrementales y manejo de errores
- `WatcherService` (basado en `watchdog`) detecta eventos `created`, `modified`, `deleted`, `moved` dentro de la ruta raíz filtrando exclusiones.
- `ChangeScheduler` normaliza los eventos:
  - Encolamos rutas de archivos `.py` afectados.
  - Aplicamos `debounce` ligero (p.ej. 250 ms) para agrupar ráfagas de cambios.
  - Si un archivo se elimina, se remueve del `SymbolIndex`.
  - Para modificaciones/creaciones movidas, se reejecuta `FileAnalyzer.parse` y se actualiza el índice.
- Errores de análisis:
  - Si `ast.parse` falla, capturamos `SyntaxError` y devolvemos un `FileSummary` con `errors=[...]` y `symbols=[]`.
  - `SymbolIndex` mantiene esta información para que la API pueda avisar a la UI (p.ej. mostrar badge de error).
  - Otros errores inesperados se registran con `logging` y se reintenta según política (p.ej. 3 intentos antes de marcar el archivo con error permanente).
- Integración con API/UI:
  - Después de cada batch de cambios aplicados, se emite un evento (SSE/WebSocket) con las rutas actualizadas.
  - En fallos críticos del watcher, notificamos a la UI y reintentamos inicialización cada `N` segundos.

## Persistencia y caché
- `SnapshotStore` administra snapshots JSON en `<root>/.cache/code-map.json`.
- Serializamos caminos de archivo en forma relativa al root cuando es posible para soportar repos clonados en distintas rutas.
- Cada `FileSummary` se exporta con sus `symbols`, `errors`, `modified_at` (`ISO8601`) y banderas futuras (p.ej. `has_docstrings`).
- En arranques:
  1. Se intenta cargar el snapshot; si existe, se inicializa `SymbolIndex` con esos datos para respuesta inmediata.
  2. Paralelamente se ejecuta un escaneo completo que actualiza el índice y sobrescribe el snapshot una vez finalizado.
- Tras cada batch del watcher se vuelve a persistir sólo los archivos afectados para mantener la caché en sincronía.
- Errores de lectura/escritura (permisos, JSON corrupto) se registran y se ignoran para no bloquear la UI; se fuerza un reescaneo completo.

## Watcher y scheduler
- Dependencia sobre `watchdog` para recibir notificaciones del filesystem con baja latencia. Si no está disponible, el servicio debe degradarse a un modo desactivado sin frenar la aplicación (fallback pendiente).
- `WatcherService` encapsula la configuración de un `Observer`, suscribe un handler que traduce eventos (`created`, `modified`, `deleted`, `moved`) a rutas normales y filtra los excluidos.
- `ChangeScheduler` mantiene una cola y un conjunto para deduplicación, aplica un `debounce` configurable (por defecto 250 ms) y expone `drain()` para entregar lotes listos para reprocesar.
- Flujo típico:
  1. El handler del watcher recibe un evento de archivo `.py` y llama a `scheduler.enqueue(path, event_type)`.
  2. Un loop (hilo o tarea) invoca `scheduler.drain()` periódicamente; este método agrupa rutas por tipo (`created`, `modified`, `deleted`, `moved`) respetando el `debounce`.
  3. El consumidor vuelve a analizar los archivos `created/modified`, elimina los `deleted` del índice y persiste un snapshot actualizado.
  4. Tras aplicar el lote se emite un hook (`on_batch_applied`) para que la capa API/UI publique eventos en tiempo real.
- Los eventos `moved` actualizan la ruta en el índice: se borra el origen y se vuelve a analizar el destino si aún es `.py`.
