# This example explains how to use client.wait_for() in voltage, which waits for a user message, and returns the voltage.Messageable object.

import voltage # Importing the main library

client = voltage.Client() # Initializing the client

@client.listen("message") # Tell our client to listen for a message
async def on_message(message): # The name for this function doesnt matter, but we'll be naming it on_message for this example.
  if message.content.lower() == "-send":
    await message.reply("Send me something nice!")
    messagegiven = await bot.wait_for("message", check=lambda message: message.author.id != bot.user.id, timeout=30) # Assign this to a variable as it returns a Messageable object for later.
    await message.reply(f"I appreciate the message, {message.author.name}, ill remember your words.. `{messagegiven.content()}`") # Replying with the message content sent by the user.

client.run("token") # Replace with your token string and run!
