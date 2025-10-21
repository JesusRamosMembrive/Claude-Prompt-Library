# Subprocess to Background Jobs

## Descripción
Cuando usas subprocess y pierdes visibilidad del progreso. Necesitas evolucionar a una solución que permita tracking, cancelación, y mejor control del proceso.

## Prompt
```
Necesito evolucionar de subprocess a background jobs con tracking:

SITUACIÓN ACTUAL:
- Uso subprocess.run() o subprocess.Popen()
- Proceso: [descripción del análisis/tarea]
- Problema: No puedo trackear progreso, solo sé cuándo termina
- Duración típica: [tiempo que tarda]

DOLOR ESPECÍFICO:
- [ ] No puedo mostrar % completado
- [ ] No puedo cancelar proceso en marcha
- [ ] No puedo ejecutar múltiples en paralelo
- [ ] No puedo reintentar si falla
- [ ] No hay logs centralizados
- [ ] Bloquea el programa principal

CONTEXTO:
- Lenguaje: [Python/Node/etc]
- Frecuencia de ejecución: [cada X tiempo]
- ¿Necesita correr en background persistente? [sí/no]
- ¿Múltiples workers? [sí/no/cuántos]
- ¿Necesita sobrevivir restart de app? [sí/no]

OPCIONES PARA EVALUAR:

1. **threading.Thread** (Python)
   - Cuándo: Procesos I/O bound, misma máquina
   - Pros: Simple, no requiere deps extra
   - Contras: GIL limita CPU-bound, no persistente

2. **multiprocessing.Process** (Python)
   - Cuándo: Procesos CPU-bound, misma máquina
   - Pros: Bypasea GIL, bueno para cálculos
   - Contras: Mayor overhead, no compartir memoria fácil

3. **asyncio + subprocess** (Python)
   - Cuándo: Múltiples procesos I/O, asyncio ya en uso
   - Pros: Eficiente para muchos procesos concurrentes
   - Contras: Complejidad de async/await

4. **Celery**
   - Cuándo: Producción, múltiples workers, necesita persistencia
   - Pros: Robusto, retry, scheduling, monitoring
   - Contras: Requiere Redis/RabbitMQ, setup complejo

5. **RQ (Redis Queue)**
   - Cuándo: Celery es overkill, pero necesitas queues
   - Pros: Más simple que Celery
   - Contras: Solo Redis, menos features

6. **APScheduler**
   - Cuándo: Necesitas scheduling más que queues
   - Pros: Simple para tareas programadas
   - Contras: No es un sistema de queues completo

AYÚDAME A DECIDIR:

1. **¿Qué opción es apropiada para mi caso?**
   - Considera: complejidad vs necesidades
   - Stage actual del proyecto
   - Si voy a escalar en futuro

2. **Estrategia de migración**
   - ¿Puedo migrar incremental?
   - ¿Cómo mantener subprocess como fallback?
   - ¿Qué cambios requiere en arquitectura?

3. **Tracking de progreso**
   - ¿Cómo el subprocess reporta %?
   - ¿Parsear stdout en tiempo real?
   - ¿Archivo de estado compartido?
   - ¿Base de datos?

4. **Plan mínimo viable**
   - ¿Qué implementar primero?
   - ¿Qué defer para después?
   - ¿Cómo validar que funciona mejor?

NO sobre-ingeniería: propón lo MÁS SIMPLE que resuelva el dolor HOY.
```

## Tags
- Categoría: evolution
- Dificultad: intermedio
- Stage: Transición 1→2
