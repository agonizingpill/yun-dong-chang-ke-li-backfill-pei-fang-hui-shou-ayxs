from fastapi import HTTPException
from core.audit import record
from core.db import transaction
from domain.catalog import lookup
from domain.intake_tables import lots, screens
from domain.rules import BINS, CONTAMINATION_LIMIT, LotState, SieveDecision, ZeroMode


def intake(form, user):
    with transaction() as conn:
        conn.execute(lots.insert().values(**form.model_dump(), available_g=form.gross_g))
        record(conn, user, f"intake:{form.code}")
        return lookup(conn, lots, form.code)


def decision(form):
    bins = [getattr(form, name + "_g") for name in BINS]
    if sum(bins) + form.foreign_g != 1000:
        raise HTTPException(422, "筛余三档和拣除杂物必须合计 1000 g")
    if form.foreign_g > CONTAMINATION_LIMIT:
        return SieveDecision.FOREIGN_MATERIAL
    if form.zero_mode == ZeroMode.STRUCTURAL:
        return SieveDecision.STRUCTURAL_ZERO if 0 in bins else SieveDecision.ZERO_DECLARATION
    if (0 in bins) != (form.zero_mode == ZeroMode.BELOW_LIMIT):
        return SieveDecision.ZERO_DECLARATION
    return SieveDecision.PASSED


def inspect(code, form, user):
    reason = decision(form)
    with transaction() as conn:
        lot = lookup(conn, lots, code, lock=True)
        if lot["reserved_g"]:
            raise HTTPException(409, "已有称量单锁定此批次。请先完成或退订再复筛")
        version = lot["sieve_revision"] + 1
        screen_code = f"{code}-{version}"
        conn.execute(screens.insert().values(code=screen_code, lot_code=code, revision=version,
                     **form.model_dump(), decision=reason, chemist=user["sub"]))
        new_state = LotState.ELIGIBLE if reason == SieveDecision.PASSED else LotState.QUARANTINED
        conn.execute(lots.update().where(lots.c.code == code)
                     .values(sieve_revision=version, state=new_state))
        record(conn, user, f"sieve:{screen_code}:{reason}")
        return {"state": new_state, "report": lookup(conn, screens, screen_code)}
