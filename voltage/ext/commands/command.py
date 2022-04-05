from __future__ import annotations
from typing import TYPE_CHECKING, Any, Awaitable, Callable, Optional, Union

from inspect import Parameter, _empty, signature
from itertools import zip_longest
from shlex import split

from voltage import Message, User, Member, NotEnoughArgs, UserNotFound, MemberNotFound

if TYPE_CHECKING:
    from .client import CommandsClient
    from .cog import Cog


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
    """

    __slots__ = (
        "message",
        "content",
        "author",
        "channel",
        "server",
        "send",
        "reply",
        "delete",
        "command",
        "me",
        "client",
    )

    def __init__(self, message: Message, command: Command, client: CommandsClient):
        self.message = message
        self.content = message.content
        self.author = message.author
        self.channel = message.channel
        self.server = message.server
        self.reply = message.reply
        self.delete = message.delete
        self.command = command
        self.client = client

        self.send = getattr(message.channel, "send")
        if message.server:
            self.me: Optional[Member] = client.cache.get_member(message.server.id, client.user.id)
        else:
            self.me = None


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
    """

    __slots__ = ("func", "name", "description", "aliases", "error_handler", "signature", "cog")

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
        self.error_handler: Optional[Callable[[Exception, CommandContext], Awaitable[Any]]] = None
        self.signature = signature(func)
        self.cog = cog

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
        if given is None:
            return None
        elif isinstance(annotation, str):
            return given
        elif annotation is _empty or annotation is Any or issubclass(annotation, str):
            return given
        elif issubclass(annotation, int):
            return int(given)
        elif issubclass(annotation, float):
            return float(given)
        elif issubclass(annotation, Member):
            if context.server:
                member = context.server.get_member(given)
                if member is None:
                    raise MemberNotFound(given)
                return member
            raise MemberNotFound(given)
        elif issubclass(annotation, User):
            user = context.client.get_user(given)
            if user is None:
                raise UserNotFound(given)
            return user

    async def invoke(self, context: CommandContext, prefix: str):
        if context.content is None:
            return
        if len((params := self.signature.parameters)) > 1:
            given = split(context.content[len(prefix + self.name) :])
            args: list[str] = []
            kwargs = {}

            for i, (param, arg) in enumerate(zip_longest(list(params.items())[1:], given)):
                if param is None:
                    break
                name, data = param

                if data.kind == data.VAR_POSITIONAL or data.kind == data.POSITIONAL_OR_KEYWORD:
                    if arg is None:
                        if data.default is _empty:
                            raise NotEnoughArgs(self, len(params) - 1, len(args))
                        arg = data.default
                    args.append(await self.convert_arg(data, arg, context))

                elif data.kind == data.KEYWORD_ONLY:
                    if i == len(params) - 2:
                        if arg is None:
                            if data.default is _empty:
                                raise NotEnoughArgs(self, len(params) - 1, len(given))
                            kwargs[name] = await self.convert_arg(data, data.default, context)
                            break
                        kwargs[name] = await self.convert_arg(data, " ".join(given[i:]), context)
                    else:
                        if arg is None:
                            if data.default is _empty:
                                raise NotEnoughArgs(self, len(params) - 1, len(given))
                            arg = data.default
                        kwargs[name] = await self.convert_arg(data, arg, context)

            if self.error_handler:
                try:
                    return await self.func(context, *args, **kwargs)
                except Exception as e:
                    return await self.error_handler(e, context)
            return await self.func(context, *args, **kwargs)
        if self.error_handler:
            try:
                return await self.func(context)
            except Exception as e:
                return await self.error_handler(e, context)
        return await self.func(context)
