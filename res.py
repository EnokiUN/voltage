import os

from dotenv import load_dotenv

import voltage

client = voltage.Client()


@client.listen("message", raw=True)
async def my_message_listener_any_name_is_ok(payload):
    if payload["content"] == "-ping":
        await client.http.send_message(payload["channel"], "pong")
    if payload["content"] == "-embed":
        await client.http.send_message(payload["channel"], "h", embeds=[{"title": "h"}])


@client.listen("ready", raw=True)
async def on_ready_function(payload):
    print("Started bot")


load_dotenv()
client.run(os.getenv("token"))
