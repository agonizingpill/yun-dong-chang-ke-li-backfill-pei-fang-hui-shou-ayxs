from sqlalchemy import CheckConstraint, Column, ForeignKey, Integer, String, Table, UniqueConstraint
from core.db import metadata

lots = Table(
    "reclaimed_lots", metadata,
    Column("code", String(24), primary_key=True),
    Column("donor_surface", String(64), nullable=False),
    Column("family", String(20), nullable=False),
    Column("gross_g", Integer, nullable=False),
    Column("available_g", Integer, nullable=False),
    Column("reserved_g", Integer, nullable=False, default=0),
    Column("state", String(20), nullable=False, default="awaiting"),
    Column("sieve_revision", Integer, nullable=False, default=0),
    CheckConstraint("gross_g >= available_g AND available_g >= reserved_g AND reserved_g >= 0"),
    CheckConstraint("state IN ('awaiting','eligible','quarantined')"),
    CheckConstraint("family IN ('epdm','tpe')"),
)

screens = Table(
    "sieve_reports", metadata,
    Column("code", String(30), primary_key=True),
    Column("lot_code", String(24), ForeignKey("reclaimed_lots.code"), nullable=False, index=True),
    Column("revision", Integer, nullable=False),
    Column("fine_g", Integer, nullable=False),
    Column("medium_g", Integer, nullable=False),
    Column("coarse_g", Integer, nullable=False),
    Column("foreign_g", Integer, nullable=False),
    Column("zero_mode", String(20), nullable=False),
    Column("decision", String(24), nullable=False),
    Column("chemist", String(80), nullable=False),
    UniqueConstraint("lot_code", "revision"),
    CheckConstraint("fine_g + medium_g + coarse_g + foreign_g = 1000"),
    CheckConstraint("fine_g >= 0 AND medium_g >= 0 AND coarse_g >= 0 AND foreign_g >= 0"),
    CheckConstraint("zero_mode IN ('none','below_limit','structural')"),
)
