"""
Redis service for job storage.
Handles storing and retrieving job data from Redis.
"""
import json
import logging
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
import redis.asyncio as aioredis

from config import settings

logger = logging.getLogger(__name__)


class RedisService:
    """Service for interacting with Redis for job storage."""
    
    def __init__(self):
        """Initialize Redis connection."""
        self.redis_client: Optional[aioredis.Redis] = None
        self._connection_pool: Optional[aioredis.ConnectionPool] = None
    
    async def connect(self):
        """Connect to Redis."""
        try:
            self._connection_pool = aioredis.ConnectionPool.from_url(
                settings.redis_url,
                max_connections=settings.redis_max_connections,
                decode_responses=False,  # We'll handle JSON encoding/decoding ourselves
            )
            self.redis_client = aioredis.Redis(connection_pool=self._connection_pool)
            
            # Test connection
            await self.redis_client.ping()
            logger.info("Connected to Redis at %s", settings.redis_url)
        except Exception as e:
            logger.error("Failed to connect to Redis: %s", str(e))
            raise
    
    async def disconnect(self):
        """Disconnect from Redis."""
        if self.redis_client:
            await self.redis_client.close()
            logger.info("Disconnected from Redis")
    
    def _get_job_key(self, job_id: str) -> str:
        """Get Redis key for a job."""
        return f"job:{job_id}"
    
    def _serialize_value(self, value: Any) -> bytes:
        """Serialize value to JSON bytes."""
        # Handle datetime serialization
        if isinstance(value, datetime):
            return value.isoformat().encode('utf-8')
        
        # Handle complex objects (like Pydantic models)
        if hasattr(value, 'model_dump'):
            return json.dumps(value.model_dump(), default=str).encode('utf-8')
        elif hasattr(value, 'dict'):
            return json.dumps(value.dict(), default=str).encode('utf-8')
        
        # Handle dicts and lists
        return json.dumps(value, default=str).encode('utf-8')
    
    def _deserialize_value(self, value: bytes) -> Any:
        """Deserialize value from JSON bytes."""
        if value is None:
            return None
        return json.loads(value.decode('utf-8'))
    
    async def set_job(self, job_id: str, job_data: Dict[str, Any], ttl_seconds: Optional[int] = None):
        """
        Store a job in Redis.
        
        Args:
            job_id: Job identifier
            job_data: Job data dictionary
            ttl_seconds: Optional TTL in seconds (defaults to redis_job_ttl_seconds)
        """
        if not self.redis_client:
            await self.connect()
        
        try:
            key = self._get_job_key(job_id)
            
            # Serialize the entire job dict
            serialized_data = {}
            for k, v in job_data.items():
                if isinstance(v, (dict, list, str, int, float, bool, type(None))):
                    # Simple types - serialize as JSON
                    serialized_data[k] = json.dumps(v, default=str) if isinstance(v, (dict, list)) else v
                else:
                    # Complex objects (Pydantic models, datetime, etc.)
                    serialized_data[k] = json.dumps(v, default=str)
            
            # Store as hash for easier partial updates
            await self.redis_client.hset(key, mapping=serialized_data)
            
            # Set TTL
            ttl = ttl_seconds or settings.redis_job_ttl_seconds
            if ttl > 0:
                await self.redis_client.expire(key, ttl)
            
            logger.debug("Stored job %s in Redis", job_id)
            
        except Exception as e:
            logger.error("Failed to store job %s in Redis: %s", job_id, str(e))
            raise
    
    async def get_job(self, job_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve a job from Redis.
        
        Args:
            job_id: Job identifier
            
        Returns:
            Job data dictionary or None if not found
        """
        if not self.redis_client:
            await self.connect()
        
        try:
            key = self._get_job_key(job_id)
            job_data = await self.redis_client.hgetall(key)
            
            if not job_data:
                return None
            
            # Deserialize the job data
            deserialized = {}
            for k, v in job_data.items():
                k_str = k.decode('utf-8') if isinstance(k, bytes) else k
                try:
                    # Try to parse as JSON first
                    deserialized[k_str] = json.loads(v.decode('utf-8') if isinstance(v, bytes) else v)
                except (json.JSONDecodeError, AttributeError):
                    # If not JSON, use as-is
                    deserialized[k_str] = v.decode('utf-8') if isinstance(v, bytes) else v
            
            logger.debug("Retrieved job %s from Redis", job_id)
            return deserialized
            
        except Exception as e:
            logger.error("Failed to retrieve job %s from Redis: %s", job_id, str(e))
            raise
    
    async def update_job(self, job_id: str, updates: Dict[str, Any]):
        """
        Update specific fields of a job.
        
        Args:
            job_id: Job identifier
            updates: Dictionary of fields to update
        """
        if not self.redis_client:
            await self.connect()
        
        try:
            key = self._get_job_key(job_id)
            
            # Check if job exists
            exists = await self.redis_client.exists(key)
            if not exists:
                raise ValueError(f"Job {job_id} not found")
            
            # Serialize updates
            serialized_updates = {}
            for k, v in updates.items():
                if isinstance(v, (dict, list)):
                    serialized_updates[k] = json.dumps(v, default=str)
                elif isinstance(v, (str, int, float, bool, type(None))):
                    serialized_updates[k] = v
                else:
                    serialized_updates[k] = json.dumps(v, default=str)
            
            # Update hash
            await self.redis_client.hset(key, mapping=serialized_updates)
            
            logger.debug("Updated job %s in Redis", job_id)
            
        except Exception as e:
            logger.error("Failed to update job %s in Redis: %s", job_id, str(e))
            raise
    
    async def delete_job(self, job_id: str):
        """
        Delete a job from Redis.
        
        Args:
            job_id: Job identifier
        """
        if not self.redis_client:
            await self.connect()
        
        try:
            key = self._get_job_key(job_id)
            await self.redis_client.delete(key)
            logger.debug("Deleted job %s from Redis", job_id)
            
        except Exception as e:
            logger.error("Failed to delete job %s from Redis: %s", job_id, str(e))
            raise
    
    async def job_exists(self, job_id: str) -> bool:
        """
        Check if a job exists in Redis.
        
        Args:
            job_id: Job identifier
            
        Returns:
            True if job exists, False otherwise
        """
        if not self.redis_client:
            await self.connect()
        
        try:
            key = self._get_job_key(job_id)
            exists = await self.redis_client.exists(key)
            return bool(exists)
        except Exception as e:
            logger.error("Failed to check job existence %s in Redis: %s", job_id, str(e))
            return False
    
    # ========================================================================
    # Helper methods for job management
    # ========================================================================
    
    async def set_job_metadata(self, job_id: str, metadata: Dict[str, Any]):
        """Store job metadata (alias for set_job for compatibility)."""
        await self.set_job(job_id, metadata)
    
    async def get_job_metadata(self, job_id: str) -> Optional[Dict[str, Any]]:
        """Get job metadata (alias for get_job for compatibility)."""
        return await self.get_job(job_id)
    
    async def update_job_status(self, job_id: str, status: str):
        """Update job status."""
        await self.update_job(job_id, {"status": status})
    
    async def update_job_progress(self, job_id: str, progress: float):
        """Update job progress percentage."""
        await self.update_job(job_id, {"progress": progress})
    
    async def set_job_results(self, job_id: str, result_type: str, results: Any):
        """
        Store job results (transcription or summary).
        
        Args:
            job_id: Job identifier
            result_type: Type of result ('transcription' or 'summary')
            results: Results data
        """
        key = f"job:{job_id}:{result_type}"
        serialized = self._serialize_value(results)
        
        if not self.redis_client:
            await self.connect()
        
        await self.redis_client.set(key, serialized)
        
        # Set TTL
        ttl = settings.redis_job_ttl_seconds
        if ttl > 0:
            await self.redis_client.expire(key, ttl)
    
    async def get_job_results(self, job_id: str, result_type: str) -> Optional[Any]:
        """
        Retrieve job results.
        
        Args:
            job_id: Job identifier
            result_type: Type of result ('transcription' or 'summary')
            
        Returns:
            Results data or None
        """
        key = f"job:{job_id}:{result_type}"
        
        if not self.redis_client:
            await self.connect()
        
        data = await self.redis_client.get(key)
        if data:
            return self._deserialize_value(data)
        return None
    
    # ========================================================================
    # Batch Processing Methods
    # ========================================================================
    
    def _get_batch_key(self, batch_id: str) -> str:
        """Get Redis key for a batch."""
        return f"batch:{batch_id}"
    
    async def create_batch(self, batch_id: str, batch_data: Dict[str, Any], job_ids: list):
        """
        Create a batch in Redis.
        
        Args:
            batch_id: Batch identifier
            batch_data: Batch metadata
            job_ids: List of job IDs in this batch
        """
        if not self.redis_client:
            await self.connect()
        
        try:
            key = self._get_batch_key(batch_id)
            
            # Store batch metadata as hash
            serialized_data = {}
            for k, v in batch_data.items():
                if isinstance(v, (dict, list)):
                    serialized_data[k] = json.dumps(v, default=str)
                else:
                    serialized_data[k] = v
            
            await self.redis_client.hset(key, mapping=serialized_data)
            
            # Store job IDs list
            jobs_key = f"{key}:jobs"
            await self.redis_client.delete(jobs_key)  # Clear existing
            if job_ids:
                await self.redis_client.rpush(jobs_key, *job_ids)
            
            # Set TTL
            ttl = settings.redis_job_ttl_seconds
            if ttl > 0:
                await self.redis_client.expire(key, ttl)
                await self.redis_client.expire(jobs_key, ttl)
            
            logger.debug("Created batch %s with %d jobs", batch_id, len(job_ids))
            
        except Exception as e:
            logger.error("Failed to create batch %s: %s", batch_id, str(e))
            raise
    
    async def get_batch(self, batch_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve batch metadata.
        
        Args:
            batch_id: Batch identifier
            
        Returns:
            Batch data dictionary or None
        """
        if not self.redis_client:
            await self.connect()
        
        try:
            key = self._get_batch_key(batch_id)
            batch_data = await self.redis_client.hgetall(key)
            
            if not batch_data:
                return None
            
            # Deserialize
            deserialized = {}
            for k, v in batch_data.items():
                k_str = k.decode('utf-8') if isinstance(k, bytes) else k
                try:
                    deserialized[k_str] = json.loads(v.decode('utf-8') if isinstance(v, bytes) else v)
                except (json.JSONDecodeError, AttributeError):
                    deserialized[k_str] = v.decode('utf-8') if isinstance(v, bytes) else v
            
            # Get job IDs list
            jobs_key = f"{key}:jobs"
            job_ids_raw = await self.redis_client.lrange(jobs_key, 0, -1)
            deserialized['job_ids'] = [
                job_id.decode('utf-8') if isinstance(job_id, bytes) else job_id
                for job_id in job_ids_raw
            ]
            
            logger.debug("Retrieved batch %s from Redis", batch_id)
            return deserialized
            
        except Exception as e:
            logger.error("Failed to retrieve batch %s: %s", batch_id, str(e))
            raise
    
    async def update_batch(self, batch_id: str, updates: Dict[str, Any]):
        """
        Update batch metadata.
        
        Args:
            batch_id: Batch identifier
            updates: Dictionary of fields to update
        """
        if not self.redis_client:
            await self.connect()
        
        try:
            key = self._get_batch_key(batch_id)
            
            # Serialize updates
            serialized_updates = {}
            for k, v in updates.items():
                if isinstance(v, (dict, list)):
                    serialized_updates[k] = json.dumps(v, default=str)
                else:
                    serialized_updates[k] = v
            
            await self.redis_client.hset(key, mapping=serialized_updates)
            logger.debug("Updated batch %s", batch_id)
            
        except Exception as e:
            logger.error("Failed to update batch %s: %s", batch_id, str(e))
            raise
    
    async def delete_batch(self, batch_id: str):
        """
        Delete a batch from Redis.
        
        Args:
            batch_id: Batch identifier
        """
        if not self.redis_client:
            await self.connect()
        
        try:
            key = self._get_batch_key(batch_id)
            jobs_key = f"{key}:jobs"
            
            await self.redis_client.delete(key)
            await self.redis_client.delete(jobs_key)
            
            logger.debug("Deleted batch %s", batch_id)
            
        except Exception as e:
            logger.error("Failed to delete batch %s: %s", batch_id, str(e))
            raise



# Global Redis service instance
_redis_service: Optional[RedisService] = None


async def get_redis_service() -> RedisService:
    """
    Get or create the global Redis service instance.
    
    Returns:
        RedisService instance
    """
    global _redis_service
    if _redis_service is None:
        _redis_service = RedisService()
        await _redis_service.connect()
    return _redis_service


async def close_redis_service():
    """Close the global Redis service connection."""
    global _redis_service
    if _redis_service:
        await _redis_service.disconnect()
        _redis_service = None

