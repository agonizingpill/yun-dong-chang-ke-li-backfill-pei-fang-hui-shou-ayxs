from fastapi import HTTPException
from sqlalchemy import delete, select

from core.audit import record
from core.db import transaction
from domain import catalog
from domain.blend_tables import tickets, zones
from domain.field_tables import cells, holds, patches, readings


def board():
    with transaction() as conn:
        # Keep unfinished work visible even when recent opened patches accumulate.
        active = select(patches).where(patches.c.opened_by.is_(None)).order_by(patches.c.code)
        opened = select(patches).where(patches.c.opened_by.is_not(None)).order_by(patches.c.code.desc()).limit(50)
        eligible = (
            select(tickets.c.code, tickets.c.zone_code, tickets.c.total_g)
            .outerjoin(patches, tickets.c.code == patches.c.code)
            .where(tickets.c.state == "released", patches.c.code.is_(None))
            .order_by(tickets.c.code)
        )
        return {
            "patches": [dict(row) for query in (active, opened) for row in conn.execute(query).mappings()],
            "eligible_tickets": [dict(row) for row in conn.execute(eligible).mappings()],
            "active_cells": [dict(row) for row in conn.execute(select(holds)).mappings()],
        }


def _detail(conn, patch):
    query = select(cells).where(cells.c.patch_code == patch["code"]).order_by(cells.c.grid_ref)
    grid = [dict(row) | {"history": []} for row in conn.execute(query).mappings()]
    by_id = {cell["id"]: cell for cell in grid}
    history = select(readings).where(readings.c.cell_id.in_(by_id)).order_by(readings.c.id)
    for row in conn.execute(history).mappings():
        by_id[row["cell_id"]]["history"].append(dict(row))
    passed = sum(bool(cell["history"] and cell["history"][-1]["passed"]) for cell in grid)
    return {"patch": patch, "cells": grid, "passed_cells": passed}


def details(code):
    with transaction() as conn:
        return _detail(conn, catalog.lookup(conn, patches, code))


def mark(code, form, user):
    with transaction() as conn:
        ticket = catalog.lookup(conn, tickets, code, lock=True)
        if ticket["state"] != "released":
            raise HTTPException(409, "只有已发料的称量单可划定补坪范围")
        zone = ticket["zone_code"]
        catalog.lookup(conn, zones, zone, lock=True)
        existing = select(patches.c.code).where(patches.c.code == code)
        if conn.execute(existing).scalar() is not None:
            raise HTTPException(409, "此称量单已有补坪工单")
        conflicts = (
            select(holds.c.grid_ref)
            .where(holds.c.zone_code == zone, holds.c.grid_ref.in_(form.grid_refs))
            .order_by(holds.c.grid_ref)
        )
        taken = conn.execute(conflicts).scalars().all()
        if taken:
            raise HTTPException(409, f"网格正在补坪：{'、'.join(taken)}")
        patch = {"code": code, "zone_code": zone, "planned_by": user["sub"], "laid_by": None, "opened_by": None}
        conn.execute(patches.insert().values(**patch))
        for grid_ref in sorted(form.grid_refs):
            result = conn.execute(cells.insert().values(patch_code=code, grid_ref=grid_ref))
            conn.execute(holds.insert().values(zone_code=zone, grid_ref=grid_ref, cell_id=result.inserted_primary_key[0]))
        record(conn, user, f"patch.mark:{code}")
        return _detail(conn, patch)


def lay(code, user):
    with transaction() as conn:
        patch = catalog.lookup(conn, patches, code, lock=True)
        if patch["laid_by"] is not None:
            raise HTTPException(409, "此补坪工单已登记实铺")
        conn.execute(patches.update().where(patches.c.code == code).values(laid_by=user["sub"]))
        record(conn, user, f"patch.lay:{code}")
        return _detail(conn, patch | {"laid_by": user["sub"]})


def measure(code, grid_ref, form, user):
    with transaction() as conn:
        patch = catalog.lookup(conn, patches, code, lock=True)
        if patch["laid_by"] is None or patch["opened_by"] is not None:
            raise HTTPException(409, "只能测读已实铺且尚未开场的网格")
        query = select(cells.c.id).where(cells.c.patch_code == code, cells.c.grid_ref == grid_ref)
        cell_id = conn.execute(query).scalar()
        if cell_id is None:
            raise HTTPException(404, "网格不在这张工单内")
        history = select(readings).where(readings.c.cell_id == cell_id).order_by(readings.c.id.desc()).limit(1)
        previous = conn.execute(history).mappings().first()
        if previous is not None and previous["passed"]:
            raise HTTPException(409, "该网格最新测读已合格")
        repeat_of = previous["id"] if previous is not None else None
        if form.repeat_of != repeat_of:
            raise HTTPException(409, "复测必须关联同一网格的最新失败读数")

        depths = (form.first_mm, form.middle_mm, form.last_mm)
        spread = max(depths) - min(depths)
        passed = all(12 <= depth <= 16 for depth in depths) and spread <= 2
        conn.execute(readings.insert().values(
            cell_id=cell_id, **form.model_dump(), spread_mm=spread, passed=passed, measured_by=user["sub"],
        ))
        record(conn, user, f"patch.measure:{code}:{grid_ref}")
        return _detail(conn, patch)


def open_pitch(code, user):
    with transaction() as conn:
        patch = catalog.lookup(conn, patches, code, lock=True)
        if patch["opened_by"] is not None:
            raise HTTPException(409, "此补坪单已签开场")
        detail = _detail(conn, patch)
        if patch["laid_by"] is None or detail["passed_cells"] != len(detail["cells"]):
            raise HTTPException(409, "须完成实铺并让全部网格测读合格后才能开场")
        conn.execute(patches.update().where(patches.c.code == code).values(opened_by=user["sub"]))
        conn.execute(delete(holds).where(holds.c.cell_id.in_([cell["id"] for cell in detail["cells"]])))
        record(conn, user, f"patch.open:{code}")
        detail["patch"]["opened_by"] = user["sub"]
        return detail
