# Plan de la interfaz de exploración de código

- [x] Definir alcance inicial y requisitos: soporte solo para Python, obtener nombres de funciones libres, clases y métodos, documentar posibles extensiones (docstrings, C++, JS/TS). La ruta raíz la selecciona el usuario desde la interfaz; se excluyen rutas de ruido como `__pycache__`, `.venv` y similares; el watcher permanece activo continuamente; la UI muestra todos los archivos incluso sin símbolos y organiza la información en jerarquía carpeta → archivo → símbolos; la validación por ahora se realiza únicamente desde la UI.
- [x] Diseñar motor de análisis con `ast`: recorrer el árbol del proyecto, extraer símbolos relevantes y normalizar su representación en una estructura común.
- [x] Establecer estrategia de almacenamiento y caché: decidir formato (JSON) y política de actualización incremental para resultados del escaneo.
- [x] Integrar sistema de observación de cambios (`watchdog`): detectar modificaciones en archivos `.py` y disparar resincronizaciones parciales mediante `WatcherService`, `ChangeScheduler` y procesamiento incremental en `ProjectScanner`.
- [x] Implementar API con FastAPI: endpoints para árbol de archivos, detalle por archivo y búsqueda básica de símbolos, stream SSE y rescan administrativo.
- [x] Prototipar interfaz React/Vite: árbol lateral, panel de detalles de símbolos y controles de filtrado/búsqueda.
- [x] Añadir canal de actualizaciones en tiempo real (SSE/WebSocket) entre el servidor y la UI para reflejar cambios detectados por el watcher.
- [ ] Preparar pruebas automatizadas y herramientas de desarrollo: tests para el parser y la API, pruebas de componentes clave y scripts de arranque.
