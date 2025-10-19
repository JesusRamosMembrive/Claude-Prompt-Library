# Estado Actual

**Fecha**: 2025-10-18
**Etapa**: 1 (Prototipado)
**Sesión**: 3

## Objetivo de Phase 1
✅ COMPLETADO: Script CLI que copia templates a proyectos nuevos o existentes

## Progreso
- [x] Crear init_project.py
- [x] Implementar copy de templates
- [x] Implementar replace de placeholders
- [x] Manejar proyectos existentes
- [x] Coexistir con .claude/ de Claude Code
- [x] Tests automatizados
- [x] Probado en proyecto real

## Decisiones tomadas

### Implementación inicial (2025-10-18)
- Un solo archivo: init_project.py (~80 líneas)
- Solo stdlib: pathlib, shutil, sys, datetime
- Sin clases, solo funciones simples
- Placeholders: PROJECT_NAME, DATE, YEAR

### Soporte para proyectos existentes (2025-10-18)
- Script crea directorio si no existe (mkdir exist_ok=True)
- Permite instalar en proyectos existentes
- Caso de uso: añadir metodología a proyectos legacy

### Coexistencia con Claude Code (2025-10-18)
**Problema encontrado:** Claude Code usa .claude/settings.local.json
**Solución:** Copiar solo archivos .md que faltan, no tocar otros archivos
**Resultado:** Coexistencia natural sin conflictos

**Lista explícita de archivos template:**
- 00-project-brief.md
- 01-current-phase.md
- 02-stage1-rules.md
- 02-stage2-rules.md
- 02-stage3-rules.md

**Lógica:** Si archivo existe → skip. Si no → copiar y reemplazar placeholders.

### Qué NO hicimos (deliberadamente)
- ❌ Múltiples tipos de templates (web-api, cli-tool, etc.)
- ❌ Prompts interactivos para rellenar placeholders
- ❌ Flag --force para reinicializar
- ❌ Validación compleja de nombres
- ❌ Configuración persistente
- ❌ Progress bars o UI fancy
- ❌ Cambiar nombre a .claude-templates/

**Por qué:** YAGNI - No hay dolor que justifique estas features todavía.

## Estado de Phase 1
**COMPLETO Y FUNCIONAL** ✅

El script hace exactamente lo que necesita:
- Copia templates a proyectos nuevos
- Añade templates a proyectos existentes
- Coexiste con Claude Code
- Reemplaza placeholders correctamente
- Tests pasan

## Próximos pasos

**ANTES de Phase 2:**
1. Usar init_project.py en 3-5 proyectos MÁS
2. Seguir metodología .claude/ en esos proyectos
3. Documentar dolor real (qué falta, qué sobra, qué molesta)
4. Evaluar si Phase 1 es suficiente o necesitamos Phase 2

**Criterios para considerar Phase 2:**
- [ ] Necesito diferentes tipos de templates (web, CLI, robot) - dolor 3+ veces
- [ ] Biblioteca de prompts es incómoda de usar - dolor 3+ veces
- [ ] Placeholders insuficientes - dolor 3+ veces
- [ ] Otras personas quieren usar esto - evidencia real

**Si NO hay dolor → Phase 1 es suficiente. Proyecto completo.**
---

## Notas de desarrollo

### Consideraciones técnicas
- Usar `pathlib.Path` para portabilidad
- `shutil.copytree` para copiar carpetas
- Reemplazo simple de placeholders con `str.replace()`
- No usar librerías externas en Phase 1

### Preguntas resueltas
- ✅ ¿Cómo manejar si el directorio destino ya existe? → `sys.exit(1)` con mensaje de error
- ✅ ¿Qué placeholders necesitamos? → `{{PROJECT_NAME}}`, `{{DATE}}`, `{{YEAR}}`

### Preguntas para próxima sesión
- ¿Necesitamos más placeholders en uso real?
- ¿Los templates básicos cubren suficientes casos de uso?
- ¿El flujo de trabajo es fluido o hay fricciones?

## Decisiones tomadas

### Coexistencia con Claude Code (2025-10-18)

**Problema:** 
- Claude Code usa `.claude/settings.local.json`
- Nuestra herramienta usa `.claude/*.md`
- Inicialmente el script rechazaba si `.claude/` existía

**Solución implementada:**
- Copiar solo archivos .md que faltan
- No tocar otros archivos en `.claude/` (como settings.local.json)
- Permite coexistencia natural
- Si archivo ya existe → skip (mensaje informativo)

**Código:**
- ~20 líneas adicionales
- Lista explícita de archivos template
- Check de existencia antes de copiar
- Solo reemplaza placeholders en archivos nuevos

**Por qué esta solución:**
- ✅ Simple (lógica clara de copy-if-not-exists)
- ✅ No destructiva (preserva todo lo existente)
- ✅ Resuelve problema real (coexistir con Claude Code)
- ✅ No interfiere (archivos .md ≠ settings.json)
- ✅ Apropiado para Phase 1

**Edge case conocido:**
- Si quieres REINICIALIZAR templates → borrar manualmente o añadir `--force` en futuro
- Dolor no experimentado todavía, defer solución