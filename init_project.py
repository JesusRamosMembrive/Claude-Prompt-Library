#!/usr/bin/env python3
"""
Claude Prompt Library - Project Initializer
Phase 2: Enhanced documentation support
"""

import sys
from pathlib import Path
from datetime import datetime
import shutil
import subprocess
import os


def run_claude_init(project_path):
    """
    Execute 'claude -p "/init"' to generate CLAUDE.md in the project directory.

    Args:
        project_path: Path object pointing to the project directory

    Returns:
        bool: True if successful, False otherwise
    """
    print("\n🤖 Running Claude Code /init to generate CLAUDE.md...")

    try:
        # Check if claude command exists
        result = subprocess.run(
            ["which", "claude"],
            capture_output=True,
            text=True
        )

        if result.returncode != 0:
            print("⚠️  Warning: 'claude' command not found in PATH")
            print("   Please install Claude Code CLI: https://docs.claude.com/")
            return False

        # Execute claude -p "/init" in the project directory
        result = subprocess.run(
            ["claude", "-p", "/init"],
            cwd=str(project_path),
            capture_output=True,
            text=True,
            timeout=120  # 2 minute timeout
        )

        # Verify CLAUDE.md was actually created
        claude_md = project_path / "CLAUDE.md"
        if claude_md.exists():
            print("✓ CLAUDE.md generated successfully")
            return True
        else:
            if result.returncode == 0:
                print("⚠️  Warning: claude /init completed but CLAUDE.md not generated")
                print("   This usually happens with empty projects. Skipping /init step.")
            else:
                print(f"⚠️  Warning: claude /init failed with error:")
                print(f"   {result.stderr}")
            return False

    except subprocess.TimeoutExpired:
        print("⚠️  Warning: claude /init timed out after 2 minutes")
        return False
    except Exception as e:
        print(f"⚠️  Warning: Failed to run claude /init: {e}")
        return False


def append_custom_instructions(claude_md_path, custom_instructions_template):
    """
    Append custom workflow instructions to CLAUDE.md.

    Args:
        claude_md_path: Path object to CLAUDE.md file
        custom_instructions_template: Path object to CUSTOM_INSTRUCTIONS.md template

    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Read custom instructions template
        if not custom_instructions_template.exists():
            print(f"⚠️  Warning: Custom instructions template not found at {custom_instructions_template}")
            return False

        custom_content = custom_instructions_template.read_text(encoding="utf-8")

        # Check if CLAUDE.md exists
        if not claude_md_path.exists():
            print(f"⚠️  Warning: CLAUDE.md not found at {claude_md_path}")
            return False

        # Read current CLAUDE.md content
        current_content = claude_md_path.read_text(encoding="utf-8")

        # Check if custom instructions already appended
        if "## Custom Workflow Instructions" in current_content:
            print("ℹ️  Custom instructions already present in CLAUDE.md, skipping...")
            return True

        # Append custom instructions with clear separator
        separator = "\n\n---\n\n# Custom Workflow Instructions\n\n"
        separator += "<!-- Added by claude-prompt-library init_project.py -->\n\n"

        updated_content = current_content.rstrip() + separator + custom_content

        # Write updated content
        claude_md_path.write_text(updated_content, encoding="utf-8")

        print("✓ Custom workflow instructions appended to CLAUDE.md")
        return True

    except Exception as e:
        print(f"⚠️  Warning: Failed to append custom instructions: {e}")
        return False


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
        "02-stage3-rules.md",
        "settings.local.json"
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

    # 8. Run Claude Code /init and append custom instructions
    claude_md_path = dest_dir / "CLAUDE.md"
    custom_instructions_template = template_source / "CUSTOM_INSTRUCTIONS.md"

    # Only run /init if CLAUDE.md doesn't exist
    if not claude_md_path.exists():
        init_success = run_claude_init(dest_dir)

        # If /init didn't create CLAUDE.md (empty project), create a basic one
        if not claude_md_path.exists():
            print("\nℹ️  Creating basic CLAUDE.md since /init didn't generate one...")
            basic_content = f"""# {project_name}

This file contains project context and instructions for Claude Code.

## Project Overview

*Add project description here*

## Tech Stack

*Add technologies used here*

## Getting Started

*Add setup instructions here*

"""
            claude_md_path.write_text(basic_content, encoding="utf-8")
            print("✓ Basic CLAUDE.md created")
    else:
        print(f"\nℹ️  CLAUDE.md already exists at {claude_md_path}")
        print(f"   Assuming it was generated by /init, proceeding to append custom instructions...")

    # Append custom instructions if CLAUDE.md exists or was just created
    if claude_md_path.exists():
        append_custom_instructions(claude_md_path, custom_instructions_template)

    # 9. Success message
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