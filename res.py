import pyvolt

client = pyvolt.Client()


@client.listen("message")
def on_message(payload):
    if payload["content"] == "ping":
        client.send_message(payload["channel"], "Hello World!", [{"id": payload["_id"], "mention": True}], [
            {"type": "text", "title": "Hello World!", "description": "This is an embed!", "color": 0xFF0000}])


client.run("")
