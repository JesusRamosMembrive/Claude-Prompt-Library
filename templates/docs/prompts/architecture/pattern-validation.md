# Pattern Validation

## Descripción
Valida si un patrón de diseño es apropiado antes de implementarlo. Evita sobre-ingeniería.

## Prompt
```
Estoy considerando usar el pattern [NOMBRE] para [situación].

ANTES de implementar, valida:

1. ¿Qué problema específico resuelve este pattern?
2. ¿Tengo evidencia REAL de ese problema en mi código actual?
3. ¿Hay solución más simple? (función, dict, clase simple)
4. ¿El pattern es apropiado para mi etapa actual? (ver .claude/02-stageN-rules.md)

Si la respuesta a 2 es NO → propón alternativa más simple.
Si la respuesta a 4 es NO → explica por qué debería esperar.
```

## Tags
- Categoría: architecture
- Dificultad: intermedio
- Stage: 2, 3
