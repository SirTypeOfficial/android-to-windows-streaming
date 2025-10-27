@echo off
echo Unregistering Virtual Camera Driver...
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
    pause
    exit /b 1
)

regsvr32 /u /s "build\Release\VirtualCamera.ax"
if errorlevel 1 (
    echo Unregistration failed!
    pause
    exit /b 1
)

echo.
echo Virtual Camera Driver unregistered successfully!
echo.

pause

