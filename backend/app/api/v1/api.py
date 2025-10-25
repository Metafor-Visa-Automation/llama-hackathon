from fastapi import APIRouter
from app.api.v1.endpoints import (
    auth, users, applications, documents
)

api_router = APIRouter()

# Include only essential endpoint routers
api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(applications.router, prefix="/applications", tags=["applications"])
api_router.include_router(documents.router, prefix="/documents", tags=["documents"])
