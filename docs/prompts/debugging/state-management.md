# State Management

## Descripción
Para problemas de estado inconsistente, race conditions, o efectos secundarios no deseados.

## Prompt
```
Tengo un problema con estado inconsistente:

SÍNTOMAS:
- ¿Qué dato está mal? [descripción]
- ¿Cuándo aparece? [secuencia de acciones]
- ¿Es reproducible? [siempre/a veces/raro]

ESTADO ESPERADO:
[descripción del estado correcto]

ESTADO ACTUAL:
[descripción del estado incorrecto]

CÓDIGO RELEVANTE:
- Dónde se modifica: [archivo:línea]
- Dónde se lee: [archivo:línea]

Necesito:
1. Identificar dónde se pierde la sincronización
2. Detectar race conditions o efectos secundarios
3. Proponer forma más simple de mantener consistencia
4. Cómo testear que queda arreglado
```

## Tags
- Categoría: debugging
- Dificultad: intermedio
- Stage: 2, 3