@echo off
REM ========================================
REM Script de Instalación Paso a Paso
REM Para Windows - Evita errores comunes
REM ========================================

echo.
echo ========================================
echo   INSTALACION DE DEPENDENCIAS - IRC UCM
echo ========================================
echo.

REM Verificar Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python no esta instalado o no esta en el PATH
    echo.
    echo Por favor instala Python 3.8+ desde https://python.org
    pause
    exit /b 1
)

echo [OK] Python instalado correctamente
python --version
echo.

REM Actualizar pip, setuptools y wheel
echo [1/5] Actualizando herramientas base...
python -m pip install --upgrade pip setuptools wheel
if errorlevel 1 (
    echo [ERROR] No se pudieron actualizar las herramientas base
    pause
    exit /b 1
)
echo [OK] Herramientas base actualizadas
echo.

REM Instalar dependencias de Google API
echo [2/5] Instalando Google Sheets API...
pip install google-auth==2.23.4
pip install google-auth-oauthlib==1.1.0
pip install google-auth-httplib2==0.1.1
pip install google-api-python-client==2.108.0
if errorlevel 1 (
    echo [WARNING] Hubo problemas con Google API, pero continuamos...
)
echo [OK] Google API instalada
echo.

REM Instalar procesamiento de datos
echo [3/5] Instalando pandas, openpyxl...
pip install pandas==2.1.4
pip install openpyxl==3.1.2
pip install xlsxwriter==3.1.9
if errorlevel 1 (
    echo [ERROR] Error al instalar pandas/openpyxl
    pause
    exit /b 1
)
echo [OK] Pandas y Excel instalados
echo.

REM Instalar matplotlib (puede tardar)
echo [4/5] Instalando matplotlib (puede tardar 1-2 min)...
pip install matplotlib==3.8.2
pip install Pillow==10.1.0
if errorlevel 1 (
    echo [ERROR] Error al instalar matplotlib
    pause
    exit /b 1
)
echo [OK] Matplotlib instalado
echo.

REM Instalar PDFs y utilidades
echo [5/5] Instalando utilidades (PDFs, logs, etc)...
pip install PyPDF2==3.0.1
pip install pdfplumber==0.10.3
pip install reportlab==4.0.7
pip install tkcalendar==1.6.1
pip install python-dateutil==2.8.2
pip install pytz==2023.3.post1
pip install colorlog==6.8.0

REM pdfrw puede dar problemas en Windows, intentar pero no es crítico
echo.
echo Intentando instalar pdfrw (no critico si falla)...
pip install pdfrw==0.4
if errorlevel 1 (
    echo [WARNING] pdfrw no se pudo instalar (no es critico)
)
echo.

REM PyInstaller
echo Instalando PyInstaller...
pip install pyinstaller==6.3.0
if errorlevel 1 (
    echo [ERROR] Error al instalar PyInstaller
    pause
    exit /b 1
)
echo.

echo ========================================
echo   INSTALACION COMPLETADA
echo ========================================
echo.
echo Resumen:
pip list | findstr "google-auth pandas matplotlib openpyxl pyinstaller"
echo.
echo Para verificar que todo funciona:
echo   python main.py
echo.
echo Para generar el ejecutable:
echo   build_exe.bat
echo.
pause
