#!/usr/bin/env python3
"""
Claude Prompt Library - Project Initializer
Phase 1: Simple template copier
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
    dest_dir = Path(project_name)
    dest_claude = dest_dir / ".claude"

    # 3. Validate destination doesn't exist
    if dest_dir.exists():
        print(f"Error: Directory '{project_name}' already exists")
        sys.exit(1)

    # 4. Validate template exists
    if not template_source.exists():
        print(f"Error: Template not found at {template_source}")
        sys.exit(1)

    # 5. Copy templates
    print(f"Creating project '{project_name}'...")
    dest_dir.mkdir(parents=True)
    shutil.copytree(template_source, dest_claude)

    # 6. Replace placeholders
    replacements = {
        "{{PROJECT_NAME}}": project_name,
        "{{DATE}}": datetime.now().strftime("%Y-%m-%d"),
        "{{YEAR}}": str(datetime.now().year)
    }

    replace_placeholders(dest_claude, replacements)

    # 7. Success message
    print(f"✓ Project '{project_name}' created successfully!")
    print(f"✓ Claude context files available at: {dest_claude}")
    print(f"\nNext steps:")
    print(f"  cd {project_name}")
    print(f"  # Open with Claude Code")
