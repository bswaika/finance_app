from __future__ import annotations

from uuid import UUID

from pydantic import BaseModel


class CustomReportBase(BaseModel):
    name: str
    description: str | None = None
    sql_query: str


class CustomReportCreate(CustomReportBase):
    pass


class CustomReportUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    sql_query: str | None = None


class CustomReportRead(CustomReportBase):
    id: UUID


