from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
import uvicorn
import logging
from contextlib import asynccontextmanager

from app.api.routes import plagiarism
from app.core.config import settings
from app.core.logging import setup_logging
from app.services.model_manager import ModelManager

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)

# Global model manager instance
model_manager = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events"""
    global model_manager
    
    # Startup
    logger.info("Starting AI Plagiarism Detection Service...")
    model_manager = ModelManager()
    await model_manager.load_models()
    logger.info("Models loaded successfully")
    
    yield
    
    # Shutdown
    logger.info("Shutting down AI Plagiarism Detection Service...")
    if model_manager:
        await model_manager.cleanup()

app = FastAPI(
    title="University Archive - AI Plagiarism Detection Service",
    description="AI-powered plagiarism detection service for university document archive",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Add middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_HOSTS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=settings.ALLOWED_HOSTS
)

# Include routers
app.include_router(
    plagiarism.router,
    prefix="/api/v1/plagiarism",
    tags=["plagiarism"]
)

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "AI Plagiarism Detection Service",
        "version": "1.0.0",
        "status": "running"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    global model_manager
    
    if not model_manager or not model_manager.is_ready():
        raise HTTPException(status_code=503, detail="Models not ready")
    
    return {
        "status": "healthy",
        "models_loaded": model_manager.get_loaded_models(),
        "service": "AI Plagiarism Detection"
    }

def get_model_manager() -> ModelManager:
    """Dependency to get model manager instance"""
    global model_manager
    if not model_manager:
        raise HTTPException(status_code=503, detail="Model manager not initialized")
    return model_manager

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8001,
        reload=True,
        log_level="info"
    )