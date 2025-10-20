# Integration Problem

## Descripción
Para diagnosticar fallos en integraciones con APIs externas, módulos, o servicios.

## Prompt
```
Falla la integración con [módulo/API/servicio]:

PROBLEMA:
- ¿Qué integración? [nombre]
- ¿Qué falla? [error/comportamiento]
- ¿Funcionaba antes? [sí/no/no sé]

CONTEXTO:
- Punto de integración: [archivo:función]
- Formato esperado: [descripción]
- Formato recibido: [descripción]
- Logs/errores:
```
[pegar logs]
```

Necesito:
1. Verificar que entiendo el contrato de la integración
2. Identificar dónde está el desajuste
3. Solución mínima para que funcione
4. Cómo prevenir que se rompa de nuevo

Si es API externa, considera que puede haber cambiado.
```

## Tags
- Categoría: debugging
- Dificultad: intermedio
- Stage: 2, 3