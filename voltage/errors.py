from __future__ import annotations

from typing import TYPE_CHECKING, Union

from aiohttp import ClientResponse

if TYPE_CHECKING:
    from .ext import commands
    from .member import Member
    from .user import User


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


class PermissionError(VoltageException):
    """
    An exception that's raised when the client doesn't have the required permissions to perform an action.
    """

    pass


class CommandNotFound(VoltageException):
    """
    An exception that's raised when a command is not found.

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

    def __init__(self, command: commands.Command, expected: int, actual: int):
        self.command = command
        self.expected = expected
        self.actual = actual

    def __str__(self):
        s = "s" if expected > 1 else ""
        return f"{self.command.name} expected {self.expected} arg{s}, got {self.actual}"


class NotFoundException(VoltageException):
    """
    An exception that is raised when a resource is not found.

    Attributes
    ----------
    resource: :class:`str`
        The name of the resource that was not found.
    """

    def __init__(self, resource: str):
        self.resource = resource

    def __str__(self):
        return f"{self.resource} not found"


class UserNotFound(NotFoundException):
    """
    An exception that is raised when a user is not found.
    """

    def __str__(self):
        return f"User {self.resource} not found"


class MemberNotFound(UserNotFound):
    """
    An exception that is raised when a member is not found.
    """

    def __str__(self):
        return f"Member {self.resource} not found"


class ChannelNotFound(NotFoundException):
    """
    An exception that is raised when a channel is not found.
    """

    def __str__(self):
        return f"Channel {self.resource} not found"


class RoleNotFound(NotFoundException):
    """
    An exception that is raised when a role is not found.
    """

    def __str__(self):
        return f"Role {self.resource} not found"


class NotBotOwner(VoltageException):
    """
    An exception that is raised when a user is not the bot owner.

    Called by the :func:`~voltage.ext.commands.is_owner` check

    Attributes
    ----------
    user: Union[:class:`voltage.User`, :class:`voltage.Member`]
        The user that tried to envoke the command.
    """

    def __init__(self, user: Union[User, Member]):
        self.user = user

    def __str__(self):
        return "You are not this bot's owner"


class NotEnoughPerms(VoltageException):
    """
    An exception that is raised when a user does not have enough permissions.

    Called by the :func:`~voltage.ext.commands.has_perms` check

    Attributes
    ----------
    user: Union[:class:`voltage.User`, :class:`voltage.Member`]
        The user that tried to envoke the command.
    """

    def __init__(self, user: Union[User, Member], perm: str):
        self.user = user
        self.perm = perm

    def __str__(self):
        return f"You do not have the {self.perm} permission required to use this command."


class BotNotEnoughPerms(VoltageException):
    """
    An exception that is raised when the bot does not have enough permissions.

    Called by the :func:`~voltage.ext.commands.has_perms` check

    Attributes
    ----------
    user: Union[:class:`voltage.User`, :class:`voltage.Member`]
        The user that tried to envoke the command.
    """

    def __init__(self, perm: str):
        self.perm = perm

    def __str__(self):
        return f"I am lacking the {self.perm} permission required to use this command."
