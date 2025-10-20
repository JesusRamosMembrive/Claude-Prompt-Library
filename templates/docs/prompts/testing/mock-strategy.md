# Mock Strategy

## Descripción
Define qué y cómo mockear en tests. Evita over-mocking que hace tests frágiles.

## Prompt
```
Necesito testear [funcionalidad] que tiene dependencias externas.

DEPENDENCIAS:
- [lista de dependencias: BD, APIs, filesystem, etc]

Para cada dependencia, analiza:
1. ¿Debo mockearla?
   - SÍ si: lenta, no determinística, side-effects, requiere setup complejo
   - NO si: rápida, determinística, parte crítica de la lógica
2. ¿Cómo mockearla?
   - Stub (retorna valores fijos)
   - Spy (verifica llamadas)
   - Fake (implementación simplificada)
3. ¿Qué casos cubrir en el mock?
   - Happy path
   - Errores esperados
   - Timeouts/fallos

Propón estrategia específica con ejemplos de código.
```

## Tags
- Categoría: testing
- Dificultad: avanzado
- Stage: 2, 3
