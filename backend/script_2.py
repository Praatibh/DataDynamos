# Create the AI Engine - Core misinformation detection system
ai_engine_code = '''
"""
TruthGuard AI Engine - Core Misinformation Detection System
Advanced multimodal AI analysis using Google Cloud services
"""

import asyncio
import hashlib
import json
import logging
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
import aiohttp
import numpy as np
from dataclasses import dataclass

# Google Cloud imports
from google.cloud import aiplatform
from google.cloud import vision
from google.cloud import videointelligence
from google.cloud import speech
from google.cloud import storage
import vertexai
from vertexai.generative_models import GenerativeModel, Part

from app.services.google_cloud import GoogleCloudService
from app.services.fact_check_apis import FactCheckService
from app.core.blockchain import BlockchainVerifier
from app.utils.helpers import calculate_confidence_score, extract_metadata
from app.config import settings

logger = logging.getLogger(__name__)

@dataclass
class AnalysisResult:
    """Structure for AI analysis results"""
    content_id: str
    authenticity_score: float
    misinformation_likelihood: float
    risk_level: str
    detection_details: Dict[str, Any]
    educational_content: Dict[str, Any]
    fact_check_sources: List[Dict]
    processing_time: float
    confidence_scores: Dict[str, float]
    metadata: Dict[str, Any]

class TruthGuardAIEngine:
    """
    Core AI engine for multimodal misinformation detection
    """
    
    def __init__(self):
        self.google_cloud = GoogleCloudService()
        self.fact_checker = FactCheckService()
        self.blockchain = BlockchainVerifier()
        
        # AI models
        self.gemini_model = None
        self.vision_client = None
        self.video_client = None
        self.speech_client = None
        
        # Performance tracking
        self.total_verifications = 0
        self.successful_detections = 0
        self.average_response_time = 0.0
        
        # Known misinformation patterns (updated dynamically)
        self.misinformation_patterns = {
            "election_manipulation": [
                "voting machines hacked",
                "fake polling results",
                "voter fraud conspiracy"
            ],
            "health_misinformation": [
                "vaccine microchips",
                "covid hoax",
                "miracle cure"
            ],
            "deepfake_indicators": [
                "unnatural facial movements",
                "inconsistent lighting",
                "audio sync issues"
            ]
        }
        
        # Trusted source domains
        self.trusted_sources = {
            "news": [
                "pti.org.in", "thehindu.com", "indianexpress.com",
                "timesofindia.com", "ndtv.com", "republicworld.com"
            ],
            "government": [
                "pib.gov.in", "mygov.in", "nic.in", "india.gov.in"
            ],
            "fact_check": [
                "boomlive.in", "altnews.in", "factchecker.in",
                "vishvasnews.com", "newsmobile.in"
            ]
        }
    
    async def initialize(self):
        """Initialize AI models and services"""
        try:
            logger.info("🤖 Initializing TruthGuard AI Engine...")
            
            # Initialize Vertex AI
            vertexai.init(project=settings.GOOGLE_CLOUD_PROJECT, location=settings.VERTEX_AI_LOCATION)
            
            # Initialize Gemini model
            self.gemini_model = GenerativeModel("gemini-2.0-flash")
            
            # Initialize Google Cloud clients
            await self.google_cloud.initialize()
            self.vision_client = self.google_cloud.vision_client
            self.video_client = self.google_cloud.video_client
            self.speech_client = self.google_cloud.speech_client
            
            # Initialize fact-checking services
            await self.fact_checker.initialize()
            
            logger.info("✅ AI Engine initialized successfully")
            
        except Exception as e:
            logger.error(f"❌ AI Engine initialization failed: {e}")
            raise
    
    async def analyze_content(
        self, 
        content: str, 
        content_type: str, 
        metadata: Optional[Dict] = None
    ) -> AnalysisResult:
        """
        Main content analysis function - routes to appropriate analyzer
        """
        start_time = time.time()
        
        try:
            logger.info(f"🔍 Analyzing {content_type} content: {content[:100]}...")
            
            # Generate content ID
            content_id = self._generate_content_id(content, metadata)
            
            # Route to appropriate analyzer
            if content_type == "text":
                result = await self._analyze_text_content(content, metadata)
            elif content_type == "image" or content_type == "image_url":
                result = await self._analyze_image_content(content, metadata)
            elif content_type == "video" or content_type == "video_url":
                result = await self._analyze_video_content(content, metadata)
            elif content_type == "audio" or content_type == "audio_url":
                result = await self._analyze_audio_content(content, metadata)
            else:
                raise ValueError(f"Unsupported content type: {content_type}")
            
            # Calculate processing time
            processing_time = time.time() - start_time
            
            # Update performance metrics
            self.total_verifications += 1
            self.average_response_time = (
                (self.average_response_time * (self.total_verifications - 1) + processing_time) 
                / self.total_verifications
            )
            
            # Create final analysis result
            analysis_result = AnalysisResult(
                content_id=content_id,
                authenticity_score=result["authenticity_score"],
                misinformation_likelihood=result["misinformation_likelihood"],
                risk_level=self._calculate_risk_level(result["misinformation_likelihood"]),
                detection_details=result["detection_details"],
                educational_content=await self._generate_educational_content(result),
                fact_check_sources=result.get("fact_check_sources", []),
                processing_time=processing_time,
                confidence_scores=result["confidence_scores"],
                metadata=metadata or {}
            )
            
            logger.info(f"✅ Analysis complete: {analysis_result.risk_level} risk level")
            return analysis_result
            
        except Exception as e:
            logger.error(f"❌ Content analysis failed: {e}")
            raise
    
    async def _analyze_text_content(self, text: str, metadata: Dict) -> Dict[str, Any]:
        """Analyze text content for misinformation"""
        
        # Prepare Gemini prompt
        analysis_prompt = f"""
        Analyze the following text for potential misinformation. Consider:
        
        1. FACTUAL ACCURACY: Check claims against known facts
        2. SOURCE CREDIBILITY: Evaluate source indicators
        3. EMOTIONAL MANIPULATION: Identify manipulative language
        4. LOGICAL CONSISTENCY: Check for contradictions
        5. BIAS DETECTION: Identify potential bias or agenda
        6. TEMPORAL CONTEXT: Check if claims are current and relevant
        
        Text to analyze:
        "{text}"
        
        Additional context: {json.dumps(metadata) if metadata else "None"}
        
        Provide analysis in JSON format with:
        {{
            "authenticity_score": float (0-1, where 1 is authentic),
            "misinformation_likelihood": float (0-1, where 1 is likely misinformation),
            "key_claims": [list of main factual claims],
            "red_flags": [list of concerning elements],
            "source_indicators": [list of source credibility markers],
            "emotional_language": [list of emotionally charged phrases],
            "fact_check_needed": boolean,
            "explanation": "detailed explanation of analysis",
            "confidence_level": float (0-1)
        }}
        """
        
        try:
            # Get Gemini analysis
            gemini_response = await self.gemini_model.generate_content_async(analysis_prompt)
            gemini_result = json.loads(gemini_response.text)
            
            # Cross-reference with fact-checking APIs
            fact_check_results = await self.fact_checker.check_claims(
                gemini_result.get("key_claims", [])
            )
            
            # Check against known misinformation patterns
            pattern_matches = self._check_misinformation_patterns(text)
            
            # Adjust scores based on pattern matches
            authenticity_score = gemini_result["authenticity_score"]
            misinformation_likelihood = gemini_result["misinformation_likelihood"]
            
            if pattern_matches:
                misinformation_likelihood = min(1.0, misinformation_likelihood + 0.3)
                authenticity_score = max(0.0, authenticity_score - 0.3)
            
            # Check source credibility if URL provided
            source_score = 1.0
            if metadata and "source_url" in metadata:
                source_score = self._evaluate_source_credibility(metadata["source_url"])
                authenticity_score = (authenticity_score + source_score) / 2
            
            return {
                "authenticity_score": authenticity_score,
                "misinformation_likelihood": misinformation_likelihood,
                "detection_details": {
                    "gemini_analysis": gemini_result,
                    "fact_check_results": fact_check_results,
                    "pattern_matches": pattern_matches,
                    "source_credibility": source_score,
                    "analysis_method": "multimodal_text_analysis"
                },
                "fact_check_sources": fact_check_results,
                "confidence_scores": {
                    "ai_confidence": gemini_result.get("confidence_level", 0.8),
                    "fact_check_confidence": self._calculate_fact_check_confidence(fact_check_results),
                    "pattern_confidence": len(pattern_matches) * 0.2,
                    "overall_confidence": gemini_result.get("confidence_level", 0.8)
                }
            }
            
        except Exception as e:
            logger.error(f"Text analysis failed: {e}")
            # Return default analysis
            return {
                "authenticity_score": 0.5,
                "misinformation_likelihood": 0.5,
                "detection_details": {"error": str(e), "analysis_method": "fallback"},
                "fact_check_sources": [],
                "confidence_scores": {"overall_confidence": 0.3}
            }
    
    async def _analyze_image_content(self, image_content: str, metadata: Dict) -> Dict[str, Any]:
        """Analyze image content for manipulation and misinformation"""
        
        try:
            # Prepare image for analysis
            if image_content.startswith("http"):
                # Download image from URL
                image_data = await self._download_image(image_content)
            else:
                # Assume base64 encoded image
                import base64
                image_data = base64.b64decode(image_content)
            
            # Google Vision API analysis
            vision_image = vision.Image(content=image_data)
            
            # Detect objects, faces, text, and properties
            objects = self.vision_client.object_localization(image=vision_image).localized_object_annotations
            faces = self.vision_client.face_detection(image=vision_image).face_annotations
            texts = self.vision_client.text_detection(image=vision_image).text_annotations
            properties = self.vision_client.image_properties(image=vision_image).image_properties_annotation
            
            # Use Gemini for advanced image analysis
            image_part = Part.from_data(image_data, mime_type="image/jpeg")
            gemini_prompt = """
            Analyze this image for potential manipulation or misinformation:
            
            1. DEEPFAKE DETECTION: Look for signs of AI-generated or manipulated faces
            2. PHOTO MANIPULATION: Check for inconsistent lighting, shadows, or editing artifacts  
            3. CONTEXTUAL ANALYSIS: Evaluate if image content matches claimed context
            4. METADATA ANALYSIS: Check for signs of digital manipulation
            5. REVERSE IMAGE SEARCH: Consider if this might be a recycled/miscontextualized image
            
            Provide analysis in JSON format with authenticity assessment.
            """
            
            gemini_response = await self.gemini_model.generate_content_async([gemini_prompt, image_part])
            gemini_result = json.loads(gemini_response.text)
            
            # Calculate manipulation score based on detection
            manipulation_indicators = {
                "face_manipulation": len(faces) > 0 and any(
                    face.detection_confidence < 0.7 for face in faces
                ),
                "inconsistent_metadata": self._check_image_metadata(properties),
                "text_overlay_suspicious": len(texts) > 0 and self._check_suspicious_text(texts),
                "unnatural_objects": any(obj.score < 0.6 for obj in objects)
            }
            
            manipulation_score = sum(manipulation_indicators.values()) / len(manipulation_indicators)
            
            # Calculate final scores
            authenticity_score = max(0.0, gemini_result.get("authenticity_score", 0.7) - manipulation_score)
            misinformation_likelihood = min(1.0, gemini_result.get("misinformation_likelihood", 0.3) + manipulation_score)
            
            return {
                "authenticity_score": authenticity_score,
                "misinformation_likelihood": misinformation_likelihood,
                "detection_details": {
                    "vision_api_results": {
                        "objects_detected": len(objects),
                        "faces_detected": len(faces),
                        "text_detected": len(texts),
                        "dominant_colors": len(properties.dominant_colors.colors)
                    },
                    "gemini_analysis": gemini_result,
                    "manipulation_indicators": manipulation_indicators,
                    "manipulation_score": manipulation_score,
                    "analysis_method": "multimodal_image_analysis"
                },
                "fact_check_sources": [],
                "confidence_scores": {
                    "vision_confidence": 0.85,
                    "gemini_confidence": gemini_result.get("confidence_level", 0.8),
                    "manipulation_confidence": 1.0 - manipulation_score,
                    "overall_confidence": 0.8
                }
            }
            
        except Exception as e:
            logger.error(f"Image analysis failed: {e}")
            return {
                "authenticity_score": 0.5,
                "misinformation_likelihood": 0.5,
                "detection_details": {"error": str(e), "analysis_method": "fallback"},
                "fact_check_sources": [],
                "confidence_scores": {"overall_confidence": 0.3}
            }
    
    async def _analyze_video_content(self, video_content: str, metadata: Dict) -> Dict[str, Any]:
        """Analyze video content for deepfakes and manipulation"""
        
        try:
            # Process video with Video Intelligence API
            if video_content.startswith("http"):
                video_uri = video_content
            else:
                # Upload video to Cloud Storage first
                video_uri = await self.google_cloud.upload_video(video_content)
            
            # Configure video analysis
            features = [
                videointelligence.Feature.OBJECT_TRACKING,
                videointelligence.Feature.FACE_DETECTION,
                videointelligence.Feature.PERSON_DETECTION,
                videointelligence.Feature.SPEECH_TRANSCRIPTION
            ]
            
            # Start video analysis
            operation = self.video_client.annotate_video(
                request={
                    "features": features,
                    "input_uri": video_uri,
                    "video_context": {
                        "speech_transcription_config": {
                            "language_code": "hi-IN",
                            "enable_automatic_punctuation": True,
                        }
                    }
                }
            )
            
            # Wait for operation to complete (with timeout)
            result = await asyncio.wait_for(operation.result(), timeout=300)
            
            # Extract analysis data
            face_detections = result.annotation_results[0].face_detection_annotations
            speech_transcriptions = result.annotation_results[0].speech_transcriptions
            
            # Analyze transcribed speech for misinformation
            transcribed_text = ""
            if speech_transcriptions:
                transcribed_text = " ".join([
                    transcript.transcript for transcript in speech_transcriptions
                ])
            
            # Use Gemini for deepfake analysis
            gemini_prompt = f"""
            Analyze this video for potential deepfakes or manipulation:
            
            Video metadata: {json.dumps(metadata) if metadata else "None"}
            Transcribed speech: "{transcribed_text}"
            Face detections: {len(face_detections)} faces found
            
            Check for:
            1. DEEPFAKE INDICATORS: Unnatural facial movements, lip-sync issues
            2. VIDEO MANIPULATION: Inconsistent compression, edited segments  
            3. AUDIO ANALYSIS: Voice cloning or synthetic speech
            4. CONTEXTUAL VERIFICATION: Content matching claimed context
            
            Provide analysis in JSON format.
            """
            
            gemini_response = await self.gemini_model.generate_content_async(gemini_prompt)
            gemini_result = json.loads(gemini_response.text)
            
            # Analyze speech content if available
            speech_analysis = {}
            if transcribed_text:
                speech_analysis = await self._analyze_text_content(transcribed_text, metadata)
            
            # Calculate combined scores
            video_authenticity = gemini_result.get("authenticity_score", 0.7)
            speech_authenticity = speech_analysis.get("authenticity_score", 0.7)
            
            # Weight video and speech analysis
            authenticity_score = (video_authenticity * 0.7) + (speech_authenticity * 0.3)
            misinformation_likelihood = 1.0 - authenticity_score
            
            return {
                "authenticity_score": authenticity_score,
                "misinformation_likelihood": misinformation_likelihood,
                "detection_details": {
                    "video_analysis": gemini_result,
                    "face_detections": len(face_detections),
                    "speech_transcription": transcribed_text,
                    "speech_analysis": speech_analysis,
                    "analysis_method": "multimodal_video_analysis"
                },
                "fact_check_sources": speech_analysis.get("fact_check_sources", []),
                "confidence_scores": {
                    "video_confidence": gemini_result.get("confidence_level", 0.7),
                    "speech_confidence": speech_analysis.get("confidence_scores", {}).get("overall_confidence", 0.7),
                    "overall_confidence": 0.75
                }
            }
            
        except Exception as e:
            logger.error(f"Video analysis failed: {e}")
            return {
                "authenticity_score": 0.5,
                "misinformation_likelihood": 0.5,
                "detection_details": {"error": str(e), "analysis_method": "fallback"},
                "fact_check_sources": [],
                "confidence_scores": {"overall_confidence": 0.3}
            }
    
    async def _analyze_audio_content(self, audio_content: str, metadata: Dict) -> Dict[str, Any]:
        """Analyze audio content for voice cloning and misinformation"""
        
        try:
            # Process audio with Speech-to-Text API
            if audio_content.startswith("http"):
                audio_uri = audio_content
            else:
                # Upload audio to Cloud Storage
                audio_uri = await self.google_cloud.upload_audio(audio_content)
            
            # Configure audio analysis
            config = speech.RecognitionConfig(
                encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
                language_code="hi-IN",
                enable_automatic_punctuation=True,
                enable_speaker_diarization=True,
                diarization_speaker_count=2,
            )
            
            audio = speech.RecognitionAudio(uri=audio_uri)
            
            # Perform speech recognition
            operation = self.speech_client.long_running_recognize(
                config=config, audio=audio
            )
            
            response = await asyncio.wait_for(operation.result(), timeout=300)
            
            # Extract transcription
            transcribed_text = ""
            speaker_info = []
            
            for result in response.results:
                transcribed_text += result.alternatives[0].transcript + " "
                
                # Extract speaker information
                for word in result.alternatives[0].words:
                    speaker_info.append({
                        "word": word.word,
                        "speaker_tag": word.speaker_tag,
                        "start_time": word.start_time.total_seconds(),
                        "end_time": word.end_time.total_seconds()
                    })
            
            # Analyze transcribed content
            text_analysis = await self._analyze_text_content(transcribed_text, metadata)
            
            # Use Gemini for voice cloning detection
            gemini_prompt = f"""
            Analyze this audio for potential voice cloning or synthetic speech:
            
            Transcribed content: "{transcribed_text}"
            Speaker changes detected: {len(set(info["speaker_tag"] for info in speaker_info))}
            Audio metadata: {json.dumps(metadata) if metadata else "None"}
            
            Check for:
            1. VOICE CLONING: Signs of synthetic or cloned voice
            2. AUDIO MANIPULATION: Edited or spliced audio segments
            3. AUTHENTICITY MARKERS: Natural speech patterns and background
            4. CONTEXTUAL VERIFICATION: Voice matching claimed speaker
            
            Provide analysis in JSON format.
            """
            
            gemini_response = await self.gemini_model.generate_content_async(gemini_prompt)
            gemini_result = json.loads(gemini_response.text)
            
            # Combine text and voice analysis
            text_score = text_analysis["authenticity_score"]
            voice_score = gemini_result.get("authenticity_score", 0.7)
            
            authenticity_score = (text_score * 0.6) + (voice_score * 0.4)
            misinformation_likelihood = 1.0 - authenticity_score
            
            return {
                "authenticity_score": authenticity_score,
                "misinformation_likelihood": misinformation_likelihood,
                "detection_details": {
                    "transcription": transcribed_text,
                    "text_analysis": text_analysis,
                    "voice_analysis": gemini_result,
                    "speaker_info": speaker_info[:10],  # Limit to first 10 for brevity
                    "analysis_method": "multimodal_audio_analysis"
                },
                "fact_check_sources": text_analysis.get("fact_check_sources", []),
                "confidence_scores": {
                    "transcription_confidence": 0.85,
                    "text_confidence": text_analysis.get("confidence_scores", {}).get("overall_confidence", 0.7),
                    "voice_confidence": gemini_result.get("confidence_level", 0.7),
                    "overall_confidence": 0.75
                }
            }
            
        except Exception as e:
            logger.error(f"Audio analysis failed: {e}")
            return {
                "authenticity_score": 0.5,
                "misinformation_likelihood": 0.5,
                "detection_details": {"error": str(e), "analysis_method": "fallback"},
                "fact_check_sources": [],
                "confidence_scores": {"overall_confidence": 0.3}
            }
    
    # Helper methods
    
    def _generate_content_id(self, content: str, metadata: Dict) -> str:
        """Generate unique content identifier"""
        content_string = f"{content}_{json.dumps(metadata or {}, sort_keys=True)}"
        return hashlib.md5(content_string.encode()).hexdigest()
    
    def _calculate_risk_level(self, misinformation_likelihood: float) -> str:
        """Calculate risk level based on misinformation likelihood"""
        if misinformation_likelihood >= 0.8:
            return "critical"
        elif misinformation_likelihood >= 0.6:
            return "high"
        elif misinformation_likelihood >= 0.4:
            return "medium"
        else:
            return "low"
    
    def _check_misinformation_patterns(self, text: str) -> List[str]:
        """Check text against known misinformation patterns"""
        matches = []
        text_lower = text.lower()
        
        for category, patterns in self.misinformation_patterns.items():
            for pattern in patterns:
                if pattern.lower() in text_lower:
                    matches.append(f"{category}: {pattern}")
        
        return matches
    
    def _evaluate_source_credibility(self, source_url: str) -> float:
        """Evaluate source credibility based on domain"""
        from urllib.parse import urlparse
        
        try:
            domain = urlparse(source_url).netloc.lower()
            
            # Check against trusted sources
            for category, domains in self.trusted_sources.items():
                if any(trusted_domain in domain for trusted_domain in domains):
                    if category == "government":
                        return 0.95
                    elif category == "fact_check":
                        return 0.9
                    elif category == "news":
                        return 0.8
            
            # Default score for unknown sources
            return 0.5
            
        except Exception:
            return 0.5
    
    async def _generate_educational_content(self, analysis_result: Dict) -> Dict[str, Any]:
        """Generate educational content based on analysis"""
        
        prompt = f"""
        Based on this content analysis: {json.dumps(analysis_result, default=str)}
        
        Generate educational content that explains:
        1. Why this content might be misleading
        2. How to identify similar misinformation patterns
        3. Best practices for fact-checking
        4. Media literacy tips relevant to this type of content
        
        Format as JSON with sections for explanation, tips, and quiz questions.
        """
        
        try:
            response = await self.gemini_model.generate_content_async(prompt)
            return json.loads(response.text)
        except Exception as e:
            logger.error(f"Educational content generation failed: {e}")
            return {
                "explanation": "Content analysis completed. Always verify information from multiple reliable sources.",
                "tips": [
                    "Check the source of information",
                    "Look for corroborating evidence",
                    "Be skeptical of sensational claims",
                    "Verify with official sources"
                ],
                "quiz": []
            }
    
    async def health_check(self) -> bool:
        """Perform health check on AI engine"""
        try:
            # Test Gemini model
            test_response = await self.gemini_model.generate_content_async("Health check test")
            return bool(test_response.text)
        except Exception:
            return False
    
    async def cleanup(self):
        """Cleanup resources"""
        logger.info("🧹 Cleaning up AI Engine resources...")
        await self.google_cloud.cleanup()
        await self.fact_checker.cleanup()
'''

# Save the AI engine file
with open('ai_engine.py', 'w') as f:
    f.write(ai_engine_code)

print("✅ AI Engine created")
print("🤖 Advanced capabilities:")
print("- Gemini 2.0 Flash integration for multimodal analysis")
print("- Text analysis with pattern matching and fact-checking")
print("- Image analysis with deepfake and manipulation detection")
print("- Video analysis with face detection and speech transcription")
print("- Audio analysis with voice cloning detection")
print("- Source credibility evaluation")
print("- Educational content generation")
print("- Performance tracking and health monitoring")