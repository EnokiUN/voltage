import voltage  # Import voltage.

client = voltage.Client()  # Initialize the client.


@client.listen("message")  # Listen for words.
async def badwords(message):  # Doesn't matter what you call the function.
    bad_words = ["fuck", "shit", "bitch", "slut"] # The words the revolt bot is looking for.
    for bad_words in message.content:
        await message.delete() # Deleting the words.

# Run the client
client.run("TOKEN")  # Replace with your own token