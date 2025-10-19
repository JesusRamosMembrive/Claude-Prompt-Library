# Estado Actual

**Fecha**: 2025-10-18
**Etapa**: 2 (Estructuración)
**Sesión**: 4

## Phase 1: COMPLETO ✅

## Phase 2: Enhanced Docs + Prompt Helper

**Objetivo:** Hacer recursos útiles accesibles y resolver "copiar prompts es tedioso"

**Dolor que justifica Phase 2:**
- Archivos útiles (PROMPT_LIBRARY.md, etc.) no se copian → difícil consultar
- Copiar prompts manualmente es tedioso → necesita helper
- Falta referencia rápida de Claude Code slash commands

**Scope Phase 2:**
- [x] Copiar archivos de referencia a docs/
- [ ] Script prompt_helper.py para buscar/copiar prompts
- [ ] Documento CLAUDE_CODE_REFERENCE.md

**NO en Phase 2 (defer a Phase 3+):**
- ❌ Prompts interactivos (queda para Phase 3)
- ❌ Análisis automático de código
- ❌ Sugerencias en tiempo real
- ❌ Integración profunda con Claude Code
- ❌ MCP automático
- ❌ Dashboard o UI

**Visión largo plazo documentada pero NO implementada:**
- Phase 3-6: Features interactivas
- Phase 7+: ML y análisis avanzado
- Ver ROADMAP.md para visión completa

# Estado Actual

**Fecha**: 2025-10-18
**Etapa**: 2 (Estructuración)
**Sesión**: 5

## Phase 2: Enhanced Docs + Prompt Helper

### Phase 2.1: Copy Reference Docs ✅ COMPLETO

**Implementado:**
- ✅ Copia 4 archivos de referencia a docs/
  - PROMPT_LIBRARY.md (biblioteca de prompts útiles)
  - QUICK_START.md (workflow con Claude Code)
  - STAGES_COMPARISON.md (referencia rápida de etapas)
  - CLAUDE_CODE_REFERENCE.md (slash commands, MCP, subagents)
- ✅ Skip si archivos ya existen (no destructivo)
- ✅ Mensajes claros de progreso
- ✅ Tests actualizados y pasando
- ✅ Probado en proyecto real (ChessPlayerAnalyzerV2)

**Código:**
- ~120 líneas en init_project.py
- Separación clara: .claude/ (tracking) vs docs/ (referencia)
- Validación de templates antes de copiar

**Tests pasando:**
- ✓ Proyecto nuevo: copia todo
- ✓ Re-run: skip archivos existentes
- ✓ Coexistencia con Claude Code settings
- ✓ Placeholders reemplazados

**Próximo:** Phase 2.2 - Script para buscar/copiar prompts fácilmente

### Phase 2.2: Prompt Helper Script ✅ COMPLETO

**Implementado:**
- ✅ Modo comando scriptable (list, show, copy)
- ✅ Modo interactivo con UI navegable
- ✅ Búsqueda flexible de prompts
- ✅ Auto-copy a clipboard (si disponible)
- ✅ Degrada gracefully sin dependencias

**Código:**
- ~300 líneas en prompt_helper.py
- Modo híbrido: auto-detección de modo
- Parsing robusto de PROMPT_LIBRARY.md

**⚠️ DECISIÓN CONSCIENTE: Dependencias externas**

Rompimos la restricción de "solo stdlib" de Etapa 2:
- `simple-term-menu`: Para modo interactivo
- `pyperclip`: Opcional, para clipboard

**Justificación:**
- UX significativamente mejor con menú navegable
- Modo comando funciona sin dependencias
- Degrada gracefully: error claro si falta dependencia
- Trade-off razonable: dependencias pequeñas, gran valor

**Alternativa considerada:**
Menú con input() básico (stdlib puro) → UX mucho peor, no justifica el esfuerzo

**Lección aprendida:**
Las reglas son guías. A veces el pragmatismo gana. Lo importante es:
1. Reconocer cuándo las rompes
2. Justificar por qué
3. Documentar la decisión
4. Asegurar degradación razonable

**Validación:**
- ✓ Comando list funciona
- ✓ Comando show funciona
- ✓ Comando copy funciona
- ✓ Modo interactivo funciona (con dependencia)
- ✓ Error claro sin dependencia

**Próximo:** Usar en proyectos reales, validar que resuelve "copiar prompts es tedioso"
```

---

## 📋 Tareas de Cierre Phase 2.2

### **1. requirements.txt** (crear)
```
# Required for interactive mode
simple-term-menu>=1.6.1

# Optional for clipboard support
pyperclip>=1.8.2

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
- [x] Necesito diferentes tipos de templates (web, CLI, robot) - dolor 3+ veces
- [x] Biblioteca de prompts es incómoda de usar - dolor 3+ veces
- [x] Placeholders insuficientes - dolor 3+ veces
- [x] Otras personas quieren usar esto - evidencia real

**Si NO hay dolor → Phase 1 es suficiente. Proyecto completo.**
---

### Phase 2.3: Automatización de Context Loading (BONUS) ✅

**Problema identificado:**
- Claude Code no lee automáticamente archivos .claude/
- Tracking manual es tedioso y propenso a errores
- Cada sesión requiere pedir explícitamente lectura de contexto

**Solución implementada:**
- Crear settings.local.json con customInstructions
- Instrucciones permanentes para Claude Code
- Workflow automático: leer contexto al inicio, actualizar al final

**Archivo: .claude/settings.local.json**
```json
{
  "customInstructions": "...",
  "permissions": {...}
}
```

**Resultado:**
- ✅ Claude Code lee contexto automáticamente
- ✅ Claude Code recuerda actualizar tracking
- ✅ Metodología funciona sin fricción
- ✅ Disciplina "automatizada" via configuración

**Lección:**
Este archivo es CRÍTICO para que la metodología funcione en la práctica.
Sin él, el tracking es manual y se pierde rápidamente.

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

**Decisión:** Implementar solo lo mínimo que resuelve dolor de Phase 2.
Validar antes de continuar a Phase 3.