from fastapi import APIRouter

from app.auth.router import router as auth_router
from app.identity.router import router as identity_router
from app.livestock.router import router as livestock_router
from app.weighment.router import router as weighment_router
from app.marketplace.router import router as marketplace_router
from app.bidding.router import router as bidding_router
from app.agreement.router import router as agreement_router
from app.transaction.router import router as transaction_router
from app.logistics.router import router as logistics_router
from app.payments.router import router as payments_router
from app.disputes.router import router as disputes_router
from app.notifications.router import router as notifications_router
from app.audit.router import router as audit_router

api_router = APIRouter()
for router in [
    auth_router,
    identity_router,
    livestock_router,
    weighment_router,
    marketplace_router,
    bidding_router,
    agreement_router,
    transaction_router,
    logistics_router,
    payments_router,
    disputes_router,
    notifications_router,
    audit_router,
]:
    api_router.include_router(router)
