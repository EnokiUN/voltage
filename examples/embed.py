import voltage  # Import voltage.

client = voltage.Client()  # Initialize the client.


@client.listen("ping") # Listen for pings
async def on_ping(message):  # Doesn't matter what you call the function.
    embed = voltage.SendableEmbed(title="Cat", description="Cat", url="https://http.cat/200")
    # Reply to a message.
    await message.reply(content="Cat", embed=embed)  # You can use "#" if you don't want any content.


# Run the client
client.run("TOKEN")  # Replace with your token.
