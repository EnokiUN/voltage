import voltage  # Import voltage.
from voltage.ext import (  # Importing the commands framework so we that we're able to create a Cog object.
    commands,
)


# Next up is the setup function, aka where all the magic happens.
# This is what's actually called by the client to be used for `add_cog`.
# Here you define your cog, define its commands then return the cog so that the client is able to add it.
# Additionally, any args / kwargs you pass to the `client.add_extension` function will be passed to the setup function.
# The client is passed by default however.
def setup(client) -> commands.Cog:

    test = commands.Cog(  # Create a new Cog object.
        # Give it a name.  # And an optional description.
        "Test",
        "Some commands for testing.",
    )  # The name and description will be used in the help command.

    # Register a command as normal, difference is you use the Cog object instead of the client in the decorator.
    @test.command()
    async def ping(ctx):  # No self parameter.
        """Sends Pong!"""
        await ctx.reply("Pong from inside a Cog!")

    return test  # Finally, return the cog object.


# To load a Cog to the client you can use `client.add_extension(path, *args, **kwargs)` with the path being the Python dotpath to your file, args and kwargs are optional.

# discord.py style subclassed cogs are also supported but aren't "that" tested yet.


class MyCog(commands.Cog):
    """My beautiful Cog!."""  # Name and description are taken automatically from the class declaration, otherwise you could set them manually.

    def __init__(self, client):
        self.client = client

        # What setting the name and description manually looks like
        self.name = "My Cog"
        self.description = "My beautiful Cog!"

    @commands.command()
    async def ping(self, ctx):
        await ctx.reply("Pong from inside a Cog!")


# The setup function will still return with the cog object.


def setup(client) -> commands.Cog:
    return MyCog(client)
