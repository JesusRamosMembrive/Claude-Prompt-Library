Goal: Estructura de carpetas y archivos .claude/ para ESTE proyecto
Deliverable: Carpeta con .claude/ funcional
Implementation: Crear manualmente los archivos siguiendo nuestra metodología
Deferred: Código, features, todo
Notes: Practicar lo que predicamos
```

### **Phase 1: Template Copier** (2-3 horas)
```
Goal: Script que copia templates a un proyecto nuevo
Deliverable: Usuario ejecuta `./init-project.py my-robot` → se crea carpeta con .claude/
Implementation: 
  - Carpeta `templates/basic/` con los 5 archivos .claude/
  - Script Python que copia templates y reemplaza placeholders
  - Todo hardcoded, zero configuración
Deferred: 
  - Múltiples tipos de template
  - CLI fancy
  - Validación de inputs
  - Prompts interactivos
Notes: Probar que la idea básica funciona
```

### **Phase 2: Prompt Library** (1-2 días)
```
Goal: Colección organizada de prompts útiles que se pueden consultar
Deliverable: Carpeta `prompts/` con prompts categorizados
Implementation:
  - Estructura: prompts/by-category/nombre-prompt.md
  - Categorías: debugging, refactoring, architecture, testing
  - Script simple para listar prompts disponibles
Deferred:
  - Search/filter
  - Copy to clipboard
  - Integración con editor
Notes: Empezar con 5-10 prompts que usas frecuentemente
```

### **Phase 3: Multiple Templates** (1 día)
```
Goal: Diferentes tipos de proyecto (CLI tool, web API, robot control, etc.)
Deliverable: Usuario puede elegir template: `./init-project.py my-api --type=web-api`
Implementation:
  - templates/cli-tool/
  - templates/web-api/
  - templates/robot-control/
  - Cada uno con .claude/ adaptado al tipo
Deferred:
  - Templates custom del usuario
  - Composición de templates
Notes: Usar los 3 tipos de proyecto que más haces
```

### **Phase 4: Interactive Init** (medio día)
```
Goal: Preguntas interactivas para personalizar el setup
Deliverable: Script pregunta: nombre, tipo, descripción → genera personalizado
Implementation:
  - input() básico con preguntas
  - Reemplaza placeholders en templates con respuestas
Deferred:
  - Validación compleja
  - Config file
  - Undo/rollback
```

### **Phase 5: Prompt Insertion** (1 día)
```
Goal: Copiar prompts de la librería al proyecto actual fácilmente
Deliverable: `./prompt insert debugging/stuck-in-loop` → añade a current-phase.md
Implementation:
  - Script lee prompt de library
  - Lo añade a .claude/01-current-phase.md con timestamp
  - Opción de editarlo antes de insertar
Deferred:
  - Gestión de prompts insertados
  - Variables en prompts


claude-prompt-library/
├── 📘 SETUP_COMPLETE.md          ← EMPIEZA AQUÍ
├── 📑 FILE_INDEX.md               ← Navegación de archivos
├── 📗 README.md                   ← Overview
├── 📕 GUIDE.md                    ← Manual completo (2000+ líneas)
├── 📙 QUICK_START.md              ← Workflow con Claude Code
├── 📓 PROMPT_LIBRARY.md           ← 20+ prompts útiles
├── 📔 STAGES_COMPARISON.md        ← Referencia rápida
│
├── .claude/                       ← Metodología de ESTE proyecto
│   ├── 00-project-brief.md
│   ├── 01-current-phase.md
│   ├── 02-stage1-rules.md
│   ├── 02-stage2-rules.md
│   └── 02-stage3-rules.md
│
├── templates/basic/.claude/       ← Templates para OTROS proyectos
│   └── [5 archivos con placeholders]
│
└── tests/test_full_flow.sh


# Ejemplos de prompts utilizados en claude

python init_project.py my-awesome-project
# → Carpeta creada con .claude/ listo
# → Placeholders reemplazados
# → En menos de 5 segundos
```

---

## 📝 Tu workflow ahora

### 1. **Abre Claude Code** en la carpeta `claude-prompt-library`

Ya tienes todo el contexto listo en `.claude/`:
- `00-project-brief.md` - Qué construir
- `01-current-phase.md` - Dónde estás
- `02-stage1-rules.md` - Reglas a seguir

### 2. **Usa este prompt inicial** (copy-paste en Claude Code)
```
Hola. Voy a implementar Phase 1 del proyecto Claude Prompt Library.

IMPORTANTE: Primero planificamos, luego implementamos paso a paso.

Por favor, lee estos archivos en orden:
1. .claude/00-project-brief.md
2. .claude/01-current-phase.md  
3. .claude/02-stage1-rules.md

Después de leerlos, responde:
- ¿Entiendes el objetivo? (script CLI que copia templates)
- ¿Entiendes que estamos en ETAPA 1 (prototipado)?
- ¿Entiendes las reglas? (máximo 3 archivos, solo stdlib, máxima simplicidad)

NO escribas código todavía. Espera mi confirmación.
```

### 3. **Pide el plan** (después de que Claude confirme)
```
Perfecto. Ahora propón la estructura MÍNIMA para init_project.py

Recuerda las restricciones de Etapa 1:
- UN solo archivo: init_project.py
- Solo stdlib: pathlib, shutil, sys, datetime
- Lo MÁS SIMPLE que funciona
- Sin clases si una función sirve
- Sin validación compleja

Dame SOLO:
1. Estructura del archivo (funciones principales)
2. Flujo de ejecución en 4-5 pasos
3. Qué placeholders necesitamos reemplazar

Formato:
```
ESTRUCTURA:
- main() - Entry point
- función1() - Propósito
- función2() - Propósito

FLUJO:
1. Parse argumentos
2. ...

PLACEHOLDERS:
- {{PROJECT_NAME}}
- ...
```

NO implementes todavía. Espera mi aprobación.
```

### 4. **Revisa el plan**

Cuando Claude te dé el plan, pregúntate:
- ¿Necesito TODAS esas funciones?
- ¿Puedo hacerlo más simple?
- ¿Cumple reglas de Etapa 1?

**Si necesitas cambios:**
```
Simplifica esto:
- [lista cambios específicos]

Ejemplo: "No necesito validate_project_name(), solo check básico inline"
```

**Si está bien:**
```
✅ Aprobado. 

Implementa init_project.py COMPLETO en un solo paso.

Debe:
- Copiar templates/basic/.claude/ a destino
- Reemplazar {{PLACEHOLDERS}}
- Print mensaje de éxito
- Manejar error básico (directorio existe)

Muéstrame el código completo cuando termines.
```

### 5. **Review del código**

Cuando Claude te muestre el código:
```
Review de init_project.py:

Contra .claude/02-stage1-rules.md:
- ¿Es UN solo archivo? 
- ¿Solo usa stdlib?
- ¿Tiene <100 líneas?
- ¿Sin clases innecesarias?
- ¿Sin abstracciones?
- ¿Es lo MÁS SIMPLE que funciona?

Lista cualquier cosa que rompa las reglas.