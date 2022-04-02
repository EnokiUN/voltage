import voltage  # Import voltage.

client = voltage.Client()  # Initialize the client.


@client.listen("message")  # Listen for message.
async def suggestion(message):  # Doesn't matter what you call the function.
    if message.content == "Wake up Enoki!":
        channel = client.get_channel("YOUR CHANNEL UUID") # You get the channel.
        await channel.send("Enoki wake up!") # Sends "Enoki wake up!" to the channel.

# Run the client
client.run("TOKEN")  # Replace with your own token