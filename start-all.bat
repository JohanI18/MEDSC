@echo off
echo ================================
echo MEDSC - Prueba Complete Setup
echo ================================
echo.

echo 🔧 PASO 1: Preparando Backend...
cd /d "%~dp0MEDSC-Monolitica\app"

echo Verificando dependencias del backend...
python -c "import flask_cors; print('✅ Flask-CORS OK')" 2>nul || (
    echo ⚠️  Instalando Flask-CORS...
    pip install flask-cors
)

echo.
echo 🚀 PASO 2: Iniciando Backend...
echo Backend se iniciará en http://localhost:5000
start "Backend Flask" cmd /k "python index.py"

timeout /t 3 >nul

echo.
echo 🔧 PASO 3: Preparando Frontend...
cd /d "%~dp0Frontend"

if not exist "node_modules" (
    echo ⚠️  Instalando dependencias del frontend...
    npm install
) else (
    echo ✅ Dependencias del frontend OK
)

echo.
echo 🚀 PASO 4: Iniciando Frontend...
echo Frontend se iniciará en http://localhost:3000
echo.
echo URLs importantes:
echo - Frontend: http://localhost:3000
echo - Backend:  http://localhost:5000
echo - Test:     http://localhost:3000/test
echo - Login:    http://localhost:3000/login
echo.
echo ¡Todo listo! Los servidores se están iniciando...

npm run dev

pause
