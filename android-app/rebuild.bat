@echo off
echo ==========================================
echo Building Android App
echo ==========================================

cd /d "%~dp0"

echo Cleaning previous build...
call gradlew.bat clean

echo Building debug APK...
call gradlew.bat assembleDebug

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ==========================================
    echo Build successful!
    echo APK location: build\outputs\apk\debug\android-app-debug.apk
    echo ==========================================
    echo.
    echo Install on device with:
    echo adb install -r build\outputs\apk\debug\android-app-debug.apk
) else (
    echo.
    echo ==========================================
    echo Build failed! Check errors above.
    echo ==========================================
)

pause

