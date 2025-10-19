# .claude/CLAUDE_CODE_REFERENCE.md

Quick reference de comandos útiles de Claude Code:

## Slash Commands Esenciales
- `/add` - Añadir archivos al contexto
- `/drop` - Remover archivos del contexto
- `/debug` - Modo debug
- etc.

## Cuándo usar subagentes
- [criterios]

## Cuándo considerar MCP
- [criterios]

(Referencia, no implementación)
```

**Por qué:**
- ✅ Documentación de referencia rápida
- ✅ Sienta bases para features futuras
- ✅ No implementa nada complejo

**Total Phase 2:** ~1 día de trabajo

---

## 🗺️ Roadmap Completo (Tu "Fase 11")

Ahora definimos el **camino completo** sin implementar todo:

### **Phase 1: Template Copier** ✅ COMPLETO
- CLI básico
- Copia templates
- Coexiste con Claude Code

### **Phase 2: Enhanced Docs + Prompt Helper** ← SIGUIENTE
- Copia archivos de referencia
- Script para buscar/copiar prompts
- Referencia de slash commands

### **Phase 3: Interactive Prompt Assistant** (futuro)
- Prompts interactivos para placeholders
- Sugerencias basadas en contexto
- Template selector (web-api, cli-tool, robot)

### **Phase 4: Claude Code Integration** (futuro)
- Detectar contexto de Claude Code
- Sugerir slash commands relevantes
- Warnings sobre over-engineering en tiempo real

### **Phase 5: Subagent Advisor** (futuro)
- Analizar complejidad de tarea
- Sugerir cuándo crear subagente
- Templates para task delegation

### **Phase 6: MCP Integration** (futuro)
- Detectar oportunidades para MCP
- Sugerir servidores MCP relevantes
- Ayuda con configuración

### **Phase 7-11: Advanced Features** (muy futuro)
- Machine learning para sugerencias
- Análisis de código para detectar patterns
- Dashboard de métricas de desarrollo
- etc.

**Pero NO implementamos nada después de Phase 2 hasta validar que Phase 2 funciona.**

---

## 📋 Phase 2 Detailed Plan

Vamos a hacer esto **bien** siguiendo la metodología.

### **Estructura de archivos después de Phase 2:**
```
mi-proyecto/
├── .claude/                          # Tracking y metodología
│   ├── 00-project-brief.md
│   ├── 01-current-phase.md
│   ├── 02-stage1-rules.md
│   ├── 02-stage2-rules.md
│   ├── 02-stage3-rules.md
│   └── CLAUDE_CODE_REFERENCE.md     # NUEVO
│
├── docs/                             # NUEVO - Referencias
│   ├── PROMPT_LIBRARY.md
│   ├── QUICK_START.md
│   └── STAGES_COMPARISON.md
│
└── README.md
```

### **Nuevos scripts en claude-prompt-library:**
```
claude-prompt-library/
├── init_project.py                   # Existente, mejorado
├── prompt_helper.py                  # NUEVO
├── templates/
│   ├── basic/.claude/               # Existente
│   └── docs/                        # NUEVO
│       ├── PROMPT_LIBRARY.md
│       ├── QUICK_START.md
│       ├── STAGES_COMPARISON.md
│       └── CLAUDE_CODE_REFERENCE.md
└── ...
```

---

## 🎯 Phase 2 Implementation Plan

### **Sesión 1: Copiar archivos de referencia** (1 hora)

**Tareas:**
1. Crear `templates/docs/` con archivos de referencia
2. Actualizar `init_project.py` para copiar `docs/`
3. Actualizar tests
4. Probar en proyecto nuevo

**Prompt inicial para Claude Code:**
```
Vamos a implementar Phase 2.1: Copiar archivos de referencia.

Lee:
1. .claude/00-project-brief.md
2. .claude/01-current-phase.md
3. .claude/02-stage2-rules.md (ahora estamos en Etapa 2)

Objetivo: Modificar init_project.py para copiar también:
- PROMPT_LIBRARY.md
- QUICK_START.md  
- STAGES_COMPARISON.md
- Nuevo: CLAUDE_CODE_REFERENCE.md

a docs/ del proyecto destino.

Propón estructura y cambios. NO implementes todavía.
```

### **Sesión 2: Prompt Helper Script** (2-3 horas)

**Prompt para Claude Code:**
```
Ahora vamos a crear prompt_helper.py

Objetivo: Script CLI simple para:
1. Listar categorías de prompts
2. Buscar prompts por categoría
3. Mostrar prompt específico
4. Copiar a clipboard (bonus si fácil)

Restricciones Etapa 2:
- UN archivo: prompt_helper.py
- Solo stdlib + pyperclip (para clipboard)
- Sin UI compleja
- Sin base de datos

Propón estructura. NO implementes todavía.