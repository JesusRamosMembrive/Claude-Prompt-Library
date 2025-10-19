# Claude Prompt Library - Roadmap

## Vision

Herramienta interactiva que ayuda a desarrollar con Claude Code de forma estructurada,
evitando over-engineering y maximizando productividad.

## Completed

### Phase 1: Template Copier ✅
- CLI básico para copiar templates
- Coexistencia con Claude Code
- Usado y validado en proyectos reales

## In Progress

### Phase 2: Enhanced Docs + Prompt Helper 🚧
**Status:** Planificado
**ETA:** 1-2 días
**Goal:** Hacer recursos accesibles, facilitar uso de prompts

**Features:**
- Copiar archivos de referencia (PROMPT_LIBRARY.md, etc.) a docs/
- prompt_helper.py para buscar y copiar prompts
- Referencia de slash commands de Claude Code

**Pain solved:** "Copiar prompts es tedioso"

## Planned (Not Started)

### Phase 3: Interactive Prompt Assistant
**Status:** Diseño pendiente
**Depends on:** Phase 2 validado con uso real
**Goal:** Setup interactivo de proyectos

**Possible features:**
- Prompts interactivos para placeholders personalizados
- Template selector (web-api, cli-tool, robot, etc.)
- Validación de inputs

**When:** Solo si Phase 2 no resuelve suficiente el dolor

### Phase 4: Claude Code Integration
**Status:** Concepto
**Goal:** Ayuda contextual con Claude Code

**Possible features:**
- Detectar contexto actual de Claude Code
- Sugerir slash commands relevantes
- Warnings de over-engineering en tiempo real
- Auto-checkpoint según metodología

**Research needed:**
- ¿Cómo detectar estado de Claude Code?
- ¿Qué APIs están disponibles?

### Phase 5: Subagent Advisor
**Status:** Concepto
**Goal:** Ayudar a decidir cuándo/cómo usar subagentes

**Possible features:**
- Analizar complejidad de tarea descrita
- Sugerir cuándo crear subagente
- Templates para task delegation
- Tracking de subagent work

### Phase 6: MCP Integration
**Status:** Concepto
**Goal:** Facilitar uso de Model Context Protocol

**Possible features:**
- Detectar oportunidades para MCP
- Sugerir servidores MCP relevantes
- Ayuda con configuración
- Templates de MCP servers

### Phase 7+: Advanced Features
**Status:** Ideas brainstorm
**Goal:** TBD basado en aprendizajes de Phases 1-6

**Possible directions:**
- ML para sugerencias personalizadas
- Análisis de código para pattern detection
- Dashboard de métricas de desarrollo
- Team collaboration features
- Integration con IDEs

## Principles

**Cada phase:**
1. Resuelve dolor específico y validado
2. Se implementa completamente antes de siguiente
3. Se usa en real antes de continuar
4. Puede ser el último (si resuelve suficiente)

**NO implementamos por:**
- "Sería cool"
- "Alguien podría necesitar"
- "Preparar para el futuro"

**SÍ implementamos cuando:**
- Dolor recurrente (3+ veces)
- Solución clara
- Impacto medible
- Usaremos inmediatamente

## Decision Points

Después de cada phase, evaluar:
- ¿El dolor se resolvió?
- ¿Apareció nuevo dolor?
- ¿Vale la pena siguiente phase?
- ¿O es suficiente aquí?

**OK terminar en cualquier phase si resuelve el problema.**