from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import upload, chat
from utils.logger import logger


app = FastAPI(
    title="Research Assistant for PDFs",
    description="Backend API for uploading research papers and answering questions with LLM",
    version="1.0.0",
)


# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"], 
    allow_headers=["*"],
)

# Include routers
app.include_router(upload.router)
app.include_router(chat.router)


@app.get("/")
async def read_root():
    """Health check endpoint"""
    logger.info("Health check successful")
    return {
        "status": "success",
        "message": "Research Assistant for PDFs Backend is running!",
        "version": "1.0.0"
    }


@app.get("/health")
async def health_check():
    """Detailed health check"""
    return {
        "status": "healthy",
        "service": "Research Assistant for PDFs",
        "version": "1.0.0"
    }


@app.on_event("startup")
async def startup_event():
    """Initialize on startup"""
    logger.info("Application starting up...")
    logger.info("Research Assistant for PDFs Backend initialized")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    logger.info("Application shutting down...")


