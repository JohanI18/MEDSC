# Script de inicialización para MEDSC en Windows
Write-Host "=== MEDSC - Inicialización de Contenedores ===" -ForegroundColor Green

# Verificar si Docker está ejecutándose
try {
    docker info | Out-Null
    Write-Host "✅ Docker está ejecutándose correctamente" -ForegroundColor Green
} catch {
    Write-Host "❌ Docker no está ejecutándose. Por favor inicia Docker Desktop" -ForegroundColor Red
    exit 1
}

# Verificar si existe el archivo .env
if (-not (Test-Path ".env")) {
    Write-Host "⚠️  Archivo .env no encontrado. Copiando desde .env.example..." -ForegroundColor Yellow
    Copy-Item ".env.example" ".env"
    Write-Host "✅ Archivo .env creado. Por favor, edita las variables de entorno antes de continuar." -ForegroundColor Green
    Write-Host "📝 Edita el archivo .env con tus configuraciones específicas" -ForegroundColor Cyan
    exit 1
}

Write-Host "📋 Archivo .env encontrado" -ForegroundColor Green
Write-Host "🔧 Validando configuración de Docker Compose..." -ForegroundColor Cyan

# Validar configuración de docker-compose
try {
    docker-compose config | Out-Null
    Write-Host "✅ Configuración de Docker Compose válida" -ForegroundColor Green
} catch {
    Write-Host "❌ Error en la configuración de Docker Compose" -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Red
    exit 1
}

Write-Host "🏗️  Construyendo contenedores (esto puede tomar varios minutos)..." -ForegroundColor Cyan
Write-Host "    - Backend (Flask + Python)..." -ForegroundColor Yellow
Write-Host "    - Frontend (Next.js + TypeScript)..." -ForegroundColor Yellow
Write-Host "    - Base de datos (MySQL)..." -ForegroundColor Yellow

# Construir contenedores
try {
    docker-compose build --parallel
    Write-Host "✅ Contenedores construidos exitosamente" -ForegroundColor Green
} catch {
    Write-Host "❌ Error al construir contenedores" -ForegroundColor Red
    Write-Host "Revisa los logs para más detalles" -ForegroundColor Yellow
    exit 1
}

Write-Host "🚀 Iniciando servicios..." -ForegroundColor Cyan
docker-compose up -d

Write-Host "⏳ Esperando que los servicios estén listos..." -ForegroundColor Yellow
Start-Sleep -Seconds 10

Write-Host ""
Write-Host "=== Estado de los Servicios ===" -ForegroundColor Green
docker-compose ps

Write-Host ""
Write-Host "=== URLs de Acceso ===" -ForegroundColor Green
Write-Host "🌐 Frontend (Next.js): http://localhost:3000" -ForegroundColor White
Write-Host "🔧 Backend (Flask): http://localhost:5000" -ForegroundColor White
Write-Host "🗄️  phpMyAdmin: http://localhost:8080" -ForegroundColor White
Write-Host ""
Write-Host "=== Comandos Útiles ===" -ForegroundColor Green
Write-Host "Ver logs: docker-compose logs -f [servicio]" -ForegroundColor White
Write-Host "Detener: docker-compose down" -ForegroundColor White
Write-Host "Reiniciar: docker-compose restart [servicio]" -ForegroundColor White
Write-Host "Reconstruir: docker-compose up --build" -ForegroundColor White
