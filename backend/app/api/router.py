from __future__ import annotations

from fastapi import APIRouter

from app.modules.admin.api import router as admin_router
from app.modules.annuity.api import router as annuity_router
from app.modules.auth.api import router as auth_router
from app.modules.billing.api import router as billing_router
from app.modules.cases.api import router as case_router
from app.modules.collections.api import router as collections_router
from app.modules.commission.api import router as commission_router
from app.modules.consulting.api import router as consulting_router
from app.modules.documents.api import router as documents_router
from app.modules.expenses.api import router as expenses_router
from app.modules.fees.api import router as fees_router
from app.modules.masterdata.applicants.api import router as applicants_router
from app.modules.masterdata.clients.api import router as clients_router
from app.modules.masterdata.countries.api import router as countries_router
from app.modules.system.api import router as system_router
from app.modules.tasks.api import router as tasks_router
from app.modules.templates.api import router as templates_router

api_router = APIRouter()
api_router.include_router(admin_router, tags=["Admin"])
api_router.include_router(auth_router, prefix="/auth", tags=["Auth"])
api_router.include_router(system_router, tags=["System"])
api_router.include_router(templates_router, tags=["Templates"])
api_router.include_router(applicants_router, tags=["Applicants"])
api_router.include_router(clients_router, tags=["Clients"])
api_router.include_router(countries_router, tags=["Countries"])
api_router.include_router(case_router, tags=["Cases"])
api_router.include_router(documents_router, tags=["Documents"])
api_router.include_router(tasks_router, tags=["Tasks"])
api_router.include_router(fees_router, tags=["Fees"])
api_router.include_router(billing_router, tags=["Billing"])
api_router.include_router(annuity_router, tags=["Annuity"])
api_router.include_router(collections_router, tags=["Collections"])
api_router.include_router(commission_router, tags=["Commission"])
api_router.include_router(consulting_router, tags=["Consulting"])
api_router.include_router(expenses_router, tags=["Expenses"])
