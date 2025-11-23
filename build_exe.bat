@echo off
REM ========================================
REM Script para generar ejecutable Windows
REM Sistema de Gestión IRC - UCM
REM ========================================

echo.
echo ========================================
echo   GENERADOR DE EJECUTABLE - IRC UCM
echo ========================================
echo.

REM Verificar que PyInstaller esté instalado
python -c "import PyInstaller" 2>nul
if errorlevel 1 (
    echo [ERROR] PyInstaller no está instalado
    echo.
    echo Instalando PyInstaller...
    pip install pyinstaller
)

echo.
echo [1/4] Limpiando builds anteriores...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
if exist GestionIRC.spec del /q GestionIRC.spec

echo [2/4] Generando ejecutable...
echo       Esto puede tardar varios minutos...
echo.

REM Crear el ejecutable
pyinstaller --name="GestionIRC" ^
    --onefile ^
    --windowed ^
    --add-data="src;src" ^
    --add-data="templates;templates" ^
    --add-data="data;data" ^
    --add-data="config.py;." ^
    --hidden-import="tkinter" ^
    --hidden-import="matplotlib" ^
    --hidden-import="pandas" ^
    --hidden-import="openpyxl" ^
    --hidden-import="google.auth" ^
    --hidden-import="google_auth_oauthlib" ^
    --hidden-import="googleapiclient" ^
    --hidden-import="pdfplumber" ^
    --hidden-import="pdfrw" ^
    --hidden-import="PIL" ^
    --collect-all="matplotlib" ^
    --collect-all="tkinter" ^
    main.py

if errorlevel 1 (
    echo.
    echo [ERROR] Falló la generación del ejecutable
    echo Revisa los errores arriba
    pause
    exit /b 1
)

echo.
echo [3/4] Copiando archivos necesarios...

REM Crear estructura de carpetas en dist
if not exist "dist\GestionIRC_Portable" mkdir "dist\GestionIRC_Portable"
if not exist "dist\GestionIRC_Portable\data\backups" mkdir "dist\GestionIRC_Portable\data\backups"
if not exist "dist\GestionIRC_Portable\templates" mkdir "dist\GestionIRC_Portable\templates"
if not exist "dist\GestionIRC_Portable\exports" mkdir "dist\GestionIRC_Portable\exports"
if not exist "dist\GestionIRC_Portable\logs" mkdir "dist\GestionIRC_Portable\logs"

REM Mover el ejecutable
move "dist\GestionIRC.exe" "dist\GestionIRC_Portable\"

REM Copiar README
copy "README.md" "dist\GestionIRC_Portable\" >nul

REM Crear archivo de ejemplo para credenciales
echo {"type": "service_account", ...} > "dist\GestionIRC_Portable\service_account.json.example"

echo.
echo [4/4] Limpiando archivos temporales...
rmdir /s /q build
del /q GestionIRC.spec

echo.
echo ========================================
echo   ¡EJECUTABLE GENERADO CORRECTAMENTE!
echo ========================================
echo.
echo Ubicación: dist\GestionIRC_Portable\GestionIRC.exe
echo.
echo Tamaño aproximado: 
dir "dist\GestionIRC_Portable\GestionIRC.exe" | find "GestionIRC.exe"
echo.
echo Para distribuir:
echo 1. Copia toda la carpeta GestionIRC_Portable
echo 2. Incluye el archivo de credenciales (service_account.json o credentials.json)
echo 3. Los usuarios solo necesitan ejecutar GestionIRC.exe
echo.

pause
