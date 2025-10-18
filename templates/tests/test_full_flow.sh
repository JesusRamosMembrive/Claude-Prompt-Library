#!/bin/bash
set -e  # Exit on any error

echo "🧪 Starting Full Flow Test - Claude Prompt Library"

# =============================================================================
# PHASE 1: Template Copier (NOT IMPLEMENTED YET)
# Implemented: TBD
# =============================================================================
echo "🔹 Phase 1: Testing template copier..."

# TODO: When init_project.py is implemented, add tests like:
# 1. Run: python init_project.py test-project
# 2. Verify: test-project/.claude/ exists
# 3. Verify: All 5 template files exist
# 4. Verify: Placeholders are replaced
# 5. Verify: Can't overwrite existing directory

echo "⚠️  Phase 1 not implemented yet - skipping tests"

# =============================================================================
# CLEANUP
# =============================================================================
echo "🧹 Cleaning up test data..."
# When tests run, clean up any test projects created
# rm -rf test-project
# rm -rf test-*

echo "🎉 All tests passed! (or skipped)"
echo ""
echo "Next steps:"
echo "1. Implement init_project.py"
echo "2. Add real tests to this file"
echo "3. Run: bash tests/test_full_flow.sh"
