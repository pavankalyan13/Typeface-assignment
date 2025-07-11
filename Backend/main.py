from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from routers.files import router as files_router
import logging
from config import CONFIG

# Configure logging
logging.basicConfig(
    level=getattr(logging, CONFIG.LOG_LEVEL),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

app = FastAPI(title="Dropbox Clone Backend")

# Enable CORS for frontend, configurable via environment variable
app.add_middleware(
    CORSMiddleware,
    allow_origins=[CONFIG.CORS_ORIGIN],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include file operation endpoints
app.include_router(files_router)

if __name__ == "__main__":
    logger.info("Starting FastAPI server")
    uvicorn.run(app, host="0.0.0.0", port=5001)