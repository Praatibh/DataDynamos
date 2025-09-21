# Create WhatsApp service integration
whatsapp_service_code = '''
"""
WhatsApp Business API Integration
Handles tipline messages and automated fact-checking responses
"""

import asyncio
import logging
import json
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
import aiohttp
from urllib.parse import quote

from app.core.ai_engine import TruthGuardAIEngine
from app.services.google_cloud import GoogleCloudService
from app.config import settings

logger = logging.getLogger(__name__)

class WhatsAppService:
    """
    WhatsApp Business API integration for automated fact-checking
    """
    
    def __init__(self):
        self.base_url = "https://graph.facebook.com/v18.0"
        self.phone_number_id = settings.WHATSAPP_PHONE_NUMBER_ID
        self.access_token = settings.WHATSAPP_ACCESS_TOKEN
        self.webhook_verify_token = settings.WHATSAPP_WEBHOOK_VERIFY_TOKEN
        
        self.ai_engine = None
        self.google_cloud = None
        
        # Multi-language response templates
        self.response_templates = {
            "en": {
                "greeting": "Hello! I'm TruthGuard AI. Send me any content you want to fact-check and I'll analyze it for misinformation.",
                "processing": "🔍 Analyzing your content... This may take a moment.",
                "result_authentic": "✅ **AUTHENTIC** (Score: {score}%)\n\n{explanation}\n\n💡 {educational_tip}",
                "result_suspicious": "⚠️ **SUSPICIOUS** (Risk: {risk}%)\n\n{explanation}\n\n📚 Learn more: {educational_content}",
                "result_misinformation": "❌ **MISINFORMATION DETECTED** (Risk: {risk}%)\n\n{explanation}\n\n🛡️ {prevention_tip}",
                "error": "Sorry, I couldn't analyze this content. Please try again or contact support.",
                "help": "Send me:\n📝 Text messages\n🖼️ Images\n🎥 Videos\n🎵 Audio\n\nI'll check them for misinformation!"
            },
            "hi": {
                "greeting": "नमस्ते! मैं TruthGuard AI हूँ। मुझे कोई भी सामग्री भेजें जिसे आप फैक्ट-चेक करवाना चाहते हैं।",
                "processing": "🔍 आपकी सामग्री का विश्लेषण कर रहा हूँ... कृपया प्रतीक्षा करें।",
                "result_authentic": "✅ **प्रामाणिक** (स्कोर: {score}%)\n\n{explanation}\n\n💡 {educational_tip}",
                "result_suspicious": "⚠️ **संदिग्ध** (जोखिम: {risk}%)\n\n{explanation}\n\n📚 और जानें: {educational_content}",
                "result_misinformation": "❌ **गलत सूचना मिली** (जोखिम: {risk}%)\n\n{explanation}\n\n🛡️ {prevention_tip}",
                "error": "माफ़ करें, मैं इस सामग्री का विश्लेषण नहीं कर सका। कृपया फिर कोशिश करें।",
                "help": "मुझे भेजें:\n📝 टेक्स्ट संदेश\n🖼️ तस्वीरें\n🎥 वीडियो\n🎵 ऑडियो\n\nमैं इन्हें गलत सूचना के लिए जाँचूंगा!"
            }
        }
    
    async def initialize(self):
        """Initialize WhatsApp service dependencies"""
        try:
            logger.info("📱 Initializing WhatsApp service...")
            
            # Import here to avoid circular imports
            from app.core.ai_engine import TruthGuardAIEngine
            from app.services.google_cloud import GoogleCloudService
            
            self.ai_engine = TruthGuardAIEngine()
            self.google_cloud = GoogleCloudService()
            
            if not self.ai_engine.gemini_model:
                await self.ai_engine.initialize()
            
            logger.info("✅ WhatsApp service initialized")
            
        except Exception as e:
            logger.error(f"❌ WhatsApp service initialization failed: {e}")
            raise
    
    async def process_webhook(self, webhook_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process incoming WhatsApp webhook"""
        try:
            logger.info(f"📥 Processing WhatsApp webhook: {webhook_data}")
            
            if "entry" not in webhook_data:
                return {"status": "ignored", "reason": "no_entry"}
            
            for entry in webhook_data["entry"]:
                if "changes" in entry:
                    for change in entry["changes"]:
                        if change.get("field") == "messages":
                            await self._process_message_change(change["value"])
            
            return {"status": "processed"}
            
        except Exception as e:
            logger.error(f"❌ Webhook processing failed: {e}")
            return {"status": "error", "error": str(e)}
    
    async def _process_message_change(self, message_data: Dict[str, Any]):
        """Process individual message from webhook"""
        try:
            if "messages" not in message_data:
                return
            
            for message in message_data["messages"]:
                await self._handle_incoming_message(message, message_data.get("contacts", []))
                
        except Exception as e:
            logger.error(f"Message processing failed: {e}")
    
    async def _handle_incoming_message(self, message: Dict[str, Any], contacts: List[Dict]):
        """Handle incoming WhatsApp message"""
        try:
            message_id = message["id"]
            from_number = message["from"]
            message_type = message["type"]
            timestamp = message["timestamp"]
            
            # Get sender name
            sender_name = "Unknown"
            for contact in contacts:
                if contact.get("wa_id") == from_number:
                    sender_name = contact.get("profile", {}).get("name", "Unknown")
                    break
            
            logger.info(f"📨 Processing message from {sender_name} ({from_number}): {message_type}")
            
            # Detect language (simple heuristic)
            detected_language = await self._detect_message_language(message)
            
            # Send processing message
            await self.send_message(
                to_number=from_number,
                message=self.response_templates[detected_language]["processing"]
            )
            
            # Extract content based on message type
            content, content_type = await self._extract_message_content(message)
            
            if not content:
                await self.send_message(
                    to_number=from_number,
                    message=self.response_templates[detected_language]["help"]
                )
                return
            
            # Perform AI analysis
            analysis_result = await self.ai_engine.analyze_content(
                content=content,
                content_type=content_type,
                metadata={
                    "source": "whatsapp",
                    "sender": from_number,
                    "sender_name": sender_name,
                    "language": detected_language,
                    "timestamp": timestamp
                }
            )
            
            # Generate response message
            response_message = await self._generate_response_message(
                analysis_result, detected_language
            )
            
            # Send response
            await self.send_message(
                to_number=from_number,
                message=response_message
            )
            
            # Store message and result
            await self._store_whatsapp_interaction(
                message=message,
                sender_name=sender_name,
                analysis_result=analysis_result,
                response_message=response_message,
                detected_language=detected_language
            )
            
            logger.info(f"✅ Message processed successfully: {message_id}")
            
        except Exception as e:
            logger.error(f"❌ Message handling failed: {e}")
            # Send error message
            try:
                await self.send_message(
                    to_number=message.get("from", ""),
                    message=self.response_templates["en"]["error"]
                )
            except:
                pass
    
    async def _detect_message_language(self, message: Dict[str, Any]) -> str:
        """Detect message language (simple implementation)"""
        try:
            # Get text content
            text_content = ""
            if message["type"] == "text":
                text_content = message.get("text", {}).get("body", "")
            elif message["type"] == "interactive" and "button_reply" in message.get("interactive", {}):
                text_content = message["interactive"]["button_reply"].get("title", "")
            
            # Simple language detection based on common words/scripts
            hindi_indicators = ["है", "हैं", "का", "के", "की", "से", "में", "पर", "और", "या"]
            
            if any(indicator in text_content for indicator in hindi_indicators):
                return "hi"
            
            return "en"  # Default to English
            
        except Exception:
            return "en"
    
    async def _extract_message_content(self, message: Dict[str, Any]) -> tuple[Optional[str], Optional[str]]:
        """Extract content and type from WhatsApp message"""
        try:
            message_type = message["type"]
            
            if message_type == "text":
                return message["text"]["body"], "text"
            
            elif message_type == "image":
                # Download image
                media_id = message["image"]["id"]
                image_url = await self._download_whatsapp_media(media_id)
                return image_url, "image_url"
            
            elif message_type == "video":
                # Download video
                media_id = message["video"]["id"]
                video_url = await self._download_whatsapp_media(media_id)
                return video_url, "video_url"
            
            elif message_type == "audio":
                # Download audio
                media_id = message["audio"]["id"]
                audio_url = await self._download_whatsapp_media(media_id)
                return audio_url, "audio_url"
            
            elif message_type == "document":
                # Handle document (limited support)
                doc = message["document"]
                if doc.get("mime_type", "").startswith("image/"):
                    media_id = doc["id"]
                    doc_url = await self._download_whatsapp_media(media_id)
                    return doc_url, "image_url"
            
            return None, None
            
        except Exception as e:
            logger.error(f"Content extraction failed: {e}")
            return None, None
    
    async def _download_whatsapp_media(self, media_id: str) -> str:
        """Download media from WhatsApp and upload to cloud storage"""
        try:
            # Get media URL from WhatsApp API
            async with aiohttp.ClientSession() as session:
                headers = {"Authorization": f"Bearer {self.access_token}"}
                
                # Get media info
                async with session.get(
                    f"{self.base_url}/{media_id}",
                    headers=headers
                ) as response:
                    media_info = await response.json()
                
                if "url" not in media_info:
                    raise Exception("No media URL in response")
                
                # Download media content
                async with session.get(
                    media_info["url"],
                    headers=headers
                ) as response:
                    media_content = await response.read()
                
                # Upload to cloud storage
                filename = f"whatsapp_media_{media_id}"
                content_type = media_info.get("mime_type", "application/octet-stream")
                
                media_url = await self.google_cloud.upload_file(
                    file_content=media_content,
                    filename=filename,
                    content_type=content_type
                )
                
                return media_url
                
        except Exception as e:
            logger.error(f"Media download failed: {e}")
            raise
    
    async def _generate_response_message(
        self, 
        analysis_result, 
        language: str
    ) -> str:
        """Generate response message based on analysis result"""
        try:
            templates = self.response_templates[language]
            
            authenticity_score = int(analysis_result.authenticity_score * 100)
            risk_score = int(analysis_result.misinformation_likelihood * 100)
            
            # Determine response type
            if analysis_result.risk_level == "critical" or risk_score >= 80:
                template = templates["result_misinformation"]
                explanation = analysis_result.detection_details.get(
                    "explanation", 
                    "This content shows strong signs of misinformation."
                )
                prevention_tip = "Always verify information from official sources before sharing."
                
                response = template.format(
                    risk=risk_score,
                    explanation=explanation,
                    prevention_tip=prevention_tip
                )
                
            elif analysis_result.risk_level in ["high", "medium"] or risk_score >= 40:
                template = templates["result_suspicious"]
                explanation = analysis_result.detection_details.get(
                    "explanation",
                    "This content requires further verification."
                )
                educational_content = "Check multiple reliable sources before believing or sharing."
                
                response = template.format(
                    risk=risk_score,
                    explanation=explanation,
                    educational_content=educational_content
                )
                
            else:
                template = templates["result_authentic"]
                explanation = analysis_result.detection_details.get(
                    "explanation",
                    "This content appears to be authentic."
                )
                educational_tip = "Always stay vigilant and cross-check important information."
                
                response = template.format(
                    score=authenticity_score,
                    explanation=explanation,
                    educational_tip=educational_tip
                )
            
            # Add blockchain verification info
            response += f"\n\n🔗 Blockchain Hash: {analysis_result.blockchain_hash[:16]}..."
            response += f"\n⏱️ Analysis time: {analysis_result.processing_time:.1f}s"
            
            # Add educational resources
            if analysis_result.educational_content:
                tips = analysis_result.educational_content.get("tips", [])
                if tips and len(tips) > 0:
                    response += f"\n\n💡 Tip: {tips[0]}"
            
            return response
            
        except Exception as e:
            logger.error(f"Response generation failed: {e}")
            return self.response_templates[language]["error"]
    
    async def send_message(self, to_number: str, message: str) -> bool:
        """Send message to WhatsApp number"""
        try:
            url = f"{self.base_url}/{self.phone_number_id}/messages"
            headers = {
                "Authorization": f"Bearer {self.access_token}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "messaging_product": "whatsapp",
                "to": to_number,
                "text": {"body": message}
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(url, headers=headers, json=payload) as response:
                    if response.status == 200:
                        logger.info(f"📤 Message sent to {to_number}")
                        return True
                    else:
                        error = await response.text()
                        logger.error(f"Failed to send message: {error}")
                        return False
                        
        except Exception as e:
            logger.error(f"Message sending failed: {e}")
            return False
    
    async def _store_whatsapp_interaction(
        self,
        message: Dict[str, Any],
        sender_name: str,
        analysis_result,
        response_message: str,
        detected_language: str
    ):
        """Store WhatsApp interaction in database"""
        try:
            interaction_data = {
                "whatsapp_id": message["id"],
                "sender_number": message["from"],
                "sender_name": sender_name,
                "message_type": message["type"],
                "content": message.get("text", {}).get("body", "") if message["type"] == "text" else "",
                "processing_status": "completed",
                "verification_id": analysis_result.content_id,
                "response_sent": True,
                "response_content": response_message,
                "language_detected": detected_language,
                "received_at": datetime.now(timezone.utc),
                "processed_at": datetime.now(timezone.utc),
                "responded_at": datetime.now(timezone.utc)
            }
            
            # Store in Firestore
            await self.google_cloud.firestore_client.collection("whatsapp_messages").add(interaction_data)
            
            logger.info(f"💾 WhatsApp interaction stored: {message['id']}")
            
        except Exception as e:
            logger.error(f"Failed to store interaction: {e}")
    
    async def get_tipline_stats(self, days: int = 30) -> Dict[str, Any]:
        """Get WhatsApp tipline statistics"""
        try:
            from datetime import datetime, timedelta
            
            # Calculate date range
            end_date = datetime.now(timezone.utc)
            start_date = end_date - timedelta(days=days)
            
            # Query WhatsApp messages
            query = (
                self.google_cloud.firestore_client.collection("whatsapp_messages")
                .where("received_at", ">=", start_date)
                .where("received_at", "<=", end_date)
            )
            
            total_messages = 0
            unique_users = set()
            message_types = {}
            languages = {}
            processed_count = 0
            
            async for doc in query.stream():
                data = doc.to_dict()
                total_messages += 1
                unique_users.add(data.get("sender_number", ""))
                
                msg_type = data.get("message_type", "unknown")
                message_types[msg_type] = message_types.get(msg_type, 0) + 1
                
                lang = data.get("language_detected", "en")
                languages[lang] = languages.get(lang, 0) + 1
                
                if data.get("processing_status") == "completed":
                    processed_count += 1
            
            return {
                "total_messages": total_messages,
                "unique_users": len(unique_users),
                "processed_messages": processed_count,
                "processing_rate": (processed_count / total_messages * 100) if total_messages > 0 else 0,
                "message_types": message_types,
                "languages": languages,
                "date_range": {
                    "start": start_date.isoformat(),
                    "end": end_date.isoformat(),
                    "days": days
                }
            }
            
        except Exception as e:
            logger.error(f"Stats calculation failed: {e}")
            return {}
    
    async def health_check(self) -> bool:
        """Check WhatsApp service health"""
        try:
            # Simple API test
            url = f"{self.base_url}/{self.phone_number_id}"
            headers = {"Authorization": f"Bearer {self.access_token}"}
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers) as response:
                    return response.status == 200
                    
        except Exception as e:
            logger.error(f"WhatsApp health check failed: {e}")
            return False
    
    async def cleanup(self):
        """Cleanup resources"""
        logger.info("🧹 Cleaning up WhatsApp service resources...")
'''

# Create configuration file
config_code = '''
"""
Configuration settings for TruthGuard AI Backend
"""

import os
from typing import List, Optional
from pydantic import BaseSettings, validator

class Settings(BaseSettings):
    """Application settings"""
    
    # Basic app configuration
    APP_NAME: str = "TruthGuard AI"
    APP_VERSION: str = "2.0.0"
    DEBUG: bool = False
    TESTING: bool = False
    
    # Server configuration
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    WORKERS: int = 1
    
    # Security settings
    SECRET_KEY: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    ALGORITHM: str = "HS256"
    
    # CORS settings
    ALLOWED_ORIGINS: List[str] = ["*"]
    ALLOWED_HOSTS: List[str] = ["*"]
    
    # Database configuration
    DATABASE_URL: str = "postgresql://user:password@localhost/truthguard"
    DATABASE_ECHO: bool = False
    
    # Google Cloud configuration
    GOOGLE_CLOUD_PROJECT: str
    GOOGLE_APPLICATION_CREDENTIALS: Optional[str] = None
    VERTEX_AI_LOCATION: str = "us-central1"
    
    # Storage configuration
    CONTENT_BUCKET_NAME: Optional[str] = None
    MODEL_BUCKET_NAME: Optional[str] = None
    MAX_FILE_SIZE: int = 50 * 1024 * 1024  # 50MB
    
    # AI Model settings
    GEMINI_MODEL_VERSION: str = "gemini-2.0-flash"
    DEFAULT_CONFIDENCE_THRESHOLD: float = 0.7
    MAX_BATCH_SIZE: int = 10
    
    # WhatsApp Business API
    WHATSAPP_PHONE_NUMBER_ID: str = ""
    WHATSAPP_ACCESS_TOKEN: str = ""
    WHATSAPP_WEBHOOK_VERIFY_TOKEN: str = ""
    WHATSAPP_APP_ID: str = ""
    WHATSAPP_APP_SECRET: str = ""
    
    # External API keys
    FACT_CHECK_API_KEY: Optional[str] = None
    SOCIAL_MEDIA_API_KEYS: dict = {}
    
    # Redis configuration (for caching)
    REDIS_URL: Optional[str] = None
    CACHE_TTL: int = 3600  # 1 hour
    
    # Email configuration
    SMTP_SERVER: Optional[str] = None
    SMTP_PORT: int = 587
    SMTP_USERNAME: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    FROM_EMAIL: Optional[str] = None
    
    # Monitoring and logging
    LOG_LEVEL: str = "INFO"
    SENTRY_DSN: Optional[str] = None
    ENABLE_METRICS: bool = True
    METRICS_PORT: int = 9090
    
    # Rate limiting
    RATE_LIMIT_PER_MINUTE: int = 60
    RATE_LIMIT_PER_HOUR: int = 1000
    PREMIUM_RATE_LIMIT_MULTIPLIER: int = 10
    
    # Webhook settings
    WEBHOOK_SECRET: Optional[str] = None
    WEBHOOK_TIMEOUT: int = 30
    
    # Feature flags
    ENABLE_COMMUNITY_REPORTS: bool = True
    ENABLE_EDUCATION_MODULES: bool = True
    ENABLE_BLOCKCHAIN_VERIFICATION: bool = True
    ENABLE_WHATSAPP_INTEGRATION: bool = True
    ENABLE_SOCIAL_MEDIA_MONITORING: bool = False
    
    # Performance settings
    MAX_CONCURRENT_ANALYSES: int = 100
    ANALYSIS_TIMEOUT: int = 300  # 5 minutes
    CLEANUP_INTERVAL: int = 3600  # 1 hour
    
    @validator("ALLOWED_ORIGINS", pre=True)
    def assemble_cors_origins(cls, v):
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)
    
    @validator("ALLOWED_HOSTS", pre=True)
    def assemble_allowed_hosts(cls, v):
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)
    
    @validator("CONTENT_BUCKET_NAME", pre=True, always=True)
    def set_content_bucket_name(cls, v, values):
        if not v:
            return f"{values.get('GOOGLE_CLOUD_PROJECT', 'truthguard')}-content-storage"
        return v
    
    @validator("MODEL_BUCKET_NAME", pre=True, always=True)
    def set_model_bucket_name(cls, v, values):
        if not v:
            return f"{values.get('GOOGLE_CLOUD_PROJECT', 'truthguard')}-model-artifacts"
        return v
    
    class Config:
        env_file = ".env"
        case_sensitive = True

# Create settings instance
settings = Settings()

# Environment-specific settings
if settings.DEBUG:
    settings.LOG_LEVEL = "DEBUG"
    settings.DATABASE_ECHO = True

# Production overrides
if not settings.DEBUG:
    settings.ALLOWED_ORIGINS = [
        "https://truthguard.ai",
        "https://www.truthguard.ai",
        "https://api.truthguard.ai"
    ]
    settings.ALLOWED_HOSTS = [
        "truthguard.ai",
        "www.truthguard.ai", 
        "api.truthguard.ai"
    ]
'''

# Create requirements.txt
requirements_content = '''# TruthGuard AI Backend Requirements

# FastAPI and server
fastapi==0.104.1
uvicorn[standard]==0.24.0
gunicorn==21.2.0

# Database and ORM
sqlalchemy==2.0.23
asyncpg==0.29.0
alembic==1.13.0
psycopg2-binary==2.9.9

# Authentication and security
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
python-multipart==0.0.6
cryptography==41.0.8

# Google Cloud services
google-cloud-aiplatform==1.38.0
google-cloud-vision==3.4.0
google-cloud-videointelligence==2.11.0
google-cloud-speech==2.21.0
google-cloud-firestore==2.13.0
google-cloud-storage==2.10.0
google-oauth2-tool==0.0.3
vertexai==1.38.0

# HTTP client and async
aiohttp==3.9.0
httpx==0.25.2
requests==2.31.0

# Data processing and validation
pydantic==2.5.0
pydantic[email]==2.5.0
python-dateutil==2.8.2
pytz==2023.3

# Caching and message queue
redis==5.0.1
celery==5.3.4

# Monitoring and logging
sentry-sdk==1.38.0
structlog==23.2.0
prometheus-client==0.19.0

# Image and media processing
Pillow==10.1.0
opencv-python==4.8.1.78
moviepy==1.0.3

# Language processing
langdetect==1.0.9
googletrans==4.0.0

# Utilities
python-dotenv==1.0.0
email-validator==2.1.0
phonenumbers==8.13.26
click==8.1.7
rich==13.7.0

# Development dependencies
pytest==7.4.3
pytest-asyncio==0.21.1
pytest-cov==4.1.0
black==23.11.0
isort==5.12.0
flake8==6.1.0
mypy==1.7.1

# Optional dependencies for advanced features
numpy==1.25.2
pandas==2.1.3
matplotlib==3.8.2
scikit-learn==1.3.2
transformers==4.36.0
torch==2.1.1
'''

# Save WhatsApp service, configuration, and requirements
with open('whatsapp_service.py', 'w') as f:
    f.write(whatsapp_service_code)

with open('config.py', 'w') as f:
    f.write(config_code)

with open('requirements.txt', 'w') as f:
    f.write(requirements_content)

print("✅ WhatsApp Business API integration created")
print("📱 Features:")
print("- Multi-language support (English, Hindi)")
print("- Automated content analysis and response")
print("- Media download and processing")
print("- Real-time fact-checking responses")
print("- Interaction tracking and analytics")
print("- Webhook processing for incoming messages")
print("")
print("✅ Configuration system created")
print("⚙️ Settings:")
print("- Environment-based configuration")
print("- Google Cloud integration settings")
print("- WhatsApp API credentials")
print("- Security and rate limiting")
print("- Feature flags and performance tuning")
print("- Development and production modes")
print("")
print("✅ Requirements file generated")
print("📦 Dependencies:")
print("- 40+ production-ready packages")
print("- Google Cloud AI services")
print("- FastAPI with async support")
print("- Database and caching systems")
print("- Authentication and security")
print("- Media processing and analysis")