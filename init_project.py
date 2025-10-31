#!/usr/bin/env python3
"""
Stage-Aware Development Framework - Project Initializer
Phase 3: Automatic stage detection integration
"""

import sys
from pathlib import Path
from datetime import datetime
import shutil
import subprocess
import os
import argparse


def run_claude_init(project_path):
    """
    Execute 'claude -p "/init"' to generate CLAUDE.md in the project directory.

    This function invokes the Claude Code CLI tool to automatically generate a CLAUDE.md
    file with project-specific context. It verifies the command exists, executes it with
    a 2-minute timeout, and validates the output file was created.

    Args:
        project_path (Path): Path object pointing to the project directory where CLAUDE.md
                            will be generated

    Returns:
        bool: True if CLAUDE.md was successfully generated, False if the command failed,
              timed out, or the file was not created

    Raises:
        No exceptions raised - all errors are caught and logged with warnings

    Notes:
        - Requires 'claude' command in PATH (Claude Code CLI)
        - Automatically handles empty projects (where /init may not generate output)
        - 2-minute timeout prevents hanging on large projects
        - Non-blocking: warnings printed but execution continues on failure
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

    This function reads the CUSTOM_INSTRUCTIONS.md template containing stage-aware
    workflow instructions and appends it to an existing CLAUDE.md file. It checks
    for duplicates to avoid appending multiple times.

    Args:
        claude_md_path (Path): Path object to the target CLAUDE.md file
        custom_instructions_template (Path): Path object to CUSTOM_INSTRUCTIONS.md template
                                            containing workflow instructions

    Returns:
        bool: True if instructions were successfully appended or already present,
              False if template/CLAUDE.md not found or write operation failed

    Notes:
        - Idempotent: checks for existing instructions marker before appending
        - Adds clear HTML comment marker for traceability
        - Preserves existing CLAUDE.md content (append-only)
        - Uses UTF-8 encoding to handle international characters
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
    """
    Replace placeholders in all .md files in dest_path.

    Recursively searches for all Markdown files and performs simple string
    replacement for project-specific values like project name and dates.

    Args:
        dest_path (Path): Root directory to search for .md files
        replacements (dict): Dictionary mapping placeholder strings to replacement values
                            (e.g., {"{{PROJECT_NAME}}": "my-project"})

    Returns:
        None

    Notes:
        - Processes .md files recursively
        - Uses UTF-8 encoding
        - Modifies files in-place
        - No validation of placeholder format
    """
    for md_file in dest_path.rglob("*.md"):
        content = md_file.read_text(encoding="utf-8")

        for placeholder, value in replacements.items():
            content = content.replace(placeholder, value)

        md_file.write_text(content, encoding="utf-8")


def detect_project_stage(project_path):
    """
    Import and run stage detection from assess_stage.py.

    Dynamically imports the assess_stage module and runs analysis on the specified
    project directory to determine its development maturity stage (1, 2, or 3).

    Args:
        project_path (str or Path): Path to the project directory to analyze

    Returns:
        dict or None: Assessment dictionary containing:
            - recommended_stage (int): 1 (Prototyping), 2 (Structuring), or 3 (Scaling)
            - confidence (str): 'high', 'medium', or 'low'
            - reasons (list): List of reasoning strings explaining the recommendation
            - metrics (dict): Project metrics (file_count, lines_of_code, patterns, etc.)
        Returns None if detection fails (module not found, analysis error, etc.)

    Notes:
        - Requires assess_stage.py in same directory
        - Graceful degradation: returns None on any error
        - Non-blocking: errors logged as warnings
    """
    try:
        # Import assess_stage function dynamically
        import assess_stage
        assessment = assess_stage.assess_stage(project_path)
        return assessment
    except Exception as e:
        print(f"⚠️  Warning: Could not detect stage: {e}")
        return None


def update_current_phase_with_stage(current_phase_file, assessment):
    """
    Update 01-current-phase.md with detected stage information.

    Injects or updates a "Detected Stage" section in the current-phase tracking file
    with auto-detection results, including metrics, reasoning, and recommended actions.

    Args:
        current_phase_file (Path): Path to 01-current-phase.md file
        assessment (dict): Assessment dictionary from detect_project_stage() containing
                          stage, confidence, reasons, and metrics

    Returns:
        bool: True if file was successfully updated, False if assessment is None,
              file not found, or write operation failed

    Notes:
        - Idempotent: replaces existing "Detected Stage" section if present
        - Truncates reasoning to top 5 reasons for readability
        - Adds timestamp for traceability
        - Includes actionable next steps
        - Uses regex for section replacement
    """
    if not assessment:
        return False

    try:
        content = current_phase_file.read_text(encoding="utf-8")

        # Build stage detection section
        stage = assessment['recommended_stage']
        confidence = assessment['confidence']
        reasons = assessment['reasons']

        stage_section = f"\n\n## 🎯 Detected Stage: Stage {stage} ({confidence.title()} Confidence)\n\n"
        stage_section += f"**Auto-detected on:** {datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n"
        stage_section += "**Detection reasoning:**\n"
        for reason in reasons[:5]:  # First 5 reasons
            stage_section += f"- {reason}\n"

        stage_section += f"\n**Metrics:**\n"
        stage_section += f"- Files: {assessment['metrics']['file_count']}\n"
        stage_section += f"- LOC: ~{assessment['metrics']['lines_of_code']}\n"
        stage_section += f"- Patterns: {', '.join(assessment['metrics']['patterns_found'][:3]) if assessment['metrics']['patterns_found'] else 'None'}\n"

        stage_section += f"\n**Recommended actions:**\n"
        stage_section += f"- Follow rules in `.claude/02-stage{stage}-rules.md` (and `.codex/stage{stage}-rules.md` if using Codex)\n"
        stage_section += f"- Use stage-aware subagents for guidance\n"
        stage_section += f"- Re-assess stage after significant changes\n"

        # Check if stage section already exists
        if "## 🎯 Detected Stage:" in content:
            # Replace existing section
            import re
            pattern = r"## 🎯 Detected Stage:.*?(?=\n##|\Z)"
            content = re.sub(pattern, stage_section.strip(), content, flags=re.DOTALL)
        else:
            # Append new section
            content = content.rstrip() + stage_section

        current_phase_file.write_text(content, encoding="utf-8")
        return True

    except Exception as e:
        print(f"⚠️  Warning: Could not update current-phase.md: {e}")
        return False


if __name__ == "__main__":
    # 1. Parse arguments
    parser = argparse.ArgumentParser(
        description="Stage-Aware Development Framework - Initialize projects with automatic stage detection"
    )
    parser.add_argument(
        "project_path",
        help="Project name (for new projects) or path (for existing projects with --existing)"
    )
    parser.add_argument(
        "--existing",
        action="store_true",
        help="Add framework to existing project and auto-detect stage"
    )
    parser.add_argument(
        "--detect-only",
        action="store_true",
        help="Only detect and display stage, don't initialize framework"
    )
    parser.add_argument(
        "--agent",
        choices=["claude", "codex", "both"],
        default="both",
        help="Which agent integrations to prepare (default: both)"
    )

    args = parser.parse_args()

    agent_choice = args.agent.lower()
    prepare_claude = agent_choice in ("claude", "both")
    prepare_codex = agent_choice in ("codex", "both")

    # Handle detect-only mode
    if args.detect_only:
        print(f"🔍 Detecting stage for: {args.project_path}")
        assessment = detect_project_stage(args.project_path)
        if assessment:
            import assess_stage
            assess_stage.print_assessment(assessment)
        else:
            print("❌ Could not detect project stage")
        sys.exit(0)

    # 2. Setup paths
    script_dir = Path(__file__).parent
    template_claude = script_dir / "templates" / "basic" / ".claude"
    template_codex = script_dir / "templates" / "basic" / ".codex"
    template_docs = script_dir / "templates" / "docs"

    if args.existing:
        # Existing project mode
        dest_dir = Path(args.project_path).resolve()
        project_name = dest_dir.name

        if not dest_dir.exists():
            print(f"❌ Error: Project directory not found: {dest_dir}")
            sys.exit(1)

        print(f"📦 Adding Stage-Aware Framework to existing project: {project_name}")
        print(f"   at: {dest_dir}")
    else:
        # New project mode
        project_name = args.project_path
        dest_dir = Path(project_name)
        print(f"🆕 Creating new project: {project_name}")

    dest_claude = dest_dir / ".claude"
    dest_codex = dest_dir / ".codex"
    dest_docs = dest_dir / "docs"

    # 3. Validate templates exist
    if not template_claude.exists():
        print(f"Error: Template not found at {template_claude}")
        sys.exit(1)

    if not template_docs.exists():
        print(f"Error: Docs template not found at {template_docs}")
        sys.exit(1)

    if prepare_codex and not template_codex.exists():
        print(f"Error: Codex template not found at {template_codex}")
        sys.exit(1)

    # 4. Create destination directories if needed
    dest_dir.mkdir(parents=True, exist_ok=True)
    dest_claude.mkdir(exist_ok=True)
    if prepare_codex:
        dest_codex.mkdir(exist_ok=True)
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
        source_file = template_claude / filename
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

    # 6.5. Copy subagents directory
    subagents_source = template_claude / "subagents"
    subagents_dest = dest_claude / "subagents"

    if subagents_source.exists():
        if not subagents_dest.exists():
            shutil.copytree(subagents_source, subagents_dest)
            print(f"✓ Copied subagents/ directory with {len(list(subagents_source.glob('*.md')))} subagent(s)")
        else:
            # Directory exists, copy individual files that don't exist
            subagents_dest.mkdir(exist_ok=True)
            copied_count = 0
            for subagent_file in subagents_source.glob("*.md"):
                dest_subagent = subagents_dest / subagent_file.name
                if not dest_subagent.exists():
                    shutil.copy2(subagent_file, dest_subagent)
                    copied_count += 1
            if copied_count > 0:
                print(f"✓ Updated subagents/ with {copied_count} new subagent(s)")
            else:
                print(f"ℹ️  subagents/ directory up to date")

    # 6.6. Copy Codex templates if requested
    codex_files_copied = []
    codex_files_skipped = []

    if prepare_codex:
        codex_template_files = [
            "AGENTS.md",
            "stage1-rules.md",
            "stage2-rules.md",
            "stage3-rules.md",
        ]

        for filename in codex_template_files:
            source_file = template_codex / filename
            dest_file = dest_codex / filename

            if dest_file.exists():
                codex_files_skipped.append(filename)
            else:
                shutil.copy2(source_file, dest_file)
                codex_files_copied.append(filename)

        if codex_files_copied:
            replacements = {
                "{{PROJECT_NAME}}": project_name,
                "{{DATE}}": datetime.now().strftime("%Y-%m-%d"),
                "{{YEAR}}": str(datetime.now().year)
            }

            for filename in codex_files_copied:
                dest_file = dest_codex / filename
                content = dest_file.read_text(encoding="utf-8")
                for placeholder, value in replacements.items():
                    content = content.replace(placeholder, value)
                dest_file.write_text(content, encoding="utf-8")

    # 7. Copy reference documentation files
    reference_files = [
        "QUICK_START.md",
        "STAGES_COMPARISON.md",
        "STAGE_CRITERIA.md",
        "GUIDE.md",
        "CLAUDE_CODE_REFERENCE.md",
        "CODEX_CLI_REFERENCE.md"
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
    if prepare_claude:
        claude_md_path = dest_dir / "CLAUDE.md"
        custom_instructions_template = template_claude / "CUSTOM_INSTRUCTIONS.md"

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

    # 8.5. Auto-detect stage for existing projects
    if args.existing:
        print("\n🔍 Detecting project stage...")
        assessment = detect_project_stage(dest_dir)

        if assessment:
            stage = assessment['recommended_stage']
            confidence = assessment['confidence']
            print(f"✓ Detected Stage {stage} ({confidence} confidence)")

            # Update 01-current-phase.md with detection results
            current_phase_file = dest_claude / "01-current-phase.md"
            if current_phase_file.exists():
                if update_current_phase_with_stage(current_phase_file, assessment):
                    print(f"✓ Updated 01-current-phase.md with stage detection")
                    print(f"   View full report: python assess_stage.py {dest_dir}")
        else:
            print("⚠️  Could not detect stage automatically")
            print("   Run manually: python assess_stage.py <project-path>")

    # 9. Success message
    print(f"✓ Project '{project_name}' initialized!")
    if prepare_claude:
        print(f"✓ Claude context files at: {dest_claude}")
    else:
        print(f"ℹ️ Claude integration skipped (--agent=codex); core stage files stored at: {dest_claude}")
    if prepare_codex:
        print(f"✓ Codex instructions at: {dest_codex}")
    else:
        print("ℹ️ Codex integration skipped (--agent=claude)")
    print(f"✓ Reference docs at: {dest_docs}")

    if files_copied:
        print(f"\nAdded {len(files_copied)} .claude/ file(s):")
        for f in files_copied:
            print(f"  + {f}")

    if files_skipped:
        print(f"\nSkipped {len(files_skipped)} existing .claude/ file(s):")
        for f in files_skipped:
            print(f"  - {f}")

    if prepare_codex:
        if codex_files_copied:
            print(f"\nAdded {len(codex_files_copied)} .codex/ file(s):")
            for f in codex_files_copied:
                print(f"  + {f}")

        if codex_files_skipped:
            print(f"\nSkipped {len(codex_files_skipped)} existing .codex/ file(s):")
            for f in codex_files_skipped:
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
    if prepare_claude and prepare_codex:
        print(f"  # Agents ready: Claude Code + Codex CLI")
    elif prepare_claude:
        print(f"  # Agent ready: Claude Code")
    elif prepare_codex:
        print(f"  # Agent ready: Codex CLI")
