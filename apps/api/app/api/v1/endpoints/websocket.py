"""
WebSocket endpoint for real-time communication.
Handles render progress, queue updates, and worker status.
"""
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query, Depends
from typing import Optional

from app.core.websocket import websocket_endpoint, get_connection_manager

router = APIRouter(tags=["websocket"])


@router.websocket("/ws")
async def websocket_connection(
    websocket: WebSocket,
    token: Optional[str] = Query(None),
    channels: Optional[str] = Query(None)
):
    """
    WebSocket endpoint for real-time updates.
    
    Query Parameters:
    - token: JWT token for authentication (optional)
    - channels: Comma-separated list of channels to subscribe to (optional)
    
    Channels:
    - global: General updates
    - renders: Render job updates
    - queue: Queue statistics
    - workers: Worker status updates
    - media: Media asset updates
    - transcode: Transcoding progress
    """
    await websocket_endpoint(websocket, token, channels)


@router.websocket("/ws/renders")
async def websocket_renders(
    websocket: WebSocket,
    token: Optional[str] = Query(None)
):
    """WebSocket endpoint specifically for render updates"""
    await websocket_endpoint(websocket, token, "renders")


@router.websocket("/ws/queue")
async def websocket_queue(
    websocket: WebSocket,
    token: Optional[str] = Query(None)
):
    """WebSocket endpoint specifically for queue updates"""
    await websocket_endpoint(websocket, token, "queue")


@router.websocket("/ws/workers")
async def websocket_workers(
    websocket: WebSocket,
    token: Optional[str] = Query(None)
):
    """WebSocket endpoint specifically for worker status"""
    await websocket_endpoint(websocket, token, "workers")


@router.websocket("/ws/uploads")
async def websocket_uploads(
    websocket: WebSocket,
    token: Optional[str] = Query(None)
):
    """WebSocket endpoint specifically for upload progress"""
    await websocket_endpoint(websocket, token, "uploads")