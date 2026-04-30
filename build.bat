@echo off
REM Script para compilar el .exe con icono

echo Compilando File Organizer con icono...
echo.

REM Verificar si PyInstaller está instalado
pip list | findstr /i pyinstaller >nul
if errorlevel 1 (
    echo PyInstaller no está instalado. Instalando...
    pip install pyinstaller
)

REM Compilar con PyInstaller
echo.
echo Creando ejecutable...
pyinstaller --onefile --windowed --icon=icon.ico --name="File Organizer" main.py

echo.
echo ¡Hecho! El ejecutable está en la carpeta "dist"
pause
