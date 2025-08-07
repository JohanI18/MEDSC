@echo off
echo ================================
echo MEDSC - Diagnóstico del Sistema
echo ================================
echo.

echo 🔍 VERIFICANDO REQUISITOS...
echo.

echo Verificando Node.js...
node --version >nul 2>&1 && (
    echo ✅ Node.js: 
    node --version
) || (
    echo ❌ Node.js no encontrado - Instala desde https://nodejs.org
)

echo.
echo Verificando Python...
python --version >nul 2>&1 && (
    echo ✅ Python: 
    python --version
) || (
    echo ❌ Python no encontrado - Instala desde https://python.org
)

echo.
echo 🔍 VERIFICANDO DEPENDENCIAS PYTHON...
cd /d "%~dp0MEDSC-Monolitica\app"

python -c "import flask; print('✅ Flask instalado')" 2>nul || echo ❌ Flask no instalado
python -c "import flask_cors; print('✅ Flask-CORS instalado')" 2>nul || echo ❌ Flask-CORS no instalado
python -c "import supabase; print('✅ Supabase instalado')" 2>nul || echo ❌ Supabase no instalado

echo.
echo 🔍 VERIFICANDO ESTRUCTURA DE ARCHIVOS...

if exist "app.py" (echo ✅ app.py encontrado) else (echo ❌ app.py no encontrado)
if exist "index.py" (echo ✅ index.py encontrado) else (echo ❌ index.py no encontrado)
if exist "requirements.txt" (echo ✅ requirements.txt encontrado) else (echo ❌ requirements.txt no encontrado)
if exist "routes\login.py" (echo ✅ routes\login.py encontrado) else (echo ❌ routes\login.py no encontrado)

echo.
echo 🔍 VERIFICANDO FRONTEND...
cd /d "%~dp0Frontend"

if exist "package.json" (echo ✅ package.json encontrado) else (echo ❌ package.json no encontrado)
if exist "node_modules" (echo ✅ node_modules encontrado) else (echo ⚠️  node_modules no encontrado - ejecuta: npm install)

echo.
echo 🔍 PROBANDO CONEXIONES...

echo Probando puerto 5000 (Backend)...
netstat -an | findstr ":5000" >nul && (
    echo ✅ Puerto 5000 en uso (Backend posiblemente corriendo)
) || (
    echo ⚠️  Puerto 5000 libre (Backend no corriendo)
)

echo Probando puerto 3000 (Frontend)...
netstat -an | findstr ":3000" >nul && (
    echo ✅ Puerto 3000 en uso (Frontend posiblemente corriendo)
) || (
    echo ⚠️  Puerto 3000 libre (Frontend no corriendo)
)

echo.
echo ================================
echo RESUMEN DE DIAGNÓSTICO COMPLETO
echo ================================
echo.
echo Si todo está ✅, ejecuta: start-all.bat
echo Si hay problemas ❌, revisa los requisitos arriba
echo.
echo URLs una vez iniciado:
echo - Test de conexión: http://localhost:3000/test
echo - Login: http://localhost:3000/login  
echo - Backend: http://localhost:5000
echo.

pause
