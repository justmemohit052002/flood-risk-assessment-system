"""
Startup script for the Flood Detection Backend API
"""

import uvicorn

import os

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent))

if __name__ == "__main__":
    port = int(os.getenv("PORT",8001))
    host = os.getenv("HOST","0.0.0.0")


    display_host = "localhost" if host in ("0.0.0.0", "::") else host

    print(f"Starting Flood Detection Backend API on {host}:{port}")
    print("API Documentation will be available at:")
    print(f"  -Swagger UI: http://{display_host}:{port}/docs")
    print(f"  -ReDoc: http://{display_host}:{port}/redoc")
    print(f"  -OpenAPI JSON: http://{display_host}:{port}/openapi.json")

    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=True,
        log_level="info"
    )