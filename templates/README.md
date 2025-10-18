# Claude Prompt Library

Herramienta para inicializar proyectos con metodología estructurada para desarrollo con Claude Code.

## ¿Qué hace?

Copia templates de archivos `.claude/` a nuevos proyectos para mantener consistencia en el workflow de desarrollo con IA agents.

## Estado actual

**Phase 1** - En desarrollo

Script básico que copia templates a proyectos nuevos.

## Uso rápido (cuando esté implementado)

```bash
python init_project.py my-new-project
cd my-new-project
# Carpeta lista con .claude/ configurado
```

## Estructura del proyecto

```
claude-prompt-library/
├── .claude/              # Metodología para ESTE proyecto
├── templates/
│   └── basic/.claude/    # Templates genéricos
├── init_project.py       # Script principal (Phase 1)
└── tests/
    └── test_full_flow.sh # Tests de integración
```

## Desarrollo

Este proyecto sigue su propia metodología:

1. Lee `.claude/00-project-brief.md` para entender el objetivo
2. Lee `.claude/01-current-phase.md` para saber dónde estamos
3. Lee `.claude/02-stageN-rules.md` para las reglas actuales

## Roadmap

- [x] Phase 0: Setup de proyecto
- [ ] Phase 1: Template copier básico
- [ ] Phase 2: Biblioteca de prompts
- [ ] Phase 3: Múltiples tipos de templates
- [ ] Phase 4: Interactive init
- [ ] Phase 5: Prompt insertion

## Filosofía

Incremental, simple, práctico. Cada fase añade valor real, no complejidad especulativa.
