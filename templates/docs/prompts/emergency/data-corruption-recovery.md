# Data Corruption Recovery

## Descripción
Plan para recuperar datos corruptos o perdidos. Prioriza minimizar pérdida de datos.

## Prompt
```
DATOS CORRUPTOS/PERDIDOS DETECTADOS

SITUACIÓN:
- ¿Qué datos están afectados? [tabla/archivo/colección]
- ¿Cuántos registros? [cantidad]
- ¿Cuándo ocurrió la corrupción? [timestamp aproximado]
- ¿Cómo se detectó? [error/reporte/validación]

TIPO DE CORRUPCIÓN:
- [ ] Datos perdidos (deleted)
- [ ] Datos incorrectos (wrong values)
- [ ] Relaciones rotas (broken references)
- [ ] Formato inválido (parse errors)
- [ ] Duplicados

BACKUPS DISPONIBLES:
- ¿Hay backup? [sí/no]
- ¿Cuándo es del backup? [timestamp]
- ¿Qué cubre? [alcance]

PLAN DE RECUPERACIÓN:
1. **Evaluar daño**
   - Identificar alcance exacto
   - Listar datos recuperables vs perdidos

2. **Detener la corrupción**
   - ¿Qué proceso está corrompiendo datos?
   - Desactivar hasta resolver

3. **Recuperar datos**
   - Restaurar desde backup (si aplica)
   - Reconstruir desde logs
   - Pedir re-ingreso manual (último recurso)

4. **Validar recuperación**
   - Verificar integridad
   - Validar relaciones
   - Testear con queries conocidos

5. **Prevenir recurrencia**
   - Fix del bug que causó corrupción
   - Añadir validaciones
   - Mejorar backups

Prioridad: NO empeorar la situación.
```

## Tags
- Categoría: emergency
- Dificultad: avanzado
- Stage: 2, 3
