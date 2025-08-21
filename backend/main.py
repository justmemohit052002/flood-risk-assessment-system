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
import random

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configure Google Generative AI
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
if GOOGLE_API_KEY:
    generativeai.configure(api_key=GOOGLE_API_KEY)
else:
    logger.warning("GOOGLE_API_KEY not found in environment variables")

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
        json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
        if json_match:
            json_str = json_match.group()
            parsed_data = json.loads(json_str)

            return {
                "risk_level": parsed_data.get("risk_level", "Medium"),
                "description": parsed_data.get("description", "Analysis completed"),
                "recommendations": parsed_data.get("recommendations", []),
                "elevation": parsed_data.get("elevation", 50.0),
                "distance_from_water": parsed_data.get("distance_from_water", 1000.0),
                "image_analysis": parsed_data.get("image_analysis", "")
            }
        else:
            return {
                "risk_level": "Medium",
                "description": "Analysis completed",
                "recommendations": [
                    "Monitor weather conditions",
                    "Stay informed about local alerts"
                ],
                "elevation": 50.0,
                "distance_from_water": 1000.0,
                "image_analysis": response_text
            }

    except Exception as e:
        logger.error(f"Error parsing Gemini response: {str(e)}")
        return {
            "risk_level": "Medium",
            "description": "Analysis completed",
            "recommendations": [
                "Monitor weather conditions",
                "Stay informed about local alerts"
            ],
            "elevation": 50.0,
            "distance_from_water": 1000.0,
            "image_analysis": response_text
        }


def generate_image_risk_assessment() -> dict:
    """Generate simulated risk assessment for image analysis"""
    risk_level = random.choice(["Low", "Medium", "High", "Very High"])

    descriptions = {
        "Low": "Image analysis shows low flood risk terrain.",
        "Medium": "Image analysis indicates moderate flood risk factors.",
        "High": "Image analysis reveals high flood risk characteristics.",
        "Very High": "Image analysis shows very high flood risk indicators."
    }

    recommendations = {
        "Low": [
            "Continue monitoring terrain changes",
            "Maintain current drainage systems",
            "Stay informed about weather patterns"
        ],
        "Medium": [
            "Improve drainage infrastructure",
            "Consider flood monitoring systems",
            "Develop emergency response plan"
        ],
        "High": [
            "Install comprehensive flood barriers",
            "Implement early warning systems",
            "Consider structural reinforcements"
        ],
        "Very High": [
            "Immediate flood protection measures needed",
            "Consider relocation to higher ground",
            "Implement comprehensive emergency protocols"
        ]
    }

    return {
        "risk_level": risk_level,
        "description": descriptions[risk_level],
        "recommendations": recommendations[risk_level],
        "elevation": round(random.uniform(10, 100), 1),
        "distance_from_water": round(random.uniform(200, 2000), 1)
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
        Please provide:
        1. Risk Level (Low/Medium/High/Very High)
        2. Description of the risk based on what you see
        3. 3-5 specific recommendations
        4. Estimated elevation in meters
        5. Estimated distance from water bodies in meters
        6. What water bodies or flood risks you can identify in image
        Format your response as JSON with these fields:
        - risk_level
        - description
        - recommendations (array of strings)
        - elevation (number)
        - distance_from_water (number)
        - image_analysis (string describing what you see)
        """

        # Call Gemini AI
        try:
            model = generativeai.GenerativeModel('gemini-2.0-flash-exp')
            response = model.generate_content([prompt, image])
            parsed_data = parse_gemini_response(response.text)
        except Exception as gemini_error:
            logger.error(f"Error calling Gemini AI: {str(gemini_error)}")
            parsed_data = generate_image_risk_assessment()
            parsed_data["image_analysis"] = "Image analysis unavailable, using simulated assessment"

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
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True, log_level="info")
