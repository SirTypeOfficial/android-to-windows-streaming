@echo off
echo Registering Virtual Camera Driver...
echo This requires Administrator privileges.
echo.

net session >nul 2>&1
if %errorLevel% neq 0 (
    echo ERROR: This script must be run as Administrator!
    pause
    exit /b 1
)

if not exist "build\Release\VirtualCamera.ax" (
    echo ERROR: VirtualCamera.ax not found!
    echo Please build the project first using build.bat
    pause
    exit /b 1
)

regsvr32 /s "build\Release\VirtualCamera.ax"
if errorlevel 1 (
    echo Registration failed!
    pause
    exit /b 1
)

echo.
echo Virtual Camera Driver registered successfully!
echo You can now use it in applications like Zoom, Skype, Teams, etc.
echo.

pause

