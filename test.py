import json
import asyncio
import aiohttp

TOKEN = ""
headers = {
    "User-Agent": "Pyvolt (beta)",
    "Content-Type": "application/json"
}

api_url = "https://api.revolt.chat/"

# Send a request using an aiohttp client to the Revolt API
async def request(client: aiohttp.ClientSession, method: str, url: str, auth: bool =True, **kwargs):
    header = headers
    if auth:
        header["x-bot-token"] = TOKEN
    async with client.request(method, api_url + url, headers=header, **kwargs) as req:
        return await req.json()

async def hearbeat(websocket):
    while True:
        await websocket.ping()
        await asyncio.sleep(15)

async def main():
    async with aiohttp.ClientSession() as client:
        data = await request(client, "GET", "users/@me/")
        print(data)
        info = await request(client, "GET", "")
        print(info)
        websocket = await aiohttp.ClientSession().ws_connect(info["ws"])
        loop = asyncio.get_event_loop()
        loop.create_task(hearbeat(websocket))
        await websocket.send_json({"type": "Authenticate", "token": TOKEN})
        async for msg in websocket:
            payload = json.loads(msg.data)
            if payload["type"] == "Message":
                if payload["content"] == "ping":
                    await request(client, "POST", "channels/{}/messages/".format(payload["channel"]), json={"content": "Hello World!", "replies": [{"id": payload["_id"], "mention": True}], "embeds": [{"type": "text", "title": "Hello World!", "description": "This is an embed!", "color": 0xFF0000}]})

loop = asyncio.get_event_loop()
loop.run_until_complete(main())