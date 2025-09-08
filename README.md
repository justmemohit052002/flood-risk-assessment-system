Flood Analyser App
===================

Analyse flood risk from an uploaded terrain image using Google Gemini, and present a clear risk summary, key metrics, AI analysis, and safety recommendations. Built with Next.js + TypeScript (frontend) and FastAPI (backend).

Features
--------
- Image upload with preview and validation (image/*, up to 10MB)
- AI-powered analysis (Google Gemini) with graceful fallback to simulated results
- Risk level, description, elevation, distance from water
- AI Analysis text (what the model “sees” in the image)
- Actionable recommendations list
- Clean, responsive UI with shadcn/ui components

Architecture
------------
- Frontend: Next.js (App Router) + TypeScript in `app/page.tsx`
  - Calls the backend endpoint to analyse images
  - Displays results with icons, badges, and structured sections
- Backend: FastAPI in `backend/main.py`
  - `POST /api/analyze/image` accepts an image and prompts Google Gemini
  - Parses the model output into a stable JSON shape
  - Falls back to a simulated assessment if the AI call fails

Tech Stack
---------
- Frontend: Next.js, React, TypeScript, shadcn/ui, Tailwind CSS
- Backend: FastAPI, Uvicorn, Python 3.10+
- AI: Google Gemini via `google-generativeai`

Prerequisites
-------------
- Node.js 18+
- Python 3.10+
- A Google Gemini API key set as `GEMINI_API_KEY` (fallback `GOOGLE_API_KEY`)

Setup
-----
1) Backend

```bash
cd backend
python -m venv .venv
. .venv/Scripts/activate   # Windows PowerShell: .venv\Scripts\Activate.ps1
pip install -r requirements.txt

# Set your Gemini key in the environment (example Windows PowerShell):
$env:GEMINI_API_KEY = "YOUR_KEY_HERE"

# Run the API
python start.py
```

The API starts at `http://localhost:8001` with docs at `http://localhost:8001/docs`.

2) Frontend

```bash
npm install
npm run dev
```

Open `http://localhost:3000` in your browser.

Configuration
-------------
- Backend environment variables
  - `GEMINI_API_KEY`: Google AI API key (preferred)
  - `GOOGLE_API_KEY`: Optional fallback
- Frontend
  - Uses `API_BASE_URL = http://localhost:8001` (configured in `app/page.tsx`)
  - Optional: If you plan to enable maps later, set `NEXT_PUBLIC_GOOGLE_MAPS_API_KEY` in `.env.local` and wire the map loader accordingly

API
---
- `POST /api/analyze/image`
  - Body: multipart/form-data with field `file` (image)
  - Response (example):

```json
{
  "success": true,
  "risk_level": "Medium",
  "description": "Analysis completed",
  "recommendations": ["Monitor weather", "Stay informed"],
  "elevation": 52.3,
  "distance_from_water": 842.1,
  "ai_analysis": "River visible to the east...",
  "message": "Image analysis completed successfully"
}
```

Development Notes
-----------------
- The Coordinates tab UI exists but coordinate analysis is not yet implemented on the backend. The image flow is complete.
- The frontend normalises `recommendations` to an array and reads AI text from `analysis` or `ai_analysis` for compatibility.

Troubleshooting
---------------
- “AI Analysis” empty: Ensure the backend is running and `GEMINI_API_KEY` is set. The backend returns `ai_analysis` even when falling back to simulation.
- CORS/Network errors: Confirm the backend is at `http://localhost:8001` and accessible from the browser.
- Large files rejected: Keep images under 10MB.

License
-------
MIT

This is a [Next.js](https://nextjs.org) project bootstrapped with [`create-next-app`](https://nextjs.org/docs/app/api-reference/cli/create-next-app).

## Getting Started

First, run the development server:

```bash
npm run dev
# or
yarn dev
# or
pnpm dev
# or
bun dev
```

Open [http://localhost:3000](http://localhost:3000) with your browser to see the result.

You can start editing the page by modifying `app/page.tsx`. The page auto-updates as you edit the file.

This project uses [`next/font`](https://nextjs.org/docs/app/building-your-application/optimizing/fonts) to automatically optimize and load [Geist](https://vercel.com/font), a new font family for Vercel.

## Learn 
