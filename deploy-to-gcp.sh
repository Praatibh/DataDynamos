#!/bin/bash
# TruthGuard AI - Simple GCP Deployment Script

echo "🚀 TruthGuard AI - Google Cloud Deployment"
echo "=========================================="

# Set variables
PROJECT_ID="your_id"
REGION="us-central1"

echo "📝 Project ID: $PROJECT_ID"

# Step 1: Create and setup project
echo "1️⃣ Creating Google Cloud project..."
gcloud projects create $PROJECT_ID --name="TruthGuard AI"
gcloud config set project $PROJECT_ID

echo "   ⚠️  Please enable billing for project $PROJECT_ID in the Google Cloud Console"
echo "   🌐 https://console.cloud.google.com/billing/linkedaccount?project=$PROJECT_ID"
read -p "   Press Enter after enabling billing..."

# Step 2: Enable APIs
echo "2️⃣ Enabling required APIs..."
gcloud services enable run.googleapis.com
gcloud services enable sql-component.googleapis.com
gcloud services enable storage.googleapis.com
gcloud services enable aiplatform.googleapis.com
gcloud services enable vision.googleapis.com
gcloud services enable videointelligence.googleapis.com
gcloud services enable speech.googleapis.com
gcloud services enable cloudbuild.googleapis.com
gcloud services enable redis.googleapis.com

# Step 3: Create service account
echo "3️⃣ Creating service account..."
gcloud iam service-accounts create truthguard-app \
    --display-name="TruthGuard App"

gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:truthguard-app@$PROJECT_ID.iam.gserviceaccount.com" \
    --role="roles/aiplatform.user"

gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:truthguard-app@$PROJECT_ID.iam.gserviceaccount.com" \
    --role="roles/storage.admin"

gcloud iam service-accounts keys create credentials-prod.json \
    --iam-account=truthguard-app@$PROJECT_ID.iam.gserviceaccount.com

# Step 4: Create database
echo "4️⃣ Creating Cloud SQL database..."
DB_PASSWORD="$(openssl rand -base64 32)"
gcloud sql instances create truthguard-db \
    --database-version=POSTGRES_15 \
    --cpu=1 \
    --memory=3840MB \
    --storage-size=10GB \
    --region=$REGION \
    --backup

gcloud sql users set-password postgres \
    --instance=truthguard-db \
    --password="$DB_PASSWORD"

gcloud sql databases create truthguard --instance=truthguard-db

CONNECTION_NAME=$(gcloud sql instances describe truthguard-db \
    --format="value(connectionName)")

# Step 5: Create Redis
echo "5️⃣ Creating Redis cache..."
gcloud redis instances create truthguard-redis \
    --size=1 \
    --region=$REGION \
    --redis-version=redis_7_0

REDIS_HOST=$(gcloud redis instances describe truthguard-redis \
    --region=$REGION \
    --format="value(host)")

# Step 6: Create storage buckets
echo "6️⃣ Creating storage buckets..."
gsutil mb gs://$PROJECT_ID-frontend
gsutil mb gs://$PROJECT_ID-uploads
gsutil iam ch allUsers:objectViewer gs://$PROJECT_ID-frontend

# Step 7: Deploy backend
echo "7️⃣ Deploying backend..."
cd backend

# Copy production credentials
cp ../credentials-prod.json credentials.json

# Create production Dockerfile if it doesn't exist
if [ ! -f "Dockerfile" ]; then
cat > Dockerfile << 'EOF'
FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y gcc g++ libpq-dev curl && rm -rf /var/lib/apt/lists/*

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
fi

# Build and deploy
gcloud builds submit --tag gcr.io/$PROJECT_ID/truthguard-backend

gcloud run deploy truthguard-backend \
    --image gcr.io/$PROJECT_ID/truthguard-backend \
    --platform managed \
    --region $REGION \
    --allow-unauthenticated \
    --memory 2Gi \
    --cpu 2 \
    --max-instances 10 \
    --set-env-vars "GOOGLE_CLOUD_PROJECT=$PROJECT_ID" \
    --set-env-vars "DATABASE_URL=postgresql://postgres:$DB_PASSWORD@/$PROJECT_ID:$REGION:truthguard-db/truthguard?host=/cloudsql/$CONNECTION_NAME" \
    --set-env-vars "REDIS_URL=redis://$REDIS_HOST:6379/0" \
    --set-env-vars "SECRET_KEY=$(openssl rand -base64 32)" \
    --add-cloudsql-instances $CONNECTION_NAME

BACKEND_URL=$(gcloud run services describe truthguard-backend \
    --region $REGION \
    --format "value(status.url)")

cd ..

# Step 8: Deploy frontend
echo "8️⃣ Deploying frontend..."
cd frontend

# Update API URL in frontend
if [ -f "app.js" ]; then
    sed -i.bak "s|http://localhost:8000|$BACKEND_URL|g" app.js
    sed -i.bak "s|API_BASE_URL = .*|API_BASE_URL = '$BACKEND_URL';|g" app.js
fi

# Upload to Cloud Storage
gsutil -m cp -r * gs://$PROJECT_ID-frontend/

# Enable web hosting
gsutil web set -m index.html gs://$PROJECT_ID-frontend

FRONTEND_URL="https://storage.googleapis.com/$PROJECT_ID-frontend/index.html"

cd ..

# Step 9: Summary
echo ""
echo "🎉 Deployment Complete!"
echo "======================"
echo ""
echo "🌐 Your TruthGuard AI platform:"
echo "   • Frontend: $FRONTEND_URL"
echo "   • Backend API: $BACKEND_URL"
echo "   • API Docs: $BACKEND_URL/docs"
echo "   • Health: $BACKEND_URL/health"
echo ""
echo "📊 Google Cloud Resources:"
echo "   • Project: $PROJECT_ID"
echo "   • Region: $REGION"
echo "   • Database: truthguard-db"
echo "   • Redis: truthguard-redis"
echo ""
echo "💾 Credentials saved:"
echo "   • Database password: $DB_PASSWORD"
echo "   • Connection name: $CONNECTION_NAME"
echo "   • Redis host: $REDIS_HOST"
echo ""
echo "🛠️ Management:"
echo "   • View logs: gcloud run logs read --service=truthguard-backend --region=$REGION"
echo "   • Scale: gcloud run services update truthguard-backend --max-instances=20 --region=$REGION"
echo ""
echo "💰 Estimated cost: $30-100/month depending on usage"
echo ""
echo "✅ Your AI misinformation detection platform is now live on Google Cloud!"
