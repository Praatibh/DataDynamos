
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
                "result_authentic": "✅ **AUTHENTIC** (Score: {score}%)

{explanation}

💡 {educational_tip}",
                "result_suspicious": "⚠️ **SUSPICIOUS** (Risk: {risk}%)

{explanation}

📚 Learn more: {educational_content}",
                "result_misinformation": "❌ **MISINFORMATION DETECTED** (Risk: {risk}%)

{explanation}

🛡️ {prevention_tip}",
                "error": "Sorry, I couldn't analyze this content. Please try again or contact support.",
                "help": "Send me:
📝 Text messages
🖼️ Images
🎥 Videos
🎵 Audio

I'll check them for misinformation!"
            },
            "hi": {
                "greeting": "नमस्ते! मैं TruthGuard AI हूँ। मुझे कोई भी सामग्री भेजें जिसे आप फैक्ट-चेक करवाना चाहते हैं।",
                "processing": "🔍 आपकी सामग्री का विश्लेषण कर रहा हूँ... कृपया प्रतीक्षा करें।",
                "result_authentic": "✅ **प्रामाणिक** (स्कोर: {score}%)

{explanation}

💡 {educational_tip}",
                "result_suspicious": "⚠️ **संदिग्ध** (जोखिम: {risk}%)

{explanation}

📚 और जानें: {educational_content}",
                "result_misinformation": "❌ **गलत सूचना मिली** (जोखिम: {risk}%)

{explanation}

🛡️ {prevention_tip}",
                "error": "माफ़ करें, मैं इस सामग्री का विश्लेषण नहीं कर सका। कृपया फिर कोशिश करें।",
                "help": "मुझे भेजें:
📝 टेक्स्ट संदेश
🖼️ तस्वीरें
🎥 वीडियो
🎵 ऑडियो

मैं इन्हें गलत सूचना के लिए जाँचूंगा!"
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
            response += f"

🔗 Blockchain Hash: {analysis_result.blockchain_hash[:16]}..."
            response += f"
⏱️ Analysis time: {analysis_result.processing_time:.1f}s"

            # Add educational resources
            if analysis_result.educational_content:
                tips = analysis_result.educational_content.get("tips", [])
                if tips and len(tips) > 0:
                    response += f"

💡 Tip: {tips[0]}"

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
