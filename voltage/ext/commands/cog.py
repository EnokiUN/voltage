from __future__ import annotations

from typing import Any, Awaitable, Callable, Optional

from .command import Command


class Cog:
    """
    A class representing a cog.

    Attributes
    ----------
    name: :class:`str`
        The name of the cog.
    description: Optional[:class:`str`]
        The description of the cog.
    commands: List[:class:`Command`]
        The commands in the cog.
    """

    name: str
    description: Optional[str]
    commands: list[Command] = []
    listeners: dict[str, Callable[..., Any]] = {}
    raw_listeners: dict[str, Callable[..., Any]] = {}
    subclassed = False

    def __new__(cls, *args, **kwargs):
        cls.name = cls.__name__
        cls.description = cls.__doc__
        for (name, attr) in cls.__dict__.items():
            if isinstance(attr, Command):
                attr.subclassed = True
                cls.commands.append(attr)
                cls.subclassed = True
            elif isinstance(attr, Callable):
                if name.startswith("on_"):
                    cls.listeners[name[3:].lower()] = attr
                    cls.subclassed = True
                elif name.startswith("raw_"):
                    cls.raw_listeners[name[4:].lower()] = attr
                    cls.subclassed = True
        return super().__new__(cls)

    def __init__(self, name: str, description: Optional[str] = None):
        self.name = name
        self.description = description

    def listen(self, event: str, *, raw: bool = False):
        """
        Registers a function to listen for an event.

        This function is meant to be used as a decorator.

        Parameters
        ----------
        func: Callable[..., Any]
            The function to call when the event is triggered.
        event: :class:`str`
            The event to listen for.
        raw: :class:`bool`
            Whether or not to listen for raw events.

        Examples
        --------

        .. code-block:: python3

            Fun = Cog("Fun")

            @Fun.listen("message")
            async def any_name_you_want(message):
                if message.content == "ping":
                    await message.channel.send("pong")

            # example of a raw event
            @Fun.listen("message", raw=True)
            async def raw(payload):
                if payload["content"] == "ping":
                    await client.http.send_message(payload["channel"], "pong")

        """

        def inner(func: Callable[..., Any]):
            if raw:
                self.raw_listeners[event.lower()] = func
            else:
                self.listeners[event.lower()] = func
            return func

        return inner

    def add_command(self, command: Command):
        """
        Adds a command to the cog.

        idk why you're doing thit but consider using the decorator for this /shrug.

        Parameters
        ----------
        command: :class:`Command`
            The command to add.
        """
        if command.cog is not None:
            raise RuntimeError("Command already has a cog.")
        command.cog = self
        self.commands.append(command)

    def command(
        self, name: Optional[str] = None, description: Optional[str] = None, aliases: Optional[list[str]] = None
    ):
        """
        A decorator for adding commands to the cog.

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
            self.add_command(command)
            return command

        return decorator
