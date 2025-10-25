from fastapi import APIRouter
from app.api.v1.endpoints import (
    auth, users, applications, documents, 
    visa_requirements, countries, tasks, 
    social_media_audit, admin, ai, support, analytics, integrations, reports
)

api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(applications.router, prefix="/applications", tags=["applications"])
api_router.include_router(documents.router, prefix="/docs", tags=["documents"])
api_router.include_router(visa_requirements.router, prefix="/visa-requirements", tags=["visa-requirements"])
api_router.include_router(countries.router, prefix="/countries", tags=["countries"])
api_router.include_router(tasks.router, prefix="/tasks", tags=["tasks"])
api_router.include_router(social_media_audit.router, prefix="/social-audits", tags=["social-media-audit"])
api_router.include_router(admin.router, prefix="/admin", tags=["admin"])
api_router.include_router(ai.router, prefix="/ai", tags=["ai"])
api_router.include_router(support.router, prefix="/support", tags=["support"])
api_router.include_router(analytics.router, prefix="/analytics", tags=["analytics"])
api_router.include_router(integrations.router, prefix="/integrations", tags=["integrations"])
api_router.include_router(reports.router, prefix="/reports", tags=["reports"])
