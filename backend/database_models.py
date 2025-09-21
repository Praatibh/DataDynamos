
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
