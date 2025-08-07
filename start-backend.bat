@echo off
echo ================================
echo MEDSC Backend Test
echo ================================
echo.

echo Iniciando servidor Flask...
echo.
echo IMPORTANTE: 
echo - Asegurate de que tienes las dependencias instaladas
echo - El servidor se iniciara en http://localhost:5000
echo - Presiona Ctrl+C para detener el servidor
echo.

cd /d "%~dp0MEDSC-Monolitica\app"

echo Verificando dependencias...
python -c "import flask_cors; print('✅ Flask-CORS instalado')" 2>nul || (
    echo ❌ Flask-CORS no encontrado. Instalando...
    pip install flask-cors
)

echo.
echo Iniciando aplicacion...
python index.py

pause
