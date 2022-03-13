import pyvolt

client = pyvolt.Client()

@client.listen("message", raw=True)
async def on_message(payload):
    if payload["content"] == "-ping":
        await client.http.send_message(payload["channel"], "pong")
    if payload["content"] == "-embed":
        await client.http.send_message(payload["channel"], "h", embeds=[{"title": "h"}])

client.run("TOKEN")
