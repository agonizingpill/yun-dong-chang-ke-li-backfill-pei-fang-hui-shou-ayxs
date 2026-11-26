from domain.blend_tables import zones
from domain.intake_tables import lots, screens

FIXTURES = (
    (zones, [
        {"code": "YH-NORTH", "label": "屿岸球场 · 北端边线", "family": "epdm", "fine_pt": 20,
         "medium_pt": 56, "coarse_pt": 24, "new_fine_pt": 30, "new_medium_pt": 42,
         "new_coarse_pt": 28, "max_clearance": 0.35, "max_reclaimed_pt": 65},
        {"code": "YH-EAST", "label": "屿岸训练场 · 东侧折返带", "family": "tpe", "fine_pt": 36,
         "medium_pt": 44, "coarse_pt": 20, "new_fine_pt": 37, "new_medium_pt": 43,
         "new_coarse_pt": 20, "max_clearance": 0.23, "max_reclaimed_pt": 45},
    ]),
    (lots, [
        {"code": "EP-1123-A", "donor_surface": "北端边线 · 第一段", "family": "epdm", "gross_g": 25500,
         "available_g": 25500, "state": "eligible", "sieve_revision": 1},
        {"code": "EP-1123-B", "donor_surface": "高校友谊赛 · 旧换材", "family": "epdm", "gross_g": 17200,
         "available_g": 17200, "state": "quarantined", "sieve_revision": 1},
        {"code": "EP-1123-C", "donor_surface": "球门缓冲线 · 拆补区域", "family": "epdm", "gross_g": 4800,
         "available_g": 4800, "state": "eligible", "sieve_revision": 1},
        {"code": "TP-1123-D", "donor_surface": "东侧折返带 · 雨后换材", "family": "tpe", "gross_g": 9200,
         "available_g": 9200, "state": "awaiting", "sieve_revision": 0},
    ]),
    (screens, [
        {"code": "EP-1123-A-1", "lot_code": "EP-1123-A", "revision": 1, "fine_g": 150, "medium_g": 630,
         "coarse_g": 220, "foreign_g": 0, "zero_mode": "none", "decision": "passed", "chemist": "operator@demo.test"},
        {"code": "EP-1123-B-1", "lot_code": "EP-1123-B", "revision": 1, "fine_g": 124, "medium_g": 723,
         "coarse_g": 129, "foreign_g": 24, "zero_mode": "none", "decision": "foreign_material", "chemist": "operator@demo.test"},
        {"code": "EP-1123-C-1", "lot_code": "EP-1123-C", "revision": 1, "fine_g": 0, "medium_g": 775,
         "coarse_g": 218, "foreign_g": 7, "zero_mode": "below_limit", "decision": "passed", "chemist": "operator@demo.test"},
    ]),
)
