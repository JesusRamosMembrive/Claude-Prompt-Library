#!/bin/bash
set -e  # Exit on any error

echo "🧪 Starting Full Flow Test - Claude Prompt Library"

# =============================================================================
# PHASE 1: Template Copier
# =============================================================================
echo "🔹 Phase 1: Testing template copier..."

# Test 1: Run init_project.py
echo "  ✓ Running: python init_project.py test-project"
python init_project.py test-project

# Test 2: Verify .claude directory exists
echo "  ✓ Verifying: test-project/.claude/ exists"
[ -d "test-project/.claude" ] || { echo "❌ .claude directory not found"; exit 1; }

# Test 3: Verify all 5 template files exist
echo "  ✓ Verifying: All 5 template files exist"
[ -f "test-project/.claude/00-project-brief.md" ] || { echo "❌ 00-project-brief.md not found"; exit 1; }
[ -f "test-project/.claude/01-current-phase.md" ] || { echo "❌ 01-current-phase.md not found"; exit 1; }
[ -f "test-project/.claude/02-stage1-rules.md" ] || { echo "❌ 02-stage1-rules.md not found"; exit 1; }
[ -f "test-project/.claude/02-stage2-rules.md" ] || { echo "❌ 02-stage2-rules.md not found"; exit 1; }
[ -f "test-project/.claude/02-stage3-rules.md" ] || { echo "❌ 02-stage3-rules.md not found"; exit 1; }

# Test 4: Verify placeholders are replaced
echo "  ✓ Verifying: Placeholders are replaced"
if grep -r "{{PROJECT_NAME}}" test-project/.claude/; then
    echo "❌ Found unreplaced {{PROJECT_NAME}} placeholder"
    exit 1
fi
if grep -r "{{DATE}}" test-project/.claude/; then
    echo "❌ Found unreplaced {{DATE}} placeholder"
    exit 1
fi
if grep -r "{{YEAR}}" test-project/.claude/; then
    echo "❌ Found unreplaced {{YEAR}} placeholder"
    exit 1
fi

# Test 5: Verify can't overwrite existing directory
echo "  ✓ Verifying: Cannot overwrite existing project"
if python init_project.py test-project 2>/dev/null; then
    echo "❌ Script should fail when directory exists"
    exit 1
fi

echo "  ✅ Phase 1 tests passed!"

# =============================================================================
# CLEANUP
# =============================================================================
echo "🧹 Cleaning up test data..."
rm -rf test-project

echo ""
echo "🎉 All tests passed!"
echo ""
echo "✅ Phase 1 implementation complete"
echo "   init_project.py is working correctly"
