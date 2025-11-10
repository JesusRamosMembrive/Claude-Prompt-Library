@echo off
REM launch-kiosk.bat - Launch Code Map in Docker with Chrome kiosk mode (Windows)
setlocal enabledelayedexpansion

REM ============================================================================
REM Banner
REM ============================================================================
echo ========================================================
echo   Code Map - Kiosk Mode Launcher (Windows)
echo ========================================================
echo.

REM ============================================================================
REM Check if Docker is running
REM ============================================================================
echo [INFO] Checking Docker...
docker info >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Docker is not running.
    echo Please start Docker Desktop and try again.
    pause
    exit /b 1
)
echo [OK] Docker is running
echo.

REM ============================================================================
REM Prompt for project path
REM ============================================================================
echo [INFO] Select project to analyze
set /p PROJECT_PATH="Enter path to project directory (or press Enter for current directory): "

REM Use current directory if no path provided
if "%PROJECT_PATH%"=="" set PROJECT_PATH=.

REM Resolve to absolute path
pushd "%PROJECT_PATH%" 2>nul
if errorlevel 1 (
    echo [ERROR] Directory '%PROJECT_PATH%' does not exist.
    pause
    exit /b 1
)
set PROJECT_PATH=%CD%
popd

echo [OK] Project path: %PROJECT_PATH%
echo.

REM ============================================================================
REM Start Docker container
REM ============================================================================
echo [INFO] Building and starting Docker container...
echo (This may take a few minutes on first run)
echo.

docker-compose up -d --build
if errorlevel 1 (
    echo [ERROR] Failed to start container
    echo Check Docker logs with: docker-compose logs
    pause
    exit /b 1
)

echo [OK] Container started successfully
echo.

REM ============================================================================
REM Wait for application to start
REM ============================================================================
echo [INFO] Waiting for application to start...

REM Simple wait (30 seconds)
timeout /t 30 /nobreak >nul

echo [OK] Application should be ready
echo.

REM ============================================================================
REM Detect Chrome installation
REM ============================================================================
echo [INFO] Launching Chrome in kiosk mode...

set CHROME_PATH=

REM Try different Chrome installation paths
if exist "C:\Program Files\Google\Chrome\Application\chrome.exe" (
    set CHROME_PATH=C:\Program Files\Google\Chrome\Application\chrome.exe
) else if exist "C:\Program Files (x86)\Google\Chrome\Application\chrome.exe" (
    set CHROME_PATH=C:\Program Files ^(x86^)\Google\Chrome\Application\chrome.exe
) else if exist "%LOCALAPPDATA%\Google\Chrome\Application\chrome.exe" (
    set CHROME_PATH=%LOCALAPPDATA%\Google\Chrome\Application\chrome.exe
) else (
    echo [ERROR] Google Chrome not found
    echo Please install Google Chrome from: https://www.google.com/chrome/
    echo.
    echo Application is running at: http://localhost:8080
    echo To stop: docker-compose down
    pause
    exit /b 1
)

echo [OK] Found Chrome: %CHROME_PATH%

REM ============================================================================
REM Launch Chrome in kiosk mode
REM ============================================================================
REM --kiosk: Full screen mode without browser UI
REM --app: Run as standalone app
REM --no-first-run: Skip first run experience
REM --disable-infobars: Hide info bars

start "" "%CHROME_PATH%" ^
    --kiosk ^
    --app=http://localhost:8080 ^
    --no-first-run ^
    --disable-infobars

REM ============================================================================
REM Success message
REM ============================================================================
echo.
echo ========================================================
echo [SUCCESS] Code Map launched in kiosk mode!
echo ========================================================
echo.
echo Controls:
echo   - Exit kiosk mode: Alt+F4
echo   - Application URL: http://localhost:8080
echo   - Analyzing project: %PROJECT_PATH%
echo.
echo Docker commands:
echo   - View logs: docker-compose logs -f
echo   - Stop container: docker-compose down
echo   - Restart container: docker-compose restart
echo.
pause
