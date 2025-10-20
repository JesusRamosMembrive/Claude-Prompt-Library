# Dependency Analysis

## Descripción
Analiza dependencias del proyecto (externas e internas) para identificar problemas.

## Prompt
```
Analiza las dependencias en [proyecto]:

DEPENDENCIAS EXTERNAS:
- Lista dependencias instaladas
- ¿Se usan todas? (buscar imports)
- ¿Hay alternativas más simples?
- ¿Hay versiones obsoletas/riesgosas?

DEPENDENCIAS INTERNAS:
- ¿Qué módulos dependen de qué?
- ¿Hay ciclos de dependencias?
- ¿Hay módulos "god" (todos dependen de él)?
- ¿Hay módulos huérfanos (nadie los usa)?

PROBLEMAS COMUNES:
- Dependencia pesada para feature trivial
- Múltiples librerías para mismo propósito
- Dependencias transitivas problemáticas

Propón mejoras concretas con justificación.
```

## Tags
- Categoría: architecture
- Dificultad: avanzado
- Stage: 2, 3
