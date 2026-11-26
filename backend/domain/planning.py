from fastapi import HTTPException
from core.audit import record
from core.db import transaction
from core.queueing import result, submit
from domain.blend_tables import lines, tickets, zones
from domain.catalog import lookup, screen_for
from domain.intake_tables import lots
from domain.movements import post
from domain.rules import BINS, LotState, TicketState


def check_lot(lot, zone):
    if lot["state"] != LotState.ELIGIBLE:
        raise HTTPException(409, f"{lot['code']} 尚未通过筛分，含杂或缺档批不能回填")
    if lot["family"] != zone["family"]:
        raise HTTPException(409, f"{lot['code']} 胶粒类型与面层不兼容")


def assess(form, user):
    if len(set(form.lot_codes)) != len(form.lot_codes):
        raise HTTPException(422, "每个回收批只能选择一次")
    with transaction() as conn:
        zone = lookup(conn, zones, form.zone_code)
        batches = []
        for code in sorted(form.lot_codes):
            lot = lookup(conn, lots, code)
            check_lot(lot, zone)
            sample = screen_for(conn, lot)
            batches.append({"code": code, "revision": lot["sieve_revision"],
                            "free_g": lot["available_g"] - lot["reserved_g"],
                            "sieve": [sample[name + "_g"] for name in BINS], "zero_mode": sample["zero_mode"]})
    return submit(user, {"zone": zone, "batches": batches, "total_g": form.total_g})


def reserve(form, user):
    computation = result(user, form.token)
    snapshot = computation["input"]
    grade = computation["result"]
    revisions = {item["code"]: item["revision"] for item in snapshot["batches"]}
    with transaction() as conn:
        zone = lookup(conn, zones, snapshot["zone"]["code"])
        conn.execute(tickets.insert().values(
            code=form.code, zone_code=zone["code"], total_g=grade["total_g"], clearance=grade["distance"],
            target_clr=grade["target_clr"], blend_clr=grade["blend_clr"], state=TicketState.RESERVED,
            opened_by=user["sub"], compute_token=form.token))
        for index, line in enumerate(grade["lines"], 1):
            code, amount = line["lot_code"], line["grams"]
            revision = revisions.get(code)
            if code:
                lot = lookup(conn, lots, code, lock=True)
                check_lot(lot, zone)
                if lot["sieve_revision"] != revision:
                    raise HTTPException(409, "复筛版本已更新，请重新计算配方")
                if lot["available_g"] - lot["reserved_g"] < amount:
                    raise HTTPException(409, f"{code} 可用重量变化，请重算称量单")
                conn.execute(lots.update().where(lots.c.code == code)
                             .values(reserved_g=lot["reserved_g"] + amount))
                post(conn, code, form.code, "reserve", amount, user)
            conn.execute(lines.insert().values(code=f"{form.code}-{index}", ticket_code=form.code,
                         lot_code=code, required_g=amount, sample_revision=revision))
        record(conn, user, f"reserve:{form.code}")
    return {"code": form.code, "state": TicketState.RESERVED}
