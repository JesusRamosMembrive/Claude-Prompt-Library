# Actualiza tests/test_full_flow.sh para validar nuevo comportamiento:

#!/bin/bash
set -e

echo "🧪 Starting Full Flow Test - Claude Prompt Library"

# Test 1: New project
echo "Test 1: New project creation..."
python init_project.py test-new
[ -f "test-new/.claude/00-project-brief.md" ] || exit 1
echo "  ✓ Passed"

# Test 2: Existing project with Claude Code
echo "Test 2: Coexistence with Claude Code settings..."
mkdir -p test-existing/.claude
echo '{"permissions": {}}' > test-existing/.claude/settings.local.json
python init_project.py test-existing
[ -f "test-existing/.claude/00-project-brief.md" ] || exit 1
[ -f "test-existing/.claude/settings.local.json" ] || exit 1
echo "  ✓ Passed"

# Test 3: Re-run on same project (skip existing)
echo "Test 3: Skip existing files..."
python init_project.py test-new 2>&1 | grep -q "Skipped"
echo "  ✓ Passed"

# Test 4: Placeholders replaced
echo "Test 4: Placeholder replacement..."
! grep -q "{{PROJECT_NAME}}" test-new/.claude/*.md || exit 1
echo "  ✓ Passed"

# Cleanup
rm -rf test-new test-existing
echo "✅ All tests passed!"