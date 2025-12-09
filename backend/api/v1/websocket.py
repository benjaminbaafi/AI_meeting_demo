"""
WebSocket API endpoints for real-time job updates.
"""
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from datetime import datetime
import logging

from utils.websocket_manager import get_ws_manager
from utils.redis_service import get_redis_service

router = APIRouter()
logger = logging.getLogger(__name__)


@router.websocket("/ws/job/{job_id}")
async def websocket_job_endpoint(websocket: WebSocket, job_id: str):
    """
    WebSocket endpoint for real-time job updates.
    
    Clients connect to this endpoint to receive real-time updates
    about job processing status, progress, and completion.
    
    Message format:
    {
        "type": "status_update",
        "job_id": "uuid",
        "status": "processing",
        "progress": 45.5,
        "current_step": "Transcribing audio",
        "timestamp": "2024-12-08T16:50:00Z"
    }
    """
    ws_manager = get_ws_manager()
    
    try:
        # Connect the WebSocket
        await ws_manager.connect_job(job_id, websocket)
        
        # Send initial status
        redis_service = await get_redis_service()
        job_metadata = await redis_service.get_job_metadata(job_id)
        
        if job_metadata:
            initial_message = {
                "type": "connected",
                "job_id": job_id,
                "status": job_metadata.get("status", "unknown"),
                "progress": job_metadata.get("progress", 0),
                "current_step": job_metadata.get("current_step", "Initializing"),
                "timestamp": datetime.utcnow().isoformat()
            }
            await websocket.send_json(initial_message)
        else:
            error_message = {
                "type": "error",
                "job_id": job_id,
                "message": "Job not found",
                "timestamp": datetime.utcnow().isoformat()
            }
            await websocket.send_json(error_message)
            await websocket.close()
            return
        
        # Keep connection alive and listen for client messages
        while True:
            try:
                # Wait for any message from client (ping/pong)
                data = await websocket.receive_text()
                
                # Echo ping/pong for keepalive
                if data == "ping":
                    await websocket.send_text("pong")
                    
            except WebSocketDisconnect:
                break
                
    except Exception as e:
        logger.error(f"WebSocket error for job {job_id}: {str(e)}")
    finally:
        await ws_manager.disconnect_job(job_id, websocket)


@router.websocket("/ws/batch/{batch_id}")
async def websocket_batch_endpoint(websocket: WebSocket, batch_id: str):
    """
    WebSocket endpoint for real-time batch updates.
    
    Clients connect to this endpoint to receive real-time updates
    about batch processing status and individual job progress.
    
    Message format:
    {
        "type": "batch_update",
        "batch_id": "uuid",
        "total_files": 5,
        "completed": 2,
        "processing": 2,
        "failed": 0,
        "progress": 60.0,
        "jobs": [...],
        "timestamp": "2024-12-08T16:50:00Z"
    }
    """
    ws_manager = get_ws_manager()
    
    try:
        # Connect the WebSocket
        await ws_manager.connect_batch(batch_id, websocket)
        
        # Send initial status
        redis_service = await get_redis_service()
        batch_data = await redis_service.get_batch(batch_id)
        
        if batch_data:
            initial_message = {
                "type": "connected",
                "batch_id": batch_id,
                "total_files": batch_data.get("total_files", 0),
                "status": batch_data.get("status", "unknown"),
                "timestamp": datetime.utcnow().isoformat()
            }
            await websocket.send_json(initial_message)
        else:
            error_message = {
                "type": "error",
                "batch_id": batch_id,
                "message": "Batch not found",
                "timestamp": datetime.utcnow().isoformat()
            }
            await websocket.send_json(error_message)
            await websocket.close()
            return
        
        # Keep connection alive
        while True:
            try:
                data = await websocket.receive_text()
                
                if data == "ping":
                    await websocket.send_text("pong")
                    
            except WebSocketDisconnect:
                break
                
    except Exception as e:
        logger.error(f"WebSocket error for batch {batch_id}: {str(e)}")
    finally:
        await ws_manager.disconnect_batch(batch_id, websocket)
