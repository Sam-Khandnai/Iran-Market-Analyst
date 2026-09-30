# 📈 Iran Market Analyst — Frontend

React + TypeScript dashboard for the Iran Market Analyst project. Provides a ChatGPT-style dark UI with live streaming analysis for **Tehran Stock Exchange (TSETMC)** symbols, plus **gold, coins, and currency** tracking.

> This is the frontend half of the project. The backend (FastAPI + LangGraph + deterministic analysis engines) lives one level up, in the parent `market-analyst/` folder. See the [root README](../README.md) for backend setup.

---

## 📋 Table of Contents

- [Features](#-features)
- [Tech Stack](#-tech-stack)
- [Prerequisites](#-prerequisites)
- [Setup](#-setup)
- [Environment Variables](#-environment-variables)
- [Running the Dev Server](#-running-the-dev-server)
- [Building for Production](#-building-for-production)
- [Project Structure](#-project-structure)
- [How It Works](#-how-it-works)
- [Troubleshooting](#-troubleshooting)

---

## ✨ Features

- 🌗 **Dark theme UI** inspired by ChatGPT / Claude, fully RTL (right-to-left) for Persian text
- ⚡ **Real-time streaming** — analysis steps (data fetch → technical → fundamental → risk → decision → explanation) appear live as the backend graph executes, via Server-Sent Events (SSE)
- 📊 **Stock analysis tab** — search any TSETMC symbol or pick from popular presets (فولاد, فملی, وبملت, etc.)
- 🥇 **Gold & Coin tab** — 18k/24k gold, world ounce, Emami coin, Bahar Azadi, half/quarter coins
- 💵 **Currency tab** — USD, EUR, AED with historical trend
- 📈 **Interactive price charts** (via Recharts) with SMA20/SMA50 overlays and volume bars
- 🎯 **Signal badges** with semantic colors (green/yellow/red) for buy/watch/sell research signals
- 🧾 **Evidence & risk factor pills** — transparent, deterministic reasoning shown alongside the AI-generated summary
- ✍️ **Typewriter effect** for the AI explanation text

---

## 🛠 Tech Stack

| Layer | Technology |
|---|---|
| Framework | React 18 + TypeScript |
| Build tool | Vite |
| Charts | Recharts |
| Icons | Lucide React |
| Styling | Plain CSS (custom dark theme, no framework) |
| Data fetching | Native `fetch` + async generators for SSE streaming |

No state management library, no CSS framework — kept intentionally lightweight.

---

## 💻 Prerequisites

- **Node.js** 18+ — [nodejs.org](https://nodejs.org/)
- **npm** (comes with Node.js)
- The **backend** running locally (see [root README](../README.md)) — the frontend has nothing to show without it

Check your versions:
```bash
node --version
npm --version
```

---

## 🚀 Setup

From the `market-analyst/frontend` directory:

```bash
npm install
```

This installs React, Recharts, Lucide React, and dev dependencies (Vite, TypeScript).

---

## 🔐 Environment Variables

Create a `.env` file in this directory (`market-analyst/frontend/.env`):

```dotenv
VITE_API_URL=http://localhost:8000
```

This tells the frontend where the FastAPI backend is running. Change it if your backend runs on a different host/port.

> All Vite env vars must be prefixed with `VITE_` to be exposed to the browser — this is a Vite requirement, not specific to this project.

---

## ▶️ Running the Dev Server

Make sure the backend is already running (see root README), then:

```bash
npm run dev
```

Vite will print a local URL, typically:

```
➜  Local:   http://localhost:5173/
```

Open that in your browser. Hot-reload is enabled — any file change updates the page instantly.

---

## 📦 Building for Production

```bash
npm run build
```

Output goes to `dist/`. Preview the production build locally:

```bash
npm run preview
```

To deploy, serve the contents of `dist/` with any static file host (Nginx, Vercel, Netlify, etc.), and make sure `VITE_API_URL` points to your deployed backend before building.

---

## 📁 Project Structure

```
frontend/
├── src/
│   ├── main.tsx                    # React entry point
│   ├── App.tsx                     # Root component, tab routing (stock/gold/currency)
│   ├── api.ts                      # All backend HTTP/SSE calls
│   ├── types.ts                    # TypeScript interfaces + popular symbol/asset lists
│   ├── styles/
│   │   └── global.css              # Dark theme, RTL layout, all component styles
│   └── components/
│       ├── SearchBar.tsx           # Symbol input + analyze button
│       ├── PopularSymbols.tsx      # Clickable stock symbol chips
│       ├── AssetTabs.tsx           # Stock / Gold & Coin / Currency tab switcher
│       ├── AssetGrid.tsx           # Asset picker + analyze flow (gold/coin/currency)
│       ├── AssetAnalysisView.tsx   # Asset analysis result display
│       ├── ProgressSteps.tsx       # Live streaming step indicator
│       ├── ScoreCard.tsx           # Technical/Fundamental/Market score cards
│       ├── SignalBadge.tsx         # Color-coded signal + confidence badge
│       ├── AnalysisSummary.tsx     # AI explanation with typewriter effect
│       ├── EvidenceList.tsx        # Key factors & risk pills
│       └── PriceChart.tsx          # Recharts price/SMA/volume chart
├── index.html
├── package.json
├── tsconfig.json
├── vite.config.ts
└── .env                            # you create this (see above)
```

---

## ⚙️ How It Works

1. User picks a stock symbol (or gold/currency asset) and clicks **Analyze**.
2. For stocks, the frontend opens a streaming `POST /v1/analyze/stream` connection. The backend runs a LangGraph pipeline and emits one SSE event per completed node (`data`, `technical`, `fundamental`, `market_context`, `news`, `risk`, `decision`, `explanation`).
3. `ProgressSteps` renders each node as it completes; the final `explanation` event carries the full structured report.
4. For gold/coin/currency, the frontend calls `GET /v1/assets/{key}/analyze`, which is a single (non-streaming) request returning the full analysis in one response — no intermediate steps to show.
5. All scores, signals, and evidence in the UI come directly from the backend's **deterministic engines**. The only AI-generated part is the prose summary text (`report.summary` / `report.signal.summary`) — everything else is math, not a language model guess.

---

## 🐛 Troubleshooting

### White/blank page, no errors in terminal

Open the browser console (`F12` → Console tab) — Vite build errors and runtime errors only show there, not in the terminal.

### "Network error" / fetch failures

1. Confirm the backend is running: visit `http://localhost:8000/health` — should return `{"status":"ok"}`
2. Confirm `.env` has the correct `VITE_API_URL`
3. Check for CORS errors in the browser console — the backend must have this frontend's origin allowed (already configured for `localhost:5173` by default)

### Streaming stalls or shows an error mid-analysis

Check the backend terminal logs — a failed TSETMC request, a database connection issue, or an LLM provider error will show there. The frontend surfaces the error message it receives, but the root cause is almost always on the backend side.

### Chart shows "not enough history yet" for gold/coin/currency

Run the backfill script from the backend root once:
```bash
uv run python scripts/backfill_asset_history.py
```

### Changes to `.tsx` files don't show up

Make sure `npm run dev` is actually running and watching this folder — restart it if you renamed/moved the `frontend` folder while it was running.

---

## 📜 License

Part of the Iran Market Analyst project. See the [root README](../README.md) for license and disclaimer.
