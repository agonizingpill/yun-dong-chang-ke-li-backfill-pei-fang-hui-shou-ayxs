from datetime import datetime, timezone
from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Table, select
from core.db import metadata, transaction

movements = Table(
    "scale_movements", metadata,
    Column("code", Integer, primary_key=True, autoincrement=True),
    Column("lot_code", String(24), ForeignKey("reclaimed_lots.code"), nullable=False),
    Column("ticket_code", String(24), ForeignKey("refill_tickets.code"), nullable=False),
    Column("action", String(24), nullable=False),
    Column("grams", Integer, nullable=False),
    Column("actor", String(80), nullable=False),
    Column("booked_at", DateTime, nullable=False),
)


def post(conn, lot_code, ticket_code, action, grams, user):
    conn.execute(movements.insert().values(lot_code=lot_code, ticket_code=ticket_code,
                 action=action, grams=grams, actor=user["sub"], booked_at=datetime.now(timezone.utc)))


def ledger():
    with transaction() as conn:
        return [dict(row) for row in conn.execute(select(movements)
                    .order_by(movements.c.code.desc()).limit(200)).mappings()]
