# Backend Quickstart

Guía rápida para poner en marcha el backend, validar que el watcher funciona y consultar el estado del índice antes de conectar la UI.

## Requisitos previos
1. Crear y activar el entorno virtual (`.venv`) y asegurarse de tener las dependencias instaladas:
   ```bash
   python -m venv .venv
   .venv/bin/pip install -r requirements.txt  # o pip install -e .
   .venv/bin/pip install watchdog            # necesario para el watcher en vivo
   .venv/bin/pip install esprima             # habilita análisis de JS/TS
   .venv/bin/pip install tree_sitter_languages  # soporte TypeScript/TSX
   .venv/bin/pip install beautifulsoup4      # extracción básica en HTML
   ```
2. Elegir un directorio de trabajo que actuarà como proyecto a analizar. En los ejemplos usamos `/tmp/code-map-playground/project`.

### Unificación de entornos virtuales

Si trabajaste previamente con otro entorno creado en la raíz (carpetas `bin/`, `lib/`, `include/`, etc.), deja únicamente `.venv/` para evitar conflictos en el `PATH`:

```bash
rm -rf bin include lib lib64 pyvenv.cfg venv
```

Después, reactiva `.venv`, reinstala dependencias si es necesario y comprueba que los comandos (`ruff`, `black`, etc.) se resuelven dentro de `.venv/bin/`.

## Arranque del servidor
```bash
export CODE_MAP_ROOT=/path/al/proyecto
.venv/bin/uvicorn code_map.server:create_app \
    --factory \
    --host 0.0.0.0 \
    --port 8000 \
    --log-level info
```

- `CODE_MAP_ROOT` define la ruta que se analizará.
- Al arrancar verás logs del estado del watcher. Si aparece “watchdog no está disponible”, el watcher queda deshabilitado (instala `watchdog` para activarlo).

### Opciones adicionales
- `CODE_MAP_INCLUDE_DOCSTRINGS` (`true` por defecto): controla si el motor añade docstrings en los resultados. Ajusta a `0` o `false` para omitirlos.

## Validación manual
1. **Crear/editar archivos** en `$CODE_MAP_ROOT`:
   ```bash
   echo 'def demo():\n    return 42' > $CODE_MAP_ROOT/demo.py
   ```
2. **Consultar el árbol y archivos**:
   ```bash
   curl http://localhost:8000/tree | jq
   curl http://localhost:8000/files/demo.py | jq
   ```
3. **Escuchar eventos SSE** (verás `event: update` cuando haya cambios):
   ```bash
   curl -N http://localhost:8000/events
   ```
4. **Forzar un rescan completo** (si el watcher está desactivado o después de muchos cambios):
   ```bash
   curl -X POST http://localhost:8000/rescan
   ```

El backend persiste un snapshot en `<root>/.code-map/code-map.json`; al reiniciar lo carga para responder rápido y luego ejecuta un escaneo completo en segundo plano.

## Integración con Ollama

Para que el panel "Stage Toolkit" pueda consultar y hacer ping a modelos locales debes tener Ollama instalado y sirviendo peticiones.

1. **Instala Ollama** siguiendo la guía oficial según tu plataforma.
2. **Arranca el servicio** antes (o en paralelo) al backend:
   ```bash
   ollama serve
   ```
   - Por defecto queda escuchando en `http://127.0.0.1:11434`.
   - Si prefieres otra dirección/puerto, exporta `OLLAMA_HOST=http://host:puerto` antes de iniciar Uvicorn.
3. **Verifica la conexión** desde nuestro backend:
   ```bash
   curl -s http://localhost:8000/integrations/ollama/status | jq
   ```
   Deberías ver `installed: true` y `running: true`. Si todo está correcto puedes probar un chat corto:
   ```bash
   curl -s -X POST http://localhost:8000/integrations/ollama/test \
     -H 'Content-Type: application/json' \
     -d '{"model":"gpt-oss:latest","prompt":"ping"}' | jq
   ```
4. **Usa la UI**. En la vista Stage Toolkit:
   - Pulsa "Iniciar Ollama" si el servicio aún no estaba levantado (esto ejecuta `ollama serve`).
   - Selecciona un modelo y lanza “Probar chat”.
   - Recuerda que la primera llamada puede tardar mientras se carga el modelo; si ves un aviso de “modelo en carga”, espera unos segundos y reintenta.

Si tienes problemas de conectividad, ejecuta `python tools/debug_ollama.py --endpoint http://127.0.0.1:11434 --model <modelo>` para comprobar TCP, `/api/tags` y un chat de prueba.

## Siguientes pasos
- Añadir logging más detallado en los batch del watcher si hace falta visibilidad extra.
- Escribir pruebas de integración una vez tengamos scripts automatizados.
- Iniciar la configuración del frontend (React/Vite) consumiendo estos endpoints.

### Hacia un setup más sencillo (plan de trabajo)
- Script único (`scripts/setup_backend.py` o `make setup`) que cree `.venv`, instale dependencias y genere `.env` local con `CODE_MAP_ROOT` y `CODE_MAP_DB_PATH`.
- Ajustar `code_map.settings.load_settings` para que, ante la ausencia de variables, asuma la carpeta actual como root y use `<root>/.code-map/state.db` por defecto.
- Refinar el pipeline de linters: usar siempre `sys.executable -m ...`, registrar el `PATH` efectivo y mostrar en la UI un aviso claro cuando se omita una herramienta.
- Mantener este documento actualizado con una tabla de problemas comunes (DB de solo lectura, reportes antiguos, etc.) y pasos para resolverlos.
