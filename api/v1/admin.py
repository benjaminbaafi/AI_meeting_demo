"""
Admin API endpoints for Redis database management.
Provides endpoints to view and manage jobs stored in Redis.
"""
from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional, Dict, Any
import logging
from datetime import datetime

from utils.redis_service import get_redis_service

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/admin/jobs")
async def list_all_jobs(
    status: Optional[str] = Query(None, description="Filter by status (queued, processing, completed, failed)"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of jobs to return"),
    offset: int = Query(0, ge=0, description="Number of jobs to skip"),
):
    """
    List all jobs in Redis database.
    
    Returns a paginated list of all jobs with their basic information.
    """
    try:
        redis_service = await get_redis_service()
        
        # Get all job keys (this is a simplified approach - in production, use Redis SCAN)
        # Note: Redis doesn't have a native "list all keys" that's efficient for large datasets
        # For now, we'll need to scan keys with pattern "job:*"
        import redis.asyncio as aioredis
        client = redis_service.redis_client
        
        if not client:
            raise HTTPException(status_code=503, detail="Redis connection not available")
        
        # Scan for all job keys
        job_keys = []
        cursor = 0
        pattern = "job:*"
        
        while True:
            cursor, keys = await client.scan(cursor, match=pattern, count=100)
            job_keys.extend(keys)
            if cursor == 0:
                break
        
        # Fetch job data
        jobs = []
        for key in job_keys[offset:offset + limit]:
            job_id = key.decode('utf-8').replace('job:', '') if isinstance(key, bytes) else key.replace('job:', '')
            job_data = await redis_service.get_job(job_id)
            
            if job_data:
                # Filter by status if provided
                if status:
                    job_status = job_data.get("status", "").lower()
                    if job_status != status.lower():
                        continue
                
                # Extract basic info
                job_summary = {
                    "job_id": job_id,
                    "status": job_data.get("status"),
                    "filename": job_data.get("filename"),
                    "file_size_bytes": job_data.get("file_size_bytes"),
                    "created_at": job_data.get("created_at"),
                    "updated_at": job_data.get("updated_at"),
                    "progress": job_data.get("progress", 0),
                    "current_step": job_data.get("current_step"),
                    "has_transcription": "transcription" in job_data,
                    "has_summary": "summary" in job_data,
                }
                jobs.append(job_summary)
        
        return {
            "total": len(job_keys),
            "limit": limit,
            "offset": offset,
            "jobs": jobs,
        }
        
    except Exception as e:
        logger.exception("Failed to list jobs")
        raise HTTPException(status_code=500, detail=f"Failed to list jobs: {str(e)}")


@router.get("/admin/jobs/{job_id}")
async def get_job_details(job_id: str):
    """
    Get full details of a specific job.
    
    Returns complete job data including transcription and summary if available.
    """
    try:
        redis_service = await get_redis_service()
        job = await redis_service.get_job(job_id)
        
        if not job:
            raise HTTPException(status_code=404, detail=f"Job {job_id} not found")
        
        return job
        
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Failed to get job details")
        raise HTTPException(status_code=500, detail=f"Failed to get job details: {str(e)}")


@router.get("/admin/stats")
async def get_redis_stats():
    """
    Get Redis database statistics.
    
    Returns information about jobs, storage usage, and Redis server info.
    """
    try:
        redis_service = await get_redis_service()
        client = redis_service.redis_client
        
        if not client:
            raise HTTPException(status_code=503, detail="Redis connection not available")
        
        # Get Redis info
        info = await client.info()
        
        # Count jobs by status
        job_keys = []
        cursor = 0
        pattern = "job:*"
        
        while True:
            cursor, keys = await client.scan(cursor, match=pattern, count=100)
            job_keys.extend(keys)
            if cursor == 0:
                break
        
        status_counts = {"queued": 0, "processing": 0, "completed": 0, "failed": 0, "cancelled": 0}
        
        for key in job_keys[:100]:  # Sample first 100 for performance
            job_id = key.decode('utf-8').replace('job:', '') if isinstance(key, bytes) else key.replace('job:', '')
            job_data = await redis_service.get_job(job_id)
            if job_data:
                status = job_data.get("status", "").lower()
                if status in status_counts:
                    status_counts[status] += 1
        
        # Get Redis memory info
        memory_info = await client.info("memory")
        
        return {
            "total_jobs": len(job_keys),
            "jobs_by_status": status_counts,
            "redis_version": info.get("redis_version", "unknown"),
            "used_memory_human": memory_info.get("used_memory_human", "unknown"),
            "used_memory_peak_human": memory_info.get("used_memory_peak_human", "unknown"),
            "connected_clients": info.get("connected_clients", 0),
            "total_commands_processed": info.get("total_commands_processed", 0),
        }
        
    except Exception as e:
        logger.exception("Failed to get Redis stats")
        raise HTTPException(status_code=500, detail=f"Failed to get stats: {str(e)}")


@router.delete("/admin/jobs/{job_id}")
async def delete_job(job_id: str):
    """
    Delete a job from Redis database.
    
    This permanently removes the job and all its data.
    """
    try:
        redis_service = await get_redis_service()
        
        # Check if job exists
        exists = await redis_service.job_exists(job_id)
        if not exists:
            raise HTTPException(status_code=404, detail=f"Job {job_id} not found")
        
        # Delete job
        await redis_service.delete_job(job_id)
        
        logger.info("Admin deleted job: %s", job_id)
        
        return {"message": f"Job {job_id} deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Failed to delete job")
        raise HTTPException(status_code=500, detail=f"Failed to delete job: {str(e)}")


@router.get("/admin/redis/keys")
async def list_redis_keys(
    pattern: str = Query("job:*", description="Key pattern to search for"),
    limit: int = Query(100, ge=1, le=1000),
):
    """
    List Redis keys matching a pattern.
    
    Useful for debugging and inspecting Redis database contents.
    """
    try:
        redis_service = await get_redis_service()
        client = redis_service.redis_client
        
        if not client:
            raise HTTPException(status_code=503, detail="Redis connection not available")
        
        keys = []
        cursor = 0
        
        while len(keys) < limit:
            cursor, found_keys = await client.scan(cursor, match=pattern, count=100)
            keys.extend(found_keys)
            if cursor == 0:
                break
        
        # Decode keys
        decoded_keys = [
            k.decode('utf-8') if isinstance(k, bytes) else k
            for k in keys[:limit]
        ]
        
        return {
            "pattern": pattern,
            "count": len(decoded_keys),
            "keys": decoded_keys,
        }
        
    except Exception as e:
        logger.exception("Failed to list Redis keys")
        raise HTTPException(status_code=500, detail=f"Failed to list keys: {str(e)}")

