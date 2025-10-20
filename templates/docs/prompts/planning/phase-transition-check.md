# Phase Transition Check

## Descripción
Evalúa si es momento de cambiar de stage basándose en dolor real experimentado.

## Prompt
```
Creo que es momento de cambiar de ETAPA [X] a ETAPA [Y].

Evidencia:
- [dolor 1]
- [dolor 2]
- [dolor 3]

Revisa los criterios en .claude/02-stageX-rules.md

Responde:
1. ¿Cumplimos los criterios para salir de Etapa X?
2. ¿Los dolores listados justifican pasar a Etapa Y?
3. ¿Qué cambios implica la nueva etapa?

Si NO es momento, explica qué falta.
Si SÍ es momento, confirma y lee las nuevas reglas.
```

## Tags
- Categoría: planning
- Dificultad: intermedio
- Stage: 1, 2, 3
