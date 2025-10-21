# Biblioteca de Prompts

Colección organizada de prompts útiles para desarrollo con Claude Code.

## Cómo Usar

### Navegación Interactiva
```bash
python prompt_helper.py
```
Menú navegable con las categorías y prompts disponibles. Auto-copia al portapapeles.

### Modo Comando
```bash
# Listar todos los prompts
python prompt_helper.py list

# Mostrar un prompt específico
python prompt_helper.py show debugging/stuck

# Copiar un prompt al portapapeles
python prompt_helper.py copy refactoring/simplification
```

## Categorías

### 🐛 DEBUGGING (5 prompts)
Resolución de problemas y diagnóstico de errores.

- **Stuck in Loop** - Cuando estás atascado y has intentado varias soluciones sin éxito
- **Error Oscuro** - Explica mensajes de error confusos en términos claros
- **Performance Issue** - Identifica cuellos de botella de rendimiento
- **State Management** - Diagnóstica problemas de estado inconsistente
- **Integration Problem** - Resuelve fallos en integraciones con APIs/módulos/servicios

### 🔧 REFACTORING (5 prompts)
Mejora de código existente.

- **Simplification Check** - Detecta sobre-ingeniería o falta de estructura
- **Code Smell Detection** - Identifica patrones problemáticos
- **Extract Function** - Oportunidades para extraer funciones y reducir complejidad
- **Dead Code Removal** - Encuentra código no utilizado que puede eliminarse
- **Naming Improvement** - Mejora nombres de variables, funciones y clases

### 🏗️ ARCHITECTURE (5 prompts)
Decisiones de diseño y estructura.

- **Design Decision** - Ayuda a elegir entre opciones arquitectónicas
- **Pattern Validation** - Valida si un patrón de diseño es apropiado
- **Layer Separation** - Evalúa separación de capas (presentación, lógica, datos)
- **Module Boundaries** - Define/valida límites entre módulos
- **Dependency Analysis** - Analiza dependencias externas e internas

### ✅ TESTING (5 prompts)
Estrategias y diseño de tests.

- **Test Strategy** - Define qué y cómo testear según el stage actual
- **Edge Case Identification** - Identifica casos borde a testear
- **Mock Strategy** - Define qué y cómo mockear en tests
- **Integration Test Design** - Diseña tests de integración efectivos
- **Test Data Management** - Estrategia para gestionar datos de prueba

### 📋 PLANNING (5 prompts)
Planificación de features y proyectos.

- **Feature Planning** - Planifica implementación de features
- **Phase Transition Check** - Evalúa si es momento de cambiar de stage
- **Technical Debt Assessment** - Evalúa y prioriza deuda técnica
- **Sprint Planning** - Planifica sprints con estimaciones realistas
- **Risk Analysis** - Identifica riesgos técnicos y propone mitigaciones

### 🚨 EMERGENCY (5 prompts)
Respuesta rápida a incidentes.

- **Rollback** - Revierte cambios de forma segura cuando algo se rompe
- **Production Bug** - Diagnóstico y fix rápido de bugs en producción
- **Memory Leak Detection** - Diagnostica y resuelve memory leaks
- **Security Incident** - Respuesta inicial a incidentes de seguridad
- **Data Corruption Recovery** - Plan para recuperar datos corruptos o perdidos

### 🔄 EVOLUTION (5 prompts)
Evolucionar de soluciones simples a complejas cuando el dolor lo justifica.

- **Subprocess to Background Jobs** - De subprocess bloqueante a threading/celery con tracking
- **File Storage to Database** - De archivos JSON/CSV a base de datos real
- **Sync to Async** - De código síncrono a asíncrono (cuándo vale la pena)
- **Script to API** - De script CLI a API REST sin perder funcionalidad
- **In-Memory to Distributed** - De cache local a Redis/soluciones distribuidas

## Estructura de Archivos

```
prompts/
├── README.md (este archivo)
├── debugging/
│   ├── stuck-in-loop.md
│   ├── error-oscuro.md
│   ├── performance-issue.md
│   ├── state-management.md
│   └── integration-problem.md
├── refactoring/
│   ├── simplification-check.md
│   ├── code-smell-detection.md
│   ├── extract-function.md
│   ├── dead-code-removal.md
│   └── naming-improvement.md
├── architecture/
│   ├── design-decision.md
│   ├── pattern-validation.md
│   ├── layer-separation.md
│   ├── module-boundaries.md
│   └── dependency-analysis.md
├── testing/
│   ├── test-strategy.md
│   ├── edge-case-identification.md
│   ├── mock-strategy.md
│   ├── integration-test-design.md
│   └── test-data-management.md
├── planning/
│   ├── feature-planning.md
│   ├── phase-transition-check.md
│   ├── technical-debt-assessment.md
│   ├── sprint-planning.md
│   └── risk-analysis.md
├── emergency/
│   ├── rollback.md
│   ├── production-bug.md
│   ├── memory-leak-detection.md
│   ├── security-incident.md
│   └── data-corruption-recovery.md
└── evolution/
    ├── subprocess-to-background-jobs.md
    ├── file-storage-to-database.md
    ├── sync-to-async.md
    ├── script-to-api.md
    └── in-memory-to-distributed.md
```

## Formato de Cada Prompt

Cada archivo de prompt sigue esta estructura:

```markdown
# [Nombre del Prompt]

## Descripción
[Cuándo usar este prompt]

## Prompt
```
[Contenido del prompt template]
```

## Tags
- Categoría: [debugging/refactoring/etc]
- Dificultad: [básico/intermedio/avanzado]
- Stage: [1/2/3]
```

## Personalización

Los prompts son **templates** - personalízalos según tu situación:

1. Reemplaza los placeholders `[descripción]` con tu información específica
2. Añade contexto de tu proyecto
3. Referencia archivos relevantes
4. Ajusta el nivel de detalle según necesites

## Contribuir

Para añadir nuevos prompts:

1. Crea un archivo `.md` en la categoría apropiada
2. Sigue el formato estándar (ver arriba)
3. El nombre del archivo debe ser descriptivo: `nombre-del-prompt.md`
4. Usa kebab-case (palabras separadas por guiones)

## Filosofía

- **Claridad**: Prompts estructurados que Claude puede seguir fácilmente
- **Pragmatismo**: Enfocados en resolver problemas reales
- **Simplicidad**: Evita over-engineering y soluciones innecesariamente complejas
- **Contexto**: Siempre considera el stage actual del proyecto

---

*Parte del [Claude Prompt Library](https://github.com/user/claude-prompt-library)*
