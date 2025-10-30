# Architecture: Stage-Aware Development Assistant

**Project Name**: `stage-keeper` (sugerencia - puedes cambiarlo)  
**Current Stage**: ETAPA 1 (Planning → Implementation)
**Target Stage**: ETAPA 1 (Prototipado)
**Complexity Level**: Minimal

## System Overview

A meta-development tool that analyzes Python codebases to detect their maturity stage (Prototipado, Estructuración, Escalado) and enforces stage-appropriate complexity rules when working with Claude Code. Prevents over-engineering by keeping developers honest about what their project actually needs.

## Problem It Solves

**Current pain**: Developers (including you) tend to over-engineer early-stage projects with abstractions, patterns, and "best practices" that aren't justified yet. Claude Code, being helpful, often suggests enterprise-level solutions for prototype problems.

**Solution**: Automatically detect project stage and inject stage-specific rules into Claude Code context, blocking inappropriate complexity.

## Stage 1 Implementation (Start Here)

### File Structure
```
stage-keeper/
├── detect_stage.py           # Main script (~150 LOC)
├── test_full_flow.sh         # Validation script
├── rules/
│   ├── stage1-rules.md      # Your existing files
│   ├── stage2-rules.md
│   └── stage3-rules.md
└── README.md                 # Basic usage
```

### Single Script Design (`detect_stage.py`)

```python
#!/usr/bin/env python3
"""
Stage Keeper - Detect project stage and enforce appropriate complexity.

Usage: python detect_stage.py [path_to_project]
"""

# Stage 1: Everything in one file, simple functions

def count_python_files(project_path):
    """Count .py files in project."""
    # Simple pathlib walk
    return file_count

def calculate_metrics(project_path):
    """Calculate basic metrics: LOC, files, complexity indicators."""
    metrics = {
        'files': count_python_files(project_path),
        'loc': count_total_lines(project_path),
        'has_classes': check_for_classes(project_path),
        'has_config': check_for_config_files(project_path),
        'has_tests': check_for_tests(project_path)
    }
    return metrics

def detect_stage(metrics):
    """Determine stage based on simple rules."""
    # ETAPA 1: PROTOTIPADO
    if metrics['files'] <= 3 and not metrics['has_classes']:
        return 'ETAPA 1: PROTOTIPADO'
    
    # ETAPA 2: ESTRUCTURACIÓN
    if metrics['files'] <= 7 and (metrics['has_classes'] or metrics['has_config']):
        return 'ETAPA 2: ESTRUCTURACIÓN'
    
    # ETAPA 3: ESCALADO
    return 'ETAPA 3: ESCALADO'

def load_rules(stage):
    """Load stage-specific rules from markdown files."""
    stage_num = extract_stage_number(stage)
    rules_file = f"rules/stage{stage_num}-rules.md"
    return read_file(rules_file)

def generate_report(metrics, stage, rules):
    """Output simple text report."""
    print(f"Stage Detected: {stage}")
    print(f"Files: {metrics['files']}, LOC: {metrics['loc']}")
    print("\nApplicable Rules:")
    print(rules)
    
def main():
    project_path = sys.argv[1] if len(sys.argv) > 1 else '.'
    
    metrics = calculate_metrics(project_path)
    stage = detect_stage(metrics)
    rules = load_rules(stage)
    
    generate_report(metrics, stage, rules)

if __name__ == '__main__':
    main()
```

## Technology Choices

### Core Stack
- **Language**: Python 3.10+ (stdlib only for Stage 1)
- **File analysis**: `pathlib` + `os.walk` - Simple, no dependencies
- **Pattern detection**: Basic `grep` or simple regex - Good enough for Stage 1
- **Output**: Plain text report - No fancy formatting needed

### Explicitly NOT Using (Yet)
- ❌ **AST parsing** - Wait until Stage 2, simple line counting works
- ❌ **Radon/McCabe** - Complexity analysis overkill for detecting stages
- ❌ **Click/Typer** - argparse is fine, CLI is simple
- ❌ **Rich/Colorama** - Pretty output is distraction
- ❌ **SQLite/JSON storage** - No persistence needed yet

## Detection Heuristics (Simple Rules)

```python
# ETAPA 1: PROTOTIPADO
files <= 3 AND no classes AND no config files

# ETAPA 2: ESTRUCTURACIÓN  
files <= 7 AND (has classes OR has config OR has multiple modules)

# ETAPA 3: ESCALADO
files > 7 OR has complex patterns OR distributed
```

**Why these rules?**
- Based on your actual stage definitions
- Easy to validate manually
- Clear, unambiguous criteria
- Can be wrong and still useful (iterate based on feedback)

## Implementation Order

### Session 1: Core Detection
1. **File counter** - Walk directory, count .py files
2. **LOC counter** - Simple line count (ignore comments later if needed)
3. **Class detector** - Grep for "^class " pattern
4. **Stage decision** - Apply simple if/elif rules
5. **Text output** - Print stage and metrics

**Success**: Can run on 3 test projects and get reasonable stage detection

### Session 2: Rule Integration  
1. **Rules loader** - Read markdown files from rules/
2. **Report generator** - Output stage + rules together
3. **test_full_flow.sh** - Test on known projects

**Success**: Script outputs stage + applicable rules

### Session 3: Pain-Driven Improvements
**Don't plan this yet** - Wait to see what hurts after using it

## Test Strategy (Stage 1 = Minimal)

### `test_full_flow.sh`
```bash
#!/bin/bash
# Test on known projects

echo "Testing Stage 1 detection (single file project)..."
python detect_stage.py test_projects/prototype

echo "Testing Stage 2 detection (structured project)..."  
python detect_stage.py test_projects/structured

echo "Testing Stage 3 detection (complex project)..."
python detect_stage.py test_projects/production

echo "All tests passed!"
```

### Test Projects (Manual Classification)
- `test_projects/prototype/` - 1 file, 80 LOC, no classes → Should detect Stage 1
- `test_projects/structured/` - 5 files, 500 LOC, has classes → Should detect Stage 2
- `test_projects/production/` - 15 files, 2000 LOC, complex → Should detect Stage 3

**Stage 1 testing philosophy**: Manual validation is fine. Automated testing when it hurts.

## Evolution Triggers

**→ ETAPA 2** - Add complexity when:
- Used on 5+ projects and detection is consistently wrong
- Need multiple detection strategies (file-based, git-based, metric-based)
- Want to persist detection history
- Need configuration for custom thresholds

**Specific pain points that would justify Stage 2**:
- "I need to tune thresholds per project type"
- "File count alone is too simplistic"
- "I want to track stage changes over time"
- "Need to integrate with Claude Code hooks"

**→ ETAPA 3** - Only when:
- Multiple teams using it
- Need plugin system for custom detectors
- Real-time monitoring required
- Complex integration with IDE/tools

## Integration with Claude Code (Future)

**Stage 1**: Manual workflow
```bash
# Before starting Claude Code session:
python detect_stage.py ~/my-project
# Copy-paste rules into Claude Code context manually
```

**Stage 2** (when manual is painful):
- Claude Code pre-session hook
- Or simple MCP server
- Auto-inject rules into context

**Stage 3** (when team adoption happens):
- Full MCP server with persistence
- IDE integration
- Real-time rule updates

## What NOT to Do in Stage 1

### Prohibited Complexity
- ❌ **Classes/OOP** - Functions are sufficient
- ❌ **Configuration files** - Hardcode thresholds in script
- ❌ **Plugins/extensions** - Single detection algorithm only
- ❌ **Caching/optimization** - Script runs in <1 second, don't care
- ❌ **Logging framework** - print() statements are fine
- ❌ **Fancy CLI** - Basic argparse or positional args
- ❌ **Error handling beyond basics** - Let it crash, fix when it hurts

### Tempting Features to Defer
- "What if we support multiple languages?" → Wait for actual need
- "Should we use AST parsing?" → Only if file-based detection fails
- "Could we add ML to learn patterns?" → Way too early
- "What about tracking stage history?" → No persistence needed yet
- "Should we make it a package?" → Single script is distributable enough

## Success Criteria (Stage 1)

- [ ] Can detect stage for 3 test projects correctly
- [ ] Runs in < 5 seconds on typical project
- [ ] Output is clear and actionable
- [ ] Includes relevant stage rules in output
- [ ] test_full_flow.sh passes
- [ ] README explains basic usage

**Not success criteria**:
- Perfect detection accuracy (70% is fine for Stage 1)
- Beautiful output (readable text is enough)
- Fast execution (< 5 sec is plenty)
- Comprehensive edge case handling

## Risk Assessment

**Low Risk** (proceed with confidence):
- Simple stdlib Python, hard to mess up
- Clear success criteria
- Easy to test manually
- Throwaway if it doesn't work

**Medium Risk** (watch for these):
- Detection heuristics might be too simplistic → OK, iterate based on real usage
- Rules might not match all project types → Fine, you're the only user initially

**High Risk** (avoid these pitfalls):
- Over-engineering the detection algorithm → Remember: simple rules, iterate later
- Trying to be comprehensive → Focus on your 2 projects first
- Building infrastructure before validation → One script, then see what hurts

## Dogfooding Strategy

**Use stage-keeper on itself**:
1. Run `detect_stage.py` on `stage-keeper/` directory
2. Should detect ETAPA 1 (1 file, simple functions)
3. If it suggests Stage 2 complexity → Your detection is wrong!
4. This is the ultimate validation

**Use stage-keeper on chess detector**:
1. Start chess detector in parallel
2. Run stage-keeper on it at each session
3. Verify stage matches your intuition
4. Document when/why stage transitions

## Next Steps

1. **Create project structure** (5 min)
2. **Implement core detection** (Session 1, ~1 hour)
3. **Test on 3 known projects** (30 min)
4. **Use on real projects for 1 week** (dogfooding)
5. **Document pain points** (when they emerge)
6. **Decide if Stage 2 is justified** (based on evidence)

---

**Remember**: This is ETAPA 1. The goal is to validate the idea works, not to build a perfect tool. Ship it, use it, learn from it, then decide if it's worth evolving.

**Anti-Pattern Alert**: If you find yourself thinking "but what if we need to..." → STOP. Write it down in a "future.md" file and forget about it until Stage 1 is validated.
