# Integration Test Design

## Descripción
Diseña tests de integración que validen que múltiples componentes funcionan juntos correctamente.

## Prompt
```
Necesito tests de integración para [sistema/feature]:

COMPONENTES INVOLUCRADOS:
- [lista de módulos/servicios que interactúan]

Define:
1. **Scope del test**
   - ¿Qué integración específica testear?
   - ¿End-to-end o subsistema?
   - ¿Qué NO incluir en este test?

2. **Setup necesario**
   - ¿BD de prueba?
   - ¿Servicios mock vs reales?
   - ¿Estado inicial requerido?

3. **Escenarios críticos**
   - Happy path completo
   - Errores en puntos de integración
   - Timeouts y retries

4. **Cleanup**
   - ¿Cómo limpiar estado después del test?

Los tests deben ser independientes y determinísticos.
```

## Tags
- Categoría: testing
- Dificultad: avanzado
- Stage: 3
