from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from routers.files import router as files_router

app = FastAPI(title="Dropbox Clone Backend")

# Enable CORS for frontend at http://localhost:3000
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
    uvicorn.run(app, host="0.0.0.0", port=5001)