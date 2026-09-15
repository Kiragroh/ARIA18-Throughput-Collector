@echo off
py -3 "%~dp0prepare_site.py" %*
if errorlevel 1 pause
