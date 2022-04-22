import voltage #import the voltage module
from voltage.ext import commands # importing commands for our client

client = commands.CommandsClient("!") # initialize our client

ungodly_words = ["sus", "baka", "suppose", "real", "amogus"] # create our list to iterate through and add items later

@client.listen('message') # specify what we're going to listen to
async def on_message(message): # the name for this can be anything you want it to be
  if any([word in message.content.lower() for word in ungodly words]): # run the if statement to trigger if the message has words in the array
    await message.reply("*GASP!* You can't say that word!") # reply to the message sent
    await message.delete() # delete the message afterwards
  elif message.content == "<@Your Bots ID>":
    message.reply("Pong!")
  await bot.handle_commands(message) 
  # Handle afterwards so other commands will work after the on_message, 

@commands.command(name="add_word") # Create our command
async def add_word(ctx, word): # Define our command
  ungodly_words.append(word.lower()) # Append to our list
  await ctx.send(f"Added `{word.lower()}` to the list of words!") # Tell user that the word was added to the list.
  
  
client.run("TOKEN") # run your bot
