# Ah shit here we go again
from __future__ import annotations

from typing import Any, Callable, Optional, Type, TypeVar, Union

# Typing, boooo
FB = TypeVar("FB", bound="FlagBase")
FV = TypeVar("FV", bound="FlagValue")


class FlagValue:
    """
    A class which represents a flag's value and provides an interface to interact with it.

    Attributes
    ----------
    value: :class:`int`
        The flag's value.
    """

    def __init__(self, func: Callable[[Any], int]):
        self.value = func(None)
        self.__doc__ = func.__doc__  # DOCUMENTATION GO BRRRRRRR

    def __get__(self: FV, instance: Optional[FB], owner: Type[FB]) -> Union[bool, FV]:
        if instance:
            return instance._has_flag(self.value)
        return self

    def __set__(self, instance: FB, value: bool):
        instance._set_flag(self.value, value)

    def __repr__(self):
        return f"<FlagValue {self.value!r}>"


# Important for flags, they all gotta inherit from this.
class FlagBase:
    """
    The base class for all voltage flags.

    Attributes
    ----------
    flags: :class:`int`
        The value of the flags.
    """

    __slots__ = ("flags",)

    def __init__(self, **kwargs: bool):
        self.flags = 0

        for k, v in kwargs.items():
            setattr(self, k, v)  # tfw self.__setattr__ isn't the "right" way to do this

    @classmethod
    def new_with_flags(cls, flags):  # Talk about convinience.
        """
        Creates a new instance of this class with the given flags.

        Parameters
        ----------
        flags: :class:`int`
            The flags to set.

        Returns
        -------
        :class:`FlagBase`
            The new instance.
        """
        inst = cls.__new__(cls)  # tfw cls() no work sometimes :/
        inst.flags = flags
        return inst

    def __eq__(self: FB, other: object) -> bool:
        if not isinstance(other, self.__class__):
            return NotImplemented
        return self.flags == other.flags

    def __ne__(self: FB, other: object) -> bool:
        return not self.__eq__(other)

    def __hash__(self):
        return hash(self.flags)

    def __repr__(self):
        return f"<{self.__class__.__name__} flags={self.flags:#x}>"

    def __iter__(self):
        for name, value in self.__class__.__dict__.items():
            if isinstance(value, FlagValue):
                yield name, value.__get__(self, self.__class__)

    def __or__(self: FB, other: FB) -> FB:
        return self.__class__.new_with_flags(self.flags | other.flags)

    def __and__(self: FB, other: FB) -> FB:
        return self.__class__.new_with_flags(self.flags & other.flags)

    def __xor__(self: FB, other: FB) -> FB:
        return self.__class__.new_with_flags(self.flags ^ other.flags)

    def __invert__(self: FB) -> FB:
        return self.__class__.new_with_flags(~self.flags)

    def __add__(self: FB, other: FB) -> FB:
        return self.__class__.new_with_flags(self.flags | other.flags)

    def __sub__(self: FB, other: FB) -> FB:
        return self.__class__.new_with_flags(self.flags & ~other.flags)

    def __le__(self: FB, other: FB) -> bool:
        return (self.flags & other.flags) == self.flags

    def __ge__(self: FB, other: FB) -> bool:
        return (self.flags | other.flags) == other.flags

    def __lt__(self: FB, other: FB) -> bool:
        return (self.flags <= other.flags) and self.flags != other.flags

    def __gt__(self: FB, other: FB) -> bool:
        return (self.flags > other.flags) and self.flags != other.flags

    def _has_flag(self: FB, flag: int) -> bool:
        return (self.flags & flag) == flag

    def _set_flag(self: FB, flag: int, value: bool):
        if value:
            self.flags |= flag
        else:
            self.flags &= ~flag


class UserFlags(FlagBase):
    """
    A class which represents a user's flags (aka badges).
    """

    @FlagValue
    def developer(self):
        """
        Whether the user has the developer badge.
        """
        return 1 << 0

    @FlagValue
    def translator(self):
        """
        Whether the user has the translator badge.
        """
        return 1 << 1

    @FlagValue
    def supporter(self):
        """
        Whether the user has the supporter badge.
        """
        return 1 << 2

    @FlagValue
    def responsible_disclosure(self):
        """
        Whether the user has the responsible disclosure badge.
        """
        return 1 << 3

    @FlagValue
    def founder(self):
        """
        Whether the user has the founder badge.
        """
        return 1 << 4

    @FlagValue
    def platform_moderator(self):
        """
        Whether the user has the platform moderator badge.
        """
        return 1 << 5

    @FlagValue
    def active_supporter(self):
        """
        Whether the user has the active supporter badge.
        """
        return 1 << 6

    @FlagValue
    def paw(self):
        """
        Whether the user has the paw badge.
        """
        return 1 << 7

    @FlagValue
    def early_adopter(self):
        """
        Whether the user has the early adopter badge.
        """
        return 1 << 8

    @FlagValue
    def reserved_relevant_joke_badge_1(self):
        """
        Whether the user has the relevant joke 1 (amogus) badge.
        """
        return 1 << 9
