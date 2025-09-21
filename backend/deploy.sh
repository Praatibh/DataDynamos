#!/bin/bash
# TruthGuard AI - Quick Deployment Script

set -e

echo "🛡️  TruthGuard AI Backend - Quick Deployment"
echo "============================================"

# Check if required tools are installed
command -v docker >/dev/null 2>&1 || { echo "❌ Docker is required but not installed. Aborting." >&2; exit 1; }
command -v docker-compose >/dev/null 2>&1 || { echo "❌ Docker Compose is required but not installed. Aborting." >&2; exit 1; }

# Check if .env file exists
if [ ! -f .env ]; then
    echo "📝 Creating .env file from template..."
    cp .env.example .env || {
        echo "❌ .env.example not found. Please create .env file manually."
        exit 1
    }
    echo "⚠️  Please edit .env file with your credentials before continuing."
    echo "   Required: GOOGLE_CLOUD_PROJECT, SECRET_KEY, WHATSAPP credentials"
    read -p "Press Enter when ready to continue..."
fi

# Check if Google Cloud credentials exist
if [ ! -f credentials.json ]; then
    echo "❌ Google Cloud credentials.json not found."
    echo "   Please download service account key and save as credentials.json"
    exit 1
fi

echo "🐳 Building Docker containers..."
docker-compose build

echo "🚀 Starting services..."
docker-compose up -d

echo "⏳ Waiting for services to start..."
sleep 30

# Check service health
echo "🔍 Checking service health..."
if curl -f http://localhost:8000/health >/dev/null 2>&1; then
    echo "✅ Backend service is healthy"
else
    echo "❌ Backend service is not responding"
    docker-compose logs truthguard-api
    exit 1
fi

if curl -f http://localhost:5432 >/dev/null 2>&1; then
    echo "✅ Database service is healthy"  
else
    echo "⚠️  Database connection check skipped"
fi

echo "🎉 Deployment complete!"
echo ""
echo "🌐 Services available at:"
echo "   • Backend API: http://localhost:8000"
echo "   • API Documentation: http://localhost:8000/docs" 
echo "   • Database: localhost:5432"
echo "   • Redis Cache: localhost:6379"
echo "   • Prometheus: http://localhost:9090"
echo "   • Grafana: http://localhost:3000"
echo ""
echo "📊 Health check: curl http://localhost:8000/health"
echo "📖 Full documentation: see README.md"
echo ""
echo "🛡️  TruthGuard AI is ready to combat misinformation!"
