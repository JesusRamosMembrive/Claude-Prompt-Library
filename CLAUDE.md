# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

---

# ⚠️ CRITICAL: START-OF-SESSION PROTOCOL

**YOU MUST follow this protocol at the start of EVERY session, without exception:**

1. **ALWAYS read these files first** (use Read tool in parallel):
   ```
   .claude/00-project-brief.md
   .claude/01-current-phase.md
   .claude/02-stage[X]-rules.md  (current stage)
   ```

2. **ALWAYS confirm to user** you've read the context:
   - State current phase/stage
   - Summarize what was last done
   - Ask for clarification if anything is unclear

3. **ONLY THEN** respond to the user's request

**This applies EVEN IF the user's first message is a simple question.**

Do NOT skip this protocol to "be helpful faster" - reading context IS being helpful.

---

## Project Overview

**Stage-Aware Development Framework** - A methodology and toolset for evolutionary software development with Claude Code. It provides:

1. **Automatic stage detection** - Analyzes your codebase to determine maturity level (Stage 1/2/3)
2. **Project templates** - Pre-configured `.claude/` context files with stage-specific rules
3. **Stage-aware subagents** - Specialized agents (architect, implementer, code-reviewer) that understand project context
4. **Anti-over-engineering enforcement** - Prevents premature complexity through strict stage rules

**Core Philosophy**: Start minimal, add complexity only when pain is felt. The framework automatically configures Claude Code to work within appropriate constraints for your project's current stage.

## Commands

### Development & Testing

```bash
# Test the full flow
bash tests/test_full_flow.sh

# Run Python scripts (no build step needed)
python init_project.py <project-name>
python assess_stage.py <project-path>
```

### Using the Tools

**Initialize a new project:**
```bash
python init_project.py my-new-project
cd my-new-project
cat docs/QUICK_START.md
```

**Assess project stage (existing projects):**
```bash
python assess_stage.py .
# Analyzes file count, LOC, patterns, architecture
# Recommends Stage 1, 2, or 3 with confidence level
```

**Use stage-aware subagents:**
Claude Code will automatically have access to:
- `.claude/subagents/architect.md` - For architecture decisions
- `.claude/subagents/implementer.md` - For stage-appropriate implementation
- `.claude/subagents/code-reviewer.md` - For complexity validation

### Testing Individual Components

```bash
# Test project initialization
python init_project.py test-project
ls -la test-project/.claude/
ls -la test-project/.claude/subagents/
ls -la test-project/docs/

# Test stage assessment
python assess_stage.py test-project
```

## Architecture

### Two-Phase System

**Phase 1: Basic CLI Template Copier** ✅ Complete
- `init_project.py` - Copies templates to new/existing projects
- Non-destructive: skips existing files
- Placeholder replacement: `{{PROJECT_NAME}}`, `{{DATE}}`, `{{YEAR}}`

**Phase 2: Stage-Aware Framework** ✅ Transformed
- Phase 2.1: Copy reference docs to `docs/` (integrated into `init_project.py`)
- Phase 2.2: Removed prompt library → Focus on stage guard
- Phase 2.3: Integrated `assess_stage.py` for automatic stage detection
- Phase 2.4: Added stage-aware subagents

### Directory Structure

```
stage-keeper/
├── init_project.py           # Main CLI - initializes projects
├── assess_stage.py           # Automatic stage detection
├── claude_assess.py          # Deep analysis helper
├── templates/
│   ├── basic/.claude/        # Template files copied to projects
│   │   ├── 00-project-brief.md
│   │   ├── 01-current-phase.md
│   │   ├── 02-stage1-rules.md
│   │   ├── 02-stage2-rules.md
│   │   ├── 02-stage3-rules.md
│   │   ├── settings.local.json
│   │   └── subagents/        # Stage-aware subagents
│   │       ├── architect.md
│   │       ├── implementer.md
│   │       ├── code-reviewer.md
│   │       └── stage-keeper-architecture.md
│   └── docs/                 # Reference docs copied to projects
│       ├── STAGES_COMPARISON.md
│       ├── STAGE_CRITERIA.md
│       ├── QUICK_START.md
│       └── GUIDE.md
└── .claude/                  # This project's own tracking
    └── 01-current-phase.md   # Development progress
```

### Key Design Decisions

**Coexistence with Claude Code** (init_project.py:56-76)
- Only copies `.md` template files if they don't exist
- Never touches `settings.local.json` if already present
- Allows adding methodology to existing projects
- Files skipped vs. copied are reported separately

**Automatic Stage Detection** (assess_stage.py)
- Analyzes file count, LOC, directory structure, patterns
- Detects common design patterns (Factory, Repository, Service, etc.)
- Provides confidence level (high/medium/low)
- Recommends stage with detailed reasoning

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

**`assess_stage.py`** - Automatic stage detection
- Analyzes existing codebase metrics
- Detects architectural patterns and complexity
- Recommends appropriate development stage
- Provides actionable reasoning for recommendation

**Stage-aware subagents** - Specialized behavior per stage
- `architect.md` - Evolutionary architecture design
- `implementer.md` - Stage-appropriate code implementation
- `code-reviewer.md` - Complexity validation
- All understand and enforce stage rules automatically

## Stage-Based Development

Projects initialized with this tool follow a three-stage methodology:

- **Stage 1 (Scaffolding)**: Minimal viable implementation, stdlib only
- **Stage 2 (Structure)**: Add essential dependencies, basic testing
- **Stage 3 (Production)**: Full testing, documentation, edge cases

**Rule**: Only advance stages when pain justifies the complexity.

The stage rules are in `templates/basic/.claude/02-stage[1-3]-rules.md` and get copied to each project.

## Working with This Repository

### Adding New Subagents

1. Create markdown file in `templates/basic/.claude/subagents/`
2. Follow frontmatter format with name, description, tools
3. Document when and how to use the subagent
4. Test with new project initialization

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

**Runtime:**
- Python 3.10+ (uses f-strings, pathlib, type hints)
- Standard library only: `pathlib`, `shutil`, `sys`, `datetime`, `subprocess`
- No external dependencies required

**Optional:**
- Claude Code CLI (`claude`) - For automatic CLAUDE.md generation
- `tree` command - For project structure visualization

## Testing Philosophy

Tests are minimal and functional (bash script):
- Test happy path only
- No unit tests (YAGNI - not needed yet)
- Manual testing for interactive mode
- Tests document expected behavior

Add tests only when bugs appear, not preemptively.

---

# Custom Workflow Instructions

<!-- Added by claude-prompt-library init_project.py -->

## 🎯 PROJECT CONTEXT

Before ANY work, read in this order:
1. .claude/00-project-brief.md - Project scope and constraints
2. .claude/01-current-phase.md - Current state and progress
3. .claude/02-stage[X]-rules.md - Rules for current stage

## 📝 SESSION WORKFLOW

⚠️ MANDATORY: At the START of EVERY session, BEFORE responding to user:

1. **ALWAYS read these files first** (use Read tool in parallel):
   - .claude/00-project-brief.md - Project scope and constraints
   - .claude/01-current-phase.md - Current state and progress
   - .claude/02-stage[X]-rules.md - Rules for current stage

2. **ALWAYS confirm to user** you've read the context:
   - State current phase/stage
   - Summarize what was last done
   - Ask for clarification if anything is unclear

3. **ONLY THEN** respond to the user's request

**This applies EVEN IF the user's first message is a simple question.**
Do NOT skip this protocol to "be helpful faster" - reading context IS being helpful.

During WORK:
- Follow stage-specific rules strictly
- Propose plans before implementing
- Get approval for architectural decisions

At END of session:
- Update .claude/01-current-phase.md with:
  * What was implemented (with file names)
  * Decisions made and why
  * What was NOT done (deferred)
  * Next steps for next session
- Keep 01-current-phase.md concise and scannable

## ⚠️ CRITICAL RULES

- Never implement without reading current context
- Never skip updating progress at end of session
- Never assume you remember from previous sessions
- Always check current stage rules before proposing solutions

## 🚫 NEVER

- Over-engineer beyond current stage
- Implement features not in project brief
- Skip the "propose then implement" workflow
- Forget to update tracking

---

# Custom Workflow Instructions

<!-- Added by claude-prompt-library init_project.py -->

## 🎯 PROJECT CONTEXT

Before ANY work, read in this order:
1. .claude/00-project-brief.md - Project scope and constraints
2. .claude/01-current-phase.md - Current state and progress
3. .claude/02-stage[X]-rules.md - Rules for current stage

## 📝 SESSION WORKFLOW

⚠️ MANDATORY: At the START of EVERY session, BEFORE responding to user:

1. **ALWAYS read these files first** (use Read tool in parallel):
   - .claude/00-project-brief.md - Project scope and constraints
   - .claude/01-current-phase.md - Current state and progress
   - .claude/02-stage[X]-rules.md - Rules for current stage

2. **ALWAYS confirm to user** you've read the context:
   - State current phase/stage
   - Summarize what was last done
   - Ask for clarification if anything is unclear

3. **ONLY THEN** respond to the user's request

**This applies EVEN IF the user's first message is a simple question.**
Do NOT skip this protocol to "be helpful faster" - reading context IS being helpful.

During WORK:
- Follow stage-specific rules strictly
- Propose plans before implementing
- Get approval for architectural decisions

At END of session:
- Update .claude/01-current-phase.md with:
  * What was implemented (with file names)
  * Decisions made and why
  * What was NOT done (deferred)
  * Next steps for next session
- Keep 01-current-phase.md concise and scannable

## ⚠️ CRITICAL RULES

- Never implement without reading current context
- Never skip updating progress at end of session
- Never assume you remember from previous sessions
- Always check current stage rules before proposing solutions

## 🚫 NEVER

- Over-engineer beyond current stage
- Implement features not in project brief
- Skip the "propose then implement" workflow
- Forget to update tracking

## 📚 PROJECT RESOURCES

Available in `docs/` folder:
- **PROMPT_LIBRARY.md** - Templates for common situations (debugging, refactoring, etc.)
- **QUICK_START.md** - Workflow guide
- **STAGES_COMPARISON.md** - Quick reference table
- **CLAUDE_CODE_REFERENCE.md** - Claude Code tips, slash commands, MCP, subagents

Use these resources when stuck or making decisions.

## 💡 REMEMBER

- Simplicity > Completeness
- Solve today's problems, not tomorrow's
- The methodology matters more than the code
- When in doubt, check the stage rules

---

*Generated by [Claude Prompt Library](https://github.com/your-repo/claude-prompt-library)*
*To update these instructions, modify templates/basic/.claude/CUSTOM_INSTRUCTIONS.md*