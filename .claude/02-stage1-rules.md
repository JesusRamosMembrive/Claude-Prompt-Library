# ETAPA 1: PROTOTIPADO - Claude Prompt Library

## Contexto
Estamos PROBANDO si la idea funciona. Prioridad: que copie templates correctamente.

## Reglas obligatorias para ESTE proyecto
- ✅ TODO en 1-2 archivos Python máximo
- ✅ Solo stdlib (pathlib, shutil, sys)
- ✅ Hardcodear paths y placeholders está OK
- ✅ Zero validación compleja (solo lo mínimo)
- ✅ Zero CLI fancy (solo sys.argv)
- ✅ Función simple > Clase

## Prohibido en esta etapa
- ❌ Click/argparse complejo
- ❌ Clases si una función sirve
- ❌ Configuración en archivo
- ❌ Múltiples tipos de templates
- ❌ Validación exhaustiva de inputs
- ❌ Logging sofisticado (print está OK)
- ❌ Manejo de errores complicado

## Estructura permitida en Phase 1
```
claude-prompt-library/
├── .claude/                    # Estos archivos
├── templates/
│   └── basic/
│       └── .claude/            # Los 5 templates
│           ├── 00-project-brief.md
│           ├── 01-current-phase.md
│           ├── 02-stage1-rules.md
│           ├── 02-stage2-rules.md
│           └── 02-stage3-rules.md
├── init_project.py             # EL script (un solo archivo)
├── tests/
│   └── test_full_flow.sh
└── README.md
```

## Criterio de calidad
¿Puedo ejecutar `python init_project.py test` y ver la carpeta creada en <1 minuto? → Si no, demasiado complejo.

## Implementación esperada de init_project.py
```python
# Aproximadamente 50-80 líneas, máximo 100
# Estructura simple:
1. Parsear argumentos (sys.argv)
2. Validar básico (directorio no existe)
3. Copiar templates/basic/ a destino
4. Reemplazar placeholders en archivos
5. Print success message
```

## Salida de esta etapa
Cambiar a Etapa 2 cuando:
- He creado 3+ proyectos usando el script
- Sé qué duele (qué falta, qué sobra)
- Tengo claro qué tipo de templates necesito

## Recordatorio
En Phase 1: Hacer que funcione > Hacer que sea bonito
