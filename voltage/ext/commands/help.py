from __future__ import annotations
from typing import TYPE_CHECKING

from voltage import SendableEmbed

if TYPE_CHECKING:
    from .command import Command, CommandContext
    from .client import CommandsClient
    from .cog import Cog

class HelpCommand:
    """
    A simple subclassable help command.
    """
    def __init__(self, client: CommandsClient):
        self.client = client

    async def send_help(self, ctx: CommandContext):
        embed = SendableEmbed(
            title="Help",
            description=f"Use `{ctx.prefix}help <command>` to get help for a command.",
            colour="#fff0f0",
            icon_url=getattr(self.client.user.display_avatar, "url"),
        )
        text = "\n### **No Category**\n"
        for command in self.client.commands.values():
            if command.cog is None:
                text += f"> {command.name}\n"
        for i in self.client.cogs.values():
            text += f"\n### **{i.name}**\n{i.description}\n"
            for j in i.commands:
                text += f"\n> {j.name}"
        if embed.description:
            embed.description += text
        return await ctx.reply("Here, have a help embed", embed=embed)

    async def send_command_help(self, ctx: CommandContext, command: Command):
            embed = SendableEmbed(
                title=f"Help for {command.name}",
                colour="#0000ff",
                icon_url=getattr(self.client.user.display_avatar, "url"),
            )
            text = str()
            text += f"\n### **Usage**\n> `{ctx.prefix}{command.usage}`"
            if command.aliases:
                text += f"\n\n### **Aliases**\n> {ctx.prefix}{', '.join(command.aliases)}"
            embed.description = command.description + text if command.description else text
            return await ctx.reply("Here, have a help embed", embed=embed)

    async def send_cog_help(self, ctx: CommandContext, cog: Cog):
        embed = SendableEmbed(
            title=f"Help for {cog.name}",
            colour="#0000ff",
            icon_url=getattr(self.client.user.display_avatar, "url"),
        )
        text = str()
        text += f"\n### **Description**\n{cog.description}"
        text += f"\n\n### **Commands**\n"
        for command in cog.commands:
            text += f"> {ctx.prefix}{command.name}\n"
        embed.description = text
        return await ctx.reply("Here, have a help embed", embed=embed)

