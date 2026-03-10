"""
分页工具
"""

from typing import List, Any, Optional
from dataclasses import dataclass


@dataclass
class PageInfo:
    """分页信息"""

    page: int = 1
    page_size: int = 20
    total: int = 0

    @property
    def total_pages(self) -> int:
        """总页数"""
        if self.total == 0:
            return 0
        return (self.total + self.page_size - 1) // self.page_size

    @property
    def has_previous(self) -> bool:
        """是否有上一页"""
        return self.page > 1

    @property
    def has_next(self) -> bool:
        """是否有下一页"""
        return self.page < self.total_pages


@dataclass
class PaginatedResponse:
    """分页响应"""

    items: List[Any]
    page: int
    page_size: int
    total: int
    total_pages: int
    has_previous: bool
    has_next: bool


def paginate(
    items: List[Any],
    page: int,
    page_size: int,
    total: int,
) -> PaginatedResponse:
    """分页数据"""
    total_pages = (total + page_size - 1) // page_size if total > 0 else 0

    return PaginatedResponse(
        items=items,
        page=page,
        page_size=page_size,
        total=total,
        total_pages=total_pages,
        has_previous=page > 1,
        has_next=page < total_pages,
    )
