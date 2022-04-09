import voltage  # Import voltage.
from voltage.ext import commands  # Importing the cog framework so we can use the cogs.


def setup(client) -> commands.Cog:  # The setup of the cog, you may replace client as whatever you named your client as but we'll use client as default.
    test = commands.Cog("Test", "Some commands for testing.")  # You may edit the description however you want, this will also be the description fo your cogs in the help command.

    # A example of a command in cog.
    @test.command()  # Setting up a cog comamnd.
    async def ping(ctx): # Defining a async function.
        """Sends Pong!""" # The command description.
        await ctx.reply("Pong")  # Sends Pong.

    return test  # Returning the cogs, this is needed to actually show and load the cog. 
