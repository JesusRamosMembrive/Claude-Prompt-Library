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
test -f test-project-temp/.claude/02-stage1-rules.md || { echo "  ✗ stage1-rules.md not found"; exit 1; }
echo "  ✓ Template files copied"

# Test 3: Verify agents copied
echo "  Test 3: Check agents..."
test -d test-project-temp/.claude/agents || { echo "  ✗ agents/ directory not created"; exit 1; }
test -f test-project-temp/.claude/agents/architect-generic.md || { echo "  ✗ architect agent not found"; exit 1; }
test -f test-project-temp/.claude/agents/implementer.md || { echo "  ✗ implementer agent not found"; exit 1; }
test -f test-project-temp/.claude/agents/code-reviewer-optimized.md || { echo "  ✗ code-reviewer agent not found"; exit 1; }
test -f test-project-temp/.claude/agents/stage-keeper-architecture.md || { echo "  ✗ stage-keeper agent not found"; exit 1; }
echo "  ✓ Agents copied (4 agents)"

# Test 4: Verify reference docs copied
echo "  Test 4: Check reference docs..."
test -f test-project-temp/docs/STAGES_COMPARISON.md || { echo "  ✗ STAGES_COMPARISON.md not found"; exit 1; }
test -f test-project-temp/docs/QUICK_START.md || { echo "  ✗ QUICK_START.md not found"; exit 1; }
echo "  ✓ Reference docs copied"

# Test 5: Check CLAUDE.md creation (may fail if claude not installed)
echo "  Test 5: Check CLAUDE.md..."
if [ -f test-project-temp/CLAUDE.md ]; then
    echo "  ✓ CLAUDE.md generated (claude CLI available)"

    # Test 6: Verify custom instructions appended
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

echo "✅ Project initialization tests passed"
echo ""
echo "🎉 All tests passed!"
echo ""
echo "Next steps:"
echo "  - Run: python init_project.py <your-project-name>"
echo "  - Use assess_stage.py to detect project stage"
echo "  - Leverage stage-aware agents in .claude/agents/"
