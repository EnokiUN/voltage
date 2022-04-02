import voltage  # Import voltage.

client = voltage.Client()  # Initialize the client.


@client.listen("message")  # Listen for words.
async def badwords(message):  # Doesn't matter what you call the function.
    bad_words = ["fuck", "shit", "bitch", "slut"] # The words the revolt bot is looking for.
    if any(word in message.content for word in bad_words):
        await message.delete() # Deleting the words.
        await message.channel.send(f"{message.author.mention} you can't say that word!") # Send a message. 

# Run the client
client.run("TOKEN")  # Replace with your own token