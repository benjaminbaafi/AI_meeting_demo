"""
WebSocket manager for real-time job status updates.
Manages WebSocket connections and broadcasts updates to clients.
"""
import asyncio
import logging
from typing import Dict, Set
from fastapi import WebSocket, WebSocketDisconnect
import json

logger = logging.getLogger(__name__)


class WebSocketManager:
    """Manages WebSocket connections for real-time updates."""
    
    def __init__(self):
        # job_id -> set of websocket connections
        self.job_connections: Dict[str, Set[WebSocket]] = {}
        # batch_id -> set of websocket connections
        self.batch_connections: Dict[str, Set[WebSocket]] = {}
        self._lock = asyncio.Lock()
    
    async def connect_job(self, job_id: str, websocket: WebSocket):
        """
        Connect a WebSocket to a job.
        
        Args:
            job_id: Job identifier
            websocket: WebSocket connection
        """
        await websocket.accept()
        
        async with self._lock:
            if job_id not in self.job_connections:
                self.job_connections[job_id] = set()
            self.job_connections[job_id].add(websocket)
        
        logger.info(f"WebSocket connected to job {job_id}")
    
    async def disconnect_job(self, job_id: str, websocket: WebSocket):
        """
        Disconnect a WebSocket from a job.
        
        Args:
            job_id: Job identifier
            websocket: WebSocket connection
        """
        async with self._lock:
            if job_id in self.job_connections:
                self.job_connections[job_id].discard(websocket)
                if not self.job_connections[job_id]:
                    del self.job_connections[job_id]
        
        logger.info(f"WebSocket disconnected from job {job_id}")
    
    async def connect_batch(self, batch_id: str, websocket: WebSocket):
        """
        Connect a WebSocket to a batch.
        
        Args:
            batch_id: Batch identifier
            websocket: WebSocket connection
        """
        await websocket.accept()
        
        async with self._lock:
            if batch_id not in self.batch_connections:
                self.batch_connections[batch_id] = set()
            self.batch_connections[batch_id].add(websocket)
        
        logger.info(f"WebSocket connected to batch {batch_id}")
    
    async def disconnect_batch(self, batch_id: str, websocket: WebSocket):
        """
        Disconnect a WebSocket from a batch.
        
        Args:
            batch_id: Batch identifier
            websocket: WebSocket connection
        """
        async with self._lock:
            if batch_id in self.batch_connections:
                self.batch_connections[batch_id].discard(websocket)
                if not self.batch_connections[batch_id]:
                    del self.batch_connections[batch_id]
        
        logger.info(f"WebSocket disconnected from batch {batch_id}")
    
    async def broadcast_job_update(self, job_id: str, message: dict):
        """
        Broadcast update to all connections watching a job.
        
        Args:
            job_id: Job identifier
            message: Message to broadcast
        """
        async with self._lock:
            connections = self.job_connections.get(job_id, set()).copy()
        
        if connections:
            message_json = json.dumps(message, default=str)
            disconnected = set()
            
            for websocket in connections:
                try:
                    await websocket.send_text(message_json)
                except Exception as e:
                    logger.warning(f"Failed to send to websocket: {e}")
                    disconnected.add(websocket)
            
            # Clean up disconnected websockets
            if disconnected:
                async with self._lock:
                    if job_id in self.job_connections:
                        self.job_connections[job_id] -= disconnected
                        if not self.job_connections[job_id]:
                            del self.job_connections[job_id]
    
    async def broadcast_batch_update(self, batch_id: str, message: dict):
        """
        Broadcast update to all connections watching a batch.
        
        Args:
            batch_id: Batch identifier
            message: Message to broadcast
        """
        async with self._lock:
            connections = self.batch_connections.get(batch_id, set()).copy()
        
        if connections:
            message_json = json.dumps(message, default=str)
            disconnected = set()
            
            for websocket in connections:
                try:
                    await websocket.send_text(message_json)
                except Exception as e:
                    logger.warning(f"Failed to send to websocket: {e}")
                    disconnected.add(websocket)
            
            # Clean up disconnected websockets
            if disconnected:
                async with self._lock:
                    if batch_id in self.batch_connections:
                        self.batch_connections[batch_id] -= disconnected
                        if not self.batch_connections[batch_id]:
                            del self.batch_connections[batch_id]
    
    async def cleanup_job(self, job_id: str):
        """
        Clean up all connections for a job.
        
        Args:
            job_id: Job identifier
        """
        async with self._lock:
            if job_id in self.job_connections:
                connections = self.job_connections[job_id].copy()
                del self.job_connections[job_id]
                
                # Close all connections
                for websocket in connections:
                    try:
                        await websocket.close()
                    except Exception:
                        pass
        
        logger.info(f"Cleaned up WebSocket connections for job {job_id}")
    
    async def cleanup_batch(self, batch_id: str):
        """
        Clean up all connections for a batch.
        
        Args:
            batch_id: Batch identifier
        """
        async with self._lock:
            if batch_id in self.batch_connections:
                connections = self.batch_connections[batch_id].copy()
                del self.batch_connections[batch_id]
                
                # Close all connections
                for websocket in connections:
                    try:
                        await websocket.close()
                    except Exception:
                        pass
        
        logger.info(f"Cleaned up WebSocket connections for batch {batch_id}")


# Global WebSocket manager instance
_ws_manager: WebSocketManager = None


def get_ws_manager() -> WebSocketManager:
    """
    Get or create the global WebSocket manager instance.
    
    Returns:
        WebSocketManager instance
    """
    global _ws_manager
    if _ws_manager is None:
        _ws_manager = WebSocketManager()
    return _ws_manager
