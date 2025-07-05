# Dropbox Clone

A file storage application with a FastAPI backend using MongoDB for metadata and MinIO for file storage, paired with a React/TypeScript/Tailwind CSS frontend. Supports uploading, listing, viewing, downloading files (`.txt`, `.jpg`, `.png`, `.json`).

## Software Requirements
- Docker/Podman
- docker-compose/Podman-compose
- Python 3.8+
- Node.js 16+

## Setup Instructions

### 1. Backend Setup
Navigate to the `Backend` directory and follow the setup steps:
```bash
cd Backend
```
Refer to `Backend/README.md` for detailed instructions, including installing dependencies, configuring environment variables, starting services, and running the server.

### 2. Frontend Setup
Navigate to the `Frontend` directory and follow the setup steps:
```bash
cd Frontend
```
Refer to `Frontend/README.md` for detailed instructions, including installing dependencies and running the application.

### 3. Verify
- Ensure the backend is running at `http://localhost:5001`.
- Open `http://localhost:3000` in your browser to access the frontend.

