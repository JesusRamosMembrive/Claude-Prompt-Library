# Technical Debt Assessment

## Descripción
Evalúa la deuda técnica acumulada y prioriza qué pagar primero.

## Prompt
```
Analiza la deuda técnica en [proyecto/módulo]:

CATEGORÍAS DE DEUDA:
1. **Code debt** (código difícil de mantener)
   - Código duplicado
   - Funciones muy largas
   - Nombres confusos
   - Tests faltantes

2. **Architecture debt** (decisiones que dificultan cambios)
   - Acoplamiento fuerte
   - Responsabilidades mezcladas
   - Dependencias problemáticas

3. **Documentation debt** (falta contexto)
   - Código sin comentarios críticos
   - README desactualizado
   - Decisiones no documentadas

Para cada deuda identificada:
1. Describe el problema específico
2. ¿Cuánto duele HOY? (1-10)
3. ¿Cuánto dolerá en 6 meses? (1-10)
4. Esfuerzo para resolver (horas)
5. Prioridad = (dolor futuro × 2 + dolor actual) / esfuerzo

Propón plan para pagar las 3 deudas de mayor prioridad.
```

## Tags
- Categoría: planning
- Dificultad: intermedio
- Stage: 2, 3
