"""
TruthGuard AI Engine
Core AI functionality for misinformation detection
"""

import os
import logging
import asyncio
import json
import hashlib
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
import aiohttp
import numpy as np
from PIL import Image
import io
import base64

# Google Cloud imports
from google.cloud import aiplatform
from google.cloud import vision
from google.cloud import speech
from google.cloud import storage
from google.oauth2 import service_account
import vertexai
from vertexai.language_models import TextGenerationModel, ChatModel
from vertexai.vision_models import ImageGenerationModel

# ML/AI imports
import torch
import transformers
from transformers import pipeline, AutoTokenizer, AutoModelForSequenceClassification
import cv2

# Local imports (all in same directory)
from config import get_settings

logger = logging.getLogger(__name__)


class TruthGuardAIEngine:
    """Main AI engine for misinformation detection"""
    
    def __init__(self):
        self.settings = get_settings()
        self.initialized = False
        self.models = {}
        self.stats = {
            "total_analyses": 0,
            "misinformation_detected": 0,
            "processing_times": []
        }
        
        # Google Cloud clients
        self.vision_client = None
        self.storage_client = None
        self.vertex_model = None
        
        # ML models
        self.text_classifier = None
        self.image_detector = None
        
        # Cache for results
        self.cache = {}
        self.cache_ttl = timedelta(hours=1)
    
    async def initialize(self):
        """Initialize all AI components"""
        try:
            logger.info("Initializing TruthGuard AI Engine...")
            
            # Initialize Google Cloud credentials
            await self._initialize_google_cloud()
            
            # Initialize ML models
            await self._initialize_ml_models()
            
            # Initialize text processing
            await self._initialize_text_processing()
            
            # Initialize image processing
            await self._initialize_image_processing()
            
            self.initialized = True
            logger.info("TruthGuard AI Engine initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize AI engine: {e}")
            raise
    
    async def _initialize_google_cloud(self):
        """Initialize Google Cloud services"""
        try:
            # Set up credentials
            if os.path.exists("credentials.json"):
                os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "credentials.json"
            
            # Initialize Vertex AI
            project_id = self.settings.get("GOOGLE_CLOUD_PROJECT", "truthguard-ai-1758454497")
            vertexai.init(project=project_id, location="us-central1")
            
            # Initialize clients
            self.vision_client = vision.ImageAnnotatorClient()
            self.storage_client = storage.Client()
            
            # Initialize Vertex AI models
            self.vertex_model = TextGenerationModel.from_pretrained("text-bison@001")
            
            logger.info("Google Cloud services initialized")
            
        except Exception as e:
            logger.warning(f"Google Cloud initialization failed: {e}")
            # Continue without Google Cloud services
    
    async def _initialize_ml_models(self):
        """Initialize machine learning models"""
        try:
            # Initialize text classification model
            model_name = "microsoft/DialoGPT-medium"
            self.text_classifier = pipeline(
                "text-classification",
                model="unitary/toxic-bert",
                tokenizer="unitary/toxic-bert"
            )
            
            logger.info("ML models initialized")
            
        except Exception as e:
            logger.warning(f"ML model initialization failed: {e}")
    
    async def _initialize_text_processing(self):
        """Initialize text processing components"""
        try:
            # Initialize language detection
            # Initialize fact-checking databases
            # Initialize NLP pipelines
            logger.info("Text processing initialized")
            
        except Exception as e:
            logger.warning(f"Text processing initialization failed: {e}")
    
    async def _initialize_image_processing(self):
        """Initialize image processing components"""
        try:
            # Initialize image manipulation detection
            # Initialize deepfake detection
            logger.info("Image processing initialized")
            
        except Exception as e:
            logger.warning(f"Image processing initialization failed: {e}")
    
    def is_ready(self) -> bool:
        """Check if the AI engine is ready"""
        return self.initialized
    
    async def analyze_text(
        self,
        text: str,
        language: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Analyze text for misinformation"""
        start_time = datetime.utcnow()
        request_id = self._generate_request_id(text)
        
        try:
            logger.info(f"Starting text analysis for request: {request_id}")
            
            # Check cache first
            cache_key = hashlib.md5(text.encode()).hexdigest()
            if cache_key in self.cache:
                cached_result = self.cache[cache_key]
                if datetime.utcnow() - cached_result["timestamp"] < self.cache_ttl:
                    logger.info(f"Returning cached result for: {request_id}")
                    return cached_result["result"]
            
            # Initialize result structure
            result = {
                "request_id": request_id,
                "is_misinformation": False,
                "confidence_score": 0.0,
                "risk_level": "low",
                "detected_patterns": [],
                "fact_checks": [],
                "sources": [],
                "explanation": "",
                "language_detected": language or "en",
                "processing_time": 0.0
            }
            
            # Detect language if not provided
            if not language:
                result["language_detected"] = await self._detect_language(text)
            
            # Perform misinformation analysis
            misinformation_result = await self._analyze_misinformation(text, context)
            result.update(misinformation_result)
            
            # Perform fact checking
            fact_check_result = await self._perform_fact_checking(text)
            result["fact_checks"] = fact_check_result
            
            # Calculate final scores
            result = await self._calculate_final_scores(result)
            
            # Calculate processing time
            processing_time = (datetime.utcnow() - start_time).total_seconds()
            result["processing_time"] = processing_time
            
            # Update statistics
            self._update_stats("text_analysis", result, processing_time)
            
            # Cache result
            self.cache[cache_key] = {
                "result": result,
                "timestamp": datetime.utcnow()
            }
            
            logger.info(f"Text analysis completed for: {request_id}")
            return result
            
        except Exception as e:
            logger.error(f"Text analysis failed for {request_id}: {e}")
            result["error"] = str(e)
            result["processing_time"] = (datetime.utcnow() - start_time).total_seconds()
            return result
    
    async def analyze_url(
        self,
        url: str,
        deep_scan: bool = False
    ) -> Dict[str, Any]:
        """Analyze URL content for misinformation"""
        start_time = datetime.utcnow()
        request_id = self._generate_request_id(url)
        
        try:
            logger.info(f"Starting URL analysis for: {url}")
            
            result = {
                "request_id": request_id,
                "url": url,
                "is_misinformation": False,
                "confidence_score": 0.0,
                "risk_level": "low",
                "content_analysis": {},
                "source_credibility": {},
                "fact_checks": [],
                "processing_time": 0.0
            }
            
            # Fetch and analyze content
            content = await self._fetch_url_content(url)
            if content:
                # Analyze text content
                text_analysis = await self.analyze_text(content.get("text", ""))
                result["content_analysis"] = text_analysis
                
                # Analyze source credibility
                source_analysis = await self._analyze_source_credibility(url)
                result["source_credibility"] = source_analysis
                
                # Deep scan if requested
                if deep_scan:
                    deep_analysis = await self._perform_deep_scan(url, content)
                    result.update(deep_analysis)
            
            # Calculate final scores
            result = await self._calculate_url_scores(result)
            
            # Calculate processing time
            processing_time = (datetime.utcnow() - start_time).total_seconds()
            result["processing_time"] = processing_time
            
            # Update statistics
            self._update_stats("url_analysis", result, processing_time)
            
            return result
            
        except Exception as e:
            logger.error(f"URL analysis failed for {url}: {e}")
            result = {
                "request_id": request_id,
                "url": url,
                "error": str(e),
                "processing_time": (datetime.utcnow() - start_time).total_seconds()
            }
            return result
    
    async def analyze_image(
        self,
        image_data: bytes,
        content_type: str
    ) -> Dict[str, Any]:
        """Analyze image for manipulation"""
        start_time = datetime.utcnow()
        request_id = self._generate_request_id(str(len(image_data)))
        
        try:
            logger.info(f"Starting image analysis for request: {request_id}")
            
            result = {
                "request_id": request_id,
                "is_manipulated": False,
                "confidence_score": 0.0,
                "manipulation_types": [],
                "authenticity_score": 0.0,
                "processing_time": 0.0
            }
            
            # Validate and process image
            image = await self._process_image(image_data, content_type)
            
            # Detect manipulation
            manipulation_result = await self._detect_image_manipulation(image)
            result.update(manipulation_result)
            
            # Check for deepfakes (if face detected)
            deepfake_result = await self._detect_deepfake(image)
            if deepfake_result:
                result["manipulation_types"].extend(deepfake_result.get("types", []))
                result["confidence_score"] = max(
                    result["confidence_score"], 
                    deepfake_result.get("confidence", 0.0)
                )
            
            # Calculate processing time
            processing_time = (datetime.utcnow() - start_time).total_seconds()
            result["processing_time"] = processing_time
            
            # Update statistics
            self._update_stats("image_analysis", result, processing_time)
            
            return result
            
        except Exception as e:
            logger.error(f"Image analysis failed for {request_id}: {e}")
            return {
                "request_id": request_id,
                "error": str(e),
                "processing_time": (datetime.utcnow() - start_time).total_seconds()
            }
    
    async def get_stats(self) -> Dict[str, Any]:
        """Get engine statistics"""
        return {
            "total_analyses": self.stats["total_analyses"],
            "misinformation_detected": self.stats["misinformation_detected"],
            "accuracy_rate": self._calculate_accuracy_rate(),
            "processing_time_avg": self._calculate_avg_processing_time(),
            "active_models": len(self.models),
            "cache_size": len(self.cache)
        }
    
    async def cleanup(self):
        """Cleanup resources"""
        try:
            logger.info("Cleaning up AI engine resources...")
            
            # Clear cache
            self.cache.clear()
            
            # Cleanup models
            self.models.clear()
            
            # Close clients
            if hasattr(self.vision_client, 'close'):
                await self.vision_client.close()
            
            self.initialized = False
            logger.info("AI engine cleanup completed")
            
        except Exception as e:
            logger.error(f"Cleanup failed: {e}")
    
    # Helper methods
    
    def _generate_request_id(self, content: str) -> str:
        """Generate unique request ID"""
        timestamp = datetime.utcnow().isoformat()
        content_hash = hashlib.md5(content.encode()).hexdigest()[:8]
        return f"{timestamp}_{content_hash}"
    
    async def _detect_language(self, text: str) -> str:
        """Detect text language"""
        try:
            # Simple language detection - replace with proper detection
            return "en"  # Default to English
        except Exception:
            return "en"
    
    async def _analyze_misinformation(
        self,
        text: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Analyze text for misinformation patterns"""
        try:
            result = {
                "is_misinformation": False,
                "confidence_score": 0.0,
                "detected_patterns": [],
                "explanation": "Text appears to be factual."
            }
            
            # Check for common misinformation patterns
            patterns = await self._check_misinformation_patterns(text)
            result["detected_patterns"] = patterns
            
            # Use ML model if available
            if self.text_classifier:
                ml_result = await self._classify_with_ml(text)
                result.update(ml_result)
            
            # Use Vertex AI if available
            if self.vertex_model:
                vertex_result = await self._analyze_with_vertex(text)
                result.update(vertex_result)
            
            return result
            
        except Exception as e:
            logger.error(f"Misinformation analysis failed: {e}")
            return {
                "is_misinformation": False,
                "confidence_score": 0.0,
                "detected_patterns": [],
                "explanation": f"Analysis failed: {str(e)}"
            }
    
    async def _check_misinformation_patterns(self, text: str) -> List[str]:
        """Check for common misinformation patterns"""
        patterns = []
        text_lower = text.lower()
        
        # Check for sensational language
        sensational_words = ["shocking", "unbelievable", "secret", "hidden truth", "they don't want you to know"]
        if any(word in text_lower for word in sensational_words):
            patterns.append("sensational_language")
        
        # Check for conspiracy indicators
        conspiracy_words = ["conspiracy", "cover-up", "mainstream media", "deep state"]
        if any(word in text_lower for word in conspiracy_words):
            patterns.append("conspiracy_indicators")
        
        # Check for lack of sources
        if "source" not in text_lower and "study" not in text_lower and len(text) > 100:
            patterns.append("lack_of_sources")
        
        return patterns
    
    async def _classify_with_ml(self, text: str) -> Dict[str, Any]:
        """Classify text using ML model"""
        try:
            if not self.text_classifier:
                return {}
            
            # This is a placeholder - implement actual classification
            result = {"confidence_score": 0.1}  # Low confidence as placeholder
            return result
            
        except Exception as e:
            logger.error(f"ML classification failed: {e}")
            return {}
    
    async def _analyze_with_vertex(self, text: str) -> Dict[str, Any]:
        """Analyze text using Vertex AI"""
        try:
            if not self.vertex_model:
                return {}
            
            prompt = f"""
            Analyze the following text for potential misinformation:
            
            Text: {text}
            
            Provide analysis in JSON format with:
            - is_misinformation: boolean
            - confidence_score: float (0-1)
            - explanation: string
            """
            
            response = await self.vertex_model.predict(prompt)
            # Parse and return response
            return {"explanation": "Analyzed with Vertex AI"}
            
        except Exception as e:
            logger.error(f"Vertex AI analysis failed: {e}")
            return {}
    
    async def _perform_fact_checking(self, text: str) -> List[Dict[str, Any]]:
        """Perform fact checking"""
        try:
            # Placeholder for fact checking logic
            return []
        except Exception as e:
            logger.error(f"Fact checking failed: {e}")
            return []
    
    async def _calculate_final_scores(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate final confidence and risk scores"""
        try:
            # Simple scoring logic
            pattern_count = len(result.get("detected_patterns", []))
            base_score = result.get("confidence_score", 0.0)
            
            # Adjust score based on patterns
            final_score = min(1.0, base_score + (pattern_count * 0.2))
            result["confidence_score"] = final_score
            
            # Determine risk level
            if final_score < 0.3:
                result["risk_level"] = "low"
            elif final_score < 0.7:
                result["risk_level"] = "medium"
            else:
                result["risk_level"] = "high"
                result["is_misinformation"] = True
            
            return result
            
        except Exception as e:
            logger.error(f"Score calculation failed: {e}")
            return result
    
    async def _fetch_url_content(self, url: str) -> Optional[Dict[str, Any]]:
        """Fetch and parse URL content"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=10) as response:
                    if response.status == 200:
                        content = await response.text()
                        return {
                            "text": content[:5000],  # Limit content size
                            "status_code": response.status,
                            "headers": dict(response.headers)
                        }
            return None
            
        except Exception as e:
            logger.error(f"Failed to fetch URL {url}: {e}")
            return None
    
    async def _analyze_source_credibility(self, url: str) -> Dict[str, Any]:
        """Analyze source credibility"""
        try:
            # Extract domain
            from urllib.parse import urlparse
            domain = urlparse(url).netloc
            
            # Simple credibility check
            credible_domains = [
                "bbc.com", "reuters.com", "ap.org", "npr.org",
                "cnn.com", "nytimes.com", "washingtonpost.com"
            ]
            
            is_credible = any(credible in domain for credible in credible_domains)
            
            return {
                "domain": domain,
                "is_credible_source": is_credible,
                "credibility_score": 0.8 if is_credible else 0.3
            }
            
        except Exception as e:
            logger.error(f"Source credibility analysis failed: {e}")
            return {"credibility_score": 0.5}
    
    async def _perform_deep_scan(self, url: str, content: Dict[str, Any]) -> Dict[str, Any]:
        """Perform deep scan of URL content"""
        try:
            return {"deep_scan_completed": True}
        except Exception as e:
            logger.error(f"Deep scan failed: {e}")
            return {}
    
    async def _calculate_url_scores(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate final URL analysis scores"""
        try:
            content_analysis = result.get("content_analysis", {})
            source_credibility = result.get("source_credibility", {})
            
            # Combine scores
            content_score = content_analysis.get("confidence_score", 0.0)
            source_score = source_credibility.get("credibility_score", 0.5)
            
            final_score = (content_score * 0.7) + ((1 - source_score) * 0.3)
            
            result["confidence_score"] = final_score
            result["is_misinformation"] = content_analysis.get("is_misinformation", False)
            
            if final_score < 0.3:
                result["risk_level"] = "low"
            elif final_score < 0.7:
                result["risk_level"] = "medium"
            else:
                result["risk_level"] = "high"
            
            return result
            
        except Exception as e:
            logger.error(f"URL score calculation failed: {e}")
            return result
    
    async def _process_image(self, image_data: bytes, content_type: str) -> Any:
        """Process image data"""
        try:
            image = Image.open(io.BytesIO(image_data))
            return image
        except Exception as e:
            logger.error(f"Image processing failed: {e}")
            raise
    
    async def _detect_image_manipulation(self, image: Any) -> Dict[str, Any]:
        """Detect image manipulation"""
        try:
            # Placeholder for image manipulation detection
            return {
                "is_manipulated": False,
                "confidence_score": 0.1,
                "manipulation_types": [],
                "authenticity_score": 0.9
            }
        except Exception as e:
            logger.error(f"Image manipulation detection failed: {e}")
            return {
                "is_manipulated": False,
                "confidence_score": 0.0,
                "manipulation_types": [],
                "authenticity_score": 0.5
            }
    
    async def _detect_deepfake(self, image: Any) -> Optional[Dict[str, Any]]:
        """Detect deepfakes in image"""
        try:
            # Placeholder for deepfake detection
            return None
        except Exception as e:
            logger.error(f"Deepfake detection failed: {e}")
            return None
    
    def _update_stats(self, analysis_type: str, result: Dict[str, Any], processing_time: float):
        """Update engine statistics"""
        try:
            self.stats["total_analyses"] += 1
            self.stats["processing_times"].append(processing_time)
            
            if result.get("is_misinformation") or result.get("is_manipulated"):
                self.stats["misinformation_detected"] += 1
            
            # Keep only recent processing times
            if len(self.stats["processing_times"]) > 1000:
                self.stats["processing_times"] = self.stats["processing_times"][-500:]
                
        except Exception as e:
            logger.error(f"Stats update failed: {e}")
    
    def _calculate_accuracy_rate(self) -> float:
        """Calculate accuracy rate"""
        try:
            total = self.stats["total_analyses"]
            if total == 0:
                return 0.0
            
            # Placeholder accuracy calculation
            return 0.85  # 85% placeholder accuracy
            
        except Exception:
            return 0.0
    
    def _calculate_avg_processing_time(self) -> float:
        """Calculate average processing time"""
        try:
            times = self.stats["processing_times"]
            if not times:
                return 0.0
            
            return sum(times) / len(times)
            
        except Exception:
            return 0.0