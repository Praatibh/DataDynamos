
"""
Pydantic schemas for API request/response models
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, EmailStr, validator
from uuid import UUID

# User schemas
class UserBase(BaseModel):
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=50)
    full_name: Optional[str] = None
    phone_number: Optional[str] = None
    user_type: str = "general_public"
    preferred_language: str = "en"
    location: Optional[str] = None
    bio: Optional[str] = None

class UserCreate(UserBase):
    password: str = Field(..., min_length=8)

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(UserBase):
    id: UUID
    is_active: bool
    is_verified: bool
    is_premium: bool
    total_verifications: int
    accuracy_score: float
    community_contributions: int
    created_at: datetime
    last_login: Optional[datetime]

    class Config:
        from_attributes = True

class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    phone_number: Optional[str] = None
    location: Optional[str] = None
    bio: Optional[str] = None
    preferred_language: Optional[str] = None

# Verification schemas
class VerificationRequest(BaseModel):
    content: str = Field(..., min_length=1, max_length=10000)
    content_type: str = Field(..., regex="^(text|image|image_url|video|video_url|audio|audio_url)$")
    metadata: Optional[Dict[str, Any]] = None
    source_platform: Optional[str] = None
    source_location: Optional[str] = None

class BatchVerificationRequest(BaseModel):
    content_items: List[VerificationRequest] = Field(..., min_items=1, max_items=10)

class VerificationResponse(BaseModel):
    verification_id: str
    content_id: str
    authenticity_score: float = Field(..., ge=0.0, le=1.0)
    misinformation_likelihood: float = Field(..., ge=0.0, le=1.0)
    risk_level: str
    detection_details: Dict[str, Any]
    educational_content: Dict[str, Any]
    fact_check_sources: List[Dict[str, Any]]
    blockchain_hash: str
    processing_time: float
    timestamp: datetime
    user_id: UUID
    file_info: Optional[Dict[str, Any]] = None

    class Config:
        from_attributes = True

# Community schemas
class CommunityReportCreate(BaseModel):
    reported_content: str = Field(..., min_length=1, max_length=5000)
    content_type: str
    content_url: Optional[str] = None
    report_category: str
    description: Optional[str] = None
    urgency_level: str = "medium"
    source_platform: Optional[str] = None
    source_location: Optional[str] = None
    estimated_reach: Optional[int] = None

class CommunityReportResponse(BaseModel):
    id: UUID
    reported_content: str
    content_type: str
    report_category: str
    description: Optional[str]
    urgency_level: str
    status: str
    created_at: datetime
    reporter_id: UUID

    class Config:
        from_attributes = True

class CommunityFeedbackCreate(BaseModel):
    verification_id: UUID
    feedback_type: str = Field(..., regex="^(helpful|not_helpful|incorrect|spam)$")
    rating: Optional[int] = Field(None, ge=1, le=5)
    comment: Optional[str] = None
    expertise_level: Optional[str] = None
    confidence_in_feedback: Optional[float] = Field(None, ge=0.0, le=1.0)

# Analytics schemas
class PlatformStats(BaseModel):
    total_verifications: int
    misinformation_detected: int
    accuracy_rate: float
    active_users: int
    daily_verifications: int
    response_time_avg: float
    threat_alerts_active: int

class TrendingThreat(BaseModel):
    category: str
    incidents: int
    growth_rate: str
    severity: str
    description: Optional[str] = None

class GeographicThreatData(BaseModel):
    region: str
    threat_count: int
    risk_level: str
    top_categories: List[str]

class RealTimeThreat(BaseModel):
    id: str
    content_type: str
    risk_level: str
    authenticity_score: float
    platform: str
    location: str
    timestamp: datetime
    prevented_shares: int

# WhatsApp schemas
class WhatsAppMessage(BaseModel):
    whatsapp_id: str
    sender_number: str
    message_type: str
    content: Optional[str] = None
    media_url: Optional[str] = None
    language_detected: Optional[str] = None

class WhatsAppResponse(BaseModel):
    message_id: str
    response_content: str
    verification_result: Optional[VerificationResponse] = None
    processing_time: float

# Education schemas
class EducationModuleProgress(BaseModel):
    module_name: str
    completion_percentage: float
    current_lesson: Optional[str]
    quiz_scores: Optional[Dict[str, float]]
    achievements_earned: Optional[List[str]]
    time_spent_minutes: int
    accuracy_rate: Optional[float]
    status: str

# Blockchain schemas
class BlockchainVerification(BaseModel):
    blockchain_hash: str
    content_hash: str
    verification_timestamp: datetime
    authenticity_score: float
    is_valid: bool

class ContentProvenance(BaseModel):
    content_hash: str
    verification_count: int
    first_seen: datetime
    last_verified: datetime
    provenance_chain: List[BlockchainVerification]

# API response schemas
class APIResponse(BaseModel):
    success: bool
    message: str
    data: Optional[Dict[str, Any]] = None
    errors: Optional[List[str]] = None
    timestamp: datetime = Field(default_factory=datetime.now)

class HealthCheckResponse(BaseModel):
    status: str
    timestamp: datetime
    version: str
    services: Dict[str, str]
    uptime_seconds: Optional[float] = None

class MetricsResponse(BaseModel):
    total_verifications: int
    misinformation_detected: int
    accuracy_rate: float
    average_response_time: float
    active_users: int
    api_requests_per_minute: float
    error_rate: float
    system_uptime: float
