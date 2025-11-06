# Stage-Aware Development Framework - Usage Guide

Complete guide for using the framework scripts and tools.

---

## 🚀 Quick Start

### For New Projects

Initialize a new project with the stage-aware framework:

```bash
python init_project.py my-new-project
cd my-new-project
```

This creates:
- `.claude/` with stage rules and tracking files
- `.claude/subagents/` with 4 specialized subagents
- `docs/` with reference documentation
- `CLAUDE.md` with project context

### For Existing Projects

Add the framework to an existing project with automatic stage detection:

```bash
python init_project.py --existing /path/to/your-project
```

This:
1. Adds `.claude/` framework files (non-destructive)
2. Copies stage-aware subagents
3. **Automatically detects** your project's stage
4. Updates `01-current-phase.md` with detection results

### Just Detect Stage

Analyze a project without modifying anything:

```bash
python init_project.py --detect-only /path/to/project
```

Or use the standalone tool:

```bash
python assess_stage.py /path/to/project
```

---

## 📋 Script Reference

### `init_project.py` - Project Initializer

Main tool for setting up the stage-aware framework.

#### **Usage**

```bash
python init_project.py [OPTIONS] <project_path>
```

#### **Arguments**

- `project_path` - Project name (new projects) or path (existing projects)

#### **Options**

- `--existing` - Add framework to existing project and auto-detect stage
- `--detect-only` - Only detect stage, don't initialize framework
- `--agent {claude|codex|both}` - Choose which assistants to configure (default: both)
- `--dry-run` - Print the planned changes without modifying the filesystem
- `--skip-claude-init` - Skip running `claude -p "/init"` even if the CLI is installed
- `--log-level LEVEL` - Adjust logging verbosity (`INFO`, `DEBUG`, etc.)
- `-h, --help` - Show help message

#### **Examples**

```bash
# Create new project
python init_project.py my-app

# Add framework to existing project
python init_project.py --existing ~/projects/my-existing-app

# Quick stage check
python init_project.py --detect-only .

# Preview actions without writing
python init_project.py my-app --dry-run

# Verbose run for troubleshooting
python init_project.py --existing ~/projects/my-existing-app --log-level DEBUG
```

#### **What It Does**

1. **Creates/validates directories:**
   - `.claude/` for framework files
   - `docs/` for reference documentation

2. **Copies templates:**
   - `00-project-brief.md` - Project scope and constraints
   - `01-current-phase.md` - Progress tracking
   - `02-stage1-rules.md` - Prototyping rules
   - `02-stage2-rules.md` - Structuring rules
   - `02-stage3-rules.md` - Production rules

3. **Copies stage-aware agents** (4 specialized assistants):
   - `architect-generic.md` - Evolutionary architecture
   - `implementer.md` - Stage-appropriate implementation
   - `code-reviewer-optimized.md` - Complexity validation
   - `stage-keeper-architecture.md` - Framework documentation

4. **Generates CLAUDE.md:**
   - Runs `claude -p "/init"` if Claude CLI available (unless `--skip-claude-init` is provided)
   - Creates basic template if not
   - Appends custom workflow instructions

5. **Auto-detects stage** (always runs):
   - Analyzes codebase metrics
   - Detects patterns and architecture
   - Updates `01-current-phase.md` with results when available

6. **Dry-run aware:**
   - With `--dry-run` all filesystem writes are skipped
   - Reports the files that would be copied or updated

---

### `assess_stage.py` - Stage Detection Tool

Standalone tool for analyzing project maturity and recommending appropriate development stage.

#### **Usage**

```bash
python assess_stage.py <project-path>
```

#### **What It Analyzes**

1. **Code metrics:**
   - File count (Python, JavaScript/TypeScript, Java, Go, Rust, Ruby, PHP, C/C++)
   - Lines of code (LOC)
   - Directory structure complexity

2. **Design patterns:**
   - Factory, Singleton, Observer
   - Repository, Service Layer
   - Adapter, Strategy, Middleware

3. **Architecture:**
   - Presence of architectural folders (models, services, etc.)
   - Number of layers
   - Separation of concerns

#### **Output**

```
============================================================
🎯 STAGE ASSESSMENT RESULTS
============================================================

📊 Recommended Stage: 2
✅ Confidence: HIGH

📈 Project Metrics:
  - Code Files: 15
  - Lines of Code: ~2500
  - Directories: 8
  - Patterns Detected: Repository, Service

💡 Reasoning:
  • Medium codebase (15 files, ~2500 LOC)
  • Basic architecture present: 3 layer(s)
  • Some patterns in use: Repository, Service
  • Structure is appropriate for Stage 2
  • 📍 Mid Stage 2 - structure emerging

📚 What This Means:
  Stage 2 (Structuring):
  - Multiple files OK
  - Simple classes when needed
  - Add structure where it helps
  - 1-2 simple patterns max
  - Avoid premature optimization

📖 Next Steps:
  1. Review .claude/02-stage2-rules.md
  2. Update .claude/01-current-phase.md with current stage
  3. Follow stage-appropriate practices
```

#### **Stage Criteria**

**Stage 1 (Prototyping):**
- ≤3 files
- <500 LOC
- No patterns
- Minimal structure
- Focus: Prove concept works

**Stage 2 (Structuring):**
- 4-20 files
- 500-3000 LOC
- 1-3 simple patterns
- Basic architecture (2-4 layers)
- Focus: Add structure for maintenance

**Stage 3 (Production):**
- 20+ files
- 3000+ LOC
- Multiple patterns
- Complex architecture (4+ layers)
- Focus: Scale and maintain

---

### `claude_assess.py` - Deep Analysis Helper

Generates detailed assessment report with project structure visualization.

#### **Usage**

```bash
python claude_assess.py <project-path>
```

#### **What It Does**

1. Runs `tree` command with filtered output
2. Executes `assess_stage.py` for metrics
3. Generates markdown report with:
   - Project structure tree
   - Automated assessment
   - Manual analysis instructions for Claude Code

#### **Requirements**

- `tree` command installed (`sudo apt install tree`)
- Optional: Pipe output to Claude Code for review

---

## 🎯 Workflow Examples

### Example 1: Starting a New Project

```bash
# 1. Initialize project
python init_project.py my-api

# 2. Navigate to project
cd my-api

# 3. Read quick start
cat docs/QUICK_START.md

# 4. Open with Claude Code
code .

# 5. In Claude Code, verify context loaded
# Check that .claude/ files are referenced
```

### Example 2: Adding Framework to Existing Project

```bash
# 1. Detect stage first
python assess_stage.py ~/projects/my-app

# 2. Add framework with auto-detection
python init_project.py --existing ~/projects/my-app

# 3. Review detection results
cat ~/projects/my-app/.claude/01-current-phase.md

# 4. Follow stage-appropriate rules
cat ~/projects/my-app/.claude/02-stage2-rules.md  # if Stage 2
```

### Example 3: Re-assessing After Major Changes

```bash
# After adding significant features
python assess_stage.py .

# If stage changed, update tracking manually
# Or re-run with --existing to update 01-current-phase.md
python init_project.py --existing .
```

### Example 4: Using Subagents

Once framework is initialized, Claude Code automatically has access to subagents in `.claude/subagents/`:

- **For architecture decisions:** Subagent understands current stage and suggests appropriate patterns
- **For implementation:** Subagent enforces stage rules (e.g., prevents abstractions in Stage 1)
- **For code review:** Subagent validates complexity is appropriate for stage

Subagents are invoked automatically by Claude Code based on task context.

---

## 📁 Project Structure After Initialization

```
my-project/
├── .claude/                    # Framework files
│   ├── 00-project-brief.md     # Scope and constraints
│   ├── 01-current-phase.md     # Progress tracking
│   ├── 02-stage1-rules.md      # Prototyping rules
│   ├── 02-stage2-rules.md      # Structuring rules
│   ├── 02-stage3-rules.md      # Production rules
│   └── subagents/              # Specialized agents
│       ├── architect-generic.md
│       ├── code-reviewer-optimized.md
│       ├── implementer.md
│       └── stage-keeper-architecture.md
├── docs/                       # Reference documentation
│   ├── CLAUDE_CODE_REFERENCE.md
│   ├── QUICK_START.md
│   ├── STAGE_CRITERIA.md
│   └── STAGES_COMPARISON.md
└── CLAUDE.md                   # Project context for Claude Code
```

---

## ⚙️ Configuration

### Custom Instructions

The framework automatically appends custom workflow instructions to `CLAUDE.md`. These enforce:

1. **Start-of-session protocol:**
   - Read `.claude/` context files
   - Confirm understanding with user
   - Only then respond to requests

2. **During work:**
   - Follow stage-specific rules strictly
   - Propose plans before implementing
   - Get approval for architectural decisions

3. **End of session:**
   - Update `01-current-phase.md`
   - Document decisions and deferred items
   - Note next steps

### Customizing Stage Rules

Edit stage rule files to adjust constraints:

```bash
# Edit Stage 2 rules to be more/less restrictive
nano .claude/02-stage2-rules.md
```

Changes apply immediately to Claude Code in next session.

### Controlling the Linter Pipeline

The backend runs the linters automatically after scans. Tune its behaviour with environment variables before launching the API:

- `CODE_MAP_DISABLE_LINTERS=1` — Skip the pipeline entirely.
- `CODE_MAP_LINTERS_TOOLS=ruff,pytest` — Execute only the listed tools (comma separated, use lowercase keys).
- `CODE_MAP_LINTERS_MAX_PROJECT_FILES=2000` — Skip runs when the project exceeds this many files.
- `CODE_MAP_LINTERS_MAX_PROJECT_SIZE_MB=200` — Skip when the workspace size (in MiB) is above the threshold.
- `CODE_MAP_LINTERS_MIN_INTERVAL_SECONDS=300` — Minimum number of seconds between automatic runs; defaults to 180.

---

## 🔧 Troubleshooting

### Issue: Stage detection fails

**Symptoms:** `assess_stage.py` returns error or empty result

**Solutions:**
1. Check project has code files (supported: Python, JS/TS, Java, Go, Rust, Ruby, PHP, C/C++)
2. Verify path is correct
3. Check file permissions
4. Run with verbose output: Add debug prints to assess_stage.py

### Issue: Claude Code doesn't load context

**Symptoms:** Claude Code doesn't reference `.claude/` files

**Solutions:**
1. Check `CLAUDE.md` exists and contains custom instructions
2. Restart Claude Code session
3. Manually reference: "Read .claude/01-current-phase.md"

### Issue: init_project.py fails on existing project

**Symptoms:** Error when running with `--existing`

**Solutions:**
1. Verify project path exists
2. Check write permissions
3. Ensure assess_stage.py is in same directory

### Issue: Preview endpoint returns 413 or 415

**Symptoms:** `/preview` responds with "Archivo demasiado grande" or "Tipo de archivo no compatible".

**Solutions:**
1. Ensure the file is smaller than 512 KiB (preview limit).
2. Only text-based formats are allowed (`text/*`, JSON, XML, JavaScript).
3. Convert binary assets to a downloadable link instead of relying on the preview API.

### Issue: Subagents not working

**Symptoms:** Claude Code doesn't invoke subagents

**Solutions:**
1. Check `.claude/subagents/` directory exists
2. Verify `.md` files have correct frontmatter YAML
3. Files should have `---` delimited YAML with name, description, tools

---

## 📊 Understanding Stage Detection

### Detection Criteria (Internal)

The detection algorithm uses these heuristics:

```python
# Stage 1 indicators
if file_count <= 3 and loc < 500:
    stage = 1

# Stage 2 indicators
elif file_count <= 20 and loc < 3000 and patterns <= 3:
    stage = 2

# Stage 3 indicators
elif file_count > 20 or loc > 3000 or patterns > 3:
    stage = 3
```

### Confidence Levels

- **High:** Clear indicators, unambiguous stage
- **Medium:** Borderline case, manual review recommended
- **Low:** Conflicting signals, definitely review manually

### Edge Cases

The tool provides warnings for:
- Few files but high LOC (needs refactoring)
- Many files but no patterns (needs structure)
- Sub-stage hints within Stage 2 (early/mid/late)

---

## 🎓 Best Practices

### When to Re-assess

Re-run stage detection when:
- Adding 5+ new files
- Doubling LOC
- Introducing new patterns
- Refactoring architecture
- Transitioning from prototype to production

### Stage Transition

Don't rush to next stage. Transition only when:
- Current stage feels painful
- Specific problems justify complexity
- Team consensus on need
- Evidence of repeated pain points

### Using with Teams

1. **Initialize once:**
   ```bash
   python init_project.py --existing .
   git add .claude/ CLAUDE.md
   git commit -m "Add stage-aware framework"
   ```

2. **Team workflow:**
   - Everyone works within stage constraints
   - Propose stage transitions in PRs
   - Use subagents for consistency
   - Update `01-current-phase.md` regularly

3. **Stage decisions:**
   - Discuss in team meetings
   - Base on evidence, not preferences
   - Document in `01-current-phase.md`

---

## 🔗 Additional Resources

- `docs/QUICK_START.md` - Quick workflow guide
- `docs/STAGE_CRITERIA.md` - Detailed stage criteria
- `docs/STAGES_COMPARISON.md` - Side-by-side comparison
- `docs/CLAUDE_CODE_REFERENCE.md` - Claude Code features

For issues or questions:
- Check `CLAUDE.md` in your project
- Review `.claude/02-stageX-rules.md` for current stage
- Re-run `assess_stage.py` for fresh analysis

---

**Version:** 3.0 (Stage Detection)
**Last Updated:** 2025-10-27
