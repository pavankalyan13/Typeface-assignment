# Dropbox Clone Frontend

## Software Requirements
- Node.js 16+
- npm

## Setup Project
1. **Navigate to Frontend**:
   ```bash
   cd dropbox-clone/Frontend
   ```

2. **Install Dependencies**:
   ```bash
   npm i
   ```

3. **Configure `.env`**:
   ```plaintext
   REACT_APP_API_BASE_URL=http://localhost:5001/api
   ```

4. **Start Services**:
   Ensure the backend is running at `http://localhost:5001` by following the `Backend/README.md` instructions.

5. **Run Frontend**:
   In the Frontend folder, run the following:
   ```bash
   npm run build
   npm run start
   ```

6. **View Application**:
   Visit `http://localhost:3000` for the frontend interface.