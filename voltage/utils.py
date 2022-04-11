from __future__ import annotations
from typing import TYPE_CHECKING, Any, Callable, TypeVar, Optional, Iterable

if TYPE_CHECKING:
    pass

T = TypeVar("T")

def get(base: Iterable[T], predicate: Callable[[T], bool]) -> Optional[T]:
    for item in base:
        if predicate(item):
            return item
    return None

