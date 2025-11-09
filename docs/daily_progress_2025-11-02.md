# Daily Progress · 2025-11-02

## Lo logrado hoy
- Detectamos el estado de Ollama desde el backend (`/integrations/ollama/status`) incluyendo versión, binario y modelos instalados.
- Añadimos un endpoint para intentar arrancar el servidor (`/integrations/ollama/start`) y cobertura de pruebas para ambos endpoints.
- Refactorizamos el frontend del Stage Toolkit para centrarse únicamente en Ollama:
  - Tarjeta “Ollama local” con estado en vivo, listado de modelos y botón “Iniciar Ollama”.
  - Formulario “Ping a Ollama” con selección de modelo, prompts opcionales y campos para endpoint/timeout.
- Creamos el script de depuración `tools/debug_ollama.py` que verifica TCP, consulta `/api/tags` y hace un chat de prueba para aislar problemas de conexión.
- Confirmamos la comunicación end-to-end entre GUI y Ollama tras cargar el modelo manualmente.

## Próximos pasos propuestos
1. Añadir manejo de colas/estado mientras se carga el modelo (detectar timeouts y sugerir “intenta de nuevo” tras la primera llamada lenta).
2. Integrar tareas útiles sobre el repositorio (por ejemplo “resume archivo seleccionado”) reutilizando el prompt del Ping y mostrando resultados en el panel.
3. Guardar preferencias de modelo/endpoint elegidos por el usuario (en store o backend) para no reintroducirlos cada sesión.
4. Añadir logs visibles en la UI cuando el arranque de Ollama falla (mostrar `original_error` y posibles soluciones) y quizás reintentos automáticos.
