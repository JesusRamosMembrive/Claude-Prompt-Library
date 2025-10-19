# Claude Prompt Library

CLI tool para inicializar proyectos con metodología estructurada de desarrollo con Claude Code.

## Estado

**Phase 1: COMPLETO** ✅

Script funcional que copia templates de metodología a proyectos nuevos o existentes.

## Instalación
```bash
git clone [tu-repo]
cd claude-prompt-library
```

## Uso

### Crear proyecto nuevo
```bash
python init_project.py my-new-project
cd my-new-project
```

### Añadir metodología a proyecto existente
```bash
cd my-existing-project
python /path/to/init_project.py .
```

### Coexiste con Claude Code
Si tu proyecto ya usa Claude Code (tiene `.claude/settings.local.json`), el script:
- Añade solo los archivos .md de metodología
- No toca archivos de configuración de Claude Code
- Ambos sistemas funcionan juntos

## Qué incluye

Copia 5 archivos a `.claude/`:
- `00-project-brief.md` - Define qué construyes
- `01-current-phase.md` - Tracking de progreso
- `02-stage1-rules.md` - Reglas de prototipado
- `02-stage2-rules.md` - Reglas de estructuración
- `02-stage3-rules.md` - Reglas de escalado

## Siguiente paso

Lee `SETUP_COMPLETE.md` para entender la metodología completa.

## Desarrollo

Para contribuir o extender:
1. Lee `.claude/` de este proyecto (ejemplo vivo)
2. Sigue `QUICK_START.md`
3. Respeta metodología de 3 etapas

## Roadmap

- [x] Phase 1: CLI básico
- [ ] Phase 2: TBD (basado en uso real)
- [ ] Phase 3: TBD

Próximas features se deciden basadas en dolor real, no especulación.
