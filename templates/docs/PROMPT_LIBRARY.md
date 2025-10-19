# Biblioteca de Prompts - Semilla

Colección de prompts útiles para diferentes situaciones de desarrollo.

*Nota: Esta es la semilla. En Phase 2 se organizará en carpetas por categoría.*

---

## DEBUGGING

### Stuck in Loop
```
Estoy atascado en este problema: [descripción]

He intentado:
- [intento 1]
- [intento 2]

Contexto:
- Archivo: [nombre]
- Líneas: [rango]
- Error: [mensaje]

Necesito que:
1. Identifiques el problema raíz
2. Expliques POR QUÉ ocurre
3. Propongas la solución MÁS SIMPLE
4. NO implementes hasta que yo apruebe

Si necesitas ver más código, pídemelo.
```

### Error Oscuro
```
Tengo este error y no entiendo qué significa:

```
[pegar error completo]
```

Contexto:
- ¿Qué estaba haciendo? [acción]
- ¿Qué esperaba? [resultado esperado]
- ¿Qué pasó? [resultado actual]

Explícame:
1. Qué significa este error en español claro
2. Qué parte del código lo causa
3. Cómo solucionarlo
```

---

## REFACTORING

### Simplification Check
```
Revisa el código que acabamos de desarrollar y evalúa:

OVER-ENGINEERING:
1. ¿Hay abstracciones sin 2+ implementaciones?
2. ¿Hay capas innecesarias?
3. ¿Hay patrones sin justificación clara?
4. ¿Hay configuración para cosas que nunca cambian?

UNDER-ENGINEERING:
1. ¿Código duplicado en 3+ lugares?
2. ¿Funciones de 100+ líneas?
3. ¿Cambios que requieren tocar 5+ archivos?
4. ¿Falta estructura evidente?

Lista cambios específicos con justificación.
NO implementes hasta mi aprobación.
```

### Code Smell Detection
```
Analiza [archivo/función] y detecta code smells:

- God objects (clases con demasiadas responsabilidades)
- Funciones muy largas (>50 líneas)
- Parámetros excesivos (>5)
- Nombres poco claros
- Lógica duplicada
- Acoplamiento fuerte
- Violaciones de principios SOLID

Para cada smell encontrado:
1. Señálalo específicamente
2. Explica por qué es problema
3. Propón solución simple

Prioriza por impacto.
```

---

## ARCHITECTURE

### Design Decision
```
Necesito decidir entre estas opciones para [problema]:

OPCIÓN A: [descripción]
Pros: [lista]
Contras: [lista]

OPCIÓN B: [descripción]
Pros: [lista]
Contras: [lista]

Contexto:
- Estamos en ETAPA [1/2/3]
- Tamaño del proyecto: [pequeño/mediano/grande]
- Complejidad actual: [descripción]

Ayúdame a decidir considerando:
1. Simplicidad
2. Mantenibilidad
3. Reglas de la etapa actual
4. Dolor que resuelve HOY (no futuro)
```

### Pattern Validation
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

---

## TESTING

### Test Strategy
```
Necesito crear tests para [funcionalidad].

Contexto:
- Fase actual: [1/2/3]
- Complejidad: [simple/media/alta]
- Dependencias externas: [lista]

Propón:
1. Qué testear (casos críticos)
2. Qué NO testear aún (overkill para la fase)
3. Estructura de test_full_flow.sh para esta fase
4. Mocks necesarios (si aplica)

Recuerda: En Phase 1, solo test_full_flow.sh end-to-end.
```

---

## PLANNING

### Feature Planning
```
Quiero añadir: [feature]

ANTES de implementar, ayúdame a planificar:

1. ¿Es apropiado para mi fase actual?
   - Revisar: .claude/01-current-phase.md
   - Revisar: .claude/00-project-brief.md (¿está en deferred?)

2. ¿Cuál es la implementación MÁS SIMPLE?
   - Sin abstracciones prematuras
   - Sin "preparar para el futuro"

3. ¿Qué archivos debo modificar?
   - Lista mínima de archivos afectados

4. ¿En qué orden implementar?
   - Pasos específicos, uno a la vez

Dame un plan. NO implementes hasta mi aprobación.
```

### Phase Transition Check
```
Creo que es momento de cambiar de ETAPA [X] a ETAPA [Y].

Evidencia:
- [dolor 1]
- [dolor 2]
- [dolor 3]

Revisa los criterios en .claude/02-stageX-rules.md

Responde:
1. ¿Cumplimos los criterios para salir de Etapa X?
2. ¿Los dolores listados justifican pasar a Etapa Y?
3. ¿Qué cambios implica la nueva etapa?

Si NO es momento, explica qué falta.
Si SÍ es momento, confirma y lee las nuevas reglas.
```

---

## COMMUNICATION

### Explain Like I'm 5
```
Explícame [concepto técnico] como si tuviera 5 años.

Usa:
- Analogías simples
- Sin jerga técnica
- Ejemplos concretos
- Máximo 5 frases

Luego, explícalo técnicamente pero claro.
```

### Documentation Request
```
Documenta [módulo/función/clase]:

Incluye:
1. ¿Qué hace? (1 frase)
2. ¿Por qué existe? (problema que resuelve)
3. ¿Cómo se usa? (ejemplo mínimo)
4. ¿Qué NO hace? (limitaciones/scope)

Formato: Docstring en el código.
Longitud: Concisa, sin obviedades.
```

---

## EMERGENCY

### Rollback
```
URGENTE: Necesito revertir los últimos cambios.

Estado actual:
- [qué se rompió]
- [último commit que funcionaba]

Ayúdame a:
1. Identificar qué cambios causan el problema
2. Revertir de forma segura
3. Verificar que todo vuelve a funcionar

NO hagas cambios automáticamente, guíame paso a paso.
```

### Production Bug
```
BUG EN PRODUCCIÓN:

Síntomas: [descripción]
Cuándo empezó: [tiempo]
Frecuencia: [siempre/a veces/raro]
Afecta a: [usuarios/funcionalidad]

Logs/errores:
```
[pegar logs]
```

Necesito:
1. Diagnóstico rápido del problema
2. Workaround temporal si existe
3. Fix mínimo que resuelva el bug
4. Qué testear antes de deployar

Prioridad: VELOCIDAD y SEGURIDAD sobre elegancia.
```

---

## NOTAS DE USO

1. Estos prompts son **templates** - personalízalos según tu situación
2. Añade contexto específico de tu proyecto
3. Siempre referencia archivos relevantes cuando sea necesario
4. Recuerda: Claude Code necesita aprobar el plan antes de implementar

## EXPANSIÓN FUTURA (Phase 2)

Esta lista se organizará en:
```
prompts/
├── debugging/
├── refactoring/
├── architecture/
├── testing/
├── planning/
├── communication/
└── emergency/
```

Cada prompt en su propio archivo `.md` con metadata (tags, fase, dificultad).
