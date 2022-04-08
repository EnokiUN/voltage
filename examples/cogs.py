import voltage  # Import voltage.
from voltage.ext import commands  # Import the framework.


def setup(client) -> commands.Cog:  # Setting up the cog.
    test = commands.Cog("Test", "Some commands for testing.")  # You may edit the description however you want.

    @test.command()  # Setting up a cog comamnd.
    async def ping(ctx):
        """Sends Pong!"""
        await ctx.reply("Pong")  # Sends Pong.

    return test  # Returning the cogs.
