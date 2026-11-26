from enum import StrEnum

GRAM_STEP = 50
BINS = ("fine", "medium", "coarse")
CONTAMINATION_LIMIT = 10


class LotState(StrEnum):
    AWAITING = "awaiting"
    ELIGIBLE = "eligible"
    QUARANTINED = "quarantined"


class TicketState(StrEnum):
    RESERVED = "reserved"
    WEIGHED = "weighed"
    RELEASED = "released"
    CANCELLED = "cancelled"


class ZeroMode(StrEnum):
    NONE = "none"
    BELOW_LIMIT = "below_limit"
    STRUCTURAL = "structural"


class SieveDecision(StrEnum):
    PASSED = "passed"
    FOREIGN_MATERIAL = "foreign_material"
    STRUCTURAL_ZERO = "structural_zero"
    ZERO_DECLARATION = "zero_declaration"
