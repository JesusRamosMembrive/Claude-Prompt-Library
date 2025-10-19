# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Claude-Prompt-Library is a methodology and toolset for structured software development with Claude Code. It provides:

1. **Project templates** - Pre-configured `.claude/` context files and reference documentation
2. **Prompt library** - Collection of useful prompts for common development scenarios
3. **Stage-based workflow** - Progressive methodology (Stage 1: Scaffolding, Stage 2: Structure, Stage 3: Production)

**Core Philosophy**: Start minimal, add complexity only when pain is felt. Track context and decisions in `.claude/` files for session continuity.

## Commands

### Development & Testing

```bash
# Test the full flow (initialization + prompt helper)
bash tests/test_full_flow.sh

# Run Python scripts (no build step needed)
python init_project.py <project-name>
python prompt_helper.py [command] [args]
```

### Using the Tools

**Initialize a new project:**
```bash
python init_project.py my-new-project
cd my-new-project
cat docs/QUICK_START.md
```

**Browse prompts (interactive mode):**
```bash
python prompt_helper.py
# Requires: simple-term-menu
# Optional: pyperclip for clipboard support
```

**Browse prompts (command mode - no dependencies):**
```bash
python prompt_helper.py list                          # List all prompts
python prompt_helper.py show debugging/stuck          # Display a prompt
python prompt_helper.py copy planning/feature         # Copy to clipboard
```

### Testing Individual Components

```bash
# Test project initialization
python init_project.py test-project
ls -la test-project/.claude/
ls -la test-project/docs/

# Test prompt helper list command
python prompt_helper.py list | grep -q "DEBUGGING"

# Test prompt helper show command
python prompt_helper.py show debugging/stuck

# Test flexible matching
python prompt_helper.py show debug/stuck           # Case insensitive
python prompt_helper.py show DEBUGGING/Stuck-In-Loop  # Dash/space flexible
```

## Architecture

### Two-Phase System

**Phase 1: Basic CLI Template Copier** ✅ Complete
- `init_project.py` - Copies templates to new/existing projects
- Non-destructive: skips existing files
- Placeholder replacement: `{{PROJECT_NAME}}`, `{{DATE}}`, `{{YEAR}}`

**Phase 2: Enhanced Docs + Prompt Helper** ✅ Complete
- Phase 2.1: Copy reference docs to `docs/` (integrated into `init_project.py`)
- Phase 2.2: `prompt_helper.py` for browsing/copying prompts
- Phase 2.3: Auto-context loading via `settings.local.json`

### Directory Structure

```
claude-prompt-library/
├── init_project.py           # Main CLI - initializes projects
├── prompt_helper.py          # Prompt browser/copier
├── requirements.txt          # Dependencies (simple-term-menu, pyperclip)
├── templates/
│   ├── basic/.claude/        # Template files copied to projects
│   │   ├── 00-project-brief.md
│   │   ├── 01-current-phase.md
│   │   ├── 02-stage1-rules.md
│   │   ├── 02-stage2-rules.md
│   │   ├── 02-stage3-rules.md
│   │   └── settings.local.json
│   └── docs/                 # Reference docs copied to projects
│       ├── PROMPT_LIBRARY.md
│       ├── QUICK_START.md
│       ├── STAGES_COMPARISON.md
│       └── CLAUDE_CODE_REFERENCE.md
└── .claude/                  # This project's own tracking
    └── 01-current-phase.md   # Development progress
```

### Key Design Decisions

**Coexistence with Claude Code** (init_project.py:56-76)
- Only copies `.md` template files if they don't exist
- Never touches `settings.local.json` if already present
- Allows adding methodology to existing projects
- Files skipped vs. copied are reported separately

**Graceful Degradation** (prompt_helper.py:11-22)
- Command mode works without dependencies (list, show, copy)
- Interactive mode requires `simple-term-menu`
- Clipboard support optional with `pyperclip`
- Clear error messages guide installation if needed

**Flexible Prompt Matching** (prompt_helper.py:149-183)
- Case-insensitive search
- Dashes/spaces/underscores normalized
- Partial matching: `debug/stuck` finds `DEBUGGING/Stuck in Loop`
- Format: `category/snippet-name`

**Placeholder System** (init_project.py:78-93)
- Simple `str.replace()` approach
- Applied only to newly copied files (not existing)
- Three placeholders: `{{PROJECT_NAME}}`, `{{DATE}}`, `{{YEAR}}`
- Minimal but sufficient for current needs

### Critical Components

**`settings.local.json`** - Most important file for methodology
- Contains `customInstructions` that auto-load on Claude Code startup
- Enforces workflow: read context → work → update tracking
- Without this, the tracking discipline breaks down
- Phase 2.3 solved "manual context loading is tedious"

**`01-current-phase.md`** - Session continuity mechanism
- Updated at end of each session
- Documents: what was done, decisions made, what was deferred, next steps
- Prevents context loss between sessions
- Lives in `.claude/` of each project (not this repo)

**`prompt_helper.py` parser** (lines 30-92)
- Extracts prompts from `PROMPT_LIBRARY.md`
- Detects categories (`## HEADING`), snippets (`### NAME`), code blocks
- Stops at non-prompt sections (`## NOTAS DE USO`)
- Returns nested dict: `{category: {snippet_name: content}}`

## Stage-Based Development

Projects initialized with this tool follow a three-stage methodology:

- **Stage 1 (Scaffolding)**: Minimal viable implementation, stdlib only
- **Stage 2 (Structure)**: Add essential dependencies, basic testing
- **Stage 3 (Production)**: Full testing, documentation, edge cases

**Rule**: Only advance stages when pain justifies the complexity.

The stage rules are in `templates/basic/.claude/02-stage[1-3]-rules.md` and get copied to each project.

## Working with This Repository

### Adding New Prompts

1. Edit `templates/docs/PROMPT_LIBRARY.md`
2. Follow format: `## CATEGORY` then `### Snippet Name` with code block
3. Test: `python prompt_helper.py show category/snippet-name`

### Adding New Template Files

1. Add to `templates/basic/.claude/` or `templates/docs/`
2. Update file list in `init_project.py` (line 56 or 96)
3. Test with: `python init_project.py test-project`

### Session Workflow

When working on this repository:

1. **Start**: Read `.claude/01-current-phase.md` for current state
2. **Work**: Follow YAGNI principle - no features without felt pain
3. **End**: Update `.claude/01-current-phase.md` with progress, decisions, next steps

### Decision Documentation

This project extensively documents **why** decisions were made:

- See `.claude/01-current-phase.md` lines 84-105 for dependency decision rationale
- Every deferred feature is listed with reason (lines 158-163)
- Pain must be felt 3+ times before adding features (lines 186-190)

## Dependencies

**Runtime (optional):**
- `simple-term-menu>=1.6.0` - For interactive mode only
- `pyperclip>=1.8.0` - For clipboard support (optional)

**Development:**
- Python 3.6+ (uses f-strings, pathlib)
- Standard library: `pathlib`, `shutil`, `sys`, `datetime`, `os`, `re`, `argparse`

Install with: `pip install -r requirements.txt`

## Testing Philosophy

Tests are minimal and functional (bash script):
- Test happy path only
- No unit tests (YAGNI - not needed yet)
- Manual testing for interactive mode
- Tests document expected behavior

Add tests only when bugs appear, not preemptively.
