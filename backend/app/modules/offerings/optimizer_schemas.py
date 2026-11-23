from uuid import UUID

from pydantic import BaseModel, Field


class GenerateScheduleRequest(BaseModel):
    term_id: UUID
    offering_ids: list[UUID] = Field(min_length=1, max_length=100)
    max_scenarios: int = Field(default=5, ge=1, le=10)


class GeneratedScenario(BaseModel):
    id: UUID
    name: str
    score: int
    offering_ids: list[UUID]


class GenerateScheduleResponse(BaseModel):
    scenarios: list[GeneratedScenario]
