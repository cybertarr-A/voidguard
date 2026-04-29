# VOIDGUARD

VOIDGUARD is a local autonomous security-monitoring prototype. It simulates encrypted telemetry from a client agent, ingests it through a FastAPI backend, scores requests with a multi-agent detection pipeline, records decisions in PostgreSQL, keeps block/rate-limit state in Redis, stores threat memory in ChromaDB, and displays results in a Next.js dashboard.

It is built for safe local testing. The included threat smoke test sends synthetic malicious-looking telemetry into VOIDGUARD itself; it does not attack any external target.

## What Works

- Encrypted telemetry ingest with AES-256-GCM
- FastAPI backend with health, auth, ingest, and alert APIs
- Redis rate limiting and temporary IP blocklist
- PostgreSQL alert persistence
- ChromaDB-backed threat-pattern memory
- Rule-based, OAuth-token, anomaly, and memory scoring
- Next.js dashboard with login, health status, summary cards, and alert table
- Repeatable smoke test that proves a synthetic threat is detected and blocked

## Architecture

```text
client/
  simulated telemetry
  AES-GCM encryption
  POST /api/v1/ingest/

backend/
  FastAPI API
  SentinelAgent -> decrypts and validates telemetry
  AnalystAgent  -> rule checks + Isolation Forest anomaly scoring
  OAuthAgent    -> auth-token behavior scoring
  MemoryAgent   -> ChromaDB similarity scoring
  DecisionEngine -> ALLOW / ALERT / BLOCK
  ResponseAgent -> PostgreSQL alert + Redis blocklist + Redis stream

dashboard/
  Next.js UI
  backend health check
  admin login
  alerts table

infra/
  PostgreSQL
  Redis
  ChromaDB
```

## Repository Layout

```text
.
├── backend/
│   ├── agents/                 Detection and response agents
│   ├── api/                    FastAPI route modules
│   ├── core/                   DB, Redis, ChromaDB, and crypto helpers
│   ├── models/                 SQLAlchemy and Pydantic models
│   ├── scripts/
│   │   └── threat_smoke_test.py
│   ├── main.py
│   └── requirements.txt
├── client/
│   ├── agent.py                Simulated telemetry sender
│   ├── collector.py            Traffic and metric generator
│   ├── crypto.py               AES-GCM encryption helper
│   └── requirements.txt
├── dashboard/
│   ├── src/app/page.tsx        VOIDGUARD dashboard
│   ├── src/app/globals.css
│   ├── Dockerfile
│   └── package.json
├── docker-compose.yml
├── .env.example
└── README.md
```

## Services

| Service | Purpose | URL / Port |
| --- | --- | --- |
| dashboard | Next.js security dashboard | http://localhost:3000 |
| backend | FastAPI backend | http://localhost:8080 |
| API docs | OpenAPI docs | http://localhost:8080/docs |
| PostgreSQL | Alert database | localhost:5432 |
| Redis | Rate limits, blocklist, alert stream | localhost:6380 on host, `redis:6379` inside Compose |
| ChromaDB | Threat memory vector store | http://localhost:8000 |
| client | Simulated telemetry sender | Compose service |

## Requirements

Recommended:

- Docker Compose, or Podman with Docker Compose compatibility

Optional local development:

- Node.js 22+ for dashboard work
- Python 3.11 for backend/client work

Do not install backend requirements into a Python 3.13 environment. The backend pins `scikit-learn==1.4.2`, which is intended for Python 3.11 here. On Kali/Debian with Python 3.13, use Docker Compose for the backend.

## Environment

Create a local env file:

```bash
cp .env.example .env
```

For local Docker Compose, Redis must use the Compose service name:

```env
REDIS_HOST=redis
REDIS_PORT=6379
REDIS_HOST_PORT=6380
REDIS_PASSWORD=""
```

ChromaDB should also use the Compose service name:

```env
CHROMA_HOST=chromadb
CHROMA_PORT=8000
```

Generate stronger secrets for local use:

```bash
openssl rand -hex 32
```

Use one generated value for `SECRET_KEY` and another for `AES_KEY`. `AES_KEY` must be exactly 64 hex characters.

## Run The Full Project

From the project root:

```bash
docker compose down
docker compose up --build
```

Wait for the services to become healthy. Then open:

```text
http://localhost:3000
```

Login to the dashboard:

```text
username: admin
password: admin
```

The dashboard shows backend health, alert totals, blocked/suspicious counts, average risk, and recent decisions.

## Verify Basic Health

Backend:

```bash
curl http://localhost:8080/health
```

Expected:

```json
{"status":"VOIDGUARD Core is online"}
```

ChromaDB:

```bash
curl http://localhost:8000/api/v1/heartbeat
```

Redis from host:

```bash
redis-cli -p 6380 ping
```

Client logs:

```bash
docker compose logs -f client
```

Expected client output:

```text
[+] Successfully sent payload
```

## Test Threat Detection

Run the built-in smoke test while the stack is running:

```bash
docker compose exec backend python scripts/threat_smoke_test.py
```

The script sends synthetic malicious telemetry through the real encrypted ingest endpoint. The sample includes:

- SQL-injection-like endpoint text
- malformed auth token
- excessive headers
- oversized body
- high CPU and memory metrics
- fresh test IP on every run

Expected output:

```text
Ingest accepted for manual-threat-test-...
Detection result:
{
  "risk_score": 100.0,
  "action_taken": "BLOCK",
  ...
}
Threat smoke test passed: sample was detected and blocked.
```

Refresh the dashboard and click `Reload`. You should see the `BLOCK` event.

## API Usage

Login:

```bash
curl -X POST http://localhost:8080/api/v1/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin&password=admin"
```

Fetch alerts:

```bash
TOKEN="paste_access_token_here"

curl http://localhost:8080/api/v1/alerts/ \
  -H "Authorization: Bearer $TOKEN"
```

API docs:

```text
http://localhost:8080/docs
```

## How Detection Is Scored

The backend combines three risk scores:

```text
final_score = analyst_score * 0.5
            + oauth_score   * 0.3
            + memory_score  * 0.2
```

Actions:

| Score | Action |
| --- | --- |
| `< 40` | `ALLOW` |
| `>= 40` | `ALERT` |
| `>= 75` | `BLOCK` |

On `BLOCK`, VOIDGUARD:

- writes an alert to PostgreSQL
- adds the IP to Redis for 24 hours
- publishes an alert payload to a Redis stream
- stores the pattern in ChromaDB memory

## Useful Commands

Start:

```bash
docker compose up --build
```

Start in background:

```bash
docker compose up -d --build
```

Stop:

```bash
docker compose down
```

Stop and delete volumes:

```bash
docker compose down -v
```

View service status:

```bash
docker compose ps
```

View backend logs:

```bash
docker compose logs -f backend
```

View dashboard logs:

```bash
docker compose logs -f dashboard
```

Rebuild only backend:

```bash
docker compose build backend
docker compose up -d backend
```

Copy updated smoke test into a running backend container without rebuild:

```bash
docker compose cp backend/scripts/threat_smoke_test.py backend:/app/scripts/threat_smoke_test.py
```

## Local Development

Docker Compose is preferred. If you run services locally, use Python 3.11.

Backend:

```bash
cd backend
python3.11 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8080
```

Client:

```bash
cd client
python3.11 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
python agent.py
```

Dashboard:

```bash
cd dashboard
npm install
npm run dev
```

Checks:

```bash
docker compose config
python -m py_compile backend/scripts/threat_smoke_test.py
cd dashboard && npm run lint && npm run build
```

## Troubleshooting

### Dashboard still shows the default Next.js page

Rebuild/restart the dashboard:

```bash
docker compose build dashboard
docker compose up -d dashboard
```

### Redis port 6379 is already in use

VOIDGUARD publishes Redis on host port `6380` by default:

```env
REDIS_HOST_PORT=6380
```

Inside Compose, keep:

```env
REDIS_HOST=redis
REDIS_PORT=6379
```

### Backend tries to connect to Redis Cloud

Your `.env` is wrong for local Compose. Use:

```env
REDIS_HOST=redis
REDIS_PORT=6379
REDIS_PASSWORD=""
```

Then restart:

```bash
docker compose down
docker compose up --build
```

### Pylance says `chromadb` cannot be resolved

That warning is from your editor interpreter, not Docker. Either:

- ignore it when running through Docker, or
- select a Python 3.11 venv with `backend/requirements.txt` installed.

### `scikit-learn` fails to install

You are probably using Python 3.13. Use Docker Compose, or create a Python 3.11 venv.

### Smoke test says no alert was recorded

First check logs:

```bash
docker compose logs --tail=120 backend
```

If the backend says it blocked the test IP, detection worked. Rebuild/copy the latest smoke test script:

```bash
docker compose build backend
docker compose up -d backend
```

## Security Notes

VOIDGUARD is a prototype. Before real deployment:

- replace the demo `admin/admin` credentials
- add proper user management
- rotate `SECRET_KEY` and `AES_KEY`
- restrict CORS to trusted origins
- add Alembic migrations
- add automated tests
- avoid exposing PostgreSQL, Redis, or ChromaDB publicly
- review the detection rules against real telemetry

## Current Limitations

- The client sends simulated telemetry, not real production traffic.
- The ML model uses a small built-in baseline.
- ChromaDB may download its default embedding model on first use.
- The dashboard polls alerts manually instead of streaming live updates.
- The project is intended for local demo and development, not production operation.

