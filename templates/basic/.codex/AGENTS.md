# Codex Agent Instructions

## 📍 Contexto del proyecto

- **Marco:** Stage-Aware Development Framework  
- **Objetivo:** Evitar sobre-ingeniería guiando a la IA según la etapa de madurez del proyecto.  
- **Stage actual:** Consulta `.codex/stage*-rules.md` y correlación con `.claude/01-current-phase.md`.

## ✅ Protocolo inicial (OBLIGATORIO)

Antes de ejecutar cualquier acción:

1. Lee los siguientes archivos (usa el comando `Read` o equivalentes de Codex):
   - `.claude/00-project-brief.md`
   - `.claude/01-current-phase.md`
   - `.codex/stage*-rules.md` correspondiente a la etapa actual
2. Confirma al usuario:
   - Qué etapa detectaste
   - Qué se completó en la última sesión
   - Qué dudas tienes antes de continuar
3. Solicita aclaraciones si falta información. No avances hasta recibir confirmación.

## 🧭 Lineamientos generales

- Respeta las reglas de la etapa indicada (Prototipado, Estructuración, Escalado).
- Propón un plan de acción antes de modificar archivos.
- Pide aprobación para decisiones arquitectónicas o para introducir dependencias nuevas.
- Prefiere soluciones evolutivas: añade complejidad sólo cuando el dolor actual lo justifique.

## 🏁 Al finalizar cada sesión

1. Actualiza `.claude/01-current-phase.md` con:
   - Cambios realizados (archivos incluidos)
   - Decisiones y justificaciones
   - Tareas pendientes o riesgos detectados
   - Próximos pasos recomendados
2. Resumen final al usuario confirmando que la documentación quedó actualizada.

## 🚫 Evita

- Introducir abstracciones o frameworks sin un problema concreto que lo exija.
- Asumir que recordamos contexto previo sin re-leer los archivos fuente.
- Ignorar reglas de etapa o combinar etapas sin validación.
- Saltarte la propuesta de plan cuando la tarea es moderada o compleja.

## 📚 Recursos adicionales

- `.codex/stage*-rules.md`: Reglas por etapa adaptadas a Codex.
- `docs/QUICK_START.md`: Flujo recomendado paso a paso.
- `docs/STAGES_COMPARISON.md`: Comparativa rápida entre etapas.
- Documentación oficial Codex CLI (`docs/config.md`, `docs/prompts.md` en repositorio principal de Codex).

---

*Este archivo se copia automáticamente por `init_project.py` y actúa como guía base para Codex. Personalízalo si el proyecto requiere instrucciones específicas.*
