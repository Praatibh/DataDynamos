
"""
Google Cloud Services Integration
Handles all Google Cloud AI service integrations
"""

import asyncio
import logging
import os
from typing import Optional, Dict, Any, List
import aiohttp
import base64

from google.cloud import aiplatform
from google.cloud import vision
from google.cloud import videointelligence  
from google.cloud import speech
from google.cloud import storage
from google.cloud import firestore
from google.oauth2 import service_account
import vertexai

from config import settings

logger = logging.getLogger(__name__)

class GoogleCloudService:
    """Unified Google Cloud services handler"""

    def __init__(self):
        self.project_id = settings.GOOGLE_CLOUD_PROJECT
        self.location = settings.VERTEX_AI_LOCATION

        # Initialize clients as None
        self.vision_client = None
        self.video_client = None
        self.speech_client = None
        self.storage_client = None
        self.firestore_client = None

        # Storage bucket names
        self.content_bucket = f"{self.project_id}-content-storage"
        self.model_bucket = f"{self.project_id}-model-artifacts"

    async def initialize(self):
        """Initialize all Google Cloud clients"""
        try:
            logger.info("🔧 Initializing Google Cloud services...")

            # Set up authentication
            if settings.GOOGLE_APPLICATION_CREDENTIALS:
                credentials = service_account.Credentials.from_service_account_file(
                    settings.GOOGLE_APPLICATION_CREDENTIALS
                )
            else:
                credentials = None

            # Initialize Vertex AI
            vertexai.init(
                project=self.project_id,
                location=self.location,
                credentials=credentials
            )

            # Initialize service clients
            self.vision_client = vision.ImageAnnotatorClient(credentials=credentials)
            self.video_client = videointelligence.VideoIntelligenceServiceClient(credentials=credentials)
            self.speech_client = speech.SpeechClient(credentials=credentials)
            self.storage_client = storage.Client(
                project=self.project_id,
                credentials=credentials
            )
            self.firestore_client = firestore.Client(
                project=self.project_id,
                credentials=credentials
            )

            # Ensure storage buckets exist
            await self._ensure_buckets_exist()

            logger.info("✅ Google Cloud services initialized")

        except Exception as e:
            logger.error(f"❌ Google Cloud initialization failed: {e}")
            raise

    async def _ensure_buckets_exist(self):
        """Ensure required storage buckets exist"""
        try:
            buckets_to_create = [self.content_bucket, self.model_bucket]

            for bucket_name in buckets_to_create:
                try:
                    bucket = self.storage_client.bucket(bucket_name)
                    if not bucket.exists():
                        bucket = self.storage_client.create_bucket(bucket_name, location="US")
                        logger.info(f"📦 Created storage bucket: {bucket_name}")
                except Exception as e:
                    logger.warning(f"Bucket creation/check failed for {bucket_name}: {e}")

        except Exception as e:
            logger.error(f"Bucket setup failed: {e}")

    async def upload_file(
        self, 
        file_content: bytes, 
        filename: str, 
        content_type: str,
        bucket_name: Optional[str] = None
    ) -> str:
        """Upload file to Google Cloud Storage"""
        try:
            bucket_name = bucket_name or self.content_bucket
            bucket = self.storage_client.bucket(bucket_name)

            # Generate unique filename with timestamp
            import uuid
            from datetime import datetime
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            unique_filename = f"{timestamp}_{uuid.uuid4().hex[:8]}_{filename}"

            blob = bucket.blob(unique_filename)
            blob.upload_from_string(file_content, content_type=content_type)

            # Make blob publicly readable for analysis
            blob.make_public()

            file_url = blob.public_url
            logger.info(f"📁 File uploaded: {unique_filename}")

            return file_url

        except Exception as e:
            logger.error(f"File upload failed: {e}")
            raise

    async def upload_video(self, video_content: str) -> str:
        """Upload video content for analysis"""
        try:
            if video_content.startswith("http"):
                return video_content

            # Decode base64 video content
            video_bytes = base64.b64decode(video_content)

            return await self.upload_file(
                file_content=video_bytes,
                filename="analysis_video.mp4",
                content_type="video/mp4"
            )

        except Exception as e:
            logger.error(f"Video upload failed: {e}")
            raise

    async def upload_audio(self, audio_content: str) -> str:
        """Upload audio content for analysis"""
        try:
            if audio_content.startswith("http"):
                return audio_content

            # Decode base64 audio content
            audio_bytes = base64.b64decode(audio_content)

            return await self.upload_file(
                file_content=audio_bytes,
                filename="analysis_audio.wav",
                content_type="audio/wav"
            )

        except Exception as e:
            logger.error(f"Audio upload failed: {e}")
            raise

    async def analyze_image_safety(self, image_content: bytes) -> Dict[str, Any]:
        """Analyze image for unsafe content using Vision API"""
        try:
            image = vision.Image(content=image_content)

            # Perform safe search detection
            response = self.vision_client.safe_search_detection(image=image)
            safe = response.safe_search_annotation

            # Get likelihood names
            likelihood_name = ('UNKNOWN', 'VERY_UNLIKELY', 'UNLIKELY', 'POSSIBLE', 'LIKELY', 'VERY_LIKELY')

            safety_scores = {
                'adult': likelihood_name[safe.adult],
                'medical': likelihood_name[safe.medical], 
                'spoofed': likelihood_name[safe.spoof],
                'violence': likelihood_name[safe.violence],
                'racy': likelihood_name[safe.racy]
            }

            # Calculate overall safety score
            risk_levels = ['VERY_UNLIKELY', 'UNLIKELY', 'POSSIBLE', 'LIKELY', 'VERY_LIKELY']
            safety_score = 1.0 - (max(risk_levels.index(score) for score in safety_scores.values()) / len(risk_levels))

            return {
                'safety_score': safety_score,
                'safety_details': safety_scores,
                'is_safe': safety_score > 0.7
            }

        except Exception as e:
            logger.error(f"Image safety analysis failed: {e}")
            return {'safety_score': 0.5, 'is_safe': True, 'error': str(e)}

    async def get_vertex_ai_prediction(
        self, 
        model_name: str, 
        instances: List[Dict], 
        parameters: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """Get prediction from Vertex AI model"""
        try:
            endpoint_name = f"projects/{self.project_id}/locations/{self.location}/endpoints/{model_name}"

            # Initialize AI Platform client
            client_options = {"api_endpoint": f"{self.location}-aiplatform.googleapis.com"}
            client = aiplatform.gapic.PredictionServiceClient(client_options=client_options)

            # Prepare request
            response = client.predict(
                endpoint=endpoint_name,
                instances=instances,
                parameters=parameters or {}
            )

            return {
                'predictions': response.predictions,
                'deployed_model_id': response.deployed_model_id,
                'model_display_name': response.model_display_name
            }

        except Exception as e:
            logger.error(f"Vertex AI prediction failed: {e}")
            raise

    async def store_verification_result(self, verification_id: str, result: Dict[str, Any]):
        """Store verification result in Firestore"""
        try:
            doc_ref = self.firestore_client.collection('verifications').document(verification_id)
            doc_ref.set({
                **result,
                'created_at': firestore.SERVER_TIMESTAMP,
                'updated_at': firestore.SERVER_TIMESTAMP
            })

            logger.info(f"📊 Verification result stored: {verification_id}")

        except Exception as e:
            logger.error(f"Result storage failed: {e}")
            raise

    async def get_verification_history(
        self, 
        user_id: str, 
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Get user's verification history"""
        try:
            query = (
                self.firestore_client.collection('verifications')
                .where('user_id', '==', user_id)
                .order_by('created_at', direction=firestore.Query.DESCENDING)
                .limit(limit)
            )

            results = []
            for doc in query.stream():
                result = doc.to_dict()
                result['id'] = doc.id
                results.append(result)

            return results

        except Exception as e:
            logger.error(f"History retrieval failed: {e}")
            return []

    async def get_platform_analytics(self, days: int = 30) -> Dict[str, Any]:
        """Get platform analytics from Firestore"""
        try:
            from datetime import datetime, timedelta

            # Calculate date range
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)

            # Query verifications in date range
            query = (
                self.firestore_client.collection('verifications')
                .where('created_at', '>=', start_date)
                .where('created_at', '<=', end_date)
            )

            # Process results
            total_verifications = 0
            misinformation_detected = 0
            content_types = {}
            risk_levels = {'low': 0, 'medium': 0, 'high': 0, 'critical': 0}

            for doc in query.stream():
                data = doc.to_dict()
                total_verifications += 1

                # Count misinformation
                if data.get('misinformation_likelihood', 0) > 0.7:
                    misinformation_detected += 1

                # Count content types
                content_type = data.get('content_type', 'unknown')
                content_types[content_type] = content_types.get(content_type, 0) + 1

                # Count risk levels
                risk_level = data.get('risk_level', 'low')
                if risk_level in risk_levels:
                    risk_levels[risk_level] += 1

            accuracy_rate = ((total_verifications - misinformation_detected) / total_verifications * 100) if total_verifications > 0 else 0

            return {
                'total_verifications': total_verifications,
                'misinformation_detected': misinformation_detected,
                'accuracy_rate': round(accuracy_rate, 2),
                'content_types': content_types,
                'risk_distribution': risk_levels,
                'date_range': {
                    'start': start_date.isoformat(),
                    'end': end_date.isoformat(),
                    'days': days
                }
            }

        except Exception as e:
            logger.error(f"Analytics retrieval failed: {e}")
            return {}

    async def health_check(self) -> bool:
        """Check health of Google Cloud services"""
        try:
            # Test Vision API
            test_image = vision.Image(content=b"dummy_content")
            # This will fail but connection test is what we need
            try:
                self.vision_client.label_detection(image=test_image)
            except:
                pass  # Expected to fail with dummy content

            # Test Firestore
            self.firestore_client.collection('health_check').limit(1).get()

            # Test Storage
            self.storage_client.list_buckets(max_results=1)

            return True

        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return False

    async def cleanup(self):
        """Cleanup resources"""
        logger.info("🧹 Cleaning up Google Cloud resources...")
        # Close any open connections if needed
        pass
