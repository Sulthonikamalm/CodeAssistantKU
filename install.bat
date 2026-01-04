@echo off
echo ============================================
echo    VOICE CODE ASSISTANT - Installer
echo ============================================
echo.

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python tidak ditemukan!
    echo Silakan install Python dari https://python.org
    pause
    exit /b 1
)

echo [OK] Python ditemukan
echo.

REM Install dependencies
echo Installing dependencies...
echo.
pip install -r requirements.txt

echo.
echo ============================================
echo    INSTALASI SELESAI!
echo ============================================
echo.
echo Langkah selanjutnya:
echo 1. Edit file 'config.txt'
echo 2. Masukkan GROQ_API_KEY Anda
echo 3. Jalankan 'run.bat' untuk memulai
echo.
pause
