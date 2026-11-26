from fastapi import APIRouter, Depends

from core.auth import actor, allow
from core.roles import REVIEW, WRITE
from domain import fieldwork
from domain.field_schema import GridRef, MarkPatch, MeasureDepth


router = APIRouter(prefix="/patches")


@router.get("")
def field_board(user=Depends(actor)):
    return fieldwork.board()


@router.get("/{code}")
def detail(code: str, user=Depends(actor)):
    return fieldwork.details(code)


@router.post("/{code}", status_code=201)
def mark(code: str, form: MarkPatch, user=Depends(actor)):
    allow(user, WRITE)
    return fieldwork.mark(code, form, user)


@router.post("/{code}/lay")
def lay(code: str, user=Depends(actor)):
    allow(user, WRITE)
    return fieldwork.lay(code, user)


@router.post("/{code}/cells/{grid_ref}/measure")
def measure(code: str, grid_ref: GridRef, form: MeasureDepth, user=Depends(actor)):
    allow(user, WRITE)
    return fieldwork.measure(code, grid_ref, form, user)


@router.post("/{code}/open")
def open_pitch(code: str, user=Depends(actor)):
    allow(user, REVIEW)
    return fieldwork.open_pitch(code, user)
