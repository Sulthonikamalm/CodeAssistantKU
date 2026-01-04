@echo off
echo ============================================
echo    VOICE CODE ASSISTANT - Starting...
echo ============================================
echo.

REM Check if config exists and has API key
findstr /C:"your_api_key_here" config.txt >nul 2>&1
if not errorlevel 1 (
    echo [ERROR] API Key belum diset!
    echo.
    echo Silakan edit file 'config.txt' dan masukkan API key Anda.
    echo.
    echo Cara mendapatkan API Key GRATIS:
    echo 1. Buka https://console.groq.com
    echo 2. Daftar/Login dengan Google
    echo 3. Buat API Key
    echo 4. Copy ke config.txt
    echo.
    pause
    exit /b 1
)

echo [OK] Config ditemukan
echo.
echo Menjalankan Voice Code Assistant...
echo.
echo ============================================
echo Shortcut: Ctrl + Alt + R
echo ============================================
echo.

python voice_assistant.py

pause
