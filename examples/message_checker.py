import voltage #import the voltage module

client = voltage.Client() # initialize our client

@client.listen('message') # specify what we're listening to
async def on_message(message): # the name for this can be anything you want it to be
  ungodly_words = ["sus", "baka", "suppose", "real", "amogus"] # create our list to iterate through later
  if ungodly_words in message.content.lower(): # run the if statement to trigger if a message is in the array
    await message.reply("*GASP!* You can't say that!") # reply to the message sent
    await message.delete() # delete the message afterwards

client.run("TOKEN") # run your bot
