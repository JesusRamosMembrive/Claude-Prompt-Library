# GUÍA DE INICIO - Claude Prompt Library

## Para empezar a desarrollar ESTE proyecto

### 1. Abre Claude Code en esta carpeta

### 2. Primer prompt (copia y pega):

```
Hola. Voy a trabajar en el proyecto Claude Prompt Library.

IMPORTANTE: Primero planificamos, luego implementamos paso a paso.

Por favor, lee estos archivos en orden:
1. .claude/00-project-brief.md
2. .claude/01-current-phase.md  
3. .claude/02-stage1-rules.md

Después de leerlos, responde:
- ¿Entiendes el objetivo del proyecto?
- ¿Entiendes que estamos en ETAPA 1 (prototipado)?
- ¿Entiendes las reglas de esta etapa?

NO escribas código todavía. Espera mi confirmación.
```

### 3. Después de que Claude confirme, pide el plan:

```
Perfecto. Ahora necesito que me propongas la estructura MÍNIMA para Phase 1.

Recuerda las restricciones:
- Máximo 3 archivos
- Solo stdlib de Python
- Lo MÁS SIMPLE que funciona

Dame SOLO:
1. Lista de archivos que crearías
2. Responsabilidad de cada archivo en 1 frase
3. Flujo de ejecución en 3-4 pasos

NO implementes aún. Espera mi aprobación.
```

### 4. Revisa el plan y aprueba (o pide cambios)

### 5. Implementación iterativa:

```
Aprobado. Procede con la implementación.

PERO: implementa UN archivo a la vez.
Empieza por init_project.py.
Espera mi OK antes de cualquier otro archivo.
```

### 6. Después de cada archivo, haz review:

```
Review de [nombre_archivo]:

¿Cumple las reglas de Etapa 1?
- ¿Algo innecesariamente complejo?
- ¿Alguna abstracción que no necesitamos?
- ¿Es lo MÁS SIMPLE que funciona?

[Da feedback específico o aprueba]
```

### 7. Cuando todo funcione, crea el test:

```
Ahora crea tests/test_full_flow.sh

Debe:
1. Sección "PHASE 1: Template Copier"
2. Ejecutar init_project.py con proyecto de prueba
3. Verificar que archivos existen
4. Verificar que placeholders están reemplazados
5. Usar `set -e` (falla al primer error)
6. Incluir cleanup al final
```

### 8. Cierre de sesión:

```
Antes de terminar, actualiza .claude/01-current-phase.md

En "Decisiones tomadas", añade:
- Qué implementamos hoy
- Qué funcionó bien
- Qué NO hicimos y por qué

En "Próxima sesión":
- Qué sería lo siguiente lógico
```

## Prompts de emergencia

### Si Claude se pasa de simple:
```
STOP. Veo estos problemas concretos:
- [lista problemas: duplicación, funciones largas, etc.]

Propón la estructura MÍNIMA que resuelve estos problemas.
Espera mi aprobación.
```

### Si Claude over-engineerea:
```
STOP. Acabas de crear [clase/abstracción].

¿Qué problema ACTUAL resuelve esto?

Si incluye "podría", "futuro", "por si acaso" → ELIMÍNALO.

Muestra la versión más simple que resuelve SOLO lo de HOY.
```

### Checkpoint de etapa:
```
Checkpoint: Revisa el código actual contra .claude/02-stage1-rules.md

Lista:
1. Qué está bien
2. Qué sobra (sobre-ingeniería)
3. Qué falta (bajo-ingeniería)

NO hagas cambios, solo análisis.
```

## Recordatorios

- Claude Code nunca implementa sin que apruebes el plan primero
- Un archivo a la vez
- Checkpoints frecuentes
- Actualiza current-phase.md al final de cada sesión
