import voltage  # Import the Voltage module
from voltage.ext import commands  # Importing commands for our client

client = commands.CommandsClient("!")  # Initializing our client

ungodly_words = ["sus", "baka", "suppose", "real", "amogus"]  # Creating our list to iterate through and add items later


@client.listen("message")  # Specify what we're going to listen to
async def on_message(message):  # The name for this can be anything you want it to be
    if any(
        [word in message.content.lower() for word in ungodly_words]
    ):  # Run the if statement to trigger if the message has words in the array
        await message.reply(
            "*GASP!* You can't say that word!", delete_after=5
        )  # Reply to the message sent and delete OUR message after 5 seconds
        await message.delete()  # Delete the USERS message
    await bot.handle_commands(message)
    # Handle afterwards so other commands will work after the on_message,


@commands.command(name="add_word")  # Create our command
async def add_word(ctx, word):  # Define our command
    ungodly_words.append(word.lower())  # Append to our list
    await ctx.send(
        f"Added `{word.lower()}` to the list of `{len(ungodly_words)}` words!"
    )  # Tell user that the word was added to the list.


# P.S: When the bot goes offline, the list of words is cleared as its only a LOCAL array.

client.run("TOKEN")  # Run the bot
