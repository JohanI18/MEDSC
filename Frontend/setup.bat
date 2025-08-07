@echo off
echo ================================
echo MEDSC Frontend - Setup Script
echo ================================
echo.

echo Verificando Node.js...
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Node.js no esta instalado. Por favor instala Node.js 18+ desde https://nodejs.org
    pause
    exit /b 1
)

echo Node.js encontrado: 
node --version

echo.
echo Instalando dependencias...
npm install

if %errorlevel% neq 0 (
    echo ERROR: Fallo la instalacion de dependencias
    pause
    exit /b 1
)

echo.
echo ================================
echo Instalacion completada!
echo ================================
echo.
echo Para iniciar el servidor de desarrollo:
echo   npm run dev
echo.
echo El frontend estara disponible en:
echo   http://localhost:3000
echo.
echo IMPORTANTE:
echo - Asegurate de que el backend Flask este ejecutandose en http://localhost:5000
echo - Revisa el archivo .env.local si necesitas cambiar la URL de la API
echo.
pause
