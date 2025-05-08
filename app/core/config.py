import os
from typing import List, Optional
from pydantic import BaseModel
from dotenv import load_dotenv

# Load environment variables from .env file if present
load_dotenv()

class Settings(BaseModel):
    # Environment
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    
    # API settings
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "PDF Converter API"
    
    # CORS settings
    CORS_ORIGINS: List[str] = os.getenv("CORS_ORIGINS", "*").split(",")
    
    # Security settings
    MAX_FILE_SIZE: int = int(os.getenv("MAX_FILE_SIZE", 10 * 1024 * 1024))  # 10MB default
    RATE_LIMIT: str = os.getenv("RATE_LIMIT", "100/day")
    
    # File storage settings
    TEMP_DIR: str = os.getenv("TEMP_DIR", os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "tmp"))
    FILE_EXPIRY_HOURS: int = int(os.getenv("FILE_EXPIRY_HOURS", 24))  # Delete files after 24 hours

settings = Settings()
