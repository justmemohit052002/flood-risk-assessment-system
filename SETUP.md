# Flood Detection App Setup Guide

## Prerequisites
- Node.js (v18 or higher)
- Python (v3.8 or higher)
- pip (Python package manager)

## Setup Instructions

### 1. Frontend Setup (Next.js)
```bash
# Install dependencies
npm install

# Start the development server
npm run dev
```
The frontend will run on `http://localhost:3000`

### 2. Backend Setup (FastAPI)
```bash
# Navigate to backend directory
cd backend

# Install Python dependencies
pip install -r requirements.txt

# Start the backend server
python main.py
```
The backend will run on `http://localhost:8000`

### 3. Environment Configuration
Create a `.env.local` file in the root directory with:
```
GOOGLE_API_KEY=your_google_ai_api_key_here
NEXT_PUBLIC_GOOGLE_MAPS_API_KEY=your_google_maps_api_key_here
```

### 4. API Keys Setup

#### Google AI API Key (Required for flood analysis)
1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Create a new API key
3. Add it to your `.env.local` file as `GOOGLE_API_KEY`

#### Google Maps API Key (Optional for interactive map)
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Enable Maps JavaScript API
3. Create credentials (API key)
4. Add it to your `.env.local` file as `NEXT_PUBLIC_GOOGLE_MAPS_API_KEY`

## Features
- **Coordinate Analysis**: Enter latitude/longitude for flood risk assessment
- **Image Analysis**: Upload terrain images for AI-powered analysis
- **Real-time Results**: Get detailed risk assessments with recommendations
- **Interactive Map**: View locations on Google Maps (when API key is configured)

## API Endpoints
- `POST /analyze-coordinates`: Analyze flood risk by coordinates
- `POST /analyze-image`: Analyze flood risk from terrain images
- `GET /`: Health check endpoint

## Troubleshooting
- Make sure both frontend and backend are running
- Check that your API keys are correctly set in `.env.local`
- Ensure CORS is properly configured (already set up in backend)
- Check browser console for any JavaScript errors

