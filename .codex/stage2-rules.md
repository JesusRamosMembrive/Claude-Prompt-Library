# ETAPA 2: ESTRUCTURACIÓN — Stage-Aware Development

## Contexto
El prototipo funciona y ya hay usuarios/proyectos reales. Necesitamos orden para crecer sin caos, pero seguimos evitando arquitectura futura.

## Dolor que justifica esta etapa
- Se requieren múltiples tipos de plantilla o variantes.
- El script principal supera ~150 LOC y mezcla demasiadas responsabilidades.
- Necesitamos reutilizar lógica (p. ej., reemplazo de placeholders) en varios puntos.
- Los tests manuales son frecuentes y empezamos a automatizarlos.

## Reglas obligatorias
- ✅ Mantener el número de archivos en 5-7 máximo.
- ✅ Separar responsabilidades por módulo (gestión de templates, CLI, utilidades).
- ✅ Sólo introducir clases si hay estado o se usa en múltiples lugares.
- ✅ Documentar el flujo y decisiones clave en `.claude/01-current-phase.md`.

## Patrón de estructura sugerido
```
<project>/
├── init_project.py           # Punto de entrada liviano
├── src/                      # Opcional, si supera 200 LOC
│   ├── template_manager.py
│   ├── placeholders.py
│   └── cli.py
├── templates/
├── docs/
└── tests/
```

## Permitido (con justificación concreta)
- ✅ CLI con argparse si existen 3+ flags/argumentos.
- ✅ Helpers reutilizables para placeholders/logging.
- ✅ Tests automatizados para los casos principales.
- ✅ Configuración simple (JSON/TOML) si evitas duplicar información.

## Sigue prohibido
- ❌ Sistemas de plugins extensibles.
- ❌ Bases de datos o almacenes externos.
- ❌ Frameworks de inyección de dependencias.
- ❌ “Por si acaso” generalizaciones.

## Salida esperada
Pasamos a Etapa 3 sólo cuando:
- Usuarios externos dependen del proyecto.
- Hay solicitudes de extensibilidad reales (no hipotéticas).
- Se necesitan integraciones con otras herramientas o CI/CD.

## Recordatorio
Cada añadido debe atacar un dolor vigente. Antes de codificar, describe el problema concreto que se resuelve.
