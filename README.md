# FireWatch AI

Early fire/smoke detection MVP from camera footage.

## Problem statement

Fires cause much more damage when detection happens late — many sites (farms, warehouses,
small businesses) have cameras already but no automated way to flag flame or smoke early.

## Solution

Upload an image or video and FireWatch AI flags flame-coloured and smoke-like regions,
with a confidence score, logging every check as an auditable alert history.

## Features

- Fire detection (flame-colour HSV thresholding)
- Smoke detection (low-saturation, high-texture haze regions)
- Configurable detection sensitivity
- Alert history with confidence scores, CSV export
- Demo mode using bundled sample images

## Architecture

```text
frontend (React/Vite/TS/Tailwind)  ->  backend (FastAPI)  ->  SQLite
                                              |
                                     HSV colour-threshold fire/smoke heuristic
```

## Technology stack

Python, FastAPI, SQLAlchemy, SQLite, OpenCV; React, TypeScript, Vite, Tailwind CSS.

## Folder structure

```text
firewatch-ai/
├── backend/
│   ├── app/          # FastAPI app, detection heuristic
│   ├── demo/           # Bundled sample images
│   └── tests/
├── frontend/
│   └── src/              # Landing page + dashboard
├── docker-compose.yml
└── README.md
```

## Installation

```bash
cd backend
python -m venv venv && venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
```

```bash
cd frontend && npm install
```

## Environment variables

`SENSITIVITY_PCT` (minimum fire/smoke pixel coverage to trigger an alert), `UPLOAD_DIR`,
`MAX_UPLOAD_MB`, `CORS_ORIGINS` — see `backend/.env.example`.

## Running locally

```bash
# Terminal 1
cd backend && venv\Scripts\activate && uvicorn app.main:app --reload
# Terminal 2
cd frontend && npm run dev
```

Open http://localhost:5173. Docker: `docker compose up --build`.

## Demo instructions

Click **Run demo sample** — analyzes one of the bundled sample images (a mix of wildfire
smoke and clear-forest photos, Wikimedia Commons, CC-licensed) so you can see both an
alert and a clean result. Upload your own image or short video to try other footage.

## API documentation

Docs at `/docs`. Key endpoints: `POST /api/analyze` (image or video), `POST
/api/analyze/demo`, `GET /api/events`, `GET /api/events/export`, `GET /api/dashboard/summary`.

## Database

SQLite: `alert_events` (fire/smoke flags, coverage %, confidence).

## Security considerations

Upload size validated server-side, CORS restricted, no secrets in source. No admin auth
in this MVP.

## Privacy considerations

Footage may incidentally capture people or property. No identity recognition is performed
by this system.

## Limitations — read before demoing

**This system is an early-warning prototype and must not replace certified fire detection
systems.** Detection is HSV colour thresholding (fire) plus a texture/brightness heuristic
(smoke) — both are classical, precedented baseline techniques, not deep-learning models:

- Fire detection will false-positive on other orange/red/yellow objects (sunsets, orange
  clothing, warning signage) and false-negative on fires whose flame colour falls outside
  the configured HSV ranges.
- Smoke detection is the noisier of the two — grey, textured surfaces (fog, dust, certain
  fabrics) can trigger it; the sensitivity threshold is set higher for smoke than fire to
  partly compensate.
- No motion-based confirmation — a single still image showing fire-like colour will alert
  the same as a live flame.

## Business model

**Target customers**: warehouses, farms, factories, schools, small businesses,
construction sites.

**Revenue**: monitoring subscription, camera + software bundle, installation service,
enterprise monitoring.

## Future improvements

- Motion-based confirmation (frame-differencing) to reduce false positives from static
  fire-coloured objects
- Deep-learning fire/smoke classifier trained on real incident footage
- SMS/email alert integration
- Multi-camera site dashboard

## Screenshots

Run locally (see "Running locally") and click **Run demo sample** on `/app`.
