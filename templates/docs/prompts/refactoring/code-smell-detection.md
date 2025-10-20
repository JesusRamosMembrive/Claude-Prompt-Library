# Code Smell Detection

## Descripción
Analiza código existente para detectar patrones problemáticos y sugerir mejoras concretas.

## Prompt
```
Analiza [archivo/función] y detecta code smells:

- God objects (clases con demasiadas responsabilidades)
- Funciones muy largas (>50 líneas)
- Parámetros excesivos (>5)
- Nombres poco claros
- Lógica duplicada
- Acoplamiento fuerte
- Violaciones de principios SOLID

Para cada smell encontrado:
1. Señálalo específicamente
2. Explica por qué es problema
3. Propón solución simple

Prioriza por impacto.
```

## Tags
- Categoría: refactoring
- Dificultad: intermedio
- Stage: 2, 3
