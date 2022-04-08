import voltage  # Import voltage.

client = voltage.Client()  # Initialize the client.


@client.listen("message")  # Listen for pings
async def on_ping(message):  # Doesn't matter what you call the function.
    if message.content.startswith("embed"):
        # Create the embed. Most of these attributes are self-explanitory
        embed = voltage.SendableEmbed(
            title="Cat",  # The title of the embed
            description="Cat",  # The description of the embed
            colour="#DEADBF",  # The colour of the "strip" at the side of the embed
            icon_url=message.author.display_avatar.url,  # The icon beside the title of the embed. "message.author.display_avatar.url" gets the user's avatar.
            media="https://http.cat/200",  # The media for the embed. Here, we have an image.
        )
        # Reply to a message.
        await message.reply(content="Cat", embed=embed)  # You can use "#" if you don't want any content.


# Run the client
client.run("TOKEN")  # Replace with your own token
