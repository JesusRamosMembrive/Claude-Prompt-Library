# Test Strategy

## Descripción
Define qué y cómo testear según el stage actual del proyecto. Evita over-testing prematuro.

## Prompt
```
Necesito crear tests para [funcionalidad].

Contexto:
- Fase actual: [1/2/3]
- Complejidad: [simple/media/alta]
- Dependencias externas: [lista]

Propón:
1. Qué testear (casos críticos)
2. Qué NO testear aún (overkill para la fase)
3. Estructura de test_full_flow.sh para esta fase
4. Mocks necesarios (si aplica)

Recuerda: En Phase 1, solo test_full_flow.sh end-to-end.
```

## Tags
- Categoría: testing
- Dificultad: intermedio
- Stage: 1, 2, 3
