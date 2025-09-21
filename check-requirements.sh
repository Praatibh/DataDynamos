#!/bin/bash
# TruthGuard AI - Pre-Deployment Requirements Checker

echo "🔍 TruthGuard AI - Deployment Requirements Check"
echo "==============================================="

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

success_count=0
total_checks=0

check_requirement() {
    local name="$1"
    local command="$2"
    local install_info="$3"

    total_checks=$((total_checks + 1))

    printf "%-20s " "$name:"

    if eval "$command" &>/dev/null; then
        echo -e "${GREEN}✅ Installed${NC}"
        success_count=$((success_count + 1))
    else
        echo -e "${RED}❌ Missing${NC}"
        echo "   Install: $install_info"
        echo ""
    fi
}

echo "Checking system requirements..."
echo ""

# Check Google Cloud CLI
check_requirement "Google Cloud CLI" "gcloud --version" "curl https://sdk.cloud.google.com | bash"

# Check Docker
check_requirement "Docker" "docker --version" "https://www.docker.com/products/docker-desktop/"

# Check if authenticated with Google Cloud
check_requirement "GCloud Auth" "gcloud auth list --filter=status:ACTIVE --format='value(account)' | head -n1 | grep -q @" "gcloud auth login"

# Check billing account
if command -v gcloud &>/dev/null; then
    check_requirement "Billing Account" "gcloud billing accounts list --filter='open=true' --format='value(name)' | head -n1 | grep -q ." "Enable billing at https://console.cloud.google.com/billing"
fi

# Check project structure
check_requirement "Backend Directory" "test -d backend && test -f backend/app_main.py" "Create backend/ directory with your Python files"

check_requirement "Frontend Directory" "test -d frontend && test -f frontend/index.html" "Create frontend/ directory with your HTML/CSS/JS files"

check_requirement "Requirements.txt" "test -f backend/requirements.txt" "Create backend/requirements.txt with Python dependencies"

echo ""
echo "📊 Requirements Summary:"
echo "   Passed: $success_count/$total_checks"

if [ $success_count -eq $total_checks ]; then
    echo -e "${GREEN}🎉 All requirements met! You're ready to deploy.${NC}"
    echo ""
    echo "🚀 Next steps:"
    echo "   1. Customize deploy-to-gcp.sh if needed (domain name, region)"
    echo "   2. Run: ./deploy-to-gcp.sh"
    echo ""
    exit 0
else
    echo -e "${RED}⚠️  Please install missing requirements before deploying.${NC}"
    echo ""
    exit 1
fi
