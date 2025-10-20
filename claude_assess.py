#!/usr/bin/env python3
"""Generate detailed assessment report for manual review."""
import sys
from pathlib import Path
import subprocess

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python claude_assess.py <project-path>")
        sys.exit(1)

    project_path = Path(sys.argv[1])

    # Get filtered tree
    try:
        tree = subprocess.check_output(
            ["tree", "-L", "3", "-I", ".venv|node_modules|.git|__pycache__|*.pyc|*.egg-info"],
            cwd=str(project_path),
            text=True,
            stderr=subprocess.DEVNULL
        )
    except:
        tree = "tree command not available - install with: sudo apt install tree"

    print("""# Stage Assessment - Deep Analysis

## Project Structure
```""")
    print(tree)
    print("""```

## Automated Assessment

""")

    # Run assess_stage.py
    try:
        assess = subprocess.check_output(
            ["python", "assess_stage.py", str(project_path)],
            text=True
        )
        print(assess)
    except:
        print("Could not run assess_stage.py")

    print("""

## Instructions for Claude Code

Analyze this project and determine the appropriate development stage:

1. **Review Structure**: Look at directory organization, file names, patterns
2. **Assess Complexity**: Consider LOC, file count, architecture layers
3. **Identify Patterns**: Look for service layers, repositories, factories, etc.
4. **Evaluate Quality**: Are files too large? Is structure appropriate?

### Decision Criteria:

**Stage 2 (Late):**
- 15-20 files, 2000-3000 LOC
- 2-3 architectural layers
- 1-2 simple patterns
- Files might be large but not overly complex
- Good for this stage: keep patterns simple

**Stage 3 (Early):**
- 15-25 files, 3000-6000 LOC  
- 3-4 architectural layers
- Multiple patterns emerging
- Might benefit from more splitting
- Good for this stage: patterns are appropriate

### Your Assessment:

Please provide:
- **Recommended Stage**: 2 (Late) or 3 (Early)
- **Confidence**: High/Medium/Low
- **Key Evidence**: What in the structure supports this?
- **Specific Recommendations**: Should files be split? Patterns needed? Any refactoring?
- **Current State**: What's working well? What needs attention?

Consider that Stage 2 → Stage 3 is gradual. If borderline, choose based on:
- **Choose Stage 2 if**: Structure works, no pain points, patterns not needed yet
- **Choose Stage 3 if**: Files are large, would benefit from patterns, architecture needed
""")
