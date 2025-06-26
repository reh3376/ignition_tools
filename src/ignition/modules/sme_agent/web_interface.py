"""SME Agent Web Interface - FastAPI Implementation.

Phase 11.3: SME Agent Integration & Interfaces
Following crawl_mcp.py methodology:
- Step 1: Environment validation first
- Step 2: Comprehensive input validation
- Step 3: Error handling with user-friendly messages
- Step 4: Modular component testing
- Step 5: Progressive complexity support
- Step 6: Resource management and cleanup

Multi-Interface Deployment:
- FastAPI chat endpoint with streaming responses
- Real-time conversation management
- Integration with existing SME Agent module
- Production-ready deployment with uvicorn
"""

import asyncio
import json
import logging
import time
import uuid
from contextlib import asynccontextmanager
from datetime import datetime
from typing import Any

import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field, validator

from .sme_agent_module import SMEAgentModule, SMEAgentValidationError

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global SME Agent instance for reuse
sme_agent_instance = None


@asynccontextmanager
async def lifespan(app: FastAPI) -> None:
    """Application lifespan management with proper resource cleanup."""
    global sme_agent_instance

    # Startup
    logger.info("🚀 Starting SME Agent Web Interface")
    try:
        # Step 1: Environment Validation First
        sme_agent_instance = SMEAgentModule()
        validation_result = sme_agent_instance.validate_environment()

        if not validation_result["valid"]:
            logger.error("❌ Environment validation failed")
            logger.error(f"Validation errors: {validation_result.get('errors', [])}")
            raise RuntimeError("SME Agent environment validation failed")

        # Initialize with basic complexity for web interface
        init_result = sme_agent_instance.initialize_components(complexity_level="standard")
        if not init_result["success"]:
            logger.error("❌ SME Agent initialization failed")
            raise RuntimeError("SME Agent initialization failed")

        logger.info("✅ SME Agent Web Interface started successfully")
        yield

    except Exception as e:
        logger.error(f"❌ Failed to start SME Agent: {e}")
        raise
    finally:
        # Cleanup
        logger.info("🔄 Shutting down SME Agent Web Interface")
        if sme_agent_instance:
            sme_agent_instance.cleanup()
        logger.info("✅ SME Agent Web Interface shutdown complete")


# FastAPI app initialization
app = FastAPI(
    title="SME Agent Web Interface",
    description="Phase 11.3: Multi-Interface Deployment for Ignition SME Agent",
    version="11.3.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# CORS middleware for web interface access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Pydantic models for API requests and responses
class ChatRequest(BaseModel):
    """Chat request model with comprehensive validation."""

    question: str = Field(..., min_length=1, max_length=10000, description="User question")
    context: str | None = Field(None, max_length=20000, description="Optional context")
    complexity: str = Field("standard", description="Complexity level")
    session_id: str | None = Field(None, description="Optional session ID for conversation history")
    stream: bool = Field(True, description="Enable streaming response")

    @validator("complexity")
    def validate_complexity(cls, v) -> None:
        """Validate complexity level."""
        allowed = ["basic", "standard", "advanced", "enterprise"]
        if v not in allowed:
            raise ValueError(f"Complexity must be one of: {allowed}")
        return v

    @validator("question")
    def validate_question(cls, v) -> None:
        """Validate question content."""
        if not v.strip():
            raise ValueError("Question cannot be empty or whitespace only")
        return v.strip()


class ChatResponse(BaseModel):
    """Chat response model."""

    response: str
    confidence: float
    sources: list[str]
    processing_time: float
    model_used: str
    knowledge_sources: list[str]
    session_id: str
    timestamp: str


class AnalysisRequest(BaseModel):
    """File analysis request model."""

    content: str = Field(..., min_length=1, max_length=100000, description="File content to analyze")
    filename: str | None = Field(None, description="Optional filename")
    complexity: str = Field("standard", description="Analysis complexity level")

    @validator("complexity")
    def validate_complexity(cls, v) -> None:
        """Validate complexity level."""
        allowed = ["basic", "standard", "advanced", "enterprise"]
        if v not in allowed:
            raise ValueError(f"Complexity must be one of: {allowed}")
        return v


class StatusResponse(BaseModel):
    """System status response."""

    status: str
    initialized: bool
    components: dict[str, Any]
    uptime: float
    version: str


# Global variables for session management
conversation_sessions = {}
start_time = time.time()


@app.get("/", tags=["Health"])
async def root() -> None:
    """Root endpoint with basic information."""
    return {
        "message": "SME Agent Web Interface - Phase 11.3",
        "version": "11.3.0",
        "status": "operational",
        "endpoints": {
            "docs": "/docs",
            "health": "/health",
            "chat": "/chat",
            "chat_stream": "/chat/stream",
            "analyze": "/analyze",
            "status": "/status",
        },
    }


@app.get("/health", tags=["Health"])
async def health_check() -> None:
    """Health check endpoint with detailed status."""
    global sme_agent_instance

    try:
        if not sme_agent_instance:
            return {"status": "unhealthy", "reason": "SME Agent not initialized"}

        # Get detailed status
        agent_status = sme_agent_instance.get_status()

        return {
            "status": "healthy" if agent_status["initialized"] else "degraded",
            "timestamp": datetime.now().isoformat(),
            "uptime": time.time() - start_time,
            "agent_status": agent_status,
            "version": "11.3.0",
        }

    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {"status": "unhealthy", "reason": str(e)}


@app.post("/chat", response_model=ChatResponse, tags=["Chat"])
async def chat_endpoint(request: ChatRequest) -> None:
    """Standard chat endpoint with complete response."""
    global sme_agent_instance

    # Step 2: Comprehensive Input Validation
    if not sme_agent_instance:
        raise HTTPException(status_code=503, detail="SME Agent not available")

    try:
        # Generate session ID if not provided
        session_id = request.session_id or str(uuid.uuid4())

        # Process question
        time.time()
        response = sme_agent_instance.ask_question(request.question, request.context)

        # Store in conversation session
        if session_id not in conversation_sessions:
            conversation_sessions[session_id] = []

        conversation_sessions[session_id].append(
            {
                "timestamp": datetime.now().isoformat(),
                "question": request.question,
                "context": request.context,
                "response": response.response,
                "confidence": response.confidence,
            }
        )

        return ChatResponse(
            response=response.response,
            confidence=response.confidence,
            sources=response.sources,
            processing_time=response.processing_time,
            model_used=response.model_used,
            knowledge_sources=response.knowledge_sources,
            session_id=session_id,
            timestamp=datetime.now().isoformat(),
        )

    except SMEAgentValidationError as e:
        # Step 3: Error Handling and User-Friendly Messages
        logger.error(f"Validation error in chat: {e}")
        raise HTTPException(status_code=400, detail=str(e))

    except Exception as e:
        logger.error(f"Chat processing failed: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@app.post("/chat/stream", tags=["Chat"])
async def chat_stream_endpoint(request: ChatRequest) -> None:
    """Streaming chat endpoint with real-time responses."""
    global sme_agent_instance

    if not sme_agent_instance:
        raise HTTPException(status_code=503, detail="SME Agent not available")

    # Generate session ID if not provided
    session_id = request.session_id or str(uuid.uuid4())

    async def generate_stream() -> None:
        """Generate streaming response."""
        try:
            # Send initial metadata
            yield f"data: {json.dumps({'type': 'start', 'session_id': session_id, 'timestamp': datetime.now().isoformat()})}\n\n"  # noqa: E501

            # Process question (simulate streaming by chunking response)
            response = sme_agent_instance.ask_question(request.question, request.context)

            # Stream response in chunks
            words = response.response.split()
            chunk_size = max(1, len(words) // 20)  # Stream in ~20 chunks

            for i in range(0, len(words), chunk_size):
                chunk = " ".join(words[i : i + chunk_size])
                chunk_data = {
                    "type": "chunk",
                    "content": chunk,
                    "chunk_index": i // chunk_size,
                    "session_id": session_id,
                }
                yield f"data: {json.dumps(chunk_data)}\n\n"
                await asyncio.sleep(0.1)  # Small delay for streaming effect

            # Send completion metadata
            completion_data = {
                "type": "complete",
                "confidence": response.confidence,
                "sources": response.sources,
                "processing_time": response.processing_time,
                "model_used": response.model_used,
                "knowledge_sources": response.knowledge_sources,
                "session_id": session_id,
                "timestamp": datetime.now().isoformat(),
            }
            yield f"data: {json.dumps(completion_data)}\n\n"

            # Store in conversation session
            if session_id not in conversation_sessions:
                conversation_sessions[session_id] = []

            conversation_sessions[session_id].append(
                {
                    "timestamp": datetime.now().isoformat(),
                    "question": request.question,
                    "context": request.context,
                    "response": response.response,
                    "confidence": response.confidence,
                }
            )

        except Exception as e:
            error_data = {
                "type": "error",
                "error": str(e),
                "session_id": session_id,
                "timestamp": datetime.now().isoformat(),
            }
            yield f"data: {json.dumps(error_data)}\n\n"

    return StreamingResponse(
        generate_stream(),
        media_type="text/plain",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Content-Type": "text/event-stream",
        },
    )


@app.post("/analyze", tags=["Analysis"])
async def analyze_endpoint(request: AnalysisRequest) -> None:
    """File analysis endpoint."""
    global sme_agent_instance

    if not sme_agent_instance:
        raise HTTPException(status_code=503, detail="SME Agent not available")

    try:
        # Create analysis question
        question = (
            "Please analyze this file and provide insights about its structure, purpose, and potential improvements."
        )
        context = (
            f"Filename: {request.filename or 'unknown'}\nContent:\n{request.content[:5000]}..."  # Limit context size
        )

        # Process analysis
        response = sme_agent_instance.ask_question(question, context)

        return {
            "analysis": response.response,
            "confidence": response.confidence,
            "sources": response.sources,
            "processing_time": response.processing_time,
            "model_used": response.model_used,
            "knowledge_sources": response.knowledge_sources,
            "filename": request.filename,
            "timestamp": datetime.now().isoformat(),
        }

    except Exception as e:
        logger.error(f"Analysis failed: {e}")
        raise HTTPException(status_code=500, detail="Analysis failed")


@app.get("/status", response_model=StatusResponse, tags=["Status"])
async def status_endpoint() -> None:
    """Detailed system status endpoint."""
    global sme_agent_instance

    try:
        if not sme_agent_instance:
            return StatusResponse(
                status="not_initialized",
                initialized=False,
                components={},
                uptime=time.time() - start_time,
                version="11.3.0",
            )

        agent_status = sme_agent_instance.get_status()

        return StatusResponse(
            status="operational" if agent_status["initialized"] else "degraded",
            initialized=agent_status["initialized"],
            components=agent_status["components"],
            uptime=time.time() - start_time,
            version="11.3.0",
        )

    except Exception as e:
        logger.error(f"Status check failed: {e}")
        raise HTTPException(status_code=500, detail="Status check failed")


@app.get("/sessions/{session_id}", tags=["Sessions"])
async def get_session_history(session_id: str) -> None:
    """Get conversation history for a session."""
    if session_id not in conversation_sessions:
        raise HTTPException(status_code=404, detail="Session not found")

    return {
        "session_id": session_id,
        "conversation_count": len(conversation_sessions[session_id]),
        "history": conversation_sessions[session_id],
    }


@app.delete("/sessions/{session_id}", tags=["Sessions"])
async def clear_session_history(session_id: str) -> None:
    """Clear conversation history for a session."""
    if session_id in conversation_sessions:
        del conversation_sessions[session_id]
        return {"message": f"Session {session_id} cleared"}

    raise HTTPException(status_code=404, detail="Session not found")


# Background task for cleanup
@app.on_event("startup")
async def startup_event() -> None:
    """Additional startup tasks."""
    logger.info("🌐 SME Agent Web Interface ready for connections")


def run_server(host: str = "0.0.0.0", port: int = 8000, reload: bool = False) -> None:
    """Run the FastAPI server with uvicorn.

    Args:
        host: Server host address
        port: Server port
        reload: Enable auto-reload for development
    """
    logger.info(f"🚀 Starting SME Agent Web Interface on {host}:{port}")

    uvicorn.run(
        "ignition.modules.sme_agent.web_interface:app",
        host=host,
        port=port,
        reload=reload,
        log_level="info",
        access_log=True,
    )


if __name__ == "__main__":
    # Step 5: Progressive Complexity Support
    # Default to development mode with reload
    run_server(reload=True)
