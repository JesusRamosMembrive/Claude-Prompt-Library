# Risk Analysis

## Descripción
Identifica riesgos técnicos en un proyecto o feature y propone mitigaciones.

## Prompt
```
Analiza riesgos técnicos para [proyecto/feature]:

CONTEXTO:
- ¿Qué estoy construyendo? [descripción]
- ¿Qué tecnologías uso? [lista]
- ¿Hay dependencias externas? [APIs, servicios, etc]
- ¿Cuál es el deadline? [fecha]

CATEGORÍAS DE RIESGO:
1. **Técnicos**
   - Tecnología nueva/desconocida
   - Complejidad subestimada
   - Integraciones complejas
   - Performance/escalabilidad

2. **De dependencies**
   - API externa puede fallar/cambiar
   - Librería con bugs conocidos
   - Servicio de terceros inestable

3. **De scope**
   - Requisitos ambiguos
   - Cambios frecuentes
   - Features mal definidas

Para cada riesgo:
1. Describe el riesgo específico
2. Probabilidad (baja/media/alta)
3. Impacto si ocurre (bajo/medio/alto)
4. Mitigación (¿cómo reducir probabilidad?)
5. Contingencia (¿qué hacer si ocurre?)

Prioriza riesgos con alta probabilidad × alto impacto.
```

## Tags
- Categoría: planning
- Dificultad: intermedio
- Stage: 2, 3
