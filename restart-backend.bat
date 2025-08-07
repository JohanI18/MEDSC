@echo off
echo ================================
echo Reiniciando Backend MEDSC
echo ================================
echo.

echo Cerrando procesos Python existentes...
taskkill /F /IM python.exe >nul 2>&1

echo.
echo Iniciando backend con los cambios aplicados...
cd /d "%~dp0MEDSC-Monolitica\app"

echo Backend iniciando en http://localhost:5000
echo Rutas API disponibles:
echo   - GET  /api/patients (Listar pacientes)  
echo   - POST /api/patients (Crear paciente)
echo   - GET  /test-cors (Test de conectividad)
echo   - POST /login (Login con JSON)
echo.

python index.py

pause
