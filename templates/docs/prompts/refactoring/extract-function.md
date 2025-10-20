# Extract Function

## Descripción
Para identificar oportunidades de extraer funciones y reducir complejidad. Útil cuando las funciones son muy largas.

## Prompt
```
Analiza [archivo/función] para identificar oportunidades de extraer funciones:

CRITERIOS:
- Bloques de código que hacen algo específico y claro
- Código que se repite 2+ veces
- Secciones con comentarios explicativos (el comentario es el nombre de la función)
- Niveles de indentación profundos (>3)

Para cada oportunidad:
1. Señala el bloque de código
2. Propón nombre descriptivo para la función
3. Identifica parámetros y valor de retorno
4. Explica qué mejora esto

Solo sugiere extracciones que mejoren la legibilidad REALMENTE.
```

## Tags
- Categoría: refactoring
- Dificultad: básico
- Stage: 2, 3
