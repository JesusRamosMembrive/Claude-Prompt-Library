# In-Memory to Distributed

## Descripción
Cuando datos en memoria (dict, variables globales, cache local) ya no son suficientes. Necesitas persistencia, compartir entre procesos, o sobrevivir restarts.

## Prompt
```
Necesito evolucionar de in-memory a solución distribuida:

SITUACIÓN ACTUAL:
- Almacenamiento: [dict, list, variables globales, LRU cache]
- Uso: [cache, session data, shared state]
- Problema: [no persiste, no comparte entre workers, etc]

DOLOR ESPECÍFICO:
- [ ] Datos se pierden al restart
- [ ] No puedo compartir entre múltiples workers/procesos
- [ ] No puedo escalar horizontalmente (múltiples servers)
- [ ] Cache se llena y crashea (sin eviction policy)
- [ ] Race conditions con acceso concurrente
- [ ] No puedo invalidar cache desde otro servicio

CONTEXTO:
- ¿Cuántos workers/servers? [cantidad]
- ¿Tamaño de datos? [MB/GB]
- ¿Necesita persistencia o solo en-memory distribuido?
- ¿Latencia aceptable? [<10ms / <100ms / >1s]

OPCIONES PARA EVALUAR:

**1. Redis** (Más común)
- Cuándo: Cache distribuido, sessions, queues simple
- Pros: Rápido, simple, muchas features, persistence opcional
- Contras: Single-threaded, datos en memoria (caro)
- Casos: Cache, rate limiting, pub/sub, leaderboards

**2. Memcached**
- Cuándo: Solo cache puro, sin features extra
- Pros: Muy simple, muy rápido
- Contras: Solo cache (no pub/sub, no data structures)
- Usar si: Redis es overkill

**3. Database con cache layer**
- PostgreSQL + pgBouncer
- MySQL + query cache
- Cuándo: Ya tienes BD, cache es secundario

**4. Application-level solutions**
- Redis-py con pooling
- Flask-Caching
- Django cache framework

**5. Advanced: Apache Kafka / RabbitMQ**
- Cuándo: Message queues, event streaming
- No es cache, es comunicación entre servicios
- Usar si: Necesitas guarantees, ordering, replay

AYÚDAME A DECIDIR:

1. **¿Qué tecnología usar?**
   Para la mayoría: Redis
   - Fácil setup (docker run redis)
   - Flexible (cache, queues, pub/sub)
   - Buena DX

2. **Estrategia de migración**

   **Paso 1: Abstraer acceso actual**
   ```python
   # Antes
   cache = {}
   value = cache.get(key)

   # Después (abstracción)
   value = cache_backend.get(key)
   ```

   **Paso 2: Implementar backend Redis**
   Mantener in-memory como fallback

   **Paso 3: Feature flag para testing**

   **Paso 4: Migrar tráfico gradualmente**

3. **Patrón Cache-Aside**
   ```
   def get_user(user_id):
       # Try cache first
       cached = redis.get(f"user:{user_id}")
       if cached:
           return cached

       # Cache miss → DB
       user = db.query(user_id)
       redis.setex(f"user:{user_id}", 3600, user)
       return user
   ```

4. **Configuración Redis**
   - Eviction policy: allkeys-lru (más común)
   - Maxmemory: límite para evitar OOM
   - Persistence: RDB si necesitas sobrevivir restarts

5. **Serialización**
   - JSON (universal, slow)
   - Pickle (Python-only, rápido)
   - MessagePack (mejor que JSON)

6. **Plan mínimo viable**
   - Docker compose con Redis local
   - Migrar 1 cache específico primero
   - Medir: hit rate, latencia, memoria
   - Criterios para success

IMPORTANTE: Redis local en Docker es suficiente para empezar. No necesitas Redis Cluster hasta millones de requests.
```

## Tags
- Categoría: evolution
- Dificultad: intermedio/avanzado
- Stage: Transición 2→3
