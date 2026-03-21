# Grok ZeroPoint - Next.js Frontend

Chat UI for the RAG backend. Matches the Grok ZeroPoint design with dark theme, sidebar, and mode toggles.

## Setup

```bash
cd frontend
npm install
```

## Run

1. **Start the Flask backend** (from project root):
   ```bash
   cd model
   python app.py
   ```
   Backend runs on `http://localhost:5000`.

2. **Start the Next.js dev server**:
   ```bash
   npm run dev
   ```
   Frontend runs on `http://localhost:3000`.

## Features

- **Think Bigger** (k=5): Default retrieval
- **Deep Search** (k=10): More context chunks
- **Brainstorm Mode** (k=15): Broader exploration

The `/api/ask` and `/api/health` routes are proxied to the Flask backend via Next.js rewrites.
