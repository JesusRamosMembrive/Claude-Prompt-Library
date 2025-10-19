## Installation

### Quick start (command mode only)
```bash
git clone [your-repo]
cd claude-prompt-library
python prompt_helper.py list
```

### Full install (with interactive mode)
```bash
pip install -r requirements.txt
python prompt_helper.py  # Opens interactive menu
```

### Dependencies
- **simple-term-menu** (required for interactive mode only)
  - Command mode works without it
  - Error message guides you if missing
- **pyperclip** (optional)
  - For clipboard support in both modes
  - Works without it, just shows text

## Usage

### Interactive Mode
```bash
python prompt_helper.py
# Beautiful terminal menu, arrow keys navigation
```

### Command Mode (scriptable)
```bash
# List all prompts
python prompt_helper.py list

# Show specific prompt
python prompt_helper.py show debugging/stuck-in-loop

# Copy to clipboard
python prompt_helper.py copy planning/feature-planning

# Flexible matching (case insensitive, spaces/dashes)
python prompt_helper.py show debug/stuck
python prompt_helper.py show DEBUGGING/Stuck-In-Loop  # Also works
```

### Examples
```bash
# In a script
PROMPT=$(python prompt_helper.py show debugging/stuck)
echo "$PROMPT" > my_debug_session.txt

# Quick reference
python prompt_helper.py show architecture/design | less
```