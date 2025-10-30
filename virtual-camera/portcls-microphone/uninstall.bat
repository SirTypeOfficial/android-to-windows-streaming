@echo off
REM Virtual Microphone Driver Uninstallation Script

echo ========================================
echo Virtual Microphone Driver Uninstallation
echo ========================================
echo.

REM Check for administrator privileges
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo Error: This script requires administrator privileges.
    echo Please run as Administrator.
    pause
    exit /b 1
)

echo Uninstalling Virtual Microphone Driver...

REM Remove the device
echo Removing device...
REM devcon remove Root\VirtualMicrophone

REM Remove the driver package
echo Removing driver package...
pnputil /delete-driver vmic.inf /uninstall /force
if %errorLevel% neq 0 (
    echo Warning: Failed to remove driver package.
    echo The driver may not be installed.
)

echo.
echo ========================================
echo Uninstallation completed!
echo ========================================
echo.
echo The Virtual Microphone driver has been removed.
echo You may need to restart your computer.
echo.
pause

