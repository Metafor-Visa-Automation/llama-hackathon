from fastapi import APIRouter
from app.api.v1.endpoints import (
    auth, users, applications, documents, 
    visa_requirements, countries, tasks, 
    social_media_audit, admin, ai, support, analytics, integrations, reports, ocr, form_filling,
    teams, user_documents, notifications, checklist_templates
)

api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(applications.router, prefix="/applications", tags=["applications"])
api_router.include_router(documents.router, prefix="/documents", tags=["documents"])
api_router.include_router(visa_requirements.router, prefix="/visa-requirements", tags=["visa-requirements"])
api_router.include_router(countries.router, prefix="/countries", tags=["countries"])
api_router.include_router(tasks.router, prefix="/tasks", tags=["tasks"])
api_router.include_router(teams.router, prefix="/teams", tags=["teams"])
api_router.include_router(user_documents.router, prefix="/user-documents", tags=["user-documents"])
api_router.include_router(notifications.router, prefix="/notifications", tags=["notifications"])
api_router.include_router(checklist_templates.router, prefix="/checklist-templates", tags=["checklist-templates"])
api_router.include_router(social_media_audit.router, prefix="/social-audits", tags=["social-media-audit"])
api_router.include_router(admin.router, prefix="/admin", tags=["admin"])
api_router.include_router(ai.router, prefix="/ai", tags=["ai"])
api_router.include_router(ocr.router, prefix="/ocr", tags=["ocr"])
api_router.include_router(form_filling.router, prefix="/form-filling", tags=["form-filling"])
api_router.include_router(support.router, prefix="/support", tags=["support"])
api_router.include_router(analytics.router, prefix="/analytics", tags=["analytics"])
api_router.include_router(integrations.router, prefix="/integrations", tags=["integrations"])
api_router.include_router(reports.router, prefix="/reports", tags=["reports"])
