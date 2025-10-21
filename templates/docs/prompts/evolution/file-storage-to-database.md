# File Storage to Database

## Descripción
Cuando almacenar datos en archivos JSON/CSV/pickle ya no es suficiente. Necesitas queries, concurrencia, o volumen justifica una base de datos real.

## Prompt
```
Necesito evolucionar de archivos a base de datos:

SITUACIÓN ACTUAL:
- Almacenamiento: [JSON/CSV/pickle/txt]
- Tamaño de datos: [MB/GB]
- Frecuencia de escritura: [por hora/día]
- Frecuencia de lectura: [por hora/día]

DOLOR ESPECÍFICO:
- [ ] Cargar TODO el archivo para leer un dato
- [ ] Problemas de concurrencia (múltiples writers)
- [ ] Queries complejas (filtros, joins, agregaciones)
- [ ] Archivos muy grandes (>100MB)
- [ ] Corrupción de datos ocasional
- [ ] Backups difíciles/manuales
- [ ] No hay índices (búsquedas lentas)

PREGUNTAS PARA DECIDIR:

1. **¿Realmente necesito BD?**
   - ¿Cuántos registros? [cantidad]
   - ¿Qué queries hago frecuentemente?
   - ¿Múltiples procesos escribiendo?
   - ¿Necesito transacciones?
   - ¿Necesito relaciones entre datos?

2. **¿SQL o NoSQL?**

   **SQL (PostgreSQL, MySQL, SQLite):**
   - Cuándo: Datos estructurados, relaciones, ACID
   - Pros: Queries potentes, integridad, maduro
   - Contras: Schema rígido, escalado vertical

   **NoSQL (MongoDB, Redis, etc):**
   - Cuándo: Schema flexible, escalado horizontal
   - Pros: Rápido para reads simples, schema-less
   - Contras: Menos garantías, queries limitadas

3. **SQLite como paso intermedio**
   - Si: Desarrollo, single-user, <1GB
   - Pros: Zero setup, portátil, SQL completo
   - Contras: No para concurrencia alta

AYÚDAME A DECIDIR:

1. **¿Qué tipo de BD usar?**
   - Considera mi caso de uso específico
   - Complejidad de setup
   - Stage actual del proyecto

2. **Estrategia de migración**
   - ¿Migrar datos históricos o empezar limpio?
   - ¿Mantener archivos como backup/legacy?
   - ¿Script de migración automático?

3. **Estructura de datos**
   - De mi JSON/CSV → tablas/colecciones
   - ¿Qué normalizar?
   - ¿Qué índices crear?

4. **ORM o SQL raw**
   - SQLAlchemy/Django ORM vs psycopg2 raw
   - Trade-off simplicidad vs control

5. **Plan mínimo viable**
   - ¿Qué migrar primero?
   - ¿Cómo validar que funciona?
   - ¿Estrategia de rollback?

Recuerda: SQLite es suficiente para el 95% de casos. No uses PostgreSQL si no lo necesitas.
```

## Tags
- Categoría: evolution
- Dificultad: intermedio
- Stage: Transición 1→2 o 2→3
