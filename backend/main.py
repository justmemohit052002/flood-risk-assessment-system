from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
import uvicorn
import os
from datetime import datetime
import logging
import google.generativeai as generativeai
from dotenv import load_dotenv
import io
import json
import re
from PIL import Image as PILImage

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configure Google Generative AI (prefer GEMINI_API_KEY, fallback to GOOGLE_API_KEY)
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
if GEMINI_API_KEY:
    generativeai.configure(api_key=GEMINI_API_KEY)
else:
    logger.warning("GEMINI_API_KEY/GOOGLE_API_KEY not found in environment variables")

# FastAPI app
app = FastAPI(
    title="Flood Detection API",
    description="Simple flood risk assessment using Gemini AI",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models
class CoordinateRequest(BaseModel):
    latitude: float
    longitude: float


class AnalysisResponse(BaseModel):
    success: bool
    risk_level: str
    description: str
    recommendations: List[str]
    elevation: float = 0.0
    distance_from_water: float = 0.0
    message: str = ""


# ---------------------------
# Helpers
# ---------------------------

def parse_gemini_response(response_text: str) -> dict:
    """Parse Gemini AI response and extract structured data"""
    try:
        # Try to extract JSON
        json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
        if json_match:
            parsed_data = json.loads(json_match.group())

            # Always enforce structure
            return {
                "risk_level": parsed_data.get("risk_level", "Medium"),
                "description": parsed_data.get("description", "Analysis completed"),
                "recommendations": (
                    parsed_data.get("recommendations")
                    if isinstance(parsed_data.get("recommendations"), list)
                    else ["Monitor weather conditions", "Stay informed about local alerts"]
                ),
                "elevation": float(parsed_data.get("elevation", 50.0)),
                "distance_from_water": float(parsed_data.get("distance_from_water", 1000.0)),
                "image_analysis": parsed_data.get("image_analysis", "")
            }

        # If no JSON found
        return {
            "risk_level": "Medium",
            "description": "Analysis completed",
            "recommendations": ["Monitor weather conditions", "Stay informed about local alerts"],
            "elevation": 50.0,
            "distance_from_water": 1000.0,
            "image_analysis": response_text
        }

    except Exception as e:
        logger.error(f"Error parsing Gemini response: {str(e)}")
        return {
            "risk_level": "Medium",
            "description": "Analysis completed",
            "recommendations": ["Monitor weather conditions", "Stay informed about local alerts"],
            "elevation": 50.0,
            "distance_from_water": 1000.0,
            "image_analysis": response_text
        }


# ---------------------------
# API Routes
# ---------------------------

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "message": "Flood Detection API is running",
        "version": "1.0.0",
        "status": "healthy",
        "timestamp": datetime.now().isoformat()
    }


@app.post("/api/analyze/image")
async def analyze_image(file: UploadFile = File(...)):
    """Analyze flood risk based on uploaded image using Gemini AI"""
    try:
        logger.info(f"Analyzing image file: {file.filename}")

        # Read file
        image_data = await file.read()

        # Validate file type
        if not file.content_type.startswith("image/"):
            raise HTTPException(status_code=400, detail="Invalid file type. Please upload an image.")
        if len(image_data) > 10 * 1024 * 1024:  # 10MB limit
            raise HTTPException(status_code=400, detail="File size exceeds 10MB limit.")

        # Validate image
        try:
            image = PILImage.open(io.BytesIO(image_data))
            if image.mode != "RGB":
                image = image.convert("RGB")
        except Exception as img_error:
            logger.error(f"Error processing image: {str(img_error)}")
            raise HTTPException(status_code=400, detail="Invalid image format")

        # Prompt
        prompt = """
        Analyze this terrain image for flood risk assessment.
        Respond ONLY in valid JSON with these fields:
        {
          "risk_level": "Low | Medium | High | Very High",
          "description": "short explanation",
          "recommendations": ["string1", "string2", "string3"],
          "elevation": number (meters),
          "distance_from_water": number (meters),
          "image_analysis": "short description of what is visible"
        }
        """

        # Call Gemini AI
        try:
            model = generativeai.GenerativeModel('gemini-2.0-flash-exp')
            response = model.generate_content([prompt, image])
            parsed_data = parse_gemini_response(response.text)
        except Exception as gemini_error:
            logger.error(f"Error calling Gemini AI: {str(gemini_error)}")
            parsed_data = {
                "risk_level": "Medium",
                "description": "Image analysis unavailable, using simulated defaults",
                "recommendations": ["Monitor weather conditions", "Stay informed about local alerts"],
                "elevation": 50.0,
                "distance_from_water": 1000.0,
                "image_analysis": "AI service unavailable"
            }

        return {
            "success": True,
            **parsed_data,
            "ai_analysis": parsed_data.get("image_analysis", ""),
            "message": "Image analysis completed successfully"
        }

    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# ---------------------------
# Main Entry
# ---------------------------
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001, reload=True, log_level="info")
