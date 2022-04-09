from __future__ import annotations

from typing import Any


class _NotSupplied:
    """
    A stand in class for when a value is not supplied and we still want to use ``None``'s functionality'
    """

    def __eq__(self, other):
        return isinstance(other, NotSupplied)

    def __bool__(self):
        return False

    def __repr__(self):
        return "NotSupplied"


NotSupplied: Any = _NotSupplied()
