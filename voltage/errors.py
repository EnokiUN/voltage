from __future__ import annotations

from typing import TYPE_CHECKING

from aiohttp import ClientResponse

if TYPE_CHECKING:
    from .ext import Command


class VoltageException(Exception):
    """
    Base class for all Voltage exceptions. This could be used to catch all exceptions made from this library.
    """

    pass


class HTTPError(VoltageException):
    """
    Exception that's raised when an HTTP request operation fails.

    Attributes
    ----------
    response: aiohttp.ClientResponse
        The response of the failed HTTP request. This is an
        instance of :class:`aiohttp.ClientResponse`.
    status: int
        The status code of the HTTP request.
    """

    def __init__(self, response: ClientResponse):
        self.response = response


class CommandNotFound(VoltageException):
    """
    An exception that is raised when a command is not found.

    Attributes
    ----------
    command: :class:`str`
        The name of the command that was not found.
    """

    def __init__(self, command: str):
        self.command = command

    def __str__(self):
        return f"Command {self.command} not found"


class NotEnoughArgs(VoltageException):
    """
    An exception that is raised when not enough args are supplied.

    Attributes
    ----------
    command: :class:`Command`
        The command that was being called.
    expected: :class:`int`
        The number of args that were expected.
    actual: :class:`int`
        The number of args that were actually supplied.
    """

    def __init__(self, command: Command, expected: int, actual: int):
        self.command = command
        self.expected = expected
        self.actual = actual

    def __str__(self):
        return f"{self.command.name} expected {self.expected} args, got {self.actual}"


class UserNotFound(VoltageException):
    """
    An exception that is raised when a user is not found.

    Attributes
    ----------
    given: :class:`str`
        The name of the user that was not found.
    """

    def __init__(self, given: str):
        self.given = given

    def __str__(self):
        return f"User {self.given} not found"


class MemberNotFound(UserNotFound):
    """
    An exception that is raised when a member is not found.

    Attributes
    ----------
    given: :class:`str`
        The name of the member that was not found.
    """

    def __str__(self):
        return f"Member {self.given} not found"
