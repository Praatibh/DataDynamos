
"""
Blockchain Verification System
Handles content hashing and provenance tracking
"""

import hashlib
import json
import logging
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
import asyncio

logger = logging.getLogger(__name__)

class BlockchainVerifier:
    """
    Blockchain-based content verification system
    """

    def __init__(self):
        self.verification_chain = []
        self.content_hashes = {}

    async def create_verification(
        self, 
        content: str, 
        analysis_result: Dict[str, Any],
        user_id: str
    ) -> str:
        """Create blockchain verification for content"""
        try:
            # Create content hash
            content_hash = self._create_content_hash(content)

            # Create verification block
            verification_block = {
                'content_hash': content_hash,
                'authenticity_score': analysis_result.get('authenticity_score'),
                'misinformation_likelihood': analysis_result.get('misinformation_likelihood'),
                'risk_level': analysis_result.get('risk_level'),
                'verification_timestamp': datetime.now(timezone.utc).isoformat(),
                'verifier': 'TruthGuard-AI-v2.0',
                'user_id': user_id,
                'analysis_details': {
                    'ai_confidence': analysis_result.get('confidence_scores', {}).get('overall_confidence'),
                    'detection_method': analysis_result.get('detection_details', {}).get('analysis_method'),
                    'fact_check_sources': len(analysis_result.get('fact_check_sources', []))
                }
            }

            # Create blockchain hash
            blockchain_hash = self._create_blockchain_hash(verification_block)
            verification_block['blockchain_hash'] = blockchain_hash

            # Add to verification chain
            self.verification_chain.append(verification_block)
            self.content_hashes[content_hash] = verification_block

            logger.info(f"🔗 Blockchain verification created: {blockchain_hash[:16]}...")

            return blockchain_hash

        except Exception as e:
            logger.error(f"Blockchain verification failed: {e}")
            raise

    def _create_content_hash(self, content: str) -> str:
        """Create SHA-256 hash of content"""
        return hashlib.sha256(content.encode('utf-8')).hexdigest()

    def _create_blockchain_hash(self, verification_block: Dict[str, Any]) -> str:
        """Create blockchain hash for verification block"""
        # Create deterministic string from block data
        block_string = json.dumps(verification_block, sort_keys=True, default=str)

        # Add previous block hash for chain integrity
        if self.verification_chain:
            previous_hash = self.verification_chain[-1]['blockchain_hash']
            block_string = f"{block_string}_{previous_hash}"

        # Create SHA-256 hash
        return hashlib.sha256(block_string.encode('utf-8')).hexdigest()

    async def verify_blockchain_integrity(self, blockchain_hash: str) -> Dict[str, Any]:
        """Verify blockchain integrity for a specific hash"""
        try:
            # Find verification block
            verification_block = None
            for block in self.verification_chain:
                if block['blockchain_hash'] == blockchain_hash:
                    verification_block = block
                    break

            if not verification_block:
                return {
                    'is_valid': False,
                    'error': 'Verification block not found'
                }

            # Recreate hash to verify integrity
            temp_block = verification_block.copy()
            original_hash = temp_block.pop('blockchain_hash')
            recreated_hash = self._create_blockchain_hash(temp_block)

            is_valid = original_hash == recreated_hash

            return {
                'is_valid': is_valid,
                'original_hash': original_hash,
                'recreated_hash': recreated_hash,
                'verification_timestamp': verification_block['verification_timestamp'],
                'authenticity_score': verification_block['authenticity_score'],
                'content_hash': verification_block['content_hash']
            }

        except Exception as e:
            logger.error(f"Blockchain verification failed: {e}")
            return {
                'is_valid': False,
                'error': str(e)
            }

    async def get_content_provenance(self, content: str) -> List[Dict[str, Any]]:
        """Get provenance chain for content"""
        try:
            content_hash = self._create_content_hash(content)

            # Find all verifications for this content
            provenance_chain = []
            for block in self.verification_chain:
                if block['content_hash'] == content_hash:
                    provenance_chain.append({
                        'verification_timestamp': block['verification_timestamp'],
                        'blockchain_hash': block['blockchain_hash'],
                        'authenticity_score': block['authenticity_score'],
                        'risk_level': block['risk_level'],
                        'verifier': block['verifier'],
                        'user_id': block['user_id']
                    })

            # Sort by timestamp
            provenance_chain.sort(key=lambda x: x['verification_timestamp'])

            return provenance_chain

        except Exception as e:
            logger.error(f"Provenance retrieval failed: {e}")
            return []

    async def get_verification_stats(self) -> Dict[str, Any]:
        """Get blockchain verification statistics"""
        try:
            total_verifications = len(self.verification_chain)

            if total_verifications == 0:
                return {
                    'total_verifications': 0,
                    'unique_content_pieces': 0,
                    'average_authenticity_score': 0,
                    'risk_distribution': {}
                }

            # Calculate statistics
            authenticity_scores = [block['authenticity_score'] for block in self.verification_chain if block['authenticity_score']]
            avg_authenticity = sum(authenticity_scores) / len(authenticity_scores) if authenticity_scores else 0

            # Risk distribution
            risk_distribution = {}
            for block in self.verification_chain:
                risk_level = block.get('risk_level', 'unknown')
                risk_distribution[risk_level] = risk_distribution.get(risk_level, 0) + 1

            return {
                'total_verifications': total_verifications,
                'unique_content_pieces': len(self.content_hashes),
                'average_authenticity_score': round(avg_authenticity, 3),
                'risk_distribution': risk_distribution,
                'chain_integrity': await self._verify_chain_integrity()
            }

        except Exception as e:
            logger.error(f"Stats calculation failed: {e}")
            return {}

    async def _verify_chain_integrity(self) -> bool:
        """Verify integrity of entire blockchain"""
        try:
            for i, block in enumerate(self.verification_chain):
                if i == 0:
                    continue  # Skip first block

                # Verify each block hash
                temp_block = block.copy()
                original_hash = temp_block.pop('blockchain_hash')

                # For chain verification, we need to include previous block hash
                previous_hash = self.verification_chain[i-1]['blockchain_hash']
                block_string = json.dumps(temp_block, sort_keys=True, default=str)
                block_string = f"{block_string}_{previous_hash}"

                recreated_hash = hashlib.sha256(block_string.encode('utf-8')).hexdigest()

                if original_hash != recreated_hash:
                    logger.error(f"Chain integrity broken at block {i}")
                    return False

            return True

        except Exception as e:
            logger.error(f"Chain integrity verification failed: {e}")
            return False
