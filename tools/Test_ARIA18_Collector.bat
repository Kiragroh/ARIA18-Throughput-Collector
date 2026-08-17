@echo off
setlocal EnableExtensions
pushd "%~dp0" || (
  echo FEHLER: Skriptordner konnte nicht geoeffnet werden.
  pause
  exit /b 1
)

set "REPORTSERVER=%~1"
set "PARENTPATH=%~2"

if not defined REPORTSERVER set /p "REPORTSERVER=ReportServer-URL, z.B. http://REPORTSERVER/ReportServer: "
if not defined REPORTSERVER (
  echo FEHLER: Eine ReportServer-URL ist erforderlich.
  popd
  pause
  exit /b 2
)

if not defined PARENTPATH set /p "PARENTPATH=SSRS-Zielordner mit Schreibrecht [/Users Folders/DOMAENE Benutzer/My Reports]: "
if not defined PARENTPATH (
  echo FEHLER: Ein SSRS-Zielordner ist erforderlich.
  popd
  pause
  exit /b 3
)

where pwsh.exe >nul 2>&1
if errorlevel 1 (
  echo FEHLER: PowerShell 7 ^(pwsh.exe^) wurde nicht gefunden.
  popd
  pause
  exit /b 4
)

pwsh.exe -NoLogo -NoProfile -ExecutionPolicy Bypass -File "%~dp0publish_and_test_rdl.ps1" -ReportServer "%REPORTSERVER%" -ParentPath "%PARENTPATH%"
set "RC=%ERRORLEVEL%"

if not "%RC%"=="0" echo FEHLER: SSRS-Test fehlgeschlagen ^(Code %RC%^).
if "%RC%"=="0" echo FERTIG: PDF und Excel wurden im validation-Ordner erzeugt; der Testreport wurde entfernt.

popd
pause
exit /b %RC%
