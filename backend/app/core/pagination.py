from __future__ import annotations

from typing import Generic, Literal, TypeVar

from pydantic import BaseModel, Field

T = TypeVar("T")


class PageParams(BaseModel):
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=200)
    sort_by: str | None = None
    sort_dir: Literal["asc", "desc"] = "desc"


def offset_limit(page: int, page_size: int) -> tuple[int, int]:
    """Convert page/page_size to offset/limit for SQL queries."""
    offset = (page - 1) * page_size
    limit = page_size
    return (offset, limit)


class PageResult(BaseModel, Generic[T]):
    items: list[T]
    page: int
    page_size: int
    total: int
