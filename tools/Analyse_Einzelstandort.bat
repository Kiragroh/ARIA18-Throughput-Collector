@echo off
setlocal
set "SCRIPT=%~dp0analyze_single_site.py"
set "INPUT=%~1"
if not defined INPUT set /p "INPUT=Pfad zur Collector-Exceldatei: "
if not exist "%INPUT%" (
  echo Datei nicht gefunden: %INPUT%
  exit /b 2
)
set "OUTPUT=%~dp1Einzelstandortauswertung"
py -3 "%SCRIPT%" "%INPUT%" --output-dir "%OUTPUT%"
if errorlevel 1 (
  echo Analyse fehlgeschlagen. Abhaengigkeiten installieren mit:
  echo py -3 -m pip install -r "%~dp0..\requirements-analysis.txt"
  exit /b 1
)
echo Fertig: %OUTPUT%
