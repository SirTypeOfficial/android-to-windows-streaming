@echo off
chcp 65001 >nul
echo ============================================
echo     فعال‌سازی OBS Virtual Camera
echo ============================================
echo.

:: بررسی نصب OBS
reg query "HKLM\SOFTWARE\OBS Studio" >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ OBS Studio نصب نشده است
    echo.
    echo لطفاً OBS Studio را از لینک زیر دانلود و نصب کنید:
    echo https://obsproject.com/
    echo.
    pause
    exit /b 1
)

echo ✓ OBS Studio یافت شد
echo.
echo راهنما:
echo 1. OBS Studio را باز کنید
echo 2. از منوی Tools گزینه "Start Virtual Camera" را انتخاب کنید
echo 3. OBS را باز نگه دارید
echo 4. برنامه این پروژه را اجرا کنید
echo.
echo توجه: برای استفاده از Virtual Camera، OBS باید در حال اجرا باشد
echo.

:: باز کردن OBS
echo آیا می‌خواهید OBS را الان باز کنید؟ (Y/N)
set /p choice=
if /i "%choice%"=="Y" (
    start "" "C:\Program Files\obs-studio\bin\64bit\obs64.exe"
    echo.
    echo ✓ OBS باز شد
    echo پس از فعال کردن Virtual Camera در OBS، برنامه را اجرا کنید
)

echo.
pause

