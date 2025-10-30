# Codex Integration Plan

## Objective

Extender el framework Stage-Aware para que, además de Claude Code, también genere instrucciones, plantillas y configuración compatible con el CLI de Codex. El usuario podrá elegir si desea preparar Claude, Codex o ambos agentes al inicializar un proyecto.

## Trabajo Planificado

1. **Auditoría y alineación de plantillas**
   - Inventariar los activos críticos existentes en `.claude/` (brief, phase tracking, stage rules, subagents, `settings.local.json`, etc.).
   - Definir la estructura espejo en `templates/basic/.codex/`, asegurando equivalentes Codex-friendly (`AGENTS.md`, reglas por etapa, prompts o documentación de apoyo).
   - Identificar contenido dependiente de características exclusivas de Claude y planificar adaptaciones (por ejemplo, comandos slash, referencias de UI).

2. **Diseño de recursos Codex**
   - Crear plantilla `AGENTS.md`/`.override` que replique el protocolo de inicio descrito en `CLAUDE.md`.
   - Preparar reglas de etapa (`stage1.md`, `stage2.md`, `stage3.md`) reutilizando contenido existente donde aplique.
   - Evaluar si se necesitan plantillas adicionales (p. ej., `config.toml`, prompts personalizados) y documentar su finalidad.

3. **Extensión de `init_project.py`**
   - Añadir argumento `--agent` (valores: `claude`, `codex`, `both`, default `both`).
   - Estructurar la lógica de copia para que sólo genere los activos seleccionados y mantenga idempotencia.
   - Garantizar que los placeholders (`{{PROJECT_NAME}}`, etc.) se reemplazan en los nuevos archivos Codex.
   - Registrar feedback al usuario detallando qué agentes se configuraron y qué archivos se omitieron por existir.

4. **Documentación y UX**
   - Actualizar `docs/QUICK_START.md` y/o crear un nuevo `CODEX.md` que explique cómo usar Codex con el proyecto inicializado.
   - Añadir referencias cruzadas en `README.md` y `CLAUDE.md` (o su homólogo Codex) aclarando que ahora existe soporte dual.
   - Incluir instrucciones para seeding opcional de `~/.codex` (global prompts/config) cuando sea relevante.

5. **Validación**
   - Ejecutar `python init_project.py` en todas las combinaciones de agente para confirmar que las rutas y mensajes son correctos.
   - Verificar que los archivos Codex generados cumplen con la jerarquía esperada y que no se sobreescriben modificaciones existentes.
   - Documentar comprobaciones manuales pendientes o tests automatizados futuros (por ejemplo, scripts en `tests/`).

## Riesgos & Consideraciones

- **Compatibilidad futura**: Codex puede evolucionar sus rutas de descubrimiento (`AGENTS.md`, prompts). Mantener referencias a la documentación oficial (`docs/config.md`, `docs/prompts.md`) y evaluar centralizar constantes en un módulo Python.
- **Configuraciones de usuario**: Evitar escribir en `~/.codex` sin confirmación explícita. Proporcionar instrucciones y, opcionalmente, un flag dedicado (`--seed-codex-home`) en iteraciones futuras.
- **Duplicación de contenido**: Usar plantillas compartidas cuando sea posible para minimizar divergencias entre Claude y Codex (p. ej., extraer reglas de etapa a archivos base y generar variaciones con mínimas diferencias).

