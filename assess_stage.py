#!/usr/bin/env python3
"""
Stage Assessment Tool
Analyzes existing project and suggests appropriate development stage.
"""

import sys
from pathlib import Path

# Directories to ignore (common noise)
IGNORE_DIRS = {
    '.venv', 'venv', 'env', 'ENV',
    'node_modules',
    '.git',
    '__pycache__', '.pytest_cache', '.mypy_cache',
    'build', 'dist', '.eggs', '*.egg-info',
    '.tox', '.nox',
    'htmlcov', '.coverage',
    '.idea', '.vscode',
    'target',  # Rust/Java
    'bin', 'obj',  # C#
    'CMakeFiles', 'cmake-build-debug', 'cmake-build-release',  # CMake
    '.qmake.stash',  # Qt
}


def should_ignore(path):
    """
    Check if path should be ignored during analysis.

    Determines if a file or directory path should be excluded from stage detection
    analysis based on common development artifacts and dependencies.

    Args:
        path (Path): Path object to check (can be file or directory)

    Returns:
        bool: True if path should be ignored (matches IGNORE_DIRS or starts with '.'),
              False if path should be analyzed

    Notes:
        - Checks all path parts (parent directories)
        - Excludes hidden files/dirs (starting with '.')
        - Uses global IGNORE_DIRS set for common exclusions
        - Prevents noise from virtualenvs, node_modules, build artifacts, etc.
    """
    parts = path.parts
    for part in parts:
        if part in IGNORE_DIRS or part.startswith('.'):
            return True
    return False


def count_files_by_extension(root_dir, extensions):
    """
    Count files with given extensions, ignoring noise.

    Recursively counts code files with specified extensions while excluding
    directories that should be ignored (virtualenvs, node_modules, etc.).

    Args:
        root_dir (Path): Root directory to search from
        extensions (list): List of file extensions to count (e.g., ['.py', '.js'])

    Returns:
        int: Total count of files matching extensions (excluding ignored paths)

    Notes:
        - Uses rglob for recursive search
        - Applies should_ignore() filter to exclude noise
        - Extensions should include the dot (e.g., '.py' not 'py')
        - Returns 0 if no matching files found
    """
    count = 0
    for ext in extensions:
        for file_path in root_dir.rglob(f"*{ext}"):
            if not should_ignore(file_path.relative_to(root_dir)):
                count += 1
    return count


def count_lines_of_code(root_dir, extensions):
    """
    Estimate lines of code, ignoring noise.

    Recursively counts total lines in all code files with specified extensions,
    excluding ignored directories. Uses simple line counting (not complexity analysis).

    Args:
        root_dir (Path): Root directory to search from
        extensions (list): List of file extensions to count (e.g., ['.py', '.js'])

    Returns:
        int: Total lines of code across all matching files (excluding ignored paths)

    Notes:
        - Counts all lines (including comments, blank lines)
        - Uses UTF-8 encoding with error tolerance ('ignore' mode)
        - Silently skips files that can't be read (permissions, binary files, etc.)
        - Not a true SLOC metric - includes comments and whitespace
        - Fast approximation suitable for stage detection
    """
    total = 0
    for ext in extensions:
        for file_path in root_dir.rglob(f"*{ext}"):
            if should_ignore(file_path.relative_to(root_dir)):
                continue
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    total += len(f.readlines())
            except:
                pass
    return total


def detect_patterns(root_dir):
    """
    Detect common design patterns in code.

    Searches for indicators of design patterns by looking for pattern-related
    keywords in file and directory names throughout the project.

    Args:
        root_dir (Path): Root directory to search from

    Returns:
        list: List of detected pattern names (e.g., ['Factory Pattern', 'Repository'])
              Returns empty list if no patterns detected

    Patterns Detected:
        - Factory Pattern: 'factory', 'Factory', 'create_'
        - Singleton: 'singleton', 'Singleton', 'getInstance'
        - Observer: 'observer', 'Observer', 'subscribe', 'emit'
        - Strategy: 'strategy', 'Strategy'
        - Repository: 'repository', 'Repository', 'repo'
        - Service Layer: 'service', 'Service', 'services/'
        - Adapter: 'adapter', 'Adapter', 'adapters/'
        - Middleware: 'middleware', 'Middleware'

    Notes:
        - Heuristic-based detection (naming conventions)
        - Does not analyze code semantics
        - May have false positives/negatives
        - Returns deduplicated list
        - Applies should_ignore() filter
    """
    patterns_found = []

    # Check for common pattern indicators
    checks = {
        'Factory Pattern': ['factory', 'Factory', 'create_'],
        'Singleton': ['singleton', 'Singleton', 'getInstance'],
        'Observer': ['observer', 'Observer', 'subscribe', 'emit'],
        'Strategy': ['strategy', 'Strategy'],
        'Repository': ['repository', 'Repository', 'repo'],
        'Service Layer': ['service', 'Service', 'services/'],
        'Adapter': ['adapter', 'Adapter', 'adapters/'],
        'Middleware': ['middleware', 'Middleware'],
    }

    for pattern_name, keywords in checks.items():
        for keyword in keywords:
            # Check file/folder names (ignoring noise directories)
            matches = [p for p in root_dir.rglob(f"*{keyword}*")
                       if not should_ignore(p.relative_to(root_dir))]
            if matches:
                patterns_found.append(pattern_name)
                break

    return list(set(patterns_found))


def analyze_structure(root_dir):
    """
    Analyze project structure complexity.

    Examines directory organization to identify architectural patterns and
    measure structural complexity based on directory count and naming conventions.

    Args:
        root_dir (Path): Root directory to analyze

    Returns:
        dict: Dictionary containing:
            - directory_count (int): Total non-ignored directories in project
            - architectural_folders (list): List of detected architectural layer names
                                          (e.g., ['models', 'services', 'controllers'])

    Architectural Folders Detected:
        - MVC: models, views, controllers
        - Layered: services, repositories, handlers, routers
        - DDD: domain, infrastructure, application, presentation
        - Common: middleware, adapters, interfaces, api, core

    Notes:
        - Uses partial name matching (e.g., 'user_service' matches 'service')
        - Applies should_ignore() filter
        - Returns deduplicated architectural folder list
        - Directory count excludes ignored paths
    """
    # Count directories (excluding ignored ones)
    all_dirs = [d for d in root_dir.rglob("*")
                if d.is_dir() and not should_ignore(d.relative_to(root_dir))]
    dir_count = len(all_dirs)

    # Check for common architectural folders
    architectural_folders = [
        'models', 'views', 'controllers', 'services',
        'repositories', 'middleware', 'adapters', 'interfaces',
        'handlers', 'routers', 'api', 'core', 'domain',
        'infrastructure', 'application', 'presentation'
    ]

    found_folders = []
    for folder in architectural_folders:
        matches = [d for d in root_dir.rglob(f"*{folder}*")
                   if d.is_dir() and not should_ignore(d.relative_to(root_dir))]
        if matches:
            found_folders.append(folder)

    return {
        'directory_count': dir_count,
        'architectural_folders': list(set(found_folders))
    }


def assess_stage(project_path):
    """
    Assess project and recommend development stage.

    Analyzes a project's codebase metrics, structure, and patterns to recommend
    the appropriate development stage (Prototyping, Structuring, or Scaling).

    Args:
        project_path (str or Path): Path to project directory to analyze

    Returns:
        dict or None: Assessment dictionary containing:
            - recommended_stage (int): 1 (Prototyping), 2 (Structuring), or 3 (Scaling)
            - confidence (str): 'high', 'medium', or 'low'
            - reasons (list): Human-readable reasons explaining the recommendation
            - metrics (dict): Project metrics:
                - file_count (int): Number of code files
                - lines_of_code (int): Total lines of code (approximate)
                - directory_count (int): Number of directories
                - patterns_found (list): Detected design patterns
                - architectural_folders (list): Detected architectural layers
        Returns None if project_path doesn't exist

    Stage Decision Criteria:
        Stage 1 (Prototyping):
            - ≤3 files, <500 LOC
            - No patterns or architecture
            - Single file preferred

        Stage 2 (Structuring):
            - ≤20 files, <3000 LOC
            - ≤3 patterns
            - Basic architecture emerging
            - Sub-stages: Early (≤8 files), Mid (≤15 files), Late (>15 files)

        Stage 3 (Scaling):
            - >20 files OR >3000 LOC OR >3 patterns
            - Complex architecture
            - Multiple patterns in use

    Confidence Adjustments:
        - Medium if: Few files but high LOC (needs refactoring)
        - Medium if: Many files but no patterns (needs structure)

    Notes:
        - Ignores common noise (node_modules, .venv, etc.)
        - Prefers lower stage when borderline (simpler is better)
        - Returns detailed reasoning for transparency
        - Includes actionable warnings and hints
    """
    root = Path(project_path).resolve()

    if not root.exists():
        return None

    # Gather metrics
    code_extensions = [
        '.py',                                    # Python
        '.js', '.ts', '.jsx', '.tsx',            # JavaScript/TypeScript
        '.java',                                  # Java
        '.go',                                    # Go
        '.rs',                                    # Rust
        '.rb',                                    # Ruby
        '.php',                                   # PHP
        '.cpp', '.cc', '.cxx', '.c',             # C/C++
        '.h', '.hpp', '.hxx',                     # C/C++ Headers
    ]

    file_count = count_files_by_extension(root, code_extensions)
    loc = count_lines_of_code(root, code_extensions)
    patterns = detect_patterns(root)
    structure = analyze_structure(root)

    metrics = {
        'file_count': file_count,
        'lines_of_code': loc,
        'directory_count': structure['directory_count'],
        'patterns_found': patterns,
        'architectural_folders': structure['architectural_folders']
    }

    # Assessment logic
    reasons = []
    stage = 1
    confidence = 'medium'

    # Stage 1 indicators
    if file_count <= 3 and loc < 500:
        stage = 1
        confidence = 'high'
        reasons.append(f"Very small codebase ({file_count} files, ~{loc} LOC)")
        reasons.append("Appropriate for prototyping stage")

    # Stage 2 indicators
    elif file_count <= 20 and loc < 3000 and len(patterns) <= 3:
        stage = 2
        confidence = 'high'
        reasons.append(f"Medium codebase ({file_count} files, ~{loc} LOC)")

        if structure['architectural_folders']:
            arch_count = len(structure['architectural_folders'])
            reasons.append(f"Basic architecture present: {arch_count} layer(s)")

            if arch_count <= 3:
                reasons.append("Structure is appropriate for Stage 2")
            else:
                reasons.append("⚠️  Consider if architecture is justified")

        if patterns:
            reasons.append(f"Some patterns in use: {', '.join(patterns[:2])}")
            if len(patterns) > 2:
                reasons.append("⚠️  Multiple patterns - ensure they're justified")
        else:
            reasons.append("No clear patterns yet - good for Stage 2")

    # Stage 3 indicators
    elif file_count > 20 or loc > 3000 or len(patterns) > 3:
        stage = 3
        confidence = 'high'
        reasons.append(f"Large codebase ({file_count} files, ~{loc} LOC)")

        if len(patterns) > 0:
            reasons.append(f"Multiple patterns: {', '.join(patterns[:4])}")

        if len(structure['architectural_folders']) > 4:
            reasons.append(f"Complex architecture: {len(structure['architectural_folders'])} layers")

    # Edge cases - adjust confidence
    if file_count <= 5 and loc > 1500:
        confidence = 'medium'
        reasons.append("⚠️  Few files but high LOC - consider refactoring")

    if file_count > 30 and len(patterns) == 0:
        confidence = 'medium'
        reasons.append("⚠️  Many files but no patterns - may need structure")

    # Sub-stage hints for Stage 2
    if stage == 2:
        if file_count <= 8 and loc < 1000:
            reasons.append("📍 Early Stage 2 - just starting to structure")
        elif file_count <= 15 and loc < 2000:
            reasons.append("📍 Mid Stage 2 - structure emerging")
        else:
            reasons.append("📍 Late Stage 2 - consider Stage 3 transition")

    return {
        'recommended_stage': stage,
        'confidence': confidence,
        'reasons': reasons,
        'metrics': metrics
    }


def print_assessment(assessment):
    """
    Pretty print assessment results to console.

    Formats and displays stage assessment results in a readable format with
    emojis, metrics, reasoning, and actionable next steps.

    Args:
        assessment (dict or None): Assessment dictionary from assess_stage()
                                   If None, prints error message

    Returns:
        None (prints to stdout)

    Output Sections:
        1. Recommended stage with confidence indicator
        2. Project metrics (files, LOC, directories, patterns, architecture)
        3. Reasoning (why this stage was chosen)
        4. Stage explanation (what each stage means)
        5. Next steps (actionable recommendations)
        6. Confidence warnings (if confidence is not high)

    Notes:
        - Uses emojis for visual clarity
        - Formatted with separator lines for readability
        - Truncates long lists (e.g., max 6 architectural folders shown)
        - Includes stage philosophy and best practices
        - Provides specific next steps
    """
    if not assessment:
        print("❌ Could not assess project")
        return

    stage = assessment['recommended_stage']
    confidence = assessment['confidence']

    # Confidence emoji
    conf_emoji = {
        'high': '✅',
        'medium': '⚠️',
        'low': '❓'
    }

    print("\n" + "=" * 60)
    print("🎯 STAGE ASSESSMENT RESULTS")
    print("=" * 60)

    print(f"\n📊 Recommended Stage: {stage}")
    print(f"{conf_emoji[confidence]} Confidence: {confidence.upper()}")

    print(f"\n📈 Project Metrics:")
    print(f"  - Code Files: {assessment['metrics']['file_count']}")
    print(f"  - Lines of Code: ~{assessment['metrics']['lines_of_code']}")
    print(f"  - Directories: {assessment['metrics']['directory_count']}")

    if assessment['metrics']['patterns_found']:
        print(f"  - Patterns Detected: {', '.join(assessment['metrics']['patterns_found'])}")

    if assessment['metrics']['architectural_folders']:
        print(f"  - Architecture: {', '.join(assessment['metrics']['architectural_folders'][:6])}")

    print(f"\n💡 Reasoning:")
    for reason in assessment['reasons']:
        print(f"  • {reason}")

    print(f"\n📚 What This Means:")

    if stage == 1:
        print("  Stage 1 (Prototyping):")
        print("  - Keep it simple: functions over classes")
        print("  - One file preferred")
        print("  - No abstractions yet")
        print("  - Prove the concept works")
    elif stage == 2:
        print("  Stage 2 (Structuring):")
        print("  - Multiple files OK")
        print("  - Simple classes when needed")
        print("  - Add structure where it helps")
        print("  - 1-2 simple patterns max")
        print("  - Avoid premature optimization")
    else:
        print("  Stage 3 (Scaling):")
        print("  - Patterns are appropriate now")
        print("  - Architecture matters")
        print("  - Optimize for maintenance")
        print("  - Design for growth")

    print(f"\n📖 Next Steps:")
    print(f"  1. Review .claude/02-stage{stage}-rules.md")
    print(f"  2. Update .claude/01-current-phase.md with current stage")
    print(f"  3. Follow stage-appropriate practices")

    if confidence != 'high':
        print(f"\n⚠️  Confidence not high - consider:")
        print(f"  - Use Claude Code for deeper analysis")
        print(f"  - Read docs/STAGE_ASSESSMENT.md for manual criteria")
        print(f"  - When in doubt, choose lower stage (simpler)")

    print("\n" + "=" * 60)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python assess_stage.py <project-path>")
        print("\nExamples:")
        print("  python assess_stage.py .")
        print("  python assess_stage.py /path/to/my-project")
        print("\nNote: Automatically ignores .venv, node_modules, .git, etc.")
        sys.exit(1)

    project_path = sys.argv[1]

    print(f"🔍 Analyzing project: {project_path}")
    print("   (ignoring .venv, node_modules, .git, __pycache__, etc.)")

    assessment = assess_stage(project_path)
    print_assessment(assessment)