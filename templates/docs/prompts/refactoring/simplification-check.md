# Simplification Check

## Descripción
Revisa código recién desarrollado para detectar sobre-ingeniería o falta de estructura. Útil después de implementar una feature.

## Prompt
```
Revisa el código que acabamos de desarrollar y evalúa:

OVER-ENGINEERING:
1. ¿Hay abstracciones sin 2+ implementaciones?
2. ¿Hay capas innecesarias?
3. ¿Hay patrones sin justificación clara?
4. ¿Hay configuración para cosas que nunca cambian?

UNDER-ENGINEERING:
1. ¿Código duplicado en 3+ lugares?
2. ¿Funciones de 100+ líneas?
3. ¿Cambios que requieren tocar 5+ archivos?
4. ¿Falta estructura evidente?

Lista cambios específicos con justificación.
NO implementes hasta mi aprobación.
```

## Tags
- Categoría: refactoring
- Dificultad: intermedio
- Stage: 2, 3
