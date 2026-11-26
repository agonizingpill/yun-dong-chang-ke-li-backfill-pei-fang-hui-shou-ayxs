from typing import Annotated

from pydantic import Field, StringConstraints, field_validator

from domain.schema import Input


GridRef = Annotated[str, StringConstraints(pattern=r"^[A-D][1-8]$")]
Depth = Annotated[int, Field(ge=0, le=35)]


class MarkPatch(Input):
    grid_refs: Annotated[list[GridRef], Field(min_length=1, max_length=8)]

    @field_validator("grid_refs")
    @classmethod
    def unique_cells(cls, refs):
        if len(set(refs)) != len(refs):
            raise ValueError("划定的网格有重复")
        return refs


class MeasureDepth(Input):
    first_mm: Depth
    middle_mm: Depth
    last_mm: Depth
    repeat_of: Annotated[int, Field(gt=0)] | None = None
