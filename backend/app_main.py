"""
TruthGuard AI - Main FastAPI Application
Backend API for misinformation detection platform
"""

import os
import logging
from typing import List, Dict, Any, Optional
from fastapi import FastAPI, File, UploadFile, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field
import asyncio
import json
from datetime import datetime

# Import local modules (all in same directory)
from ai_engine import TruthGuardAIEngine
from config import get_settings
from database_models import init_database
from api_schemas import (
    TextAnalysisRequest,
    TextAnalysisResponse,
    URLAnalysisRequest,
    URLAnalysisResponse,
    HealthResponse
)

# Initialize FastAPI app
app = FastAPI(
    title="TruthGuard AI API",
    description="AI-powered misinformation detection platform",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure this properly for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global instances
settings = get_settings()
ai_engine = None
security = HTTPBearer()

# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    global ai_engine
    
    try:
        logger.info("Starting TruthGuard AI Backend...")
        
        # Initialize database
        await init_database()
        logger.info("Database initialized")
        
        # Initialize AI engine
        ai_engine = TruthGuardAIEngine()
        await ai_engine.initialize()
        logger.info("AI engine initialized")
        
        logger.info("TruthGuard AI Backend started successfully")
        
    except Exception as e:
        logger.error(f"Failed to start application: {e}")
        raise


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    logger.info("Shutting down TruthGuard AI Backend...")
    if ai_engine:
        await ai_engine.cleanup()


@app.get("/", response_model=Dict[str, str])
async def root():
    """Root endpoint"""
    return {
        "message": "TruthGuard AI API",
        "version": "1.0.0",
        "status": "active"
    }


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    try:
        # Check AI engine status
        ai_status = "healthy" if ai_engine and ai_engine.is_ready() else "unhealthy"
        
        # Check database status
        db_status = "healthy"  # Add actual DB check here if needed
        
        return HealthResponse(
            status="healthy" if ai_status == "healthy" and db_status == "healthy" else "unhealthy",
            timestamp=datetime.utcnow(),
            services={
                "ai_engine": ai_status,
                "database": db_status
            }
        )
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Service unhealthy"
        )


@app.post("/analyze/text", response_model=TextAnalysisResponse)
async def analyze_text(
    request: TextAnalysisRequest,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Analyze text for misinformation"""
    try:
        if not ai_engine:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="AI engine not initialized"
            )
        
        logger.info(f"Analyzing text: {request.text[:100]}...")
        
        # Perform analysis
        result = await ai_engine.analyze_text(
            text=request.text,
            language=request.language,
            context=request.context
        )
        
        return TextAnalysisResponse(
            request_id=result.get("request_id"),
            is_misinformation=result.get("is_misinformation", False),
            confidence_score=result.get("confidence_score", 0.0),
            risk_level=result.get("risk_level", "low"),
            detected_patterns=result.get("detected_patterns", []),
            fact_checks=result.get("fact_checks", []),
            sources=result.get("sources", []),
            explanation=result.get("explanation", ""),
            processing_time=result.get("processing_time", 0.0)
        )
        
    except Exception as e:
        logger.error(f"Text analysis failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Analysis failed"
        )


@app.post("/analyze/url", response_model=URLAnalysisResponse)
async def analyze_url(
    request: URLAnalysisRequest,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Analyze URL content for misinformation"""
    try:
        if not ai_engine:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="AI engine not initialized"
            )
        
        logger.info(f"Analyzing URL: {request.url}")
        
        # Perform URL analysis
        result = await ai_engine.analyze_url(
            url=request.url,
            deep_scan=request.deep_scan
        )
        
        return URLAnalysisResponse(
            request_id=result.get("request_id"),
            url=request.url,
            is_misinformation=result.get("is_misinformation", False),
            confidence_score=result.get("confidence_score", 0.0),
            risk_level=result.get("risk_level", "low"),
            content_analysis=result.get("content_analysis", {}),
            source_credibility=result.get("source_credibility", {}),
            fact_checks=result.get("fact_checks", []),
            processing_time=result.get("processing_time", 0.0)
        )
        
    except Exception as e:
        logger.error(f"URL analysis failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="URL analysis failed"
        )


@app.post("/analyze/image")
async def analyze_image(
    file: UploadFile = File(...),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Analyze image for manipulation"""
    try:
        if not ai_engine:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="AI engine not initialized"
            )
        
        # Validate file type
        if not file.content_type or not file.content_type.startswith('image/'):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="File must be an image"
            )
        
        logger.info(f"Analyzing image: {file.filename}")
        
        # Read file content
        content = await file.read()
        
        # Perform image analysis
        result = await ai_engine.analyze_image(content, file.content_type)
        
        return {
            "request_id": result.get("request_id"),
            "filename": file.filename,
            "is_manipulated": result.get("is_manipulated", False),
            "confidence_score": result.get("confidence_score", 0.0),
            "manipulation_types": result.get("manipulation_types", []),
            "authenticity_score": result.get("authenticity_score", 0.0),
            "processing_time": result.get("processing_time", 0.0)
        }
        
    except Exception as e:
        logger.error(f"Image analysis failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Image analysis failed"
        )


@app.get("/stats")
async def get_stats(
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Get platform statistics"""
    try:
        # Get statistics from AI engine
        stats = await ai_engine.get_stats() if ai_engine else {}
        
        return {
            "total_analyses": stats.get("total_analyses", 0),
            "misinformation_detected": stats.get("misinformation_detected", 0),
            "accuracy_rate": stats.get("accuracy_rate", 0.0),
            "processing_time_avg": stats.get("processing_time_avg", 0.0),
            "active_users": stats.get("active_users", 0)
        }
        
    except Exception as e:
        logger.error(f"Stats retrieval failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve stats"
        )


if __name__ == "__main__":
    import uvicorn
    
    port = int(os.environ.get("PORT", 8080))
    host = "0.0.0.0"
    
    uvicorn.run(
        "app_main:app",
        host=host,
        port=port,
        reload=False,
        log_level="info"
    )