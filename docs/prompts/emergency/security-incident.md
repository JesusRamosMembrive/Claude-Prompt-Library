# Security Incident

## Descripción
Respuesta inicial a incidentes de seguridad. Prioriza contención y análisis.

## Prompt
```
INCIDENTE DE SEGURIDAD DETECTADO

TIPO DE INCIDENTE:
- [ ] Acceso no autorizado
- [ ] Data leak/exposure
- [ ] Vulnerabilidad explotada
- [ ] Ataque DoS
- [ ] Otro: [describir]

DETALLES:
- ¿Qué fue afectado? [sistema/datos específicos]
- ¿Cuándo se detectó? [timestamp]
- ¿Cómo se detectó? [alertas/usuario/logs]
- ¿Evidencia? [pegar logs relevantes]

PASOS INMEDIATOS:
1. **Contención**
   - ¿Qué acceso cerrar?
   - ¿Qué servicios desactivar temporalmente?
   - ¿Qué secrets rotar?

2. **Análisis**
   - ¿Cómo ocurrió?
   - ¿Qué vulnerabilidad se explotó?
   - ¿Cuánto daño se hizo?

3. **Comunicación**
   - ¿A quién notificar?
   - ¿Qué decir a usuarios?

4. **Remediación**
   - Fix de la vulnerabilidad
   - Limpieza de daños
   - Prevención de reincidencia

NO implementar fix sin entender el problema completo.
```

## Tags
- Categoría: emergency
- Dificultad: avanzado
- Stage: 2, 3
