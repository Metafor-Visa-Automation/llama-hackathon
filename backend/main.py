from fastapi import FastAPI, HTTPException, Depends, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import uvicorn
import os
from dotenv import load_dotenv

from app.routes import auth, visa_applications, documents, social_media_audit
from app.core.config import settings
from app.core.firebase import initialize_firebase

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI(
    title="VisaPrep AI API",
    description="AI-powered visa application automation platform",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],  # Frontend URLs
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Firebase
initialize_firebase()

# Include routers
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(visa_applications.router, prefix="/api/visa", tags=["Visa Applications"])
app.include_router(documents.router, prefix="/api/documents", tags=["Documents"])
app.include_router(social_media_audit.router, prefix="/api/social-media", tags=["Social Media Audit"])

@app.get("/")
async def root():
    return {"message": "VisaPrep AI API is running", "version": "1.0.0"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "VisaPrep AI Backend"}

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
