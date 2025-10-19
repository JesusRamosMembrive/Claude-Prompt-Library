#!/bin/bash
set -e

echo "🧪 Testing Claude-Prompt-Library Full Flow"
echo "=========================================="

# =============================================================================
# PHASE 1: Project Initialization
# =============================================================================
echo ""
echo "🔹 Testing project initialization..."

# Cleanup from previous test runs
rm -rf test-project-temp

# Test 1: Create new project
echo "  Test 1: Initialize new project..."
python init_project.py test-project-temp > /dev/null 2>&1 || true

# Verify project structure created
test -d test-project-temp/.claude || { echo "  ✗ .claude/ directory not created"; exit 1; }
test -d test-project-temp/docs || { echo "  ✗ docs/ directory not created"; exit 1; }
echo "  ✓ Project structure created"

# Test 2: Verify template files copied
echo "  Test 2: Check template files..."
test -f test-project-temp/.claude/00-project-brief.md || { echo "  ✗ project-brief.md not found"; exit 1; }
test -f test-project-temp/.claude/01-current-phase.md || { echo "  ✗ current-phase.md not found"; exit 1; }
test -f test-project-temp/.claude/settings.local.json || { echo "  ✗ settings.local.json not found"; exit 1; }
echo "  ✓ Template files copied"

# Test 3: Verify reference docs copied
echo "  Test 3: Check reference docs..."
test -f test-project-temp/docs/PROMPT_LIBRARY.md || { echo "  ✗ PROMPT_LIBRARY.md not found"; exit 1; }
test -f test-project-temp/docs/QUICK_START.md || { echo "  ✗ QUICK_START.md not found"; exit 1; }
echo "  ✓ Reference docs copied"

# Test 4: Check CLAUDE.md creation (may fail if claude not installed)
echo "  Test 4: Check CLAUDE.md..."
if [ -f test-project-temp/CLAUDE.md ]; then
    echo "  ✓ CLAUDE.md generated (claude CLI available)"

    # Test 5: Verify custom instructions appended
    if grep -q "Custom Workflow Instructions" test-project-temp/CLAUDE.md; then
        echo "  ✓ Custom instructions appended to CLAUDE.md"
    else
        echo "  ✗ Custom instructions not found in CLAUDE.md"
        exit 1
    fi
else
    echo "  ⚠️  CLAUDE.md not generated (claude CLI not available - this is OK)"
    echo "     In production, ensure Claude Code CLI is installed"
fi

# Cleanup
rm -rf test-project-temp

echo "✅ Phase 1 tests passed"

# =============================================================================
# PHASE 2.2: Prompt Helper
# =============================================================================
echo ""
echo "🔹 Testing prompt helper..."

# Test 1: List works without dependencies
echo "  Test 1: List command..."
python prompt_helper.py list | grep -q "DEBUGGING"
echo "  ✓ List works"

# Test 2: Show command
echo "  Test 2: Show command..."
python prompt_helper.py show debugging/stuck | grep -q "atascado"
echo "  ✓ Show works"

# Test 3: Flexible matching
echo "  Test 3: Flexible matching..."
python prompt_helper.py show debug/stuck | grep -q "atascado"
python prompt_helper.py show DEBUGGING/Stuck-In-Loop | grep -q "atascado"
echo "  ✓ Flexible matching works"

# Test 4: Error handling
echo "  Test 4: Error handling..."
python prompt_helper.py show nonexistent/prompt 2>&1 | grep -q -i "no se encontró"
echo "  ✓ Error handling works"

# Note: Interactive mode test skipped (requires terminal)
echo "  ℹ️  Interactive mode: manual test only"

echo "✅ Phase 2.2 tests passed"