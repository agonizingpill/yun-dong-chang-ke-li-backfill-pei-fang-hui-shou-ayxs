from sqlalchemy import CheckConstraint, Column, Float, ForeignKey, Integer, JSON, String, Table, UniqueConstraint
from core.db import metadata

zones = Table(
    "playing_zones", metadata,
    Column("code", String(24), primary_key=True),
    Column("label", String(64), nullable=False),
    Column("family", String(20), nullable=False),
    Column("fine_pt", Integer, nullable=False),
    Column("medium_pt", Integer, nullable=False),
    Column("coarse_pt", Integer, nullable=False),
    Column("new_fine_pt", Integer, nullable=False),
    Column("new_medium_pt", Integer, nullable=False),
    Column("new_coarse_pt", Integer, nullable=False),
    Column("max_clearance", Float, nullable=False),
    Column("max_reclaimed_pt", Integer, nullable=False),
    CheckConstraint("fine_pt + medium_pt + coarse_pt = 100"),
    CheckConstraint("new_fine_pt + new_medium_pt + new_coarse_pt = 100"),
    CheckConstraint("fine_pt > 0 AND medium_pt > 0 AND coarse_pt > 0"),
    CheckConstraint("new_fine_pt > 0 AND new_medium_pt > 0 AND new_coarse_pt > 0"),
    CheckConstraint("max_reclaimed_pt BETWEEN 1 AND 100 AND max_clearance > 0"),
)

tickets = Table(
    "refill_tickets", metadata,
    Column("code", String(24), primary_key=True),
    Column("zone_code", String(24), ForeignKey("playing_zones.code"), nullable=False),
    Column("total_g", Integer, nullable=False),
    Column("clearance", Float, nullable=False),
    Column("target_clr", JSON, nullable=False),
    Column("blend_clr", JSON, nullable=False),
    Column("state", String(16), nullable=False),
    Column("opened_by", String(80), nullable=False),
    Column("finalized_by", String(80)),
    Column("compute_token", String(50), nullable=False, unique=True),
    CheckConstraint("total_g > 0"),
    CheckConstraint("state IN ('reserved','weighed','released','cancelled')"),
)

lines = Table(
    "weigh_lines", metadata,
    Column("code", String(32), primary_key=True),
    Column("ticket_code", String(24), ForeignKey("refill_tickets.code"), nullable=False, index=True),
    Column("lot_code", String(24), ForeignKey("reclaimed_lots.code")),
    Column("sample_revision", Integer),
    Column("required_g", Integer, nullable=False),
    Column("actual_g", Integer),
    UniqueConstraint("ticket_code", "lot_code"),
    CheckConstraint("required_g > 0 AND (actual_g IS NULL OR actual_g > 0)"),
    CheckConstraint("(lot_code IS NULL AND sample_revision IS NULL) OR "
                    "(lot_code IS NOT NULL AND sample_revision IS NOT NULL)"),
)
