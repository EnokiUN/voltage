from __future__ import annotations

from asyncio import gather
from inspect import Parameter, _empty, isclass, ismethod, signature
from itertools import zip_longest
from shlex import split
from typing import TYPE_CHECKING, Any, Awaitable, Callable, Optional, Union

# internal imports
from voltage import Member, MemberNotFound, Message, NotEnoughArgs, User, UserNotFound

from . import converters

if TYPE_CHECKING:
    from .check import Check
    from .client import CommandsClient
    from .cog import Cog


async def dummy_func(self, *args, **kwargs):
    return NotImplemented


class CommandContext:
    """
    A context for a command.

    Attributes
    ----------
    message: :class:`voltage.Message`
        The message that invoked the command.
    content: :class:`str`
        The content of the message that invoked the command.
    author: Union[:class:`voltage.User`, :class:`voltage.Member`]
        The author of the message that invoked the command.
    channel: :class:`voltage.Channel`
        The channel that the command was invoked in.
    server: :class:`voltage.Server`
        The server that the command was invoked in.
    command: :class:`Command`
        The command that was invoked.
    prefix: :class:`str`
        The prefix used to invoke the command.
    """

    __slots__ = (
        "message",
        "content",
        "author",
        "channel",
        "server",
        "send",
        "typing",
        "reply",
        "delete",
        "command",
        "me",
        "client",
        "prefix",
    )

    def __init__(self, message: Message, command: Command, client: CommandsClient, prefix: str):
        self.message = message
        self.content = message.content
        self.author = message.author
        self.channel = message.channel
        self.server = message.server
        self.reply = message.reply
        self.delete = message.delete
        self.command = command
        self.client = client

        self.send = getattr(message.channel, "send", dummy_func)
        self.typing = getattr(message.channel, "typing", dummy_func)
        if message.server:
            self.me: Optional[Member] = client.cache.get_member(
                message.server.id, client.user.id)
        else:
            self.me = None

        self.prefix = prefix


class Command:
    """
    A class representing a command.

    Attributes
    ----------
    name: :class:`str`
        The name of the command.
    description: Optional[:class:`str`]
        The description of the command.
    aliases: Optional[List[:class:`str`]]
        The aliases of the command.
    cog: Optional[:class:`Cog`]
        The cog that the command belongs to.
    checks: list[:class:`Check`]
        The checks that must be passed for the command to be invoked.
    usage: str
        The usage of the command.
    """

    __slots__ = ("func", "name", "description", "aliases",
                 "error_handler", "signature", "cog", "checks", "usage_str", "subclassed")

    def __init__(
        self,
        func: Callable[..., Awaitable[Any]],
        name: Optional[str] = None,
        description: Optional[str] = None,
        aliases: Optional[list[str]] = None,
        cog: Optional[Cog] = None,
    ):
        self.func = func
        self.name = name or func.__name__
        self.description = description or func.__doc__
        self.aliases = aliases or [self.name]
        self.error_handler: Optional[Callable[[
            Exception, CommandContext], Awaitable[Any]]] = None
        self.signature = signature(func)
        self.cog = cog
        self.checks: list[Check] = []
        self.subclassed = False

        self.usage_str = ""

    @property
    def usage(self) -> str:
        """
        The usage of the command.
        """
        if self.usage_str:
            return self.usage_str
        usage = list()
        start = 2 if self.subclassed else 1
        for name, param in list(self.signature.parameters.items())[start:]:
            if param.default is not _empty:
                if param.default is not _empty and param.default is not None:
                    usage.append(f"[{name}={param.default}]")
                else:
                    usage.append(f"[{name}]")
            else:
                usage.append(f"<{name}>")

        self.usage_str = f"{self.name} {' '.join(usage)}"
        return self.usage_str

    def error(self, func: Callable[[Exception, CommandContext], Awaitable[Any]]):
        """
        Sets the error handler for this command.

        Parameters
        ----------
        func: :class:`Callable[[Exception, CommandContext], Awaitable[Any]]`
            The function to call when an error occurs.
        """
        self.error_handler = func
        return self

    async def convert_arg(self, arg: Parameter, given: str, context: CommandContext) -> Any:
        annotation = arg.annotation
        if isinstance(annotation, str):
            return given
        if given is None:
            return None
        elif annotation is _empty or annotation is Any or issubclass(annotation, str):
            return given
        if isclass(annotation):
            if issubclass(annotation, converters.Converter):
                return await annotation().convert(context, given)
            if func := getattr(converters, f"{annotation.__name__.capitalize()}Converter", None):
                return await func().convert(context, given)
        return str(given)

    async def invoke(self, context: CommandContext, prefix: str):
        if context.content is None:
            return
        if self.checks:
            results = await gather(*[check.check(context) for check in self.checks])
            if any([check is False for check in results]):
                return

        start_index = 2 if self.subclassed else 1

        if len((params := self.signature.parameters)) > start_index:
            given = split(context.content[len(prefix + self.name):])
            args: list[str] = []
            kwargs = {}

            for i, (param, arg) in enumerate(zip_longest(list(params.items())[start_index:], given)):
                if param is None:
                    break
                name, data = param

                if data.kind == data.VAR_POSITIONAL or data.kind == data.POSITIONAL_OR_KEYWORD:
                    if arg is None:
                        if data.default is _empty:
                            raise NotEnoughArgs(
                                self, len(params) - 1, len(args))
                        arg = data.default
                    args.append(await self.convert_arg(data, arg, context))

                elif data.kind == data.KEYWORD_ONLY:
                    if i == len(params) - 2:
                        if arg is None:
                            if data.default is _empty:
                                raise NotEnoughArgs(
                                    self, len(params) - 1, len(given))
                            kwargs[name] = await self.convert_arg(data, data.default, context)
                            break
                        kwargs[name] = await self.convert_arg(data, " ".join(given[i:]), context)
                    else:
                        if arg is None:
                            if data.default is _empty:
                                raise NotEnoughArgs(
                                    self, len(params) - 1, len(given))
                            arg = data.default
                        kwargs[name] = await self.convert_arg(data, arg, context)

            coro = (
                self.func(self.cog, context, *args, **kwargs)
                if self.subclassed
                else self.func(context, *args, **kwargs)
            )

            if self.error_handler:
                try:
                    return await coro
                except Exception as e:
                    return await self.error_handler(e, context)
            return await coro

        coro = self.func(
            self.cog, context) if self.subclassed else self.func(context)

        if self.error_handler:
            try:
                return await coro
            except Exception as e:
                return await self.error_handler(e, context)
        return await coro


def command(name: Optional[str] = None, description: Optional[str] = None, aliases: Optional[list[str]] = None):
    """
    A decorator that creates a :class:`Command` from an asynchronous function.

    Parameters
    ----------
    name: Optional[:class:`str`]
        The name of the command.
    description: Optional[:class:`str`]
        The description of the command.
    aliases: Optional[List[:class:`str`]]
        The aliases of the command.
    """

    def decorator(func: Callable[..., Awaitable[Any]]):
        command = Command(func, name, description, aliases)
        return command

    return decorator
