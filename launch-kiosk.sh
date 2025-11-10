#!/bin/bash
# launch-kiosk.sh - Launch Code Map in Docker with Chrome kiosk mode (Linux/macOS)

set -e

# ============================================================================
# Colors for output
# ============================================================================
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# ============================================================================
# Banner
# ============================================================================
echo -e "${BLUE}════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}  Code Map - Kiosk Mode Launcher (Linux/macOS)${NC}"
echo -e "${BLUE}════════════════════════════════════════════════════════${NC}\n"

# ============================================================================
# Check if Docker is running
# ============================================================================
echo -e "${BLUE}[INFO] Checking Docker...${NC}"
if ! sudo docker info > /dev/null 2>&1; then
    echo -e "${RED}[ERROR] Docker is not running.${NC}"
    echo -e "${YELLOW}Please start Docker first and try again.${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Docker is running${NC}\n"

# ============================================================================
# Prompt for project path
# ============================================================================
echo -e "${BLUE}[INFO] Select project to analyze${NC}"
read -p "Enter path to project directory (or press Enter for current directory): " PROJECT_PATH

# Use current directory if no path provided
if [ -z "$PROJECT_PATH" ]; then
    PROJECT_PATH="."
fi

# Resolve to absolute path
PROJECT_PATH=$(cd "$PROJECT_PATH" && pwd)

# Validate path exists
if [ ! -d "$PROJECT_PATH" ]; then
    echo -e "${RED}[ERROR] Directory '$PROJECT_PATH' does not exist.${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Project path: $PROJECT_PATH${NC}\n"

# Export for docker-compose
export PROJECT_PATH

# ============================================================================
# Start Docker container
# ============================================================================
echo -e "${BLUE}[INFO] Building and starting Docker container...${NC}"
echo -e "${YELLOW}(This may take a few minutes on first run)${NC}"

if sudo docker compose up -d --build; then
    echo -e "${GREEN}✓ Container started successfully${NC}\n"
else
    echo -e "${RED}[ERROR] Failed to start container${NC}"
    echo -e "${YELLOW}Check Docker logs with: sudo docker compose logs${NC}"
    exit 1
fi

# ============================================================================
# Wait for healthcheck
# ============================================================================
echo -e "${BLUE}[INFO] Waiting for application to start...${NC}"

# Wait up to 60 seconds for container to be healthy
TIMEOUT=60
ELAPSED=0
while [ $ELAPSED -lt $TIMEOUT ]; do
    HEALTH=$(sudo docker inspect --format='{{.State.Health.Status}}' code-map-app 2>/dev/null || echo "starting")

    if [ "$HEALTH" = "healthy" ]; then
        echo -e "${GREEN}✓ Application is ready${NC}\n"
        break
    fi

    echo -n "."
    sleep 2
    ELAPSED=$((ELAPSED + 2))
done

if [ $ELAPSED -ge $TIMEOUT ]; then
    echo -e "\n${YELLOW}[WARNING] Healthcheck timeout reached${NC}"
    echo -e "${YELLOW}Attempting to open browser anyway...${NC}\n"
fi

# ============================================================================
# Detect Chrome binary
# ============================================================================
echo -e "${BLUE}[INFO] Launching Chrome in kiosk mode...${NC}"

CHROME_BIN=""

# Try different Chrome binary names
if command -v google-chrome > /dev/null 2>&1; then
    CHROME_BIN="google-chrome"
elif command -v google-chrome-stable > /dev/null 2>&1; then
    CHROME_BIN="google-chrome-stable"
elif command -v chromium-browser > /dev/null 2>&1; then
    CHROME_BIN="chromium-browser"
elif command -v chromium > /dev/null 2>&1; then
    CHROME_BIN="chromium"
elif [ -f "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" ]; then
    CHROME_BIN="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
else
    echo -e "${RED}[ERROR] Chrome/Chromium not found${NC}"
    echo -e "${YELLOW}Please install Google Chrome or Chromium${NC}"
    echo -e "${BLUE}Application is running at: http://localhost:8080${NC}"
    echo -e "${BLUE}To stop: sudo docker compose down${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Found Chrome: $CHROME_BIN${NC}"

# ============================================================================
# Launch Chrome in kiosk mode
# ============================================================================
# --kiosk: Full screen mode without browser UI
# --app: Run as standalone app
# --no-first-run: Skip first run experience
# --disable-infobars: Hide info bars
# & : Run in background so script can complete

"$CHROME_BIN" \
    --kiosk \
    --app=http://localhost:8080 \
    --no-first-run \
    --disable-infobars \
    > /dev/null 2>&1 &

CHROME_PID=$!

# ============================================================================
# Success message
# ============================================================================
echo -e "\n${GREEN}════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}✓ Code Map launched successfully in kiosk mode!${NC}"
echo -e "${GREEN}════════════════════════════════════════════════════════${NC}\n"

echo -e "${BLUE}Controls:${NC}"
echo -e "  • Exit kiosk mode: ${YELLOW}Alt+F4${NC} or ${YELLOW}Ctrl+W${NC}"
echo -e "  • Application URL: ${YELLOW}http://localhost:8080${NC}"
echo -e "  • Analyzing project: ${YELLOW}$PROJECT_PATH${NC}"
echo -e "\n${BLUE}Docker commands:${NC}"
echo -e "  • View logs: ${YELLOW}sudo docker compose logs -f${NC}"
echo -e "  • Stop container: ${YELLOW}sudo docker compose down${NC}"
echo -e "  • Restart container: ${YELLOW}sudo docker compose restart${NC}\n"

# ============================================================================
# Wait for Chrome to close (optional)
# ============================================================================
# Uncomment to keep script running until Chrome closes
# wait $CHROME_PID
# echo -e "${BLUE}[INFO] Chrome closed. Container still running.${NC}"
# echo -e "${BLUE}To stop: sudo docker compose down${NC}"
