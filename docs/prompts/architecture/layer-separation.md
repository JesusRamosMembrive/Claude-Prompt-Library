# Layer Separation

## Descripción
Evalúa si las capas de la aplicación (presentación, lógica, datos) están bien separadas o hay violaciones.

## Prompt
```
Analiza la separación de capas en [módulo/proyecto]:

CAPAS ESPERADAS:
- Presentación/UI (interfaz usuario, CLI, API endpoints)
- Lógica de negocio (reglas, algoritmos, validaciones)
- Acceso a datos (BD, archivos, APIs externas)

VIOLACIONES A DETECTAR:
- UI que accede directamente a datos (sin capa intermedia)
- Lógica de negocio en capa de presentación
- Acceso a datos que contiene lógica de negocio
- Dependencias circulares entre capas

Para cada violación:
1. Señala el código específico
2. Explica qué capa debería manejar eso
3. Propón reestructuración simple
4. Evalúa urgencia del cambio

Solo propón cambios si el dolor es real (no teórico).
```

## Tags
- Categoría: architecture
- Dificultad: avanzado
- Stage: 2, 3
