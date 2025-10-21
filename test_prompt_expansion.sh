#!/bin/bash
# Test script for prompt expansion feature

set -e  # Exit on error

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

PROJECT_NAME="test-prompt-expansion-$$"
echo "🧪 Testing Prompt Expansion Feature"
echo "===================================="
echo ""

# Test 1: Initialize project
echo "Test 1: Initialize project..."
python init_project.py "$PROJECT_NAME"
if [ -d "$PROJECT_NAME" ]; then
    echo "✓ Project created"
else
    echo "✗ Project creation failed"
    exit 1
fi

# Test 2: Verify prompts directory exists
echo "Test 2: Verify prompts directory..."
if [ -d "$PROJECT_NAME/docs/prompts" ]; then
    echo "✓ Prompts directory exists"
else
    echo "✗ Prompts directory missing"
    exit 1
fi

# Test 3: Count prompt files
PROMPT_COUNT=$(find "$PROJECT_NAME/docs/prompts" -name "*.md" ! -name "README.md" | wc -l)
if [ "$PROMPT_COUNT" -eq 35 ]; then
    echo "✓ Found 35 prompt files"
else
    echo "✗ Expected 35 prompts, found $PROMPT_COUNT"
    exit 1
fi

# Test 4: Verify categories exist
EXPECTED_CATEGORIES="debugging refactoring architecture testing planning emergency evolution"
for category in $EXPECTED_CATEGORIES; do
    if [ -d "$PROJECT_NAME/docs/prompts/$category" ]; then
        echo "✓ Category '$category' exists"
    else
        echo "✗ Category '$category' missing"
        exit 1
    fi
done

# Test 5: Test prompt_helper.py list
echo "Test 5: Test prompt_helper list..."
LISTED_PROMPTS=$(python prompt_helper.py list | grep -c "^  -" || true)
if [ "$LISTED_PROMPTS" -eq 35 ]; then
    echo "✓ prompt_helper lists 35 prompts"
else
    echo "✗ Expected 35 prompts, listed $LISTED_PROMPTS"
    exit 1
fi

# Test 6: Test prompt_helper.py show
echo "Test 6: Test prompt_helper show..."
if python prompt_helper.py show debugging/stuck > /dev/null 2>&1; then
    echo "✓ prompt_helper show works"
else
    echo "✗ prompt_helper show failed"
    exit 1
fi

# Test 7: Verify README exists
echo "Test 7: Verify README in prompts..."
if [ -f "$PROJECT_NAME/docs/prompts/README.md" ]; then
    echo "✓ README.md exists in prompts/"
else
    echo "✗ README.md missing"
    exit 1
fi

# Cleanup (commented out for inspection)
# rm -rf "$PROJECT_NAME"

echo ""
echo "===================================="
echo "✓ All tests passed!"
echo "Test project created at: $PROJECT_NAME"
echo ""
