from __future__ import annotations

import sys
from importlib import import_module, reload
from inspect import _empty
from types import ModuleType
from typing import TYPE_CHECKING, Any, Awaitable, Callable, Optional, Union, Type

# internal imports
from voltage import Client, CommandNotFound, Message, SendableEmbed

from .command import Command, CommandContext

if TYPE_CHECKING:
    from .cog import Cog
    from .help import HelpCommand


class CommandsClient(Client):
    """
    A class representing a client that uses commands.

    Attributes
    ----------
    prefix: Union[str, list[str], Callable[[Message, CommandsClient], Awaitable[Any]]]
        The prefixes that the client will respond to.
    help_command: Type[HelpCommand]
        The help command class.
    commands: dict[str, Command]
        The commands that the client will respond to.
    cogs: List[:class:`Cog`]
        The cogs that are loaded.
    extensions: dict[str, tuple[ModuleType, str]]
        The extensions that are loaded.
    """
    __slots__ = ("cogs", "extensions", "help_command", "prefix", "commands")

    def __init__(self, prefix: Union[str, list[str], Callable[[Message, CommandsClient], Awaitable[Any]]], help_command: Type[HelpCommand] = HelpCommand):
        super().__init__()
        self.listeners = {"message": self.handle_commands}
        self.prefix = prefix
        self.cogs: dict[str, Cog] = {}
        self.extensions: dict[str, tuple[ModuleType, str]] = {}
        self.help_command = help_command(self)
        self.commands: dict[str, Command] = {
            "help": Command(self.help, "help", "Displays help for a command.", ["h", "help"], None)
        }

    async def help(self, ctx: CommandContext, target: Optional[str] = None):
        """
        Basic help command.
        """
        if target is None:
            return await self.help_command.send_help(ctx)
        elif command := self.commands.get(target):
            return await self.help_command.send_command_help(ctx, command)
        elif cog := self.cogs.get(target):
            return await self.help_command.send_cog_help(ctx, cog)
        await ctx.reply(f"Command {target} not found.")

    async def get_prefix(
        self, message: Message, prefix: Union[str, list[str], Callable[[Message, CommandsClient], Awaitable[Any]]]
    ) -> str:
        if message.content is None:
            raise ValueError("Message content is None.")
        if isinstance(prefix, str):
            return prefix
        elif isinstance(prefix, list):
            for p in prefix:
                if message.content.startswith(p):
                    return p
        elif callable(prefix):
            return await self.get_prefix(message, await prefix(message, self))
        return str(prefix)

    def add_command(self, command: Command):
        """
        Adds a command to the client.

        Parameters
        ----------
        command: :class:`Command`
            The command to add.
        """
        for alias in command.aliases:
            if alias in self.commands:
                raise ValueError(f"Command {alias} already exists.")
            self.commands[alias] = command

    def add_cog(self, cog: Cog):
        """
        Adds a cog to the client.

        Parameters
        ----------
        cog: :class:`Cog`
            The cog to add.
        """
        self.cogs[cog.name] = cog
        for command in cog.commands:
            self.add_command(command)
        if func := cog.listeners.get("load"):
            func()

    def remove_cog(self, cog: Cog) -> Cog:
        """
        Removes a cog from the client.

        Parameters
        ----------
        cog: :class:`Cog`
            The cog to remove.

        Returns
        -------
        :class:`Cog`
            The cog that was removed.
        """
        items = list(self.commands.items())
        for command_name, command in items:
            if command.cog:
                if command.cog.name == cog.name:
                    cmd = self.commands.pop(command_name)
                    del cmd
        cog = self.cogs.pop(cog.name)
        if func := cog.listeners.get("unload"):
            func()
        return cog

    def add_extension(self, path: str, *args, **kwargs):
        """
        Adds an extension to the client.

        Parameters
        ----------
        path: :class:`str`
            The path to the extension as a python dotpath.
        """
        module = import_module(path)
        cog = module.setup(self, *args, **kwargs)
        self.extensions[path] = (module, cog.name)
        if not hasattr(module, "setup"):
            raise AttributeError(f"Extension {path} does not have a setup function.")
        reload(module)
        self.add_cog(cog)

    def reload_extension(self, path: str):
        """
        Reloads an extension.

        Parameters
        ----------
        path: :class:`str`
            The path to the extension as a python dotpath.
        """
        self.remove_extension(path)
        self.add_extension(path)

    def remove_extension(self, path: str):
        """
        removes an extension.

        Parameters
        ----------
        path: :class:`str`
            The path to the extension as a python dotpath.
        """
        if not path in self.extensions:
            raise KeyError(f"Extension {path} does not exist.")
        module, name = self.extensions.pop(path)
        cog = self.remove_cog(self.cogs[name])
        del cog
        del module
        del name
        mod = sys.modules.pop(path)
        del mod

    def command(
        self, name: Optional[str] = None, description: Optional[str] = None, aliases: Optional[list[str]] = None
    ):
        """
        A decorator for adding commands to the client.

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

    async def cog_dispatch(self, event: str, cog: Cog, *args, **kwargs):
        if func := cog.listeners.get(event):
            if self.error_handlers.get(event):
                try:
                    await func(*args, **kwargs)
                except Exception as e:
                    await self.error_handlers[event](e, *args, **kwargs)
            else:
                await func(*args, **kwargs)

    async def dispatch(self, event: str, *args, **kwargs):
        event = event.lower()

        for i in self.waits.get(event, []):
            if i[0](*args, **kwargs):
                i[1].set_result(*args, **kwargs)
                self.waits[event].remove(i)

        for cog in self.cogs.values():
            self.loop.create_task(self.cog_dispatch(event, cog, *args, **kwargs))

        if func := self.listeners.get(event):
            if self.error_handlers.get(event):
                try:
                    await func(*args, **kwargs)
                except Exception as e:
                    await self.error_handlers[event](e, *args, **kwargs)
            else:
                await func(*args, **kwargs)

    async def cog_raw_dispatch(self, event: str, cog: Cog, payload: dict[Any, Any]):
        if func := cog.raw_listeners.get(event):
            await func(payload)

    async def raw_dispatch(self, payload: dict[Any, Any]):
        event = payload["type"].lower()

        for cog in self.cogs.values():
            self.loop.create_task(self.cog_raw_dispatch(event, cog, payload))

        if func := self.raw_listeners.get(event):
            await func(payload)

    async def handle_commands(self, message: Message):
        prefix = await self.get_prefix(message, self.prefix)
        if message.content is None:
            return
        if message.content.startswith(prefix):
            content = message.content[len(prefix) :]
            command = content.split(" ")[0]
            if not command:
                return
            if command in self.commands:
                if "command" in self.error_handlers:
                    try:
                        return await self.commands[command].invoke(
                            CommandContext(message, self.commands[command], self, prefix), prefix
                        )
                    except Exception as e:
                        return await self.error_handlers["command"](
                            e, CommandContext(message, self.commands[command], self, prefix)
                        )
                return await self.commands[command].invoke(
                    CommandContext(message, self.commands[command], self, prefix), prefix
                )
            raise CommandNotFound(command)
