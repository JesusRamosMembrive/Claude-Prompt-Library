# Discovery · Sección "Linters"

## Objetivo
- Añadir una sección dedicada a linters/quality checks dentro de la app Stage-Aware, visible desde la navegación principal.
- Orquestar un pipeline de validación que ejecute herramientas estándar (`ruff`, `black`, `mypy`, `bandit`, `pytest`, `pytest-cov`, `pre-commit`) y comprobaciones personalizadas (ej. alertar cuando un archivo supera cierto umbral de líneas).
- Integrar notificaciones de escritorio que adviertan de fallos o hallazgos relevantes tras cada ejecución.

## Estado actual
- El repositorio no define todavía una sección UI relacionada con linters.
- Comprobación de dependencias (salida de `pip show <tool>`): todas las herramientas listadas (`ruff`, `black`, `mypy`, `bandit`, `pytest`, `pytest-cov`, `pre-commit`) no están instaladas en el entorno actual.
  - Instalación recomendada (único comando):\
    `pip install ruff black mypy bandit pytest pytest-cov pre-commit`
- `requirements.txt` sólo incluye dependencias backend básicas y `pytest`. Será necesario decidir si ampliamos ese fichero, creamos `requirements-dev.txt` o documentamos la instalación manual.
- No hay script centralizado para ejecutar linters ni reglas personalizadas.
- No existe mecanismo de notificaciones de escritorio integrado.

## Requerimientos funcionales
- Mostrar en la nueva sección web:
  - Lista de herramientas y reglas aplicadas.
  - Estado/resultados de la última ejecución (idealmente con fecha y resumen).
  - Destacar reglas personalizadas (ej. “archivo >500 líneas” con umbral configurable).
- Permitir lanzar los linters manualmente desde la app o, al menos, reflejar el resultado de ejecuciones externas (watcher o pipeline).
- Notificar en escritorio cuando:
  - Alguna herramienta falla.
  - Se activa una regla personalizada crítica (p. ej. exceso de líneas).
- Mantener la experiencia en español y alineada con el diseño existente.

## Requerimientos técnicos iniciales
- Script orquestador (ej. `scripts/run_quality_checks.py` o Makefile) que:
  - Ejecute las herramientas en orden apropiado (formateadores → analizadores → tests → métricas personalizadas).
  - Devuelva un artefacto (JSON/YAML) con resultados y métricas que la UI pueda consumir.
  - Permita configurar umbrales (líneas máximas, exclusiones, etc.).
- Configuración de `pre-commit` para herramientas rápidas (ruff, black, quizás mypy con `--strict` parcial).
- Comprobación personalizada de longitud de archivos:
  - Implementar en Python para reutilizar lógica (usar `pathlib`, contar líneas).
  - Registrar las rutas infractoras y mensaje sugerido (“Considere refactorizar”).
- Servicio de notificaciones:
  - Componente backend que invoque `notify-send` (Linux), `osascript` (macOS) o librería multiplataforma (`plyer`, `desktop-notifier`), según disponibilidad.
  - Debe integrarse con el watcher existente o con la ejecución del script central.
- UI:
  - Nueva ruta `Linters` en `HeaderBar`.
  - Crear vista (`LintersView.tsx`) y componentes de presentación (tabla/resumen/alertas).
  - Consultar API o recurso local para poblar datos (pendiente definir endpoint en backend).

## Propuesta de arquitectura de flujo
1. **Watcher / Trigger**: el watcher existente detecta cambios y lanza `scripts/run_quality_checks.py`.
2. **Pipeline**:
   - Ejecuta herramientas estándar (paralelizable donde convenga).
   - Corre validaciones personalizadas (longitud de archivo, otras reglas a futuro).
   - Genera reporte estructurado (JSON) con:
     - Resultado por herramienta (ok/fallo, salida relevante).
     - Resumen de reglas personalizadas.
     - Timestamp y lista de archivos afectados.
3. **Persistencia ligera**:
   - Guardar el JSON en una ubicación conocida (ej. `workspace/.linters/last_report.json`) o exponerlo mediante API.
4. **Notificaciones**:
   - Si se detectan fallos/alertas críticas, emitir notificación nativa.
5. **Frontend**:
   - Consumir el endpoint o el archivo expuesto por el backend.
   - Mostrar resumen, historial breve y detalles (posible tabla con filtros).
   - Permitir navegación hacia documentación de cada regla/herramienta.

## Riesgos & preguntas abiertas
- **Portabilidad de notificaciones**: confirmar sistemas objetivo (Linux/macOS/Windows) para seleccionar librería/estrategia.
- **Coste en tiempo de ejecución**: `pytest` + `pytest-cov` pueden ser lentos; decidir si se ejecutan siempre o sólo bajo demanda.
- **Gestión de dependencias**: elegir si las herramientas se instalan en entorno global, virtualenv o se documenta instalación manual.
- **Integración backend**: validar cómo el backend actual expone datos (FastAPI); definir endpoint para reportes de linters.
- **Histórico**: determinar si se necesita historial o sólo el último reporte.

## Próximos pasos propuestos
1. Acordar política de dependencias (añadir a `requirements-dev.txt`, `pyproject.toml` o doc).
2. Diseñar estructura del reporte JSON y endpoint/servicio backend que lo sirva.
3. Implementar prototipo del script orquestador y la comprobación de longitud de archivos.
4. Integrar notificaciones básicas (empezando por Linux con `notify-send` como MVP).
5. Construir la vista `Linters` en el frontend consumiendo datos mock hasta que el backend esté listo.
6. Iterar sobre reglas personalizadas y documentar cómo extenderlas.

## Estructura del reporte (propuesta)
- **`root_path`** y **`generated_at`**: contexto temporal del análisis.
- **`summary`** (`ReportSummary`):
  - `overall_status`: estado agregado (`pass`, `warn`, `fail`, etc.).
  - Totales por estado (`total_checks`, `checks_passed`, `checks_warned`, `checks_failed`).
  - Métricas globales (`duration_ms`, `files_scanned`, `lines_scanned`, `issues_total`, `critical_issues`).
- **`tools`** (`ToolRunResult[]`):
  - Información operacional (comando ejecutado, duración, exit code, versión).
  - Estado individual (`status`), número de incidencias y una muestra (`issues_sample` con `IssueDetail`).
  - Extractos de stdout/stderr para facilitar el diagnóstico.
- **`custom_rules`** (`CustomRuleResult[]`):
  - Estado de cada regla propia, descripciones y violaciones con detalle (archivo, línea, severidad, sugerencia).
- **`coverage`** (`CoverageSnapshot`): métricas de cobertura (statements/branches, líneas faltantes).
- **`metrics`**: diccionario para KPI adicionales (p. ej. tiempo total, archivos modificados).
- **`chart_data`** (`ChartData`):
  - `issues_by_tool`: recuento listo para gráficos de barras.
  - `issues_by_severity`: distribución para un gráfico de rosquilla.
  - `top_offenders`: archivos con mayor número de incidencias (ideal para listas ordenadas).
- **`notes`**: observaciones o recomendaciones generadas tras el pipeline.

Los modelos viven en `code_map/linters/report_schema.py` y se diseñaron para serializarse a JSON sin pérdida,
sirviendo directamente al frontend para renderizar tarjetas-resumen, tablas, timelines y gráficos.
