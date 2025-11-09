# Stage-Aware Development Framework

**Prevent over-engineering. Guide evolution. Stay in control.**

A methodology and toolset for evolutionary software development with Claude Code **and** Codex CLI. Automatically detects your project's maturity and configures your preferred agent(s) to operate within appropriate constraints.

---

## 🎯 The Problem

When developing with AI assistants like Claude Code or Codex:
- ✗ Too easy to over-engineer early prototypes
- ✗ AI suggests enterprise patterns for 100-line scripts
- ✗ Hard to maintain "start simple" discipline
- ✗ Context loss between sessions breaks momentum

## 💡 The Solution

**Stage-Aware Development Framework** enforces evolutionary development through:

1. **Automatic Stage Detection** - Analyzes codebase and recommends Stage 1/2/3
2. **Stage-Specific Rules** - Prevents complexity until justified
3. **Specialized Subagents** - Architect, implementer, reviewer that understand stage context
4. **Session Continuity** - Tracking files preserve decisions and progress

---

## 🚀 Quick Start

### New Project

```bash
# Both agents (default)
python init_project.py my-new-project

# Claude únicamente
python init_project.py my-new-project --agent=claude

# Codex únicamente
python init_project.py my-new-project --agent=codex

# Ensayar sin modificar nada
python init_project.py my-new-project --dry-run

cd my-new-project
```

Siempre se generan los archivos base de seguimiento (`.claude/`).  
Cuando seleccionas Codex, también se crea `.codex/` con `AGENTS.md` y reglas por etapa adaptadas al CLI.

### Existing Project

```bash
python init_project.py --existing /path/to/project
```

Adds framework + **auto-detects stage** + updates tracking.

### Just Check Stage

```bash
python init_project.py --detect-only /path/to/project
```

Analyzes project without modifying anything.

---

## 📊 How It Works

### 1. Stage Detection

Analyzes your codebase:
- File count & lines of code
- Design patterns present
- Architecture complexity
- Directory structure

**Example output:**
```
📊 Recommended Stage: 2
✅ Confidence: HIGH

📈 Metrics:
  - Files: 15
  - LOC: ~2500
  - Patterns: Repository, Service

💡 Reasoning:
  • Medium codebase (15 files, ~2500 LOC)
  • Basic architecture: 3 layers
  • 📍 Mid Stage 2 - structure emerging
```

### 2. Stage Rules

Projects get `.claude/02-stageX-rules.md` files that Claude Code enforces:

**Stage 1 (Prototyping):**
- One file preferred
- No abstractions
- Hardcoded values OK
- Prove concept works

**Stage 2 (Structuring):**
- Multiple files when helpful
- Simple classes allowed
- 1-2 patterns max
- Add structure for real pain

**Stage 3 (Production):**
- Patterns appropriate
- Architecture matters
- Optimization justified
- Design for scale

### 3. Specialized Subagents

Four agents understand stage context:

- **architect** - Designs architecture appropriate for stage
- **implementer** - Writes code enforcing stage rules
- **code-reviewer** - Validates complexity matches stage
- **stage-keeper** - Documents framework itself

### 4. Session Tracking

Progress tracked in `.claude/01-current-phase.md`:
- What was implemented
- Decisions made and why
- What was deferred
- Next steps

Prevents context loss between Claude Code sessions.

---

## 🎓 Core Philosophy

### YAGNI with Evidence

**You Aren't Gonna Need It** - Until you prove you do.

- Stage 1: Prove the concept
- Stage 2: Add structure when refactoring hurts
- Stage 3: Scale when usage demands it

### Evolutionary Architecture

Don't design for scale at the start. Design to evolve easily.

### Maintain Control

AI executes. Human decides. Framework enforces.

---

## 📁 What You Get

After initialization:

```
your-project/
├── .claude/
│   ├── 00-project-brief.md        # Scope
│   ├── 01-current-phase.md        # Progress + stage detection
│   ├── 02-stage1-rules.md         # Prototyping rules
│   ├── 02-stage2-rules.md         # Structuring rules
│   ├── 02-stage3-rules.md         # Production rules
│   └── subagents/                 # 4 specialized agents
├── docs/                          # Reference docs
└── CLAUDE.md                      # Project context
```

---

## 🔧 Commands Reference

### init_project.py

```bash
# New project
python init_project.py my-app

# Existing project (auto-detects stage)
python init_project.py --existing /path/to/project

# Detect only
python init_project.py --detect-only /path/to/project

# Preview actions without writing
python init_project.py my-app --dry-run

# Increase logging verbosity
python init_project.py --existing /path/to/project --log-level DEBUG
```

**Key options**

- `--agent {claude|codex|both}` to pick which assistants to configure.
- `--dry-run` prints what would change without touching the filesystem.
- `--log-level LEVEL` (`INFO` by default) surfaces detailed progress when troubleshooting.

### assess_stage.py

```bash
# Detailed stage analysis
python assess_stage.py /path/to/project
```

### claude_assess.py

```bash
# Deep analysis with tree visualization
python claude_assess.py /path/to/project
```

**→ Full documentation:** [USAGE.md](./USAGE.md)

---

## 📚 Documentation

- **[USAGE.md](./USAGE.md)** - Complete usage guide with examples
- **[docs/QUICK_START.md](./docs/QUICK_START.md)** - Quick workflow guide
- **[docs/STAGE_CRITERIA.md](./docs/STAGE_CRITERIA.md)** - Detailed stage criteria
- **[docs/STAGES_COMPARISON.md](./docs/STAGES_COMPARISON.md)** - Side-by-side comparison

### ⚙️ Linter Pipeline Controls

Configure automated lint runs via environment variables before starting the API or CLI:

- `CODE_MAP_DISABLE_LINTERS=1` — Skip the pipeline entirely.
- `CODE_MAP_LINTERS_TOOLS=ruff,pytest` — Limit execution to a subset of tools.
- `CODE_MAP_LINTERS_MAX_PROJECT_FILES=2000` — Skip the run when the project exceeds this file count.
- `CODE_MAP_LINTERS_MAX_PROJECT_SIZE_MB=200` — Skip when the workspace is larger than the threshold.
- `CODE_MAP_LINTERS_MIN_INTERVAL_SECONDS=300` — Minimum seconds between automatic runs (default 180).

---

## 🎯 Use Cases

### For Individual Developers

Stop over-engineering side projects. Start simple, evolve with evidence.

### For Teams

Consistent development standards. Everyone works at appropriate complexity level.

### For Prototypes

Force simplicity. Prevent "production-ready" code for throwaway experiments.

### For Existing Projects

Assess current state. Get recommendation. Follow appropriate rules going forward.

---

## 🧪 Example: Stage Detection in Action

**Empty project → Stage 1:**
```bash
python init_project.py --existing my-new-idea
# Detected Stage 1 (0 files)
# Rule: One file, no abstractions
```

**After prototyping → Stage 2:**
```bash
python assess_stage.py my-new-idea
# Detected Stage 2 (8 files, 1200 LOC)
# Rule: Multiple files OK, 1-2 patterns
```

**In production → Stage 3:**
```bash
python assess_stage.py my-production-app
# Detected Stage 3 (35 files, 6000 LOC)
# Rule: Patterns appropriate, architect for scale
```

---

## ⚙️ Requirements

**Runtime:**
- Python 3.10+
- Standard library only (no external dependencies)

**Optional:**
- Claude Code CLI (`claude`) - For CLAUDE.md generation
- `tree` command - For project visualization

---

## 🛠️ Installation

```bash
# Clone repository
git clone https://github.com/your-org/stage-aware-framework
cd stage-aware-framework

# Use directly (no installation needed)
python init_project.py my-project
```

---

## 🔍 How Stage Detection Works

### Detection Algorithm

```python
# Stage 1: Prototyping
if files <= 3 and loc < 500:
    stage = 1

# Stage 2: Structuring
elif files <= 20 and loc < 3000 and patterns <= 3:
    stage = 2

# Stage 3: Production
else:
    stage = 3
```

Plus analysis of:
- Design patterns (Factory, Repository, Service, etc.)
- Architecture layers (models, services, controllers, etc.)
- Directory structure complexity

### Confidence Levels

- **High** - Clear indicators, trust the recommendation
- **Medium** - Borderline, manual review recommended
- **Low** - Conflicting signals, definitely review manually

---

## 🤝 Philosophy in Practice

### Real Example: API Development

**Week 1 (Stage 1):**
```python
# main.py - 150 lines
# All in one file, hardcoded, works
```

**Week 3 (Stage 2 - pain felt):**
```
api/
  routes.py      # Routes separated
  handlers.py    # Logic extracted
  models.py      # Data structures
  main.py        # Entry point
```

**Month 3 (Stage 3 - scale needed):**
```
api/
  routes/        # Route modules
  services/      # Business logic
  models/        # Data layer
  middleware/    # Cross-cutting
  tests/         # Comprehensive
```

**The framework prevents jumping to Month 3 structure in Week 1.**

---

## 📖 Background

This framework emerged from experience developing with Claude Code and other AI assistants.

**The pattern:** AI is incredibly helpful but tends toward over-engineering. It's easier to suggest a Repository pattern than to question if it's needed.

**The solution:** Explicit stage rules that AI must follow. Automatic detection of project maturity. Specialized subagents that understand context.

**The result:** Better software, faster. Simple when simple suffices. Complex when complexity is justified.

---

## 🎬 Next Steps

1. **Read [USAGE.md](./USAGE.md)** for complete guide
2. **Initialize a project** with `init_project.py`
3. **Check stage** of existing projects
4. **Use subagents** for stage-appropriate guidance
5. **Re-assess** after major changes

---

## 📊 Project Status

**Current Version:** 3.0 (Stage Detection Integration)

**Recent Updates:**
- ✅ Automatic stage detection (v3.0)
- ✅ Integrated subagents (v2.5)
- ✅ Removed prompt library focus (v2.0)
- ✅ Project initialization (v1.0)

**Roadmap:**
- [ ] Stage transition validation
- [ ] Team collaboration features
- [ ] IDE integrations
- [ ] Web dashboard

---

## 🙋 FAQ

**Q: Do I have to follow the stages strictly?**
A: No. They're guides, not rules. Adapt to your context.

**Q: Can I customize stage rules?**
A: Yes. Edit `.claude/02-stageX-rules.md` files directly.

**Q: What if stage detection is wrong?**
A: Manual override: edit `01-current-phase.md` directly.

**Q: Does this work without Claude Code?**
A: Yes. The framework works with any AI assistant or human development.

**Q: What about non-Python projects?**
A: Fully supported. Detection works for Python, JavaScript/TypeScript, Java, Go, Rust, Ruby, PHP, C/C++, and more.

---

## 📝 License

MIT License - Use freely, commercially or personally.

---

## 🤝 Contributing

This is an open methodology. Adapt, extend, share your improvements.

Key areas for contribution:
- Detection algorithm refinements
- New subagent types
- Stage rule improvements
- Language-specific criteria

---

**Built with:** Python, YAGNI principles, and experience from too many over-engineered prototypes.

**Maintained by:** The "let's keep it simple" philosophy.

---

*"The best architecture is the one you add when you need it, not the one you designed when you didn't."*
