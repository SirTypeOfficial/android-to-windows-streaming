@echo off
chcp 65001 >nul
title Android Stream Receiver

echo ================================================
echo    Android Stream Receiver - راه‌اندازی سریع
echo ================================================
echo.

:: بررسی Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python نصب نشده است
    echo.
    echo لطفاً Python 3.8 یا بالاتر نصب کنید
    pause
    exit /b 1
)

echo ✓ Python یافت شد
echo.

:: بررسی وابستگی‌ها
echo بررسی و نصب وابستگی‌ها...
pip install -q -r requirements.txt
if %errorlevel% neq 0 (
    echo ⚠ مشکل در نصب وابستگی‌ها
    pause
)
echo.

:: بررسی دستگاه‌های مجازی
echo بررسی دستگاه‌های مجازی...
python setup_virtual_devices.py
echo.

:: اجرای برنامه اصلی
echo ================================================
echo    شروع برنامه...
echo ================================================
echo.

python main.py

echo.
echo برنامه بسته شد
pause

