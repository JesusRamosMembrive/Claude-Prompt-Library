# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

---

## Project Overview

This repository contains **two integrated systems**:

### 1. Stage-Aware Development Framework
CLI tools for evolutionary software development that prevent over-engineering:
- `init_project.py` - Initialize projects with `.claude/` tracking structure
- `assess_stage.py` - Analyze codebases and recommend Stage 1/2/3
- `stage_config.py` - Core stage detection algorithms and thresholds
- `stage_init/` - Modular initialization logic (CLI, templates, updaters)

### 2. Code Map Backend
FastAPI service for code analysis and quality tooling:
- `code_map/server.py` - FastAPI application factory
- `code_map/analyzer.py` - Multi-language code parsing (Python, JS/TS, HTML)
- `code_map/linters/pipeline.py` - Automated linter execution (ruff, mypy, bandit, pytest)
- `code_map/integrations/ollama_service.py` - AI-powered code insights via Ollama
- `code_map/api/` - REST endpoints for analysis, graphs, linters, settings

---

## Commands Reference

### Stage-Aware Framework

```bash
# Initialize new project
python init_project.py my-new-project

# Add framework to existing project (with auto-detection)
python init_project.py --existing /path/to/project

# Detect project stage only
python assess_stage.py /path/to/project
# OR
python init_project.py --detect-only /path/to/project

# Preview changes without writing
python init_project.py my-project --dry-run

# Configure for specific agent (claude, codex, or both)
python init_project.py my-project --agent=claude
```

### Code Map Backend

```bash
# Run development server
python -m code_map.cli run --root /path/to/project
# OR
python -m code_map --root /path/to/project

# Access API docs at: http://localhost:8000/docs
```

### Testing

```bash
# Run all tests
pytest

# Specific test suites
pytest tests/test_linters_pipeline.py
pytest tests/test_analysis_engine.py
pytest tests/test_stage_config.py

# With coverage
pytest --cov=code_map --cov=stage_init

# Full flow test (stage framework)
bash tests/test_full_flow.sh
```

---

## Architecture

### High-Level Structure

**Stage Framework (Standalone CLI)**
- Pure Python 3.10+ using only stdlib (no external dependencies)
- `init_project.py` → delegates to `stage_init/` modules
- `assess_stage.py` → uses `stage_config.py` for detection logic
- Templates in `templates/basic/.claude/` and `templates/docs/`

**Code Map (Web Service)**
- FastAPI async application
- Multi-language analyzers using tree-sitter, esprima, BeautifulSoup
- Automated linter pipeline with configurable tools
- Optional Ollama integration for AI insights
- File watching and change scheduling

### Key Integrations

**Stage Detection in Code Map:**
- `code_map/stage_toolkit.py` provides stage assessment via `assess_stage.py`
- `code_map/api/stage.py` exposes REST endpoint: `POST /api/stage/assess`
- Uses symbol index from code analysis for deeper insights when available

**Linter Pipeline Configuration:**
Set environment variables before starting the API:
```bash
CODE_MAP_DISABLE_LINTERS=1                      # Skip linters entirely
CODE_MAP_LINTERS_TOOLS=ruff,pytest              # Limit to specific tools
CODE_MAP_LINTERS_MAX_PROJECT_FILES=2000         # Skip if too many files
CODE_MAP_LINTERS_MAX_PROJECT_SIZE_MB=200        # Skip if project too large
CODE_MAP_LINTERS_MIN_INTERVAL_SECONDS=300       # Minimum seconds between runs
```

**Ollama Integration:**
- `code_map/integrations/ollama_service.py` - Core service
- `code_map/insights/ollama_service.py` - Insights-specific wrapper
- Configurable via settings: model, base URL, focus areas
- Provides AI-powered code analysis and suggestions

### Directory Structure

```
/
├── init_project.py              # Stage framework CLI entry point
├── assess_stage.py              # Stage detection CLI
├── claude_assess.py             # Deep analysis helper
├── stage_config.py              # Stage detection algorithms & thresholds
├── stage_init/                  # Modular initialization logic
│   ├── cli.py                   # Argument parsing
│   ├── initializer.py           # Core initialization
│   ├── templates.py             # Template management
│   └── stage_update.py          # Stage tracking updates
├── templates/                   # Project initialization templates
│   ├── basic/.claude/           # Tracking files, stage rules, subagents
│   └── docs/                    # Reference documentation
├── code_map/                    # FastAPI backend
│   ├── server.py                # Application factory
│   ├── cli.py                   # CLI commands (run, config)
│   ├── analyzer.py              # Python code parsing
│   ├── ts_analyzer.py           # TypeScript/JavaScript parsing
│   ├── js_analyzer.py           # Additional JS analysis
│   ├── html_analyzer.py         # HTML parsing
│   ├── index.py                 # Symbol indexing
│   ├── dependencies.py          # Dependency graph
│   ├── class_graph.py           # Class hierarchy
│   ├── uml_graph.py             # UML diagram generation
│   ├── linters/                 # Linter pipeline
│   │   ├── pipeline.py          # Orchestration
│   │   ├── discovery.py         # Tool detection
│   │   ├── storage.py           # Results persistence
│   │   └── report_schema.py     # Report formats
│   ├── integrations/            # External services
│   │   └── ollama_service.py    # Ollama AI integration
│   ├── insights/                # AI insights
│   │   ├── ollama_service.py    # Insights-specific wrapper
│   │   └── storage.py           # Insights persistence
│   ├── api/                     # REST endpoints
│   │   ├── routes.py            # Main router
│   │   ├── analysis.py          # Code analysis
│   │   ├── linters.py           # Linter reports
│   │   ├── integrations.py      # Ollama integration
│   │   ├── stage.py             # Stage assessment
│   │   ├── graph.py             # Dependency graphs
│   │   └── preview.py           # Code previews
│   ├── settings.py              # Configuration
│   ├── state.py                 # Application state
│   └── watcher.py               # File watching
├── tests/                       # Test suite
│   ├── test_full_flow.sh        # Integration test
│   ├── test_linters_pipeline.py
│   ├── test_analysis_engine.py
│   ├── test_stage_*.py
│   └── test_api.py
└── tools/                       # Development utilities
    ├── debug_ollama.py
    └── test_backend_ollama.py
```

---

## Development Workflows

### Working on Stage Framework

**Adding detection logic:**
1. Update `stage_config.py` with new metrics/thresholds
2. Test with: `python assess_stage.py <project-path>`
3. Update tests in `tests/test_stage_config.py`
4. Run: `bash tests/test_full_flow.sh`

**Modifying templates:**
1. Edit files in `templates/basic/.claude/` or `templates/docs/`
2. Test: `python init_project.py test-temp --dry-run`
3. Verify with actual init: `python init_project.py test-temp`
4. Update `tests/test_full_flow.sh` if structure changed

### Working on Code Map

**Adding analyzer features:**
1. Update relevant analyzer in `code_map/` (e.g., `analyzer.py`, `ts_analyzer.py`)
2. Add tests in `tests/test_analysis_engine.py`
3. Update API endpoints in `code_map/api/` if exposing new functionality
4. Test: `pytest tests/test_analysis_engine.py -v`

**Modifying linter pipeline:**
1. Edit `code_map/linters/pipeline.py` for orchestration
2. Edit `code_map/linters/discovery.py` to add new tools
3. Test: `pytest tests/test_linters_pipeline.py -v`
4. Verify environment variable controls work
5. Test API integration: `POST /api/linters/run`

**Adding Ollama features:**
1. Update `code_map/integrations/ollama_service.py`
2. Test locally with Ollama running
3. Use debug tool: `python tools/debug_ollama.py`
4. Test backend: `python tools/test_backend_ollama.py`
5. Add API endpoints in `code_map/api/integrations.py`

---

## Critical Design Decisions

### Stage Framework: Non-Destructive Initialization

**Philosophy:** Allow adding framework to existing projects safely.

Implementation in `stage_init/initializer.py`:
- Only copies files if they don't exist
- Never overwrites existing `.claude/` files
- Reports skipped vs. copied files separately
- Preserves user customizations

### Stage Framework: Placeholder System

Simple `str.replace()` approach in copied template files:
- `{{PROJECT_NAME}}` - Project directory name
- `{{DATE}}` - Current date (YYYY-MM-DD)
- `{{YEAR}}` - Current year
- Applied only to newly copied files (not existing ones)

### Code Map: Linter Pipeline Design

**Graceful Degradation:**
- Auto-discovers available tools (ruff, mypy, bandit, pytest)
- Runs only installed tools, skips missing ones
- Respects size/file thresholds to avoid performance issues
- Minimum interval prevents excessive runs
- Environment variables provide runtime control

Implementation: `code_map/linters/pipeline.py`

### Code Map: Symbol Index Integration

**Enhanced Stage Detection:**
- Code Map's `SymbolIndex` provides deep code analysis
- Detects design patterns, class hierarchies, dependencies
- Used by `assess_stage.py` when available (via API or direct import)
- Falls back to basic file/LOC metrics if unavailable

Integration: `code_map/stage_toolkit.py`

---

## Dependencies

### Stage Framework (Core)
- **Python 3.10+** only
- **No external dependencies** (stdlib only: `pathlib`, `shutil`, `sys`, `datetime`, `subprocess`)
- Optional: `claude` CLI for CLAUDE.md generation

### Code Map Backend

Install with: `pip install -r requirements.txt`

**Core (required):**
- fastapi>=0.110,<0.120
- pydantic>=2.7,<3
- uvicorn[standard]>=0.29,<0.32
- watchdog>=3.0,<5
- typer>=0.12,<1

**Testing:**
- pytest>=8.2,<9
- pytest-asyncio>=0.23,<0.24
- pytest-cov>=5.0,<6
- httpx>=0.27,<0.28

**Linters (used by pipeline):**
- ruff>=0.5,<0.6
- black>=24.4,<25
- mypy>=1.10,<1.11
- bandit>=1.7.10,<1.8

**Analyzers (optional):**
- beautifulsoup4>=4.12,<5 (HTML analysis)
- esprima>=4.0,<5 (JavaScript parsing)
- tree_sitter>=0.20,<0.22 (Multi-language AST)
- tree_sitter_languages>=1.10,<2

---

## Common Development Tasks

### Add New Stage Rule

1. Create `templates/basic/.claude/02-stageN-rules.md`
2. Update `stage_config.py` with new `StageDefinition`
3. Test: `python init_project.py test-project --dry-run`
4. Update documentation in `docs/STAGE_CRITERIA.md`

### Add New Linter Tool

1. Add detection logic in `code_map/linters/discovery.py`
2. Add execution logic in `code_map/linters/pipeline.py`
3. Add tests in `tests/test_linters_pipeline.py`
4. Document in README.md (environment variables section)

### Add New API Endpoint

1. Create/edit module in `code_map/api/`
2. Define Pydantic schemas if needed (see `code_map/api/schemas.py`)
3. Register router in `code_map/api/routes.py`
4. Add tests in `tests/test_api.py`
5. Test manually via FastAPI docs: `http://localhost:8000/docs`

### Integrate New AI Service

1. Create service module in `code_map/integrations/`
2. Follow pattern from `ollama_service.py`
3. Add configuration to `code_map/settings.py`
4. Create API endpoints in `code_map/api/integrations.py`
5. Create debug/test tools in `tools/`

---

## Testing Strategy

### Stage Framework Tests
- **Integration:** `bash tests/test_full_flow.sh` (covers full initialization flow)
- **Unit:** `pytest tests/test_stage_*.py`
- **Manual:** Use `--dry-run` flag for safe testing
- **Validation:** Test on real projects with known stages

### Code Map Tests
- **Unit:** `pytest tests/test_*.py`
- **Focused:** `pytest tests/test_linters_pipeline.py -v`
- **Integration:** Start server and test via `http://localhost:8000/docs`
- **Coverage:** `pytest --cov=code_map --cov=stage_init`

### Philosophy
- Test real behavior, avoid mocking when possible
- Add tests when bugs appear (not preemptively - YAGNI)
- Document expected behavior through tests
- Integration tests verify end-to-end flows

---

## Session Continuity

This project follows its own stage-aware methodology:

**Key context files:**
- [.claude/00-project-brief.md](.claude/00-project-brief.md) - Project scope and constraints
- [.claude/01-current-phase.md](.claude/01-current-phase.md) - Current development state, decisions, next steps
- [.claude/02-stage3-rules.md](.claude/02-stage3-rules.md) - Production-level development rules (current stage)

**Workflow:**
- **Session start:** Read the above files to understand current state
- **During work:** Follow stage-specific rules, propose before implementing
- **Session end:** Update `01-current-phase.md` with progress and decisions

---

## Core Philosophy

**YAGNI (You Aren't Gonna Need It):**
- Add features only when pain is felt 3+ times
- Start minimal, evolve with evidence
- Stage framework enforces this discipline

**Evolutionary Architecture:**
- **Stage 1:** Prove the concept (single file, hardcoded values)
- **Stage 2:** Add structure when refactoring hurts (multiple files, simple patterns)
- **Stage 3:** Scale when usage demands it (full architecture, optimization)

**Maintain Control:**
- AI executes, humans decide, framework enforces
- Stage rules prevent over-engineering
- Explicit constraints guide development

---

## Git Workflow

**Current branch:** `integrate-ollama`
**Main branch:** `first-steps` (target for PRs)

Recent work focuses on:
- Ollama insights integration
- Linter pipeline enhancements
- Stage detection algorithm refinements
- Code Map API expansion

When creating PRs, target the `first-steps` branch.
