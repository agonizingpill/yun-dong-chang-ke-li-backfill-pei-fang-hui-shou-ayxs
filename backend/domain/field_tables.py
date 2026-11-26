from sqlalchemy import Boolean, CheckConstraint, Column, ForeignKey, Integer, String, Table, UniqueConstraint

from core.db import metadata


patches = Table(
    "field_patches", metadata,
    Column("code", String(24), ForeignKey("refill_tickets.code"), primary_key=True),
    Column("zone_code", String(24), ForeignKey("playing_zones.code"), nullable=False),
    Column("planned_by", String(80), nullable=False),
    Column("laid_by", String(80)),
    Column("opened_by", String(80)),
    CheckConstraint("opened_by IS NULL OR laid_by IS NOT NULL"),
)

cells = Table(
    "patch_cells", metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("patch_code", String(24), ForeignKey("field_patches.code"), nullable=False),
    Column("grid_ref", String(2), nullable=False),
    UniqueConstraint("patch_code", "grid_ref"),
)

holds = Table(
    "active_patch_cells", metadata,
    Column("zone_code", String(24), ForeignKey("playing_zones.code"), primary_key=True),
    Column("grid_ref", String(2), primary_key=True),
    Column("cell_id", Integer, ForeignKey("patch_cells.id"), nullable=False, unique=True),
)

readings = Table(
    "patch_depth_readings", metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("cell_id", Integer, ForeignKey("patch_cells.id"), nullable=False, index=True),
    Column("first_mm", Integer, nullable=False),
    Column("middle_mm", Integer, nullable=False),
    Column("last_mm", Integer, nullable=False),
    Column("spread_mm", Integer, nullable=False),
    Column("passed", Boolean, nullable=False),
    Column("repeat_of", Integer, ForeignKey("patch_depth_readings.id"), unique=True),
    Column("measured_by", String(80), nullable=False),
    CheckConstraint("first_mm BETWEEN 0 AND 35 AND middle_mm BETWEEN 0 AND 35 AND last_mm BETWEEN 0 AND 35"),
    CheckConstraint("spread_mm BETWEEN 0 AND 35"),
)
