from voltage.ext import commands  # Import the commands module from ``voltage.ext``

import voltage

client = commands.CommandsClient(
    "-"
)  # Create a CommandsClient (client that has commands (original ik)) with the prefix set to "-".


@client.listen("ready")  # You can still listen to events.
async def ready():
    print("Gaaah, It's rewind time.")


@client.command()  # Register a command using the ``command`` decorator.
async def ping(ctx):
    """Sends Pong!"""  # Name and description can be passed in the decorator or automatically inferred.
    await ctx.reply("Pong")  # Reply to the context's message.


# When you set a command's name explicitly the function's name is disregarded.
# Automatic type conversion is a thing I suppose.
@client.command(name="whois", description="Tells you who a person ***truly*** is", aliases=["wi"])
async def whoiscommand(ctx, person: voltage.Member):
    await ctx.reply("{0} is !!{0}!!".format(person.name))


client.run("TOKEN")  # Again, replace with your bot token.
