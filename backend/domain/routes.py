from fastapi import APIRouter, Depends
from core.auth import actor, allow
from core.roles import REVIEW, WRITE
from domain import blend_tables, catalog, field_routes, intake_tables, movements, planning, scale, screening
from domain.schema import Intake, Preview, Reserve, Screen, Weigh

bay = APIRouter(prefix="/bay")
sieve = APIRouter(prefix="/sieve")
fit = APIRouter(prefix="/fit")
scale_router = APIRouter(prefix="/weigh")
routers = (bay, sieve, fit, scale_router, field_routes.router)


@bay.get("")
def inventory(user=Depends(actor)):
    return catalog.overview()


@bay.post("", status_code=201)
def receive(form: Intake, user=Depends(actor)):
    allow(user, WRITE)
    return screening.intake(form, user)


@sieve.get("")
def reports(user=Depends(actor)):
    return catalog.recent(intake_tables.screens)


@sieve.post("/{code}")
def grade(code: str, form: Screen, user=Depends(actor)):
    allow(user, WRITE)
    return screening.inspect(code, form, user)


@fit.post("", status_code=202)
def calculate(form: Preview, user=Depends(actor)):
    allow(user, WRITE)
    return planning.assess(form, user)


@fit.post("/reserve", status_code=201)
def reserve(form: Reserve, user=Depends(actor)):
    allow(user, WRITE)
    return planning.reserve(form, user)


@scale_router.get("")
def tickets(user=Depends(actor)):
    return catalog.recent(blend_tables.tickets)


@scale_router.get("/ledger")
def issue_ledger(user=Depends(actor)):
    return movements.ledger()


@scale_router.get("/{code}")
def detail(code: str, user=Depends(actor)):
    return catalog.detail(code)


@scale_router.post("/{code}/read")
def weigh(code: str, form: Weigh, user=Depends(actor)):
    allow(user, WRITE)
    return scale.weigh(code, form, user)


@scale_router.post("/{code}/release")
def release(code: str, user=Depends(actor)):
    allow(user, REVIEW)
    return scale.finalize(code, user)


@scale_router.post("/{code}/cancel")
def cancel(code: str, user=Depends(actor)):
    allow(user, REVIEW)
    return scale.finalize(code, user, cancel=True)
