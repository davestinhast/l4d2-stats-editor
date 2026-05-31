@echo off
cd /d "%~dp0"
title Build L4D2 Stats Editor
echo.

REM ── Paso 1: compilar sam_bridge.cs con .NET Framework 32-bit ───────────────
echo [1/3] Compilando sam_bridge.exe (C# usando SAM.API.dll)...

set CSC=C:\Windows\Microsoft.NET\Framework\v4.0.30319\csc.exe
if not exist "%CSC%" (
    echo  ERROR: csc.exe no encontrado en %CSC%
    echo  Necesitas .NET Framework 4.x instalado.
    pause & exit /b 1
)

REM Copia SAM.API.dll a la carpeta de trabajo
copy /Y "C:\Users\INHO\Desktop\XD\SAM.API.dll" "%~dp0SAM.API.dll" >nul

"%CSC%" /r:SAM.API.dll /platform:x86 /optimize+ /out:sam_bridge.exe sam_bridge.cs
if %errorlevel% neq 0 (
    echo.
    echo  ERROR: Fallo al compilar sam_bridge.cs
    pause & exit /b 1
)
echo  sam_bridge.exe OK

REM ── Paso 2: instalar dependencias Python ───────────────────────────────────
echo.
echo [2/3] Instalando dependencias Python (rich + pyinstaller)...
pip install rich pyinstaller --quiet
if %errorlevel% neq 0 (
    echo  ERROR: pip fallo.
    pause & exit /b 1
)
echo  OK

REM ── Paso 3: compilar l4d2_editor.py como .exe ─────────────────────────────
echo.
echo [3/3] Compilando l4d2_editor.exe...
python -m PyInstaller ^
    --onefile ^
    --console ^
    --name "L4D2_Stats_Editor" ^
    --add-data "sam_bridge.exe;." ^
    --add-data "SAM.API.dll;." ^
    l4d2_editor.py

if %errorlevel% neq 0 (
    echo.
    echo  ERROR: PyInstaller fallo.
    pause & exit /b 1
)

REM Copia archivos necesarios al lado del .exe
copy /Y sam_bridge.exe  "dist\sam_bridge.exe"  >nul
copy /Y SAM.API.dll     "dist\SAM.API.dll"     >nul
echo 550 > "dist\steam_appid.txt"

echo.
if exist "dist\L4D2_Stats_Editor.exe" (
    echo ============================================
    echo  LISTO
    echo  .exe en: %~dp0dist\L4D2_Stats_Editor.exe
    echo.
    echo  La carpeta dist\ tiene todo lo necesario:
    echo    L4D2_Stats_Editor.exe
    echo    sam_bridge.exe
    echo    SAM.API.dll
    echo    steam_appid.txt
    echo  No separes esos archivos.
    echo ============================================
) else (
    echo  FALLO — el .exe no se creo.
)
echo.
pause
