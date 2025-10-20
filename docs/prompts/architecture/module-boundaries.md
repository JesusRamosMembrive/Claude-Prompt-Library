# Module Boundaries

## Descripción
Define o valida los límites entre módulos. Previene acoplamiento excesivo.

## Prompt
```
Analiza los límites de módulos en [proyecto]:

OBJETIVO:
Cada módulo debe tener:
- Responsabilidad clara y única
- Interfaz pública bien definida
- Mínimas dependencias externas

PROBLEMAS A DETECTAR:
- Módulos que dependen de detalles internos de otros
- Imports cruzados (A importa B, B importa A)
- Módulo que usa >10 módulos diferentes
- Funcionalidad que no sabe dónde vivir

Para el proyecto actual:
1. Lista módulos existentes y su propósito
2. Identifica dependencias entre módulos
3. Detecta acoplamiento problemático
4. Propón reorganización si es necesario

¿La estructura actual facilita o dificulta los cambios?
```

## Tags
- Categoría: architecture
- Dificultad: avanzado
- Stage: 2, 3
