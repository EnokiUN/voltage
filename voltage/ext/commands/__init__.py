"""
The built-in voltage commands framework.

Commands frameworks example:

.. code-block:: python3

    import voltage
    from voltage.ext import commands # Import the commands module from ``voltage.ext``

    client = commands.CommandsClient("-") # Create a CommandsClient (client that has commands (original ik)) with the prefix set to "-".

    @client.listen("ready") # You can still listen to events.
    async def ready():
        print("Gaaah, It's rewind time.")

    @client.command() # Register a command using the ``command`` decorator.
    async def ping(ctx): # Name and description can be passed in the decorator or automatically inferred.
        await ctx.reply("Pong") # Reply to the context's message.

    client.run("TOKEN") # Again, replace with your bot token.

"""

from .check import (
    Check as Check,
    bot_has_perms as bot_has_perms,
    check as check,
    has_perms as has_perms,
    is_owner as is_owner,
    is_server_owner,
)
from .client import CommandsClient as CommandsClient
from .cog import Cog as Cog, SubclassedCog as SubclassedCog
from .command import (
    Command as Command,
    CommandContext as CommandContext,
    command as command,
)
from .converters import Converter as Converter, converter as converter
from .help import HelpCommand as HelpCommand

__all__ = [
    "Check",
    "bot_has_perms",
    "check",
    "has_perms",
    "is_owner",
    "is_server_owner",
    "CommandsClient",
    "Cog",
    "SubclassedCog",
    "Command",
    "CommandContext",
    "command",
    "Converter",
    "converter",
    "HelpCommand",
]
