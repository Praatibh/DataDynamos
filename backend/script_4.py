# Create database models and schemas
database_models_code = '''
"""
Database Models for TruthGuard AI Platform
SQLAlchemy models for all data entities
"""

from datetime import datetime, timezone
from typing import Optional, List
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text, JSON, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
import uuid

Base = declarative_base()

class User(Base):
    """User model"""
    __tablename__ = "users"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, index=True, nullable=False)
    username = Column(String(100), unique=True, index=True, nullable=False)
    full_name = Column(String(200), nullable=True)
    phone_number = Column(String(20), nullable=True)
    hashed_password = Column(String(255), nullable=False)
    
    # User type and permissions
    user_type = Column(String(50), default="general_public")  # general_public, journalist, educator, government
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    is_premium = Column(Boolean, default=False)
    
    # Profile information
    profile_picture = Column(String(500), nullable=True)
    bio = Column(Text, nullable=True)
    location = Column(String(200), nullable=True)
    preferred_language = Column(String(10), default="en")
    
    # Platform statistics
    total_verifications = Column(Integer, default=0)
    accuracy_score = Column(Float, default=0.0)
    community_contributions = Column(Integer, default=0)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    last_login = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    verifications = relationship("Verification", back_populates="user")
    community_reports = relationship("CommunityReport", back_populates="reporter")

class Verification(Base):
    """Content verification model"""
    __tablename__ = "verifications"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    
    # Content information
    content_id = Column(String(64), index=True, nullable=False)  # MD5 hash of content
    content_type = Column(String(20), nullable=False)  # text, image, video, audio
    content_hash = Column(String(64), index=True, nullable=False)  # SHA-256 hash
    original_content = Column(Text, nullable=True)  # Store if not too large
    content_url = Column(String(1000), nullable=True)  # URL if content is stored externally
    
    # Analysis results
    authenticity_score = Column(Float, nullable=False)
    misinformation_likelihood = Column(Float, nullable=False)
    risk_level = Column(String(20), nullable=False)  # low, medium, high, critical
    
    # Detailed analysis
    detection_details = Column(JSON, nullable=True)
    educational_content = Column(JSON, nullable=True)
    fact_check_sources = Column(JSON, nullable=True)
    confidence_scores = Column(JSON, nullable=True)
    
    # Blockchain verification
    blockchain_hash = Column(String(64), unique=True, nullable=False)
    
    # Processing information
    processing_time = Column(Float, nullable=False)
    ai_model_version = Column(String(50), default="gemini-2.0-flash")
    
    # Metadata
    source_platform = Column(String(50), nullable=True)  # whatsapp, twitter, facebook, etc.
    source_location = Column(String(200), nullable=True)
    additional_metadata = Column(JSON, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    # Relationships
    user = relationship("User", back_populates="verifications")
    community_feedback = relationship("CommunityFeedback", back_populates="verification")

class CommunityReport(Base):
    """Community-submitted misinformation reports"""
    __tablename__ = "community_reports"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    reporter_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    
    # Reported content
    reported_content = Column(Text, nullable=False)
    content_type = Column(String(20), nullable=False)
    content_url = Column(String(1000), nullable=True)
    
    # Report details
    report_category = Column(String(50), nullable=False)  # health_misinfo, election_misinfo, deepfake, etc.
    description = Column(Text, nullable=True)
    urgency_level = Column(String(20), default="medium")
    
    # Source information
    source_platform = Column(String(50), nullable=True)
    source_location = Column(String(200), nullable=True)
    estimated_reach = Column(Integer, nullable=True)
    
    # Processing status
    status = Column(String(20), default="pending")  # pending, processing, verified, dismissed
    ai_verification_id = Column(UUID(as_uuid=True), ForeignKey("verifications.id"), nullable=True)
    moderator_notes = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    # Relationships
    reporter = relationship("User", back_populates="community_reports")

class CommunityFeedback(Base):
    """Community feedback on verification results"""
    __tablename__ = "community_feedback"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    verification_id = Column(UUID(as_uuid=True), ForeignKey("verifications.id"), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    
    # Feedback details
    feedback_type = Column(String(20), nullable=False)  # helpful, not_helpful, incorrect, spam
    rating = Column(Integer, nullable=True)  # 1-5 rating
    comment = Column(Text, nullable=True)
    
    # Additional information
    expertise_level = Column(String(20), nullable=True)  # novice, intermediate, expert
    confidence_in_feedback = Column(Float, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    
    # Relationships
    verification = relationship("Verification", back_populates="community_feedback")

class ThreatAlert(Base):
    """High-risk misinformation threat alerts"""
    __tablename__ = "threat_alerts"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    verification_id = Column(UUID(as_uuid=True), ForeignKey("verifications.id"), nullable=True)
    
    # Alert details
    alert_type = Column(String(50), nullable=False)  # critical_misinfo, mass_disinformation, deepfake_campaign
    threat_level = Column(String(20), nullable=False)  # high, critical
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=False)
    
    # Impact assessment
    estimated_reach = Column(Integer, nullable=True)
    affected_demographics = Column(JSON, nullable=True)
    potential_harm_level = Column(String(20), nullable=True)
    
    # Geographic information
    affected_regions = Column(JSON, nullable=True)
    source_location = Column(String(200), nullable=True)
    
    # Response status
    alert_status = Column(String(20), default="active")  # active, monitoring, resolved
    response_actions = Column(JSON, nullable=True)
    stakeholders_notified = Column(JSON, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    expires_at = Column(DateTime(timezone=True), nullable=True)

class WhatsAppMessage(Base):
    """WhatsApp tipline messages"""
    __tablename__ = "whatsapp_messages"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Message details
    whatsapp_id = Column(String(100), unique=True, nullable=False)  # WhatsApp message ID
    sender_number = Column(String(20), nullable=False)
    message_type = Column(String(20), nullable=False)  # text, image, video, audio, document
    content = Column(Text, nullable=True)
    media_url = Column(String(1000), nullable=True)
    
    # Processing status
    processing_status = Column(String(20), default="received")  # received, processing, verified, responded
    verification_id = Column(UUID(as_uuid=True), ForeignKey("verifications.id"), nullable=True)
    response_sent = Column(Boolean, default=False)
    response_content = Column(Text, nullable=True)
    
    # Message metadata
    sender_name = Column(String(200), nullable=True)
    language_detected = Column(String(10), nullable=True)
    urgency_level = Column(String(20), default="normal")
    
    # Timestamps
    received_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    processed_at = Column(DateTime(timezone=True), nullable=True)
    responded_at = Column(DateTime(timezone=True), nullable=True)

class EducationProgress(Base):
    """User progress in educational modules"""
    __tablename__ = "education_progress"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    
    # Module information
    module_name = Column(String(100), nullable=False)
    module_version = Column(String(20), default="1.0")
    
    # Progress tracking
    completion_percentage = Column(Float, default=0.0)
    current_lesson = Column(String(100), nullable=True)
    quiz_scores = Column(JSON, nullable=True)
    achievements_earned = Column(JSON, nullable=True)
    
    # Performance metrics
    time_spent_minutes = Column(Integer, default=0)
    accuracy_rate = Column(Float, nullable=True)
    improvement_score = Column(Float, nullable=True)
    
    # Status
    status = Column(String(20), default="in_progress")  # in_progress, completed, paused
    
    # Timestamps
    started_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    completed_at = Column(DateTime(timezone=True), nullable=True)
    last_accessed = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

class APIUsage(Base):
    """API usage tracking"""
    __tablename__ = "api_usage"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    
    # Request details
    endpoint = Column(String(100), nullable=False)
    method = Column(String(10), nullable=False)
    request_id = Column(String(100), nullable=False)
    
    # Usage metrics
    processing_time = Column(Float, nullable=False)
    response_status = Column(Integer, nullable=False)
    content_type = Column(String(20), nullable=True)
    
    # Resource consumption
    ai_model_calls = Column(Integer, default=0)
    cloud_storage_usage = Column(Float, default=0.0)  # MB
    cost_estimation = Column(Float, nullable=True)  # USD
    
    # Client information
    user_agent = Column(String(500), nullable=True)
    ip_address = Column(String(45), nullable=True)
    platform = Column(String(50), nullable=True)  # web, mobile, api
    
    # Timestamps
    timestamp = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
'''

# Create Pydantic schemas
schemas_code = '''
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
'''

# Save database models and schemas
with open('database_models.py', 'w') as f:
    f.write(database_models_code)

with open('api_schemas.py', 'w') as f:
    f.write(schemas_code)

print("✅ Database models created")
print("📊 Models:")
print("- User: Complete user management with profile and statistics")
print("- Verification: Content verification results with blockchain")
print("- CommunityReport: User-submitted misinformation reports")
print("- CommunityFeedback: Feedback on verification accuracy")
print("- ThreatAlert: High-risk misinformation alerts")
print("- WhatsAppMessage: Tipline message processing")
print("- EducationProgress: Learning module progress tracking")
print("- APIUsage: Comprehensive usage analytics")
print("")
print("✅ Pydantic schemas created")
print("📝 Schemas:")
print("- Request/Response models for all endpoints")
print("- Data validation and serialization")
print("- Type hints and field constraints")
print("- Comprehensive API documentation support")