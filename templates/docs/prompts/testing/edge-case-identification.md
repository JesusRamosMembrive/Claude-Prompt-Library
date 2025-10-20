# Edge Case Identification

## Descripción
Identifica casos borde que deben testearse para asegurar robustez del código.

## Prompt
```
Analiza [función/módulo] e identifica casos borde a testear:

CASOS COMUNES:
- Inputs vacíos ([], "", null, undefined, 0)
- Inputs extremos (muy grande, muy pequeño, negativo)
- Tipos inesperados
- Límites de rangos (off-by-one)
- Condiciones de carrera
- Errores de red/IO
- Datos malformados

Para cada caso identificado:
1. Describe el caso específico
2. Explica qué podría fallar
3. Define comportamiento esperado
4. Propón cómo testearlo
5. Prioriza por probabilidad × impacto

No testear casos ultra-raros (ocurren <1 vez/año).
```

## Tags
- Categoría: testing
- Dificultad: intermedio
- Stage: 2, 3
