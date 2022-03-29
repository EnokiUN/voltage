import voltage  # Import voltage.

client = voltage.Client()  # Initialize the client.


@client.listen("message")
async def on_message(message):  # Doesn't matter what you call the function.
    if message.content.startswith("-ping"):
        embed = voltage.SendableEmbed(title="Cat", description="Cat", url="https://http.cat/200")
        # Reply to a message.
        await message.reply(content="Cat", embed=embed)  # You can use "#" if you don't want any content.


# Run the client which is an abstraction of calling the start coroutine.
client.run("TOKEN")  # Replace with your token.
