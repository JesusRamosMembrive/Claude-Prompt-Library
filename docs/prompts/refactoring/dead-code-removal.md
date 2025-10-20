# Dead Code Removal

## Descripción
Identifica código no utilizado, comentado, o imports innecesarios que pueden eliminarse de forma segura.

## Prompt
```
Analiza el proyecto/archivo y encuentra código muerto:

BUSCAR:
- Funciones/clases nunca llamadas
- Imports no utilizados
- Variables declaradas pero no usadas
- Código comentado (>10 líneas)
- Parámetros que no se usan
- Archivos completos sin referencias

Para cada caso:
1. Señala el código muerto específico
2. Verifica que NO se usa (grep, referencias)
3. Evalúa si es seguro eliminar
4. Propón plan de eliminación segura

Si hay dudas sobre si se usa → NO eliminar, marcar con TODO.
```

## Tags
- Categoría: refactoring
- Dificultad: básico
- Stage: 2, 3
