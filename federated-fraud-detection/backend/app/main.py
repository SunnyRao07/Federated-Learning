"""
FastAPI main application
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from app.api import router

# Create FastAPI app
app = FastAPI(
    title="Federated Fraud Detection API",
    description="Privacy-preserving fraud detection using federated learning",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API router
app.include_router(router, prefix="/api", tags=["Federated Learning"])

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Federated Fraud Detection API",
        "version": "1.0.0",
        "docs": "/docs",
        "endpoints": {
            "train": "POST /api/train",
            "metrics": "GET /api/metrics",
            "predict": "POST /api/predict",
            "attack_test": "GET /api/attack-test",
            "status": "GET /api/status",
            "history": "GET /api/history",
            "clients": "GET /api/clients",
            "reset": "DELETE /api/reset"
        }
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
