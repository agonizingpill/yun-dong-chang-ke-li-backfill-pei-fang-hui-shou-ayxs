from enum import StrEnum

class Role(StrEnum):
    OPERATOR = 'operator'
    REVIEWER = 'reviewer'
    VIEWER = 'viewer'

WRITE = (Role.OPERATOR, Role.REVIEWER)
REVIEW = (Role.REVIEWER,)
READ = tuple(Role)
