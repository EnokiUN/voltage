from __future__ import annotations

from typing import TYPE_CHECKING, Callable, Iterable, Optional, TypeVar, List

if TYPE_CHECKING:
    pass

T = TypeVar("T")


def get(base: Iterable[T], predicate: Callable[[T], bool]) -> Optional[T]:
    for item in base:
        if predicate(item):
            return item
    return None


def chunks(lst: List, size: int) -> List[List]:
    for i in range(0, len(lst), size):
        yield lst[i:i + size]
