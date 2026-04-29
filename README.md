# VOIDGUARD

VOIDGUARD is a prototype autonomous security monitoring platform. It contains a simulated telemetry client, a FastAPI detection backend, a multi-agent risk scoring pipeline, PostgreSQL alert storage, Redis-based rate limiting and blocklisting, ChromaDB-backed threat memory, and a Next.js dashboard shell.

The project is designed as a local demo and development foundation for an AI-assisted cyber-defense system. It is not production-hardened yet, but the main components and data flow are already in place.

## What This Project Does

VOIDGUARD simulates security telemetry from an agent, encrypts that telemetry, sends it to a backend, analyzes the request for suspicious behavior, and records the resulting action.

At a high level:

```text
Python client agent
  -> generates simulated traffic
  -> encrypts telemetry with AES-256-GCM
  -> posts encrypted payloads to FastAPI

FastAPI backend
  -> rate-limits agents with Redis
  -> decrypts and validates telemetry
  -> scores traffic with multiple analysis agents
  -> stores alerts in PostgreSQL
  -> stores block decisions in Redis
  -> stores attack patterns in ChromaDB

Next.js dashboard
  -> intended frontend for viewing alerts and system state
```

## Repository Layout

```text
.
├── backend/              FastAPI API and detection pipeline
│   ├── agents/           Detection, memory, decision, and response agents
│   ├── api/              HTTP route modules
│   ├── core/             Database, Redis, security, and ChromaDB clients
│   ├── models/           SQLAlchemy and Pydantic models
│   ├── main.py           FastAPI app entry point
│   └── requirements.txt  Python backend dependencies
├── client/               Simulated telemetry sender
│   ├── agent.py          Client loop that sends encrypted payloads
│   ├── collector.py      Simulated traffic and system metric generator
│   ├── crypto.py         AES-GCM encryption helper
│   └── requirements.txt  Python client dependencies
├── dashboard/            Next.js frontend app
│   ├── src/app/          App router pages and styles
│   ├── Dockerfile        Production dashboard container
│   └── package.json      Frontend scripts and dependencies
├── docker-compose.yml    Full local stack orchestration
├── .env.example          Example runtime configuration
└── README.md             Project documentation
```

## Main Components

### Client Agent

The client in `client/agent.py` runs an infinite loop. Every two seconds it:

1. Generates simulated API traffic using `TelemetryCollector`.
2. Serializes the telemetry to JSON.
3. Encrypts the JSON with AES-256-GCM using `CryptoModule`.
4. Sends the encrypted payload to the backend ingest endpoint.

The generated traffic intentionally includes occasional anomalies, such as:

- SQL injection-like endpoint strings
- malformed auth tokens
- oversized request bodies
- suspicious user agents
- excessive headers

This gives the backend something meaningful to detect during local testing.

### Backend API

The backend is a FastAPI service exposed on port `8080`.

Important routes:

| Route | Method | Purpose |
| --- | --- | --- |
| `/health` | `GET` | Confirms the backend is online |
| `/api/v1/auth/login` | `POST` | Returns a JWT for the demo admin user |
| `/api/v1/ingest/` | `POST` | Accepts encrypted telemetry from agents |
| `/api/v1/alerts/` | `GET` | Returns recent alerts |
| `/docs` | `GET` | Interactive OpenAPI documentation |

### Detection Agents

The backend uses several small "agent" classes inside `backend/agents/`.

| Agent | File | Responsibility |
| --- | --- | --- |
| SentinelAgent | `sentinel.py` | Base64-decodes, decrypts, parses, and validates telemetry |
| AnalystAgent | `analyst.py` | Performs rule-based and Isolation Forest anomaly checks |
| OAuthAgent | `oauth.py` | Checks auth-token presence, shape, and suspicious access behavior |
| MemoryAgent | `memory.py` | Queries and stores similar attack patterns in ChromaDB |
| DecisionEngine | `decision.py` | Combines scores and chooses `ALLOW`, `ALERT`, or `BLOCK` |
| ResponseAgent | `response.py` | Writes alerts, blocks malicious IPs, and publishes alert events |

The final score is weighted like this:

```text
final_score = analyst_score * 0.5
            + oauth_score   * 0.3
            + memory_score  * 0.2
```

Default action thresholds:

| Score | Action |
| --- | --- |
| `< 40` | `ALLOW` |
| `>= 40` | `ALERT` |
| `>= 75` | `BLOCK` |

### Data Stores

| Store | Use |
| --- | --- |
| PostgreSQL | Persists alert records |
| Redis | Rate limits agents, stores temporary IP blocklist entries, publishes alert stream events |
| ChromaDB | Stores and queries previous attack-pattern memory |

### Dashboard

The dashboard is a Next.js app on port `3000`. It currently has project metadata, styling, and production Docker support, but the main page is still a starter screen. The intended next step is to connect it to:

- `/api/v1/auth/login`
- `/api/v1/alerts/`
- Redis stream updates, if real-time alert UI is added later

## Requirements

- Docker Compose, or Podman with Docker Compose compatibility
- Node.js 22+ for local dashboard development
- Python 3.11+ for local backend/client development

Docker Compose is the easiest way to run the project because it starts PostgreSQL, Redis, ChromaDB, backend, dashboard, and client together.

## Quick Start

Create a local environment file:

```bash
cp .env.example .env
```

Start the full stack:

```bash
docker compose up --build
```

Open these URLs:

- Dashboard: http://localhost:3000
- Backend health: http://localhost:8080/health
- API docs: http://localhost:8080/docs
- ChromaDB: http://localhost:8000

Stop the stack:

```bash
docker compose down
```

Stop the stack and delete stored data volumes:

```bash
docker compose down -v
```

## Environment Configuration

The project reads runtime configuration from `.env`.

Important values:

```env
PROJECT_NAME="VOIDGUARD"
API_V1_STR="/api/v1"

SECRET_KEY="change-this"
AES_KEY="64-hex-character-aes-key"

DATABASE_URL="postgresql+asyncpg://postgres:voidguard_pwd@db:5432/voidguard"

REDIS_HOST=redis
REDIS_PORT=6379
REDIS_PASSWORD=""

CHROMA_HOST=chromadb
CHROMA_PORT=8000
```

`AES_KEY` must be exactly 64 hexadecimal characters because AES-256 requires a 32-byte key.

Generate stronger local secrets:

```bash
openssl rand -hex 32
```

Use one generated value for `SECRET_KEY` and another generated value for `AES_KEY`.

## Running Individual Parts

### Infrastructure Only

Start only PostgreSQL, Redis, and ChromaDB:

```bash
docker compose up db redis chromadb
```

### Backend Locally

Run this from the project root after the infrastructure services are running:

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8080
```

### Client Locally

Run this from the project root while the backend is running:

```bash
cd client
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python agent.py
```

### Dashboard Locally

Run this from the project root:

```bash
cd dashboard
npm install
npm run dev
```

Then open:

```text
http://localhost:3000
```

## API Examples

Health check:

```bash
curl http://localhost:8080/health
```

Login with the demo admin account:

```bash
curl -X POST http://localhost:8080/api/v1/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin&password=admin"
```

Fetch recent alerts by replacing `TOKEN` with the returned access token:

```bash
curl http://localhost:8080/api/v1/alerts/ \
  -H "Authorization: Bearer TOKEN"
```

Watch backend logs:

```bash
docker compose logs -f backend
```

Watch client telemetry sender logs:

```bash
docker compose logs -f client
```

## Development Checks

Validate Docker Compose:

```bash
docker compose config
```

Check Python syntax:

```bash
python -m compileall backend client
```

Lint the dashboard:

```bash
cd dashboard
npm run lint
```

Build the dashboard:

```bash
cd dashboard
npm run build
```

## Security Notes

This project is currently demo-grade. Before using it outside local development, address these items:

- Replace the hardcoded `admin/admin` demo login.
- Validate JWTs on protected backend routes, not just bearer-token presence.
- Restrict CORS to trusted dashboard origins.
- Rotate `SECRET_KEY` and `AES_KEY`.
- Add database migrations with Alembic instead of creating tables automatically at startup.
- Add automated tests for ingest, scoring, auth, and alert retrieval.
- Avoid exposing database, Redis, and ChromaDB ports publicly in production.

## Current Limitations

- The dashboard is not fully wired into the backend alert API yet.
- The telemetry collector is simulated, not attached to real application traffic.
- The Isolation Forest model uses a tiny built-in baseline and is not trained on real data.
- ChromaDB memory uses simple text payloads and default embedding behavior.
- There is no user management system yet.

## Troubleshooting

Check running services:

```bash
docker compose ps
```

Check backend logs:

```bash
docker compose logs backend
```

If the backend is not healthy, confirm infrastructure services are healthy:

```bash
docker compose ps db redis chromadb
```

If the client reports connection failures, check:

```bash
curl http://localhost:8080/health
```

If encrypted telemetry fails to process, confirm the backend and client use the same `AES_KEY`.

If a port is already in use, change the left side of the port mapping in `docker-compose.yml`. Example:

```yaml
ports:
  - "8081:8080"
```

If you want a clean database and vector store:

```bash
docker compose down -v
docker compose up --build
```

## Suggested Next Upgrades

Good next steps for the project:

- Build the dashboard alert table and login flow.
- Add real JWT verification dependencies to protected routes.
- Add unit tests for each detection agent.
- Add integration tests for encrypted ingest.
- Add Alembic migrations.
- Add a WebSocket or Server-Sent Events endpoint for live dashboard alerts.
- Replace simulated telemetry with real collector integrations.

