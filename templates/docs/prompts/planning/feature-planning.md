# Feature Planning

## Descripción
Planifica la implementación de una feature antes de empezar. Verifica que sea apropiada para el stage actual.

## Prompt
```
Quiero añadir: [feature]

ANTES de implementar, ayúdame a planificar:

1. ¿Es apropiado para mi fase actual?
   - Revisar: .claude/01-current-phase.md
   - Revisar: .claude/00-project-brief.md (¿está en deferred?)

2. ¿Cuál es la implementación MÁS SIMPLE?
   - Sin abstracciones prematuras
   - Sin "preparar para el futuro"

3. ¿Qué archivos debo modificar?
   - Lista mínima de archivos afectados

4. ¿En qué orden implementar?
   - Pasos específicos, uno a la vez

Dame un plan. NO implementes hasta mi aprobación.
```

## Tags
- Categoría: planning
- Dificultad: básico
- Stage: 1, 2, 3
