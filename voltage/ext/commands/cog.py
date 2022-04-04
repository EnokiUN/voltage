from __future__ import annotations
from typing import TYPE_CHECKING, Optional, Callable, Any, Awaitable

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
    __slots__ = ('name', 'description', 'commands')

    def __init__(self, name: str, description: Optional[str] = None):
        self.name = name
        self.description = description
        self.commands: list[Command] = [] 

    def add_command(self, command: Command):
        """
        Adds a command to the cog.
        
        idk why you're doing thit but consider using the decorator for this /shrug.

        Parameters
        ----------
        command: :class:`Command`
            The command to add.
        """
        self.commands.append(command)

    def command(self, name: Optional[str] = None, description: Optional[str] = None, aliases: Optional[list[str]] = None):
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
            command = Command(func, name, description, aliases, self)
            self.add_command(command)
            return command
        return decorator
