#!/bin/bash

# Script de inicialización para MEDSC
echo "=== MEDSC - Inicialización de Contenedores ==="

# Verificar si existe el archivo .env
if [ ! -f ".env" ]; then
    echo "⚠️  Archivo .env no encontrado. Copiando desde .env.example..."
    cp .env.example .env
    echo "✅ Archivo .env creado. Por favor, edita las variables de entorno antes de continuar."
    echo "📝 Edita el archivo .env con tus configuraciones específicas"
    exit 1
fi

echo "🔧 Construyendo contenedores..."
docker-compose build

echo "🚀 Iniciando servicios..."
docker-compose up -d

echo "⏳ Esperando que los servicios estén listos..."
sleep 10

echo ""
echo "=== Estado de los Servicios ==="
docker-compose ps

echo ""
echo "=== URLs de Acceso ==="
echo "🌐 Frontend (Next.js): http://localhost:3000"
echo "🔧 Backend (Flask): http://localhost:5000"
echo "🗄️  phpMyAdmin: http://localhost:8080"
echo ""
echo "=== Comandos Útiles ==="
echo "Ver logs: docker-compose logs -f [servicio]"
echo "Detener: docker-compose down"
echo "Reiniciar: docker-compose restart [servicio]"
echo "Reconstruir: docker-compose up --build"
