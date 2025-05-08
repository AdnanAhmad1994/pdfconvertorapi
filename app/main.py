from fastapi import FastAPI, Request, BackgroundTasks, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
import asyncio
import logging
import os
from app.core.config import settings
from app.api.api import api_router
from app.api.endpoints.conversion import cleanup_expired_tasks
from app.security.api_key import get_api_key

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

# Set up templates and static files directories
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))

app = FastAPI(
    title="PDF Converter API",
    description="API for converting PDF files to various formats (DOCX, JPEG, PPT, HTML)",
    version="1.0.0",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
app.mount("/static", StaticFiles(directory=os.path.join(BASE_DIR, "static")), name="static")

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    """Serve the API welcome page"""
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/ui", response_class=HTMLResponse)
async def converter_ui(request: Request):
    """Serve the PDF converter UI"""
    return templates.TemplateResponse("converter.html", {"request": request})

@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {"status": "ok", "version": "1.0.0"}

# Include API router
app.include_router(api_router, prefix=settings.API_V1_STR)

@app.on_event("startup")
async def startup_event():
    """Start background tasks."""
    # Create temp directory if it doesn't exist
    os.makedirs(settings.TEMP_DIR, exist_ok=True)
    logger.info(f"Temp directory: {settings.TEMP_DIR}")
    
    # Schedule cleanup task
    asyncio.create_task(periodic_cleanup())
    logger.info("Started background cleanup task")

async def periodic_cleanup():
    """Run cleanup task periodically."""
    while True:
        await asyncio.sleep(60 * 60)  # Run cleanup every hour
        try:
            cleanup_expired_tasks()
            logger.info("Performed scheduled cleanup of expired tasks")
        except Exception as e:
            logger.error(f"Error in cleanup task: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
