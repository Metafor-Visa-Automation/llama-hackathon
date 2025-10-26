from fastapi import APIRouter
from app.api.v1.endpoints import (
    auth, users, applications, user_documents, letter_generation, ai_form_filling, ai_visa
)

api_router = APIRouter()

# Include only essential endpoint routers
api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(applications.router, prefix="/applications", tags=["applications"])
api_router.include_router(user_documents.router, prefix="/documents", tags=["Documents & OCR"])
api_router.include_router(letter_generation.router, prefix="/letters", tags=["Letter Generation"])
api_router.include_router(ai_form_filling.router, prefix="/ai", tags=["AI Form Filling"])
api_router.include_router(ai_visa.router, prefix="/ai", tags=["AI Visa Services"])
