# Gemini Banking Bot

## Tech stack

- Frontend: React, TypeScript, Vite, MUI (Material UI)
- Backend: Python, Flask, Waitress
- AI: google-genai (LLM integration)
- DevOps: Docker, Docker Compose
- Extras: python-dotenv for configuration, ESLint + TypeScript for frontend quality

## Engineering decisions

- Waitress used for a simple, production-suitable WSGI server.
- Environment variables are managed with `.env` files and `python-dotenv` for clear separation between prod and dev settings.
- Dockerized backend to keep runtime predictable and reproducible.

## Project structure

- client/ — React + TypeScript front-end (Vite) with UI components and an API client in `client/src/api`.
- server/ — Python Flask service, Dockerfile, and Docker Compose configuration. Key files:
  - `wsgi.py` — Flask app and Waitress startup hook
  - `service.py` — business logic and LLM orchestration
  - `request_dtos.py` — DTOs used to serialize/deserialize requests/responses
  - `requirements.txt` — Python dependencies
  - `Dockerfile` — server image build
  - `docker-compose.yml` — compose file for local/container orchestration

## Environment variables

The server expects environment configuration via a file copied into the image as `.env` (the Dockerfile copies `.env-prod` into `/app/.env`). There is a placeholder `.env-sample` file in the repo root; use it to create your own local `.env` before running.

Typical variables you may need (examples - DO NOT store secrets in repo):

- GEMINI_BANKING_ENVIRONMENT=dev|prod
- GOOGLE_API_KEY or other credentials required by `google-genai`

## Running locally (development)

Frontend (from repo root):

1. Open a terminal and run:

```powershell
cd client
npm install
npm run dev
```

2. The Vite dev server will start (port printed in the console). The client is configured to call the server API; adjust proxy settings if needed.

Backend (from `server/`):

1. Create a local env file (for example `server/.env`) and populate required keys (see Environment variables above).
2. From the `server` folder, create a virtualenv and install dependencies or use the Docker flow below.

```powershell
cd server
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python wsgi.py
```

The application uses Waitress on port 8080 in non-prod. In production the container runs Waitress.

## Running with Docker (recommended for consistent environment)

From the `server` folder (PowerShell):

```powershell
cd server
docker build -t gemini-banking-server:latest .
docker compose -f docker-compose.yml up -d

# stop
docker compose down
```

## API overview

- POST /account/prompt — Accepts a prompt and uses the LLM to decide whether to call deposit/withdrawal functions. Returns a structured JSON response including whether a function was called and the resulting balance or messages.
- POST /account/action — Accepts a direct deposit or withdrawal request (DTO) and returns the new balance or error code.

Example DTOs and serialization are implemented in `server/request_dtos.py`.
