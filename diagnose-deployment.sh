#!/bin/bash
# TruthGuard AI - Deployment Diagnostics

echo "🔍 TruthGuard AI - Deployment Diagnostics"
echo "========================================="

PROJECT_ID="truthguard-ai-1758454497"

# Check project
echo "📋 Project Information:"
echo "   Current project: $(gcloud config get-value project)"
echo "   Target project: $PROJECT_ID"

if [ "$(gcloud config get-value project)" != "$PROJECT_ID" ]; then
    echo "⚠️  Project mismatch - setting correct project..."
    gcloud config set project $PROJECT_ID
fi

# Check APIs
echo ""
echo "🔧 Required APIs Status:"
apis=("containerregistry.googleapis.com" "run.googleapis.com" "cloudbuild.googleapis.com")
for api in "${apis[@]}"; do
    if gcloud services list --enabled --filter="name:$api" --format="value(name)" | grep -q "$api"; then
        echo "   $api: ✅ Enabled"
    else
        echo "   $api: ❌ Disabled"
    fi
done

# Check container images
echo ""
echo "🐳 Container Images:"
if gcloud container images list --repository=gcr.io/$PROJECT_ID --format="table(name)" 2>/dev/null; then
    echo "   Images found in registry"
else
    echo "   ❌ No images found in registry"
fi

# Check Cloud Run services
echo ""
echo "🚀 Cloud Run Services:"
gcloud run services list --region=us-central1 --format="table(metadata.name,status.url,status.conditions[0].type,status.conditions[0].status)" 2>/dev/null || echo "   No services found"

# Check recent builds
echo ""
echo "🔨 Recent Builds:"
gcloud builds list --limit=3 --format="table(id,status,createTime)" 2>/dev/null || echo "   No builds found"

# Check file structure
echo ""
echo "📂 Local File Structure:"
if [ -d "backend" ]; then
    echo "   backend/ directory: ✅"
    echo "   Files in backend/:"
    ls -la backend/ | head -10

    # Check specific files
    echo ""
    echo "📄 Required Files:"
    files=("backend/app_main.py" "backend/requirements.txt" "backend/Dockerfile")
    for file in "${files[@]}"; do
        if [ -f "$file" ]; then
            echo "   $file: ✅"
        else
            echo "   $file: ❌ Missing"
        fi
    done

    # Check credentials
    if [ -f "backend/credentials.json" ] || [ -f "backend/credentials-prod.json" ]; then
        echo "   credentials file: ✅"
    else
        echo "   credentials file: ❌ Missing"
    fi
else
    echo "   backend/ directory: ❌ Missing"
fi

# Get latest logs if service exists
echo ""
echo "📝 Recent Logs (if service exists):"
gcloud run logs read --service=truthguard-backend --region=us-central1 --limit=5 2>/dev/null || echo "   No logs available (service may not exist)"

echo ""
echo "🎯 Next Steps:"
if [ ! -d "backend" ]; then
    echo "   1. Create backend/ directory with your Python files"
    echo "   2. Make sure app_main.py is your main FastAPI file"
elif [ ! -f "backend/app_main.py" ]; then
    echo "   1. Make sure your main FastAPI file is named app_main.py"
    echo "   2. Place it in the backend/ directory"
else
    echo "   1. Run: ./fix-deployment.sh"
    echo "   2. This will build and deploy your container"
fi

echo ""
echo "💡 For detailed troubleshooting: see CLOUD_RUN_ERROR_FIX.md"
