@echo off
REM Virtual Microphone Driver Installation Script

echo ========================================
echo Virtual Microphone Driver Installation
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

REM Enable test signing mode
echo Enabling test signing mode...
bcdedit /set testsigning on
if %errorLevel% neq 0 (
    echo Warning: Failed to enable test signing mode.
    echo You may need to enable it manually.
)

echo.
echo Installing Virtual Microphone Driver...

REM Remove old driver if exists
pnputil /delete-driver vmic.inf /uninstall /force >nul 2>&1

REM Add the driver package
pnputil /add-driver "%~dp0inf\vmic.inf" /install
if %errorLevel% neq 0 (
    echo Error: Failed to install driver package.
    pause
    exit /b 1
)

echo.
echo Creating device node...

REM Create the device using devcon or pnputil
REM Note: You may need to install Windows SDK for devcon.exe
REM devcon install "%~dp0inf\vmic.inf" Root\VirtualMicrophone

echo.
echo ========================================
echo Installation completed!
echo ========================================
echo.
echo IMPORTANT: You may need to restart your computer
echo for the changes to take effect.
echo.
echo After restart, the Virtual Microphone should appear
echo in your sound settings as both a playback and
echo recording device.
echo.
pause

