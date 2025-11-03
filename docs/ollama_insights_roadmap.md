# Ollama Insights Roadmap

## Configuración y opción del usuario
- [x] Añadir preferencia en el backend para activar/desactivar los insights automáticos de Ollama.
- [x] Exponer la configuración en la API (`GET/PUT /settings`) e incluir flags para modelo y frecuencia.
- [x] Crear controles en el frontend Stage Toolkit para activar la característica, seleccionar modelo y definir frecuencia.
- [x] Guardar la selección en el estado frontend y sincronizarla con el backend.

## Pipeline backend de insights
- [x] Implementar un scheduler asincrónico que ejecute el pipeline cuando la preferencia esté habilitada.
- [x] Preparar prompts detallados con:
  - [x] Resumen del último reporte de linters.
  - [x] Estado Stage y recomendaciones actuales.
  - [x] Cambios recientes relevantes (si hay acceso al snapshot).
- [x] Crear un endpoint específico (`POST /integrations/ollama/analyze`) para ejecuciones bajo demanda.
- [x] Serializar y persistir resultados (p.ej. tabla de “insights” reutilizando el esquema de notificaciones).

## Frontend: presentación de insights
- [x] Construir una vista/panel dentro del Stage Toolkit que muestre las últimas recomendaciones de Ollama.
- [x] Incluir estado de ejecución (última vez, próxima corrida programada, modelo usado).
- [x] Permitir ejecutar el análisis manualmente desde la UI (botón “Generar ahora”).
- [ ] Añadir filtros o categorías (refactor, linters, patrones) para que el usuario navegue fácilmente por los resultados.

## Manejo de errores y control
- [ ] Gestionar timeouts y reintentos controlados, mostrando feedback claro cuando Ollama no responda.
- [ ] Registrar logs detallados en caso de fallos (con información del endpoint, modelo y prompts).
- [ ] Añadir opción para limpiar historial de insights generados automáticamente.

## Iteraciones futuras
- [ ] Generar propuestas de cambios concretos (por ejemplo, diffs/pseudocódigo) cuando sea viable.
- [ ] Integrar comparativas entre ejecuciones (qué recomendaciones fueron aplicadas).
- [ ] Permitir configurar distintos perfiles de prompts (refactor, deuda técnica, patrones de arquitectura).
