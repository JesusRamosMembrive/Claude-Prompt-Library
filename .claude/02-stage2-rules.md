# ETAPA 2: ESTRUCTURACIÓN - Claude Prompt Library

## Contexto
Script básico funciona. Ahora añadimos estructura para múltiples templates y organización.

## Dolor que justifica entrar en Etapa 2
- Quiero diferentes tipos de templates (cli, web-api, robot, etc.)
- El script está creciendo y hace varias cosas sin organización
- Necesito reutilizar lógica de placeholder replacement
- Tests están creciendo y necesitan estructura

## Reglas obligatorias
- ✅ Máximo 5-7 archivos
- ✅ Separar por responsabilidades claras
- ✅ Clases solo si hay estado a gestionar
- ✅ Preguntar antes de añadir: abstracciones, interfaces

## Estructura permitida en Phase 2+
```
claude-prompt-library/
├── .claude/
├── templates/
│   ├── basic/
│   ├── cli-tool/
│   ├── web-api/
│   └── robot-control/
├── prompts/                    # Nueva: biblioteca de prompts
│   ├── debugging/
│   ├── refactoring/
│   └── architecture/
├── src/                        # Solo si >200 líneas de código
│   ├── template_manager.py    # Si múltiples templates
│   ├── placeholder.py          # Si lógica compleja
│   └── cli.py                  # Si UI crece
├── init_project.py             # Mantener como entry point
├── tests/
│   └── test_full_flow.sh
└── README.md
```

## Permitido (con justificación)
- ✅ Clase TemplateManager si gestionas 3+ tipos de templates
- ✅ Separar módulos si cada uno tiene 50+ líneas
- ✅ CLI con argparse si tienes 5+ opciones
- ✅ Función para placeholder replacement si se usa en 3+ lugares

## Prohibido todavía
- ❌ Plugin system
- ❌ Config file complejo
- ❌ Database
- ❌ API REST
- ❌ Factory patterns sin 3+ implementaciones

## Patterns que PODRÍAN aparecer
- **Strategy**: Si tienes diferentes tipos de templates con lógica diferente
- **Facade**: Si necesitas simplificar interacción con templates + prompts
- **Template Method** (no el de templates, el pattern): Si hay secuencia común de pasos

## Salida de esta etapa
Cambiar a Etapa 3 cuando:
- Herramienta en uso real por varias personas
- Necesitas extensibilidad real (usuarios añaden sus templates)
- Integración con otras herramientas (IDE, CI/CD)

## Recordatorio
Solo añadir estructura que resuelve dolor actual, no futuro.
