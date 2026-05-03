# TaskFlow

TaskFlow is a full-stack task and project management app with user authentication, role-aware project access, and task assignment workflows.

## What it does
- User signup and login with JWT-based auth.
- Create and manage projects.
- Add/remove project members.
- Create, update, and delete tasks inside projects.
- Enforce access control (owner/member rules) at API level.

## Tech stack
- Frontend: React + Vite + Tailwind CSS
- Backend: FastAPI + SQLAlchemy
- Database: PostgreSQL
- Auth: JWT + bcrypt password hashing
- Deployment: Nginx + Uvicorn + systemd (EC2)

## Project structure
- `frontend/` → React UI and API client
- `backend/` → FastAPI app, routers, models, schemas, auth

## What was learned
- Designing end-to-end auth flow (signup/login/token usage).
- Building permission checks at route level for secure multi-user access.
- Structuring CRUD APIs with SQLAlchemy models and Pydantic schemas.
- Debugging real deployment issues (DNS, SSL, reverse proxy, service startup).
- Handling password hashing edge cases and dependency compatibility in production.

## Run locally (quick)
1. Backend
   - `cd backend`
   - `python -m venv .venv && .venv\Scripts\activate` (Windows) or `source .venv/bin/activate` (Linux)
   - `pip install -r requirements.txt`
   - Set `DATABASE_URL`
   - `uvicorn app.main:app --reload`
2. Frontend
   - `cd frontend`
   - `npm install`
   - `npm run dev`

## Note
For production, configure environment variables (`DATABASE_URL`, `JWT_SECRET_KEY`) and use HTTPS behind Nginx.