# Dropbox Clone Backend

FastAPI backend for file storage with MongoDB (metadata) and MinIO (files). Supports `.txt`, `.jpg`, `.png`, `.json`.

## Software Requirements
- Python 3.8+
- Docker/Podman
- docker-compose
- pip

## Setup Project
1. **Navigate to Backend**:
   ```bash
   cd dropbox-clone/Backend
   ```

2. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure `.env`**:
   ```plaintext
   STORAGE_BACKEND=minio
   MINIO_ENDPOINT=localhost:9000
   MINIO_ACCESS_KEY=admin
   MINIO_SECRET_KEY=supersecret
   MINIO_BUCKET=myfiles
   MINIO_SECURE=False
   MONGODB_URI=mongodb://admin:supersecret@localhost:27017
   MONGODB_DATABASE=mydb
   LOG_LEVEL=INFO
   ```

4. **Start Services MongoDB and MinIO**:
   ```bash
   docker-compose up -d
   ```
   

5. **Run Server**:
  In Backend Folder run the following
   ```bash
   uvicorn main:app --host 0.0.0.0 --port 5001
   ```

6. **View API Docs**:
   Visit `http://localhost:5001/docs` for Swagger UI.

## Additional Information
- **Endpoints**:
  - `GET /api/health`: System health check
  - `POST /api/upload`: Upload files
  - `GET /api/files`: List files
  - `GET /api/download/{file_id}`: Download file
- **Supported Files**: `.txt`, `.jpg`, `.png`, `.json`
- **Storage**: MinIO (default) or local (`STORAGE_BACKEND=local`)