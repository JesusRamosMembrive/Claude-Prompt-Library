# Backend Quickstart

Guía rápida para poner en marcha el backend, validar que el watcher funciona y consultar el estado del índice antes de conectar la UI.

## Requisitos previos
1. Crear y activar el entorno virtual (`.venv`) y asegurarse de tener las dependencias instaladas:
   ```bash
   python -m venv .venv
   .venv/bin/pip install -r requirements.txt  # o pip install -e .
   .venv/bin/pip install watchdog            # necesario para el watcher en vivo
   ```
2. Elegir un directorio de trabajo que actuarà como proyecto a analizar. En los ejemplos usamos `/tmp/code-map-playground/project`.

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

El backend persiste un snapshot en `<root>/.cache/code-map.json`; al reiniciar lo carga para responder rápido y luego ejecuta un escaneo completo en segundo plano.

## Siguientes pasos
- Añadir logging más detallado en los batch del watcher si hace falta visibilidad extra.
- Escribir pruebas de integración una vez tengamos scripts automatizados.
- Iniciar la configuración del frontend (React/Vite) consumiendo estos endpoints.
