# Project Brief: Claude Prompt Library

## ¿Qué estoy construyendo?
Una herramienta CLI para inicializar proyectos con estructura `.claude/` correcta y acceder a biblioteca de prompts reutilizables.

## ¿Cuál es el caso de uso mínimo?
Usuario ejecuta `python init_project.py my-new-project` → se crea carpeta `my-new-project/` con estructura `.claude/` completa y lista para usar.

## ¿Qué NO voy a hacer en Phase 1?
- [ ] Múltiples tipos de templates (solo uno básico)
- [ ] CLI con argparse/click (solo argumentos simples)
- [ ] Validación de inputs sofisticada
- [ ] Interactive prompts (stdin)
- [ ] Biblioteca de prompts (solo templates)
- [ ] Configuración persistente
- [ ] Tests unitarios (solo test_full_flow.sh)
- [ ] Instalación con pip
- [ ] Documentación extensa

## Criterio de éxito de Phase 1
- [ ] Ejecuto `python init_project.py test-project`
- [ ] Se crea carpeta `test-project/.claude/` con 5 archivos
- [ ] Los archivos tienen placeholders reemplazados correctamente
- [ ] Puedo abrir Claude Code en esa carpeta y empezar a trabajar
- [ ] `test_full_flow.sh` pasa sin errores

## Tipo de proyecto
CLI tool / Developer tool

## Stack tentativo
- Python 3.10+ (lo que ya tengo)
- stdlib únicamente (Path, shutil, argparse básico)
- Bash para tests
