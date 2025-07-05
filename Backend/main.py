from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from routers.files import router as files_router
import logging
from config import LOG_LEVEL

# Configure logging
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

app = FastAPI(title="Dropbox Clone Backend")

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include file operation endpoints
app.include_router(files_router)

if __name__ == "__main__":
    logger.info("Starting FastAPI server")
    uvicorn.run(app, host="0.0.0.0", port=5001)