# Sync to Async

## Descripción
Cuando código síncrono bloquea tu aplicación y necesitas async/await. Decisión de cuándo la complejidad de async se justifica.

## Prompt
```
Necesito evaluar si migrar de sync a async:

SITUACIÓN ACTUAL:
- Lenguaje: [Python/JavaScript/etc]
- Operaciones bloqueantes: [APIs, DB, IO]
- Problema: [requests bloquean, no escala, etc]

DOLOR ESPECÍFICO:
- [ ] Requests HTTP bloquean el programa
- [ ] No puedo hacer múltiples requests concurrentes
- [ ] UI se congela durante operaciones I/O
- [ ] Throughput bajo (pocas req/seg)
- [ ] Workers/threads no escalan suficiente

ANTES DE MIGRAR, CONSIDERA:

**¿REALMENTE necesito async?**
- Threading/multiprocessing ya lo intenté?
- ¿Es I/O bound o CPU bound? (async solo ayuda con I/O)
- ¿Cuántas operaciones concurrentes necesito?
- ¿Mi equipo entiende async/await?

**Alternativas más simples:**
1. **ThreadPoolExecutor** (Python)
   - Más simple que async
   - Suficiente para 10-100 requests concurrentes

2. **Conexiones concurrentes sin async**
   - grequests (Python)
   - Promise.all() (JavaScript ya async)

OPCIONES ASYNC:

**Python:**
- `asyncio` + `aiohttp` para HTTP
- `asyncio` + `asyncpg` para PostgreSQL
- `httpx` (sync y async en misma API)

**JavaScript/Node:**
- Ya es async por defecto
- Usar async/await en lugar de callbacks

**Rust:**
- `tokio` o `async-std`

AYÚDAME A DECIDIR:

1. **¿Vale la pena la complejidad?**
   - Benchmarks: ¿cuánto mejora realmente?
   - Costo: código más complejo, debugging más difícil
   - ¿Hay pain points específicos que async resuelve?

2. **Estrategia de migración**
   - ¿Migrar todo o solo partes críticas?
   - ¿Puedo tener código sync y async conviviendo?
   - ¿Qué librerías cambiar? (requests → aiohttp)

3. **Patrones async**
   - gather() vs create_task() vs TaskGroup
   - Cómo manejar errores en operaciones concurrentes
   - Límites de concurrencia (no abrir 10000 conexiones)

4. **Testing async**
   - pytest-asyncio
   - Mocks de operaciones async

5. **Plan mínimo viable**
   - ¿Qué función migrar primero?
   - ¿Cómo medir mejora?
   - Criterios para rollback si no vale la pena

IMPORTANTE: Async añade complejidad significativa. Solo hazlo si el dolor es REAL y alternativas simples no funcionan.
```

## Tags
- Categoría: evolution
- Dificultad: avanzado
- Stage: Transición 2→3
