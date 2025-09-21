#!/bin/bash
# Quick fix for Cloud Run deployment

echo "🔧 Fixing TruthGuard AI Cloud Run Deployment"
echo "============================================"

PROJECT_ID="truthguard-ai-1758454497"
REGION="us-central1"

# Set project
gcloud config set project $PROJECT_ID

# Go to backend directory
if [ ! -d "backend" ]; then
    echo "❌ backend/ directory not found. Please run this from your project root."
    exit 1
fi

cd backend

# Check required files
echo "📋 Checking required files..."
if [ ! -f "app_main.py" ]; then
    echo "❌ app_main.py not found in backend/ directory"
    echo "   Please make sure your main FastAPI file is named app_main.py"
    exit 1
fi

if [ ! -f "requirements.txt" ]; then
    echo "❌ requirements.txt not found"
    echo "📝 Creating basic requirements.txt..."
    cat > requirements.txt << 'EOF'
fastapi==0.104.1
uvicorn[standard]==0.24.0
asyncpg==0.29.0
sqlalchemy==2.0.23
pydantic==2.5.0
google-cloud-aiplatform==1.38.0
google-cloud-vision==3.4.0
google-cloud-videointelligence==2.11.0
google-cloud-speech==2.21.0
google-cloud-firestore==2.13.0
google-cloud-storage==2.10.0
redis==5.0.1
aiohttp==3.9.0
python-multipart==0.0.6
alembic==1.13.0
psycopg2-binary==2.9.9
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
EOF
    echo "✅ Created requirements.txt"
fi

if [ ! -f "Dockerfile" ]; then
    echo "📝 Creating Dockerfile..."
    cat > Dockerfile << 'EOF'
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y gcc g++ libpq-dev curl && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN useradd --create-home appuser && chown -R appuser:appuser /app
USER appuser

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

CMD ["uvicorn", "app_main:app", "--host", "0.0.0.0", "--port", "8000"]
EOF
    echo "✅ Created Dockerfile"
fi

# Ensure credentials exist
if [ ! -f "credentials.json" ]; then
    if [ -f "../credentials-prod.json" ]; then
        cp ../credentials-prod.json credentials.json
        echo "✅ Copied credentials-prod.json to credentials.json"
    elif [ -f "../credentials.json" ]; then
        cp ../credentials.json credentials.json
        echo "✅ Copied credentials.json"
    else
        echo "⚠️  credentials.json not found - you may need to download it from Google Cloud Console"
    fi
fi

# Enable required APIs
echo "🔧 Enabling APIs..."
gcloud services enable containerregistry.googleapis.com
gcloud services enable run.googleapis.com
gcloud services enable cloudbuild.googleapis.com

# Build container
echo "🔨 Building container..."
echo "   This may take 3-5 minutes..."

if gcloud builds submit --tag gcr.io/$PROJECT_ID/truthguard-backend; then
    echo "✅ Container built successfully"
else
    echo "❌ Container build failed"
    echo "   Check the build logs above for errors"
    exit 1
fi

# Deploy to Cloud Run
echo "🚀 Deploying to Cloud Run..."
gcloud run deploy truthguard-backend \
    --image gcr.io/$PROJECT_ID/truthguard-backend \
    --platform managed \
    --region $REGION \
    --allow-unauthenticated \
    --memory 2Gi \
    --cpu 2 \
    --max-instances 10 \
    --set-env-vars "DEBUG=False,GOOGLE_CLOUD_PROJECT=$PROJECT_ID" \
    --timeout 300

# Get service URL
SERVICE_URL=$(gcloud run services describe truthguard-backend \
    --region $REGION \
    --format "value(status.url)")

echo ""
echo "🎉 Deployment Complete!"
echo "Service URL: $SERVICE_URL"
echo "Health Check: $SERVICE_URL/health"
echo "API Docs: $SERVICE_URL/docs"
echo ""

# Test the deployment
echo "🧪 Testing deployment..."
if curl -f "$SERVICE_URL/health" >/dev/null 2>&1; then
    echo "✅ Health check passed - service is running!"
else
    echo "⚠️  Health check failed - checking logs..."
    gcloud run logs read --service=truthguard-backend --region=$REGION --limit=10
fi

cd ..

echo ""
echo "📊 Service Information:"
echo "   Project: $PROJECT_ID"
echo "   Region: $REGION"
echo "   Service: truthguard-backend"
echo "   URL: $SERVICE_URL"
echo ""
echo "🛠️  Management commands:"
echo "   View logs: gcloud run logs read --service=truthguard-backend --region=$REGION"
echo "   Update: gcloud builds submit --tag gcr.io/$PROJECT_ID/truthguard-backend && gcloud run deploy truthguard-backend --image gcr.io/$PROJECT_ID/truthguard-backend --region=$REGION"
