# Naming Improvement

## Descripción
Mejora los nombres de variables, funciones, y clases para que sean más descriptivos y consistentes.

## Prompt
```
Revisa los nombres en [archivo/módulo] y sugiere mejoras:

PROBLEMAS A DETECTAR:
- Nombres de 1-2 letras (excepto i, j en loops)
- Nombres genéricos (data, info, manager, handler)
- Nombres inconsistentes (getUserData vs fetchUserInfo)
- Nombres que no reflejan el propósito real
- Abreviaciones no estándar
- Nombres con typos

Para cada nombre problemático:
1. Señala la ubicación
2. Explica por qué el nombre es confuso
3. Propón nombre mejor que sea:
   - Descriptivo
   - Consistente con el resto del código
   - No demasiado largo (max 4 palabras)
4. Lista impacto del cambio (cuántas referencias)

Prioriza cambios con mayor impacto en claridad.
```

## Tags
- Categoría: refactoring
- Dificultad: básico
- Stage: 2, 3
