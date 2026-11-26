from typing import Annotated, Literal
from pydantic import BaseModel, ConfigDict, Field, StringConstraints
from domain.rules import GRAM_STEP, ZeroMode

Code = Annotated[str, StringConstraints(strip_whitespace=True, pattern=r"^[A-Z0-9][A-Z0-9-]{2,23}$")]
Weight = Annotated[int, Field(ge=0, le=1000)]


class Input(BaseModel):
    model_config = ConfigDict(extra="forbid")


class Intake(Input):
    code: Code
    donor_surface: Annotated[str, StringConstraints(strip_whitespace=True, min_length=2, max_length=64)]
    family: Literal["epdm", "tpe"]
    gross_g: Annotated[int, Field(ge=1000, le=500_000)]


class Screen(Input):
    fine_g: Weight
    medium_g: Weight
    coarse_g: Weight
    foreign_g: Weight
    zero_mode: ZeroMode


class Preview(Input):
    zone_code: Code
    total_g: Annotated[int, Field(ge=1000, le=60_000, multiple_of=GRAM_STEP)]
    lot_codes: Annotated[list[Code], Field(min_length=1, max_length=2)]


class Reserve(Input):
    code: Code
    token: Annotated[str, StringConstraints(pattern=r"^[0-9a-f]{32}$")]


class Weigh(Input):
    line_code: Annotated[str, StringConstraints(min_length=1, max_length=32)]
    grams: Annotated[int, Field(gt=0, le=60_050, multiple_of=GRAM_STEP)]
