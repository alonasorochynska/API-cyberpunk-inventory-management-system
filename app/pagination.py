from fastapi import Request, HTTPException
from typing import List, Generic, TypeVar, Optional
from pydantic import BaseModel


T = TypeVar("T")


class PaginatedResponse(BaseModel, Generic[T]):
    page: int
    limit: int
    total_pages: int
    total_items: int
    items: List[T]
    next_page: Optional[str]
    prev_page: Optional[str]


def paginate(query, page: int, limit: int, request: Request):
    if page < 1 or limit < 1:
        raise HTTPException(status_code=400, detail="Page and limit must be greater than 0.")

    total_items = query.count()
    total_pages = (total_items + limit - 1) // limit
    skip = (page - 1) * limit
    items = query.offset(skip).limit(limit).all()

    next_page = None
    prev_page = None

    if page < total_pages:
        next_page = str(request.url.include_query_params(page=page + 1))

    if page > 1:
        prev_page = str(request.url.include_query_params(page=page - 1))

    return {
        "page": page,
        "limit": limit,
        "total_pages": total_pages,
        "total_items": total_items,
        "items": items,
        "next_page": next_page,
        "prev_page": prev_page
    }
