#!/usr/bin/env python3
"""
Claude Prompt Library - Project Initializer
Phase 2: Enhanced documentation support
"""

import sys
from pathlib import Path
from datetime import datetime
import shutil


def replace_placeholders(dest_path, replacements):
    """Replace placeholders in all .md files in dest_path"""
    for md_file in dest_path.rglob("*.md"):
        content = md_file.read_text(encoding="utf-8")

        for placeholder, value in replacements.items():
            content = content.replace(placeholder, value)

        md_file.write_text(content, encoding="utf-8")


if __name__ == "__main__":
    # 1. Parse arguments
    if len(sys.argv) != 2:
        print("Usage: python init_project.py <project-name>")
        sys.exit(1)

    project_name = sys.argv[1]

    # 2. Setup paths
    script_dir = Path(__file__).parent
    template_source = script_dir / "templates" / "basic" / ".claude"
    template_docs = script_dir / "templates" / "docs"

    dest_dir = Path(project_name)
    dest_claude = dest_dir / ".claude"
    dest_docs = dest_dir / "docs"

    # 3. Validate templates exist
    if not template_source.exists():
        print(f"Error: Template not found at {template_source}")
        sys.exit(1)

    if not template_docs.exists():
        print(f"Error: Docs template not found at {template_docs}")
        sys.exit(1)

    # 4. Create destination directories if needed
    dest_dir.mkdir(parents=True, exist_ok=True)
    dest_claude.mkdir(exist_ok=True)
    dest_docs.mkdir(exist_ok=True)

    # 5. Copy only missing .claude/ template files
    template_files = [
        "00-project-brief.md",
        "01-current-phase.md",
        "02-stage1-rules.md",
        "02-stage2-rules.md",
        "02-stage3-rules.md"
    ]

    files_copied = []
    files_skipped = []

    for filename in template_files:
        source_file = template_source / filename
        dest_file = dest_claude / filename

        if dest_file.exists():
            files_skipped.append(filename)
        else:
            shutil.copy2(source_file, dest_file)
            files_copied.append(filename)

    # 6. Replace placeholders ONLY in newly copied files
    if files_copied:
        replacements = {
            "{{PROJECT_NAME}}": project_name,
            "{{DATE}}": datetime.now().strftime("%Y-%m-%d"),
            "{{YEAR}}": str(datetime.now().year)
        }

        for filename in files_copied:
            dest_file = dest_claude / filename
            content = dest_file.read_text(encoding="utf-8")

            for placeholder, value in replacements.items():
                content = content.replace(placeholder, value)

            dest_file.write_text(content, encoding="utf-8")

    # 7. Copy reference documentation files
    reference_files = [
        "PROMPT_LIBRARY.md",
        "QUICK_START.md",
        "STAGES_COMPARISON.md",
        "CLAUDE_CODE_REFERENCE.md"
    ]

    ref_files_copied = []
    ref_files_skipped = []

    for filename in reference_files:
        source_file = template_docs / filename
        dest_file = dest_docs / filename

        if dest_file.exists():
            ref_files_skipped.append(filename)
        else:
            shutil.copy2(source_file, dest_file)
            ref_files_copied.append(filename)

    # 8. Success message
    print(f"✓ Project '{project_name}' initialized!")
    print(f"✓ Claude context files at: {dest_claude}")
    print(f"✓ Reference docs at: {dest_docs}")

    if files_copied:
        print(f"\nAdded {len(files_copied)} .claude/ file(s):")
        for f in files_copied:
            print(f"  + {f}")

    if files_skipped:
        print(f"\nSkipped {len(files_skipped)} existing .claude/ file(s):")
        for f in files_skipped:
            print(f"  - {f}")

    if ref_files_copied:
        print(f"\nAdded {len(ref_files_copied)} reference doc(s):")
        for f in ref_files_copied:
            print(f"  + {f}")

    if ref_files_skipped:
        print(f"\nSkipped {len(ref_files_skipped)} existing reference doc(s):")
        for f in ref_files_skipped:
            print(f"  - {f}")

    print(f"\nNext steps:")
    print(f"  cd {project_name}")
    print(f"  cat docs/QUICK_START.md  # Read this first")
    print(f"  # Open with Claude Code")