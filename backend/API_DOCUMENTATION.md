# TruthGuard AI Backend API Documentation

## Overview

TruthGuard AI provides a comprehensive REST API for advanced misinformation detection using multimodal AI analysis, blockchain verification, and community-driven fact-checking.

## Base URL

```
Production: https://api.truthguard.ai
Development: http://localhost:8000
```

## Authentication

All API endpoints except health checks require Bearer token authentication:

```bash
Authorization: Bearer <your-jwt-token>
```

### Get Access Token

```bash
POST /api/v1/auth/login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "your-password"
}
```

## Core Endpoints

### 1. Content Verification

#### Single Content Verification

```bash
POST /api/v1/verify/content
Authorization: Bearer <token>
Content-Type: application/json

{
  "content": "Text content or URL to verify",
  "content_type": "text",
  "metadata": {
    "source_platform": "whatsapp",
    "source_location": "Mumbai"
  }
}
```

**Response:**
```json
{
  "verification_id": "uuid",
  "content_id": "md5-hash",
  "authenticity_score": 0.85,
  "misinformation_likelihood": 0.15,
  "risk_level": "low",
  "detection_details": {
    "analysis_method": "multimodal_text_analysis",
    "confidence_level": 0.9,
    "key_claims": ["claim1", "claim2"],
    "red_flags": [],
    "fact_check_results": []
  },
  "educational_content": {
    "explanation": "Content analysis explanation",
    "tips": ["tip1", "tip2"],
    "quiz": []
  },
  "blockchain_hash": "sha256-hash",
  "processing_time": 1.2,
  "timestamp": "2025-09-21T01:00:00Z",
  "user_id": "uuid"
}
```

#### Batch Verification

```bash
POST /api/v1/verify/batch
Authorization: Bearer <token>
Content-Type: application/json

{
  "content_items": [
    {
      "content": "First content to verify",
      "content_type": "text"
    },
    {
      "content": "Second content to verify", 
      "content_type": "text"
    }
  ]
}
```

#### File Upload Verification

```bash
POST /api/v1/verify/file
Authorization: Bearer <token>
Content-Type: multipart/form-data

file: <binary-file-data>
content_type: image
```

### 2. Real-time Threat Monitoring

#### Get Active Threats

```bash
GET /api/v1/threats/realtime
Authorization: Bearer <token>
```

**Response:**
```json
{
  "timestamp": "2025-09-21T01:00:00Z",
  "active_threats": 15,
  "critical_alerts": 3,
  "latest_detections": [
    {
      "id": "threat-1",
      "type": "deepfake_video",
      "risk_level": "critical",
      "authenticity_score": 0.12,
      "platform": "Twitter",
      "location": "Delhi",
      "prevented_shares": 45000
    }
  ],
  "trending_topics": [
    {
      "category": "Election Manipulation",
      "incidents": 3456,
      "growth_rate": "+45%",
      "severity": "critical"
    }
  ],
  "platform_stats": {
    "total_verifications_today": 125000,
    "misinformation_detected_today": 15420,
    "accuracy_rate": 96.8,
    "response_time_avg": 0.8
  }
}
```

### 3. WhatsApp Integration

#### Process Webhook

```bash
POST /api/v1/whatsapp/webhook
Content-Type: application/json

{
  "object": "whatsapp_business_account",
  "entry": [
    {
      "id": "entry-id",
      "changes": [
        {
          "value": {
            "messaging_product": "whatsapp",
            "metadata": {},
            "contacts": [],
            "messages": []
          },
          "field": "messages"
        }
      ]
    }
  ]
}
```

#### Get Tipline Statistics

```bash
GET /api/v1/whatsapp/stats?days=30
Authorization: Bearer <token>
```

### 4. Community Features

#### Submit Misinformation Report

```bash
POST /api/v1/community/report
Authorization: Bearer <token>
Content-Type: application/json

{
  "reported_content": "Content to report",
  "content_type": "text",
  "report_category": "health_misinformation",
  "description": "Why this is misinformation",
  "urgency_level": "high",
  "source_platform": "facebook",
  "estimated_reach": 10000
}
```

#### Submit Verification Feedback

```bash
POST /api/v1/community/feedback
Authorization: Bearer <token>
Content-Type: application/json

{
  "verification_id": "uuid",
  "feedback_type": "helpful",
  "rating": 5,
  "comment": "Accurate detection",
  "expertise_level": "intermediate",
  "confidence_in_feedback": 0.9
}
```

### 5. Analytics

#### Get Platform Analytics

```bash
GET /api/v1/analytics/platform?days=30
Authorization: Bearer <token>
```

#### Get User Analytics

```bash
GET /api/v1/analytics/user
Authorization: Bearer <token>
```

### 6. Blockchain Verification

#### Verify Blockchain Hash

```bash
GET /api/v1/blockchain/verify/{blockchain_hash}
Authorization: Bearer <token>
```

#### Get Content Provenance

```bash
POST /api/v1/blockchain/provenance
Authorization: Bearer <token>
Content-Type: application/json

{
  "content": "Content to trace"
}
```

## Error Responses

All endpoints return consistent error responses:

```json
{
  "success": false,
  "message": "Error description",
  "errors": ["Detailed error messages"],
  "timestamp": "2025-09-21T01:00:00Z"
}
```

### HTTP Status Codes

- `200` - Success
- `201` - Created
- `400` - Bad Request
- `401` - Unauthorized
- `403` - Forbidden
- `404` - Not Found
- `422` - Validation Error
- `429` - Rate Limited
- `500` - Internal Server Error
- `503` - Service Unavailable

## Rate Limits

- **Free Tier**: 60 requests/minute, 1000 requests/hour
- **Premium Tier**: 600 requests/minute, 10000 requests/hour
- **Enterprise**: Custom limits

Rate limit headers:
```
X-RateLimit-Limit: 60
X-RateLimit-Remaining: 45
X-RateLimit-Reset: 1640995200
```

## SDKs and Libraries

### Python SDK

```bash
pip install truthguard-python
```

```python
from truthguard import TruthGuardClient

client = TruthGuardClient(api_key="your-api-key")
result = client.verify_content("Content to check", "text")
print(f"Authenticity: {result.authenticity_score}")
```

### JavaScript SDK

```bash
npm install @truthguard/js-sdk
```

```javascript
import { TruthGuardClient } from '@truthguard/js-sdk';

const client = new TruthGuardClient({ apiKey: 'your-api-key' });
const result = await client.verifyContent('Content to check', 'text');
console.log(`Authenticity: ${result.authenticity_score}`);
```

## Webhooks

Register webhooks to receive real-time notifications:

```bash
POST /api/v1/webhooks/register
Authorization: Bearer <token>
Content-Type: application/json

{
  "url": "https://your-app.com/webhook",
  "events": ["threat_detected", "verification_completed"],
  "secret": "webhook-secret"
}
```

## Support

- Documentation: https://docs.truthguard.ai
- API Status: https://status.truthguard.ai
- Support Email: support@truthguard.ai
- WhatsApp Tipline: +91-XXXX-TRUTHGUARD
