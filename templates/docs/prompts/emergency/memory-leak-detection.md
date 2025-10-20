# Memory Leak Detection

## Descripción
Diagnostica y resuelve problemas de uso excesivo de memoria o memory leaks.

## Prompt
```
PROBLEMA: Uso de memoria crece indefinidamente

SÍNTOMAS:
- ¿Cuánto crece? [MB/hora]
- ¿Cuándo empezó? [fecha/commit]
- ¿Qué operación causa el crecimiento? [acción específica]
- ¿Es reproducible? [siempre/a veces]

INFORMACIÓN DEL SISTEMA:
- Lenguaje/runtime: [Python/Node/etc]
- Memoria inicial: [X MB]
- Memoria después de N operaciones: [Y MB]

ÁREAS SOSPECHOSAS:
- Caches sin límite de tamaño
- Event listeners no removidos
- Referencias circulares
- Archivos/conexiones no cerrados
- Objetos grandes en closures

Necesito:
1. Identificar el leak específico
2. Herramientas para profile memoria
3. Fix que resuelva el leak
4. Cómo verificar que está resuelto
```

## Tags
- Categoría: emergency
- Dificultad: avanzado
- Stage: 2, 3
