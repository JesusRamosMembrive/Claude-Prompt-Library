# Script to API

## Descripción
Cuando tu script CLI funciona bien pero otros necesitan usarlo. Evolucionar a API REST sin perder la funcionalidad CLI.

## Prompt
```
Necesito evolucionar mi script a API:

SITUACIÓN ACTUAL:
- Tengo script CLI que funciona: [descripción]
- Invocación: `python script.py args...`
- Funcionalidad: [qué hace]

DOLOR QUE JUSTIFICA API:
- [ ] Otros proyectos/servicios necesitan usarlo
- [ ] Frontend web necesita acceso
- [ ] Automatización desde otros sistemas
- [ ] Múltiples usuarios concurrentes
- [ ] Necesito auth/permisos
- [ ] Deployment y updates independientes

DECISIONES ARQUITECTÓNICAS:

1. **¿Qué tipo de API?**

   **REST (FastAPI, Flask, Express)**
   - Cuándo: CRUD, recursos, estándar
   - Pros: Universal, simple, bien entendido
   - Contras: Over-fetching, múltiples requests

   **GraphQL**
   - Cuándo: Queries flexibles, frontend complejo
   - Pros: Cliente pide lo que necesita
   - Contras: Complejidad, caching más difícil

   **gRPC**
   - Cuándo: Service-to-service, performance crítico
   - Pros: Rápido, tipado fuerte
   - Contras: No browser-friendly, tooling complejo

   **Para 95% de casos → REST con FastAPI/Flask**

2. **¿Mantener CLI o deprecar?**
   - **Opción A**: CLI llama a API (CLI = cliente ligero)
   - **Opción B**: Shared core logic, CLI y API separados
   - **Opción C**: Deprecar CLI gradualmente

3. **Framework**
   - **FastAPI** (Python): Moderno, async, auto-docs
   - **Flask** (Python): Simple, maduro, más flexible
   - **Express** (Node): Estándar, muchos middlewares

AYÚDAME A DISEÑAR:

1. **Arquitectura**
   - ¿Cómo extraer lógica core del CLI?
   - ¿Qué va en API vs qué queda en cliente?
   - ¿Auth necesaria? (API key, JWT, OAuth)

2. **Endpoints**
   De mi script actual → endpoints REST:
   ```
   Función actual: process_data(input_file, options)
   → POST /api/v1/process
     Body: {data: ..., options: {...}}
   ```

   Lista mis funciones y propón endpoints

3. **Manejo de long-running tasks**
   Si proceso tarda >5seg:
   - Opción A: Webhook cuando complete
   - Opción B: WebSocket con updates
   - Opción C: Polling endpoint (POST → job_id, GET /jobs/{id})

4. **Migración incremental**
   - Paso 1: Extraer core logic a módulo compartido
   - Paso 2: API con 1-2 endpoints críticos
   - Paso 3: CLI usa API internamente
   - Paso 4: Expandir API según necesidad

5. **Deployment**
   - ¿Dónde hostear? (Vercel, Railway, fly.io, VPS)
   - ¿Dockerizar?
   - ¿CI/CD?

6. **Plan mínimo viable**
   - ¿Qué endpoint implementar primero?
   - ¿Cómo testear sin afectar CLI actual?
   - Criterios de éxito

REGLA: Mantén API simple. No añadas features "por si acaso". Añade cuando haya dolor real.
```

## Tags
- Categoría: evolution
- Dificultad: intermedio
- Stage: Transición 1→2 o 2→3
