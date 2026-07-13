from contextlib import asynccontextmanager
from pathlib import Path
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from app.api.routes import router as research_router
from app.search.bm25 import get_bm25_index
from app.utils.logger import logger
from app.utils.config import settings

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Handles application startup and shutdown lifecycle events.
    Preloads and tokenizes the 10,000 documents BM25 index to speed up API responses.
    """
    logger.info("Starting Multi-Agent Web Research & Summarization System...")
    logger.info(f"Configuration - Model: '{settings.gemini_model}' | Log Level: '{settings.log_level}'")
    
    # Initialize and fit BM25 index at startup
    try:
        get_bm25_index()
        logger.info("BM25 Index pre-loaded and cached successfully.")
    except Exception as e:
        logger.critical(f"Critical failure loading BM25 index on startup: {e}")
        
    yield
    
    logger.info("Shutting down Multi-Agent Web Research & Summarization System...")

app = FastAPI(
    title="Multi-Agent Web Research & Summarization System",
    description="Autonomous multi-agent research agent system using FastAPI, LangGraph, and Google Gemini.",
    version="1.0.0",
    lifespan=lifespan
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Exception handler for general internal server errors
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled request exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": f"Internal Server Error: {str(exc)}"}
    )

# Include routes
app.include_router(research_router, tags=["Research"])

# Mount static files directory for reports download
reports_path = Path("reports")
reports_path.mkdir(exist_ok=True)
app.mount("/reports", StaticFiles(directory="reports"), name="reports")

@app.get("/health", tags=["Diagnostic"])
async def health_check():
    """
    Liveness probe.
    """
    return {"status": "healthy", "model": settings.gemini_model}
