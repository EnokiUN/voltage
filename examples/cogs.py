import voltage 
from voltage.ext import commands

def setup(client) -> commands.Cog:
    test = commands.Cog("Test", "Some commands for testing.") # You may edit the description however you want.

    @test.command()
    async def ping(ctx):
        """Sends Pong!"""
        await ctx.reply("Pong") 

    return test # You returning the cogs.