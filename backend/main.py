from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import uvicorn
import os
from datetime import datetime
import logging
import google.generativeai as genai
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

# Configure Google Generative AI
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
    logger.info("Gemini API key configured successfully")
else:
    logger.error("GEMINI_API_KEY/GOOGLE_API_KEY not found in environment variables")

# FastAPI app
app = FastAPI(
    title="Flood Detection API",
    description="Flood risk assessment using Gemini AI with detailed analysis",
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
class AnalysisResponse(BaseModel):
    success: bool
    risk_level: str
    description: str
    recommendations: List[str]
    elevation: float = 0.0
    distance_from_water: float = 0.0
    ai_analysis: str = ""
    message: str = ""
    error: Optional[str] = None


def parse_gemini_response(response_text: str) -> tuple[dict, Optional[str]]:
    """Parse Gemini AI response and extract structured data."""
    try:
        json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
        if json_match:
            try:
                parsed_data = json.loads(json_match.group())
                return {
                    "risk_level": parsed_data.get("risk_level", "Medium"),
                    "description": str(parsed_data.get("description", "")).strip(),
                    "recommendations": [str(r).strip() for r in parsed_data.get("recommendations", [])],
                    "elevation": float(parsed_data.get("elevation", 0.0)),
                    "distance_from_water": float(parsed_data.get("distance_from_water", 0.0)),
                    "ai_analysis": str(parsed_data.get("image_analysis", "")).strip()
                }, None
            except json.JSONDecodeError as je:
                return None, f"Invalid JSON: {str(je)}"
        else:
            return None, "No JSON found in response"
    except Exception as e:
        return None, f"Parse error: {str(e)}"


@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "message": "Flood Detection API is running",
        "version": "1.0.0",
        "status": "healthy",
        "timestamp": datetime.now().isoformat()
    }


@app.post("/api/analyze/image", response_model=AnalysisResponse)
async def analyze_image(file: UploadFile = File(...)):
    """Analyze flood risk based on uploaded image using Gemini AI"""
    try:
        logger.info(f"Analyzing image: {file.filename}")
        
        image_data = await file.read()
        
        if not file.content_type.startswith("image/"):
            logger.warning(f"Invalid file type: {file.content_type}")
            raise HTTPException(status_code=400, detail="Invalid file type")
        if len(image_data) > 10 * 1024 * 1024:
            logger.warning(f"File too large: {len(image_data)}")
            raise HTTPException(status_code=400, detail="File size exceeds 10MB")
        
        try:
            image = PILImage.open(io.BytesIO(image_data))
            if image.mode != "RGB":
                image = image.convert("RGB")
            logger.info(f"Image validated: {image.size}")
        except Exception as img_error:
            logger.error(f"Error processing image: {str(img_error)}")
            raise HTTPException(status_code=400, detail="Invalid image format")
        
        prompt = """
You are an expert disaster risk analyst specializing in flood safety. Analyze this terrain image for flood risk.

RESPOND WITH VALID JSON ONLY (no other text):

{
  "risk_level": "Low | Medium | High | Very High",
  "description": "2-3 sentences about the flood risk",
  "recommendations": ["3-5 practical safety recommendations"],
  "elevation": number or 0,
  "distance_from_water": number or 0,
  "image_analysis": "Detailed description of visible features"
}
"""
        
        if not GEMINI_API_KEY:
            logger.error("Gemini API key not configured")
            return AnalysisResponse(
                success=False,
                risk_level="Unknown",
                description="API key not configured",
                recommendations=[],
                ai_analysis="",
                message="API configuration error",
                error="Missing API key"
            )
        
        try:
            logger.info("Calling Gemini API")
            model = genai.GenerativeModel('gemini-3.5-flash')
            response = model.generate_content([prompt, image])
            
            if not response or not response.text:
                logger.error("Empty Gemini response")
                return AnalysisResponse(
                    success=False,
                    risk_level="Unknown",
                    description="Empty API response",
                    recommendations=[],
                    ai_analysis="",
                    message="API returned empty response",
                    error="Empty response"
                )
            
            logger.info(f"Gemini response: {len(response.text)} chars")
            parsed_data, parse_error = parse_gemini_response(response.text)
            
            if parse_error:
                logger.error(f"Parse error: {parse_error}")
                return AnalysisResponse(
                    success=False,
                    risk_level="Unknown",
                    description="Failed to parse analysis",
                    recommendations=[],
                    ai_analysis=response.text[:300],
                    message="Failed to parse AI response",
                    error=parse_error
                )
            
            logger.info(f"Success - Risk: {parsed_data['risk_level']}")
            return AnalysisResponse(
                success=True,
                **parsed_data,
                message="Analysis completed",
                error=None
            )
            
        except Exception as gemini_error:
            error_msg = f"Gemini API error: {str(gemini_error)}"
            logger.error(error_msg, exc_info=True)
            return AnalysisResponse(
                success=False,
                risk_level="Unknown",
                description="AI service error",
                recommendations=[],
                ai_analysis="",
                message=str(gemini_error)[:100],
                error=error_msg
            )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Server error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001, reload=True, log_level="info")
