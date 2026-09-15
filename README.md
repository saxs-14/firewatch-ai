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
                            MobileNetV2 fire/smoke/neutral classifier (trained)
                                  + HSV colour-threshold heuristic (ensemble)
```

## Technology stack

Python, FastAPI, SQLAlchemy, SQLite, OpenCV, PyTorch/TorchVision; React, TypeScript, Vite,
Tailwind CSS.

## Folder structure

```text
firewatch-ai/
├── backend/
│   ├── app/
│   │   └── ml_model/  # Trained TorchScript classifier (firewatch_classifier.pt)
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

- **API key required on every endpoint except `/api/health`.** Set `API_KEY` (backend
  `.env`) and `VITE_API_KEY` (frontend `.env`) to the same value before deploying anywhere
  reachable outside your own machine — the default (`dev-local-key-change-me`) is for
  local development only. Single-tenant "licensed instance" model, not per-user accounts.
- Rate limiting (15 req/60s/IP) on `/api/analyze*`.
- Upload size validated server-side, CORS restricted, no secrets in source.

## Privacy considerations

Footage may incidentally capture people or property. No identity recognition is performed
by this system.

## Limitations — read before demoing

**This system is an early-warning prototype and must not replace certified fire detection
systems.** Detection combines a trained model with the original HSV heuristic:

- **A MobileNetV2 transfer-learning classifier** (frozen ImageNet backbone + trained
  classifier head) fine-tuned on the DeepQuestAI Fire-Smoke-Dataset (2,700 images,
  fire/smoke/neutral), reaching 94.8% held-out validation accuracy. It predicts a single
  class per frame, so a frame showing both fire and smoke together will only register as
  whichever the model judges dominant — the HSV coverage percentages (below) still report
  both independently.
- **HSV colour thresholding (fire) plus a texture/brightness heuristic (smoke)** — the
  original classical baseline — still runs alongside the model and can independently
  trigger an alert. An alert fires if *either* signal detects something, which trades a
  higher false-positive rate for a lower chance of missing a real fire/smoke event.
  Fire detection will still false-positive on other orange/red/yellow objects (sunsets,
  orange clothing, warning signage); smoke detection is the noisier of the two (grey,
  textured surfaces like fog or dust can trigger it).
- No motion-based confirmation — a single still image showing fire-like colour or the
  model's fire class will alert the same as a live flame.

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
