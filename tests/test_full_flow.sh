#!/bin/bash
set -e

echo "🧪 Starting Full Flow Test - Claude Prompt Library"

# Change to project root directory
cd "$(dirname "$0")/.."

# =============================================================================
# PHASE 1 & 2: Template & Docs Copier
# =============================================================================
echo "🔹 Testing template and docs copier..."

# Test 1: New project gets everything
echo "  Test 1: New project creation..."
python init_project.py test-new

# Check .claude/ files
if [ ! -f "test-new/.claude/00-project-brief.md" ]; then
    echo "  ✗ Missing .claude/ templates"
    exit 1
fi

# Check docs/ files (NEW)
if [ ! -f "test-new/docs/PROMPT_LIBRARY.md" ]; then
    echo "  ✗ Missing docs/PROMPT_LIBRARY.md"
    exit 1
fi

if [ ! -f "test-new/docs/QUICK_START.md" ]; then
    echo "  ✗ Missing docs/QUICK_START.md"
    exit 1
fi

if [ ! -f "test-new/docs/STAGES_COMPARISON.md" ]; then
    echo "  ✗ Missing docs/STAGES_COMPARISON.md"
    exit 1
fi

if [ ! -f "test-new/docs/CLAUDE_CODE_REFERENCE.md" ]; then
    echo "  ✗ Missing docs/CLAUDE_CODE_REFERENCE.md"
    exit 1
fi

echo "  ✓ All files copied correctly"

# Test 2: Re-run skips existing
echo "  Test 2: Skip existing files..."
python init_project.py test-new 2>&1 | grep -q "Skipped"
echo "  ✓ Skips existing files correctly"

# Test 3: Placeholders replaced
echo "  Test 3: Placeholder replacement..."
if grep -q "{{PROJECT_NAME}}" test-new/.claude/*.md; then
    echo "  ✗ Placeholders not replaced"
    exit 1
fi
echo "  ✓ Placeholders replaced correctly"

# Test 4: Coexist with Claude Code settings
echo "  Test 4: Coexistence with Claude Code..."
mkdir -p test-existing/.claude
echo '{"permissions": {}}' > test-existing/.claude/settings.local.json
python init_project.py test-existing

if [ ! -f "test-existing/.claude/settings.local.json" ]; then
    echo "  ✗ Claude Code settings deleted!"
    exit 1
fi

if [ ! -f "test-existing/docs/PROMPT_LIBRARY.md" ]; then
    echo "  ✗ Docs not copied to existing project"
    exit 1
fi

echo "  ✓ Coexists with Claude Code settings"

echo "✅ All tests passed!"

# =============================================================================
# CLEANUP
# =============================================================================
echo "🧹 Cleaning up..."
rm -rf test-new test-existing

echo "🎉 Phase 1 & 2 tests complete!"