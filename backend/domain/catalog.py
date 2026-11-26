from fastapi import HTTPException
from sqlalchemy import and_, desc, select
from core.db import transaction
from domain.blend_tables import lines, tickets, zones
from domain.intake_tables import lots, screens


def lookup(conn, table, code, lock=False):
    query = select(table).where(table.c.code == code)
    if lock:
        query = query.with_for_update()
    item = conn.execute(query).mappings().first()
    if item is None:
        raise HTTPException(404, f"没有编号为 {code} 的记录")
    return dict(item)


def recent(table):
    with transaction() as conn:
        return [dict(r) for r in conn.execute(
            select(table).order_by(desc(table.c.code)).limit(100)).mappings()]


def screen_for(conn, lot):
    record = conn.execute(select(screens).where(and_(
        screens.c.lot_code == lot["code"], screens.c.revision == lot["sieve_revision"]
    ))).mappings().first()
    if record is None:
        raise HTTPException(409, f"{lot['code']} 尚无当前筛分报告")
    return dict(record)


def ticket_lines(conn, code):
    query = select(lines).where(lines.c.ticket_code == code).order_by(lines.c.code)
    return [dict(row) for row in conn.execute(query).mappings()]


def detail(code):
    with transaction() as conn:
        return {"ticket": lookup(conn, tickets, code), "lines": ticket_lines(conn, code)}


def overview():
    with transaction() as conn:
        records = [dict(row) for row in conn.execute(
            select(lots).order_by(lots.c.code).limit(100)).mappings()]
        specs = [dict(row) for row in conn.execute(select(zones).order_by(zones.c.code)).mappings()]
        return {"lots": records, "zones": specs}
