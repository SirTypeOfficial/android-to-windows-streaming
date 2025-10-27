@echo off
echo Building Virtual Camera Driver...

if not exist build mkdir build
cd build

cmake .. -G "Visual Studio 17 2022" -A x64
if errorlevel 1 (
    echo CMake configuration failed
    pause
    exit /b 1
)

cmake --build . --config Release
if errorlevel 1 (
    echo Build failed
    pause
    exit /b 1
)

echo.
echo Build completed successfully!
echo.
echo To register the filter, run as Administrator:
echo   regsvr32 build\Release\VirtualCamera.ax
echo.
echo To unregister:
echo   regsvr32 /u build\Release\VirtualCamera.ax
echo.

pause

