"""MCP Tools Main Application.

This module provides the main FastAPI application for the MCP Tools service,
including health checks, authentication, and development tools functionality.
"""

import os
from typing import Any, Dict

import structlog
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Configure logging
logger = structlog.get_logger()

# Initialize FastAPI app
app = FastAPI(
    title="MCP Tools Service",
    description="Machine Control Program Tools Service for IGN Scripts",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health check response model
class HealthResponse(BaseModel):
    """Health check response model."""
    status: str
    version: str
    details: Dict[str, Any]

@app.get("/health", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    """Health check endpoint.
    
    Returns:
        HealthResponse: Health status information
    """
    return HealthResponse(
        status="healthy",
        version="1.0.0",
        details={
            "service": "mcp-tools",
            "environment": os.getenv("ENVIRONMENT", "development")
        }
    )

@app.get("/")
async def root() -> Dict[str, str]:
    """Root endpoint.
    
    Returns:
        Dict[str, str]: Welcome message
    """
    return {"message": "Welcome to MCP Tools Service"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8082,
        reload=True
    ) 