from __future__ import annotations
from typing import TYPE_CHECKING, Any, Callable, TypeVar, Optional

if TYPE_CHECKING:
    pass

T = TypeVar("T")

def get(base: list[T], predicate: Callable[[T], bool]) -> Optional[T]:
    for item in base:
        if predicate(item):
            return item
    return None

