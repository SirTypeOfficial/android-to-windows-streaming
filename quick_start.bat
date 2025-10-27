@echo off
echo ========================================
echo Android to Windows Streaming - Quick Start
echo ========================================
echo.

:menu
echo Select an option:
echo 1. Setup Windows App
echo 2. Run Windows App
echo 3. Build Virtual Camera Driver
echo 4. Register Virtual Camera Driver
echo 5. Unregister Virtual Camera Driver
echo 6. Exit
echo.
set /p choice="Enter your choice (1-6): "

if "%choice%"=="1" goto setup_windows
if "%choice%"=="2" goto run_windows
if "%choice%"=="3" goto build_vcam
if "%choice%"=="4" goto register_vcam
if "%choice%"=="5" goto unregister_vcam
if "%choice%"=="6" goto end
goto menu

:setup_windows
echo.
echo Setting up Windows application...
cd windows-app
call setup.bat
cd ..
goto menu

:run_windows
echo.
echo Running Windows application...
cd windows-app
call run.bat
cd ..
goto menu

:build_vcam
echo.
echo Building Virtual Camera Driver...
cd virtual-camera
call build.bat
cd ..
goto menu

:register_vcam
echo.
echo Registering Virtual Camera Driver...
echo This requires Administrator privileges!
cd virtual-camera
call register.bat
cd ..
goto menu

:unregister_vcam
echo.
echo Unregistering Virtual Camera Driver...
cd virtual-camera
call unregister.bat
cd ..
goto menu

:end
echo.
echo Goodbye!
pause
exit

