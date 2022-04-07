import voltage

client = voltage.Client()

@client.listen('message')
async def on_message(message):
  ungodly_words = ["sus", "baka", "suppose", "real", "amogus"]
  if message.content.lower() in ungodly_words:
    await message.reply("*GASP!* You can't say that!")
    await message.delete()

client.run("TOKEN")
