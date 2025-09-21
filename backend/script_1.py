# Create the main FastAPI application
main_app_code = '''
"""
TruthGuard AI - Main FastAPI Application
Advanced AI-powered misinformation detection platform backend
"""

import os
import logging
from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import uvicorn
from datetime import datetime
import asyncio
from typing import List, Optional, Dict, Any

# Internal imports
from app.core.ai_engine import TruthGuardAIEngine
from app.core.blockchain import BlockchainVerifier
from app.core.security import SecurityManager
from app.services.google_cloud import GoogleCloudService
from app.services.whatsapp_service import WhatsAppService
from app.api import auth, verification, analytics, whatsapp, community
from app.database import get_database, init_db
from app.config import settings
from app.schemas.verification_schemas import (
    VerificationRequest, 
    VerificationResponse,
    BatchVerificationRequest
)
from app.schemas.user_schemas import UserCreate, UserResponse, UserLogin
from app.schemas.content_schemas import ContentAnalysis, ThreatAlert
from app.utils.helpers import generate_unique_id, log_api_usage

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Initialize core services
ai_engine = TruthGuardAIEngine()
blockchain_verifier = BlockchainVerifier()
security_manager = SecurityManager()
google_cloud = GoogleCloudService()
whatsapp_service = WhatsAppService()

# Security
security = HTTPBearer()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan management"""
    # Startup
    logger.info("🚀 Starting TruthGuard AI Backend")
    await init_db()
    await ai_engine.initialize()
    await google_cloud.initialize()
    logger.info("✅ Backend initialization complete")
    
    yield
    
    # Shutdown
    logger.info("🛑 Shutting down TruthGuard AI Backend")
    await ai_engine.cleanup()
    await google_cloud.cleanup()

# Create FastAPI application
app = FastAPI(
    title="TruthGuard AI - Misinformation Detection API",
    description="Advanced AI-powered platform for detecting and combating misinformation",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Add middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(
    TrustedHostMiddleware, 
    allowed_hosts=settings.ALLOWED_HOSTS
)

# Include routers
app.include_router(auth.router, prefix="/api/v1/auth", tags=["Authentication"])
app.include_router(verification.router, prefix="/api/v1/verify", tags=["Verification"])
app.include_router(analytics.router, prefix="/api/v1/analytics", tags=["Analytics"])
app.include_router(whatsapp.router, prefix="/api/v1/whatsapp", tags=["WhatsApp"])
app.include_router(community.router, prefix="/api/v1/community", tags=["Community"])

@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "TruthGuard AI - Advanced Misinformation Detection Platform",
        "version": "2.0.0",
        "status": "operational",
        "features": [
            "Multimodal AI Analysis",
            "Real-time Detection",
            "Blockchain Verification",
            "WhatsApp Integration",
            "Community Network"
        ],
        "endpoints": {
            "documentation": "/docs",
            "health": "/health",
            "metrics": "/metrics",
            "verification": "/api/v1/verify",
            "analytics": "/api/v1/analytics"
        }
    }

@app.get("/health")
async def health_check():
    """Comprehensive health check"""
    try:
        # Check database connection
        db_status = await get_database().execute("SELECT 1")
        
        # Check AI engine status
        ai_status = await ai_engine.health_check()
        
        # Check Google Cloud services
        gcp_status = await google_cloud.health_check()
        
        # Check WhatsApp service
        whatsapp_status = await whatsapp_service.health_check()
        
        return {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "services": {
                "database": "operational" if db_status else "degraded",
                "ai_engine": "operational" if ai_status else "degraded",
                "google_cloud": "operational" if gcp_status else "degraded",
                "whatsapp": "operational" if whatsapp_status else "degraded"
            },
            "version": "2.0.0"
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
        )

@app.post("/api/v1/verify/content", response_model=VerificationResponse)
async def verify_content(
    request: VerificationRequest,
    background_tasks: BackgroundTasks,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """
    Main content verification endpoint
    Supports text, image, video, and audio analysis
    """
    try:
        # Authenticate user
        user = await security_manager.verify_token(credentials.credentials)
        
        # Generate unique verification ID
        verification_id = generate_unique_id()
        
        # Log API usage
        await log_api_usage(user.id, "content_verification", verification_id)
        
        # Perform AI analysis
        analysis_result = await ai_engine.analyze_content(
            content=request.content,
            content_type=request.content_type,
            metadata=request.metadata
        )
        
        # Generate blockchain verification
        blockchain_hash = await blockchain_verifier.create_verification(
            content=request.content,
            analysis_result=analysis_result,
            user_id=user.id
        )
        
        # Create response
        response = VerificationResponse(
            verification_id=verification_id,
            content_id=analysis_result.content_id,
            authenticity_score=analysis_result.authenticity_score,
            misinformation_likelihood=analysis_result.misinformation_likelihood,
            risk_level=analysis_result.risk_level,
            detection_details=analysis_result.detection_details,
            blockchain_hash=blockchain_hash,
            educational_content=analysis_result.educational_content,
            fact_check_sources=analysis_result.fact_check_sources,
            processing_time=analysis_result.processing_time,
            timestamp=datetime.now(),
            user_id=user.id
        )
        
        # Store verification result in background
        background_tasks.add_task(
            ai_engine.store_verification_result,
            verification_id,
            response
        )
        
        # Send real-time alerts if high risk
        if analysis_result.risk_level in ["high", "critical"]:
            background_tasks.add_task(
                security_manager.send_threat_alert,
                response
            )
        
        return response
        
    except Exception as e:
        logger.error(f"Content verification failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/verify/batch")
async def batch_verify_content(
    request: BatchVerificationRequest,
    background_tasks: BackgroundTasks,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """
    Batch content verification for multiple items
    """
    try:
        user = await security_manager.verify_token(credentials.credentials)
        
        # Check batch limits
        if len(request.content_items) > settings.MAX_BATCH_SIZE:
            raise HTTPException(
                status_code=400,
                detail=f"Batch size exceeds maximum of {settings.MAX_BATCH_SIZE}"
            )
        
        # Process all items concurrently
        tasks = []
        for item in request.content_items:
            task = ai_engine.analyze_content(
                content=item.content,
                content_type=item.content_type,
                metadata=item.metadata
            )
            tasks.append(task)
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Process results and create blockchain verifications
        verification_responses = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logger.error(f"Batch item {i} failed: {result}")
                continue
                
            verification_id = generate_unique_id()
            blockchain_hash = await blockchain_verifier.create_verification(
                content=request.content_items[i].content,
                analysis_result=result,
                user_id=user.id
            )
            
            response = VerificationResponse(
                verification_id=verification_id,
                content_id=result.content_id,
                authenticity_score=result.authenticity_score,
                misinformation_likelihood=result.misinformation_likelihood,
                risk_level=result.risk_level,
                detection_details=result.detection_details,
                blockchain_hash=blockchain_hash,
                educational_content=result.educational_content,
                fact_check_sources=result.fact_check_sources,
                processing_time=result.processing_time,
                timestamp=datetime.now(),
                user_id=user.id
            )
            
            verification_responses.append(response)
        
        return {
            "batch_id": generate_unique_id(),
            "total_items": len(request.content_items),
            "processed_items": len(verification_responses),
            "failed_items": len(request.content_items) - len(verification_responses),
            "results": verification_responses,
            "processing_time": sum(r.processing_time for r in verification_responses)
        }
        
    except Exception as e:
        logger.error(f"Batch verification failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/verify/file")
async def verify_file_upload(
    file: UploadFile = File(...),
    content_type: str = "image",
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """
    File upload verification endpoint
    Supports images, videos, and audio files
    """
    try:
        user = await security_manager.verify_token(credentials.credentials)
        
        # Validate file type and size
        if file.size > settings.MAX_FILE_SIZE:
            raise HTTPException(
                status_code=400,
                detail=f"File size exceeds maximum of {settings.MAX_FILE_SIZE} bytes"
            )
        
        # Read file content
        file_content = await file.read()
        
        # Upload to cloud storage
        file_url = await google_cloud.upload_file(
            file_content=file_content,
            filename=file.filename,
            content_type=file.content_type
        )
        
        # Analyze uploaded file
        analysis_result = await ai_engine.analyze_file(
            file_url=file_url,
            file_type=content_type,
            filename=file.filename
        )
        
        # Create blockchain verification
        blockchain_hash = await blockchain_verifier.create_verification(
            content=file_url,
            analysis_result=analysis_result,
            user_id=user.id
        )
        
        verification_id = generate_unique_id()
        
        response = VerificationResponse(
            verification_id=verification_id,
            content_id=analysis_result.content_id,
            authenticity_score=analysis_result.authenticity_score,
            misinformation_likelihood=analysis_result.misinformation_likelihood,
            risk_level=analysis_result.risk_level,
            detection_details=analysis_result.detection_details,
            blockchain_hash=blockchain_hash,
            educational_content=analysis_result.educational_content,
            fact_check_sources=analysis_result.fact_check_sources,
            processing_time=analysis_result.processing_time,
            timestamp=datetime.now(),
            user_id=user.id,
            file_info={
                "filename": file.filename,
                "file_size": file.size,
                "file_url": file_url
            }
        )
        
        return response
        
    except Exception as e:
        logger.error(f"File verification failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/threats/realtime")
async def get_realtime_threats(
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """
    Get real-time misinformation threats and alerts
    """
    try:
        user = await security_manager.verify_token(credentials.credentials)
        
        # Get latest threat detections
        threats = await ai_engine.get_realtime_threats(limit=50)
        
        # Get trending misinformation topics
        trending = await ai_engine.get_trending_threats()
        
        # Get geographic threat distribution
        geographic_data = await ai_engine.get_geographic_threats()
        
        return {
            "timestamp": datetime.now().isoformat(),
            "active_threats": len(threats),
            "critical_alerts": len([t for t in threats if t.risk_level == "critical"]),
            "latest_detections": threats,
            "trending_topics": trending,
            "geographic_distribution": geographic_data,
            "platform_stats": {
                "total_verifications_today": await ai_engine.get_daily_verifications(),
                "misinformation_detected_today": await ai_engine.get_daily_misinformation_count(),
                "accuracy_rate": await ai_engine.get_current_accuracy_rate(),
                "response_time_avg": await ai_engine.get_avg_response_time()
            }
        }
        
    except Exception as e:
        logger.error(f"Realtime threats retrieval failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/metrics")
async def get_metrics():
    """
    Prometheus-compatible metrics endpoint
    """
    try:
        metrics = await ai_engine.get_platform_metrics()
        
        return {
            "total_verifications": metrics.total_verifications,
            "misinformation_detected": metrics.misinformation_detected,
            "accuracy_rate": metrics.accuracy_rate,
            "average_response_time": metrics.avg_response_time,
            "active_users": metrics.active_users,
            "api_requests_per_minute": metrics.api_requests_per_minute,
            "error_rate": metrics.error_rate,
            "system_uptime": metrics.system_uptime
        }
        
    except Exception as e:
        logger.error(f"Metrics retrieval failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
        workers=settings.WORKERS if not settings.DEBUG else 1
    )
'''

# Save the main application file
with open('app_main.py', 'w') as f:
    f.write(main_app_code)

print("✅ Main FastAPI application created")
print("📦 Key features:")
print("- Multi-modal content verification endpoint")
print("- Batch processing for multiple items")
print("- File upload verification")
print("- Real-time threat monitoring")
print("- Health checks and metrics")
print("- Authentication and security")
print("- Background task processing")
print("- Comprehensive error handling")