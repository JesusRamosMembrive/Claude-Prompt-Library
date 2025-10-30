# ETAPA 1: PROTOTIPADO — Stage-Aware Development

## Contexto
Estamos validando la idea más simple posible. Prioridades: velocidad y feedback temprano. Toda complejidad extra se pospone.

## Reglas obligatorias
- ✅ Máx. 1-2 archivos principales (Python u otro lenguaje dominante)
- ✅ Sólo stdlib / dependencias críticas
- ✅ Hardcodes aceptables mientras aceleren la validación
- ✅ Flujos lineales y funciones pequeñas

## Prohibido en esta etapa
- ❌ Frameworks complejos o CLI avanzados
- ❌ Clases/abstracciones si una función lo resuelve
- ❌ Configuración persistente o plugins
- ❌ Manejo de errores elaborado sin necesidad evidente
- ❌ Tests extensos (sólo happy path crítico si agrega valor)

## Estructura recomendada
```
<project>/
├── init_project.py           # Script principal simple
├── templates/                # Copia directa sin lógica adicional
└── README.md                 # Instrucciones mínimas
```

## Criterio de calidad
> ¿Puedo ejecutar el script principal y obtener el resultado esperado en < 1 minuto?  
> Si la respuesta es no, probablemente estamos añadiendo complejidad innecesaria.

## Cuándo pasar a Etapa 2
- Se crearon ≥3 proyectos con el flujo actual.
- Existen dolores claros: múltiples tipos de plantilla, placeholders repetitivos, necesidades de organización básica.
- Hay evidencia de uso continuo que justifica inversión adicional.

## Recordatorio
Prefiere soluciones descartables a riesgo de nunca validar la idea. Lo perfecto es enemigo de lo útil.
