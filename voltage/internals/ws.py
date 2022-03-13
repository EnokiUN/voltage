from asyncio import get_event_loop, sleep
from json import loads
from typing import Callable, Any, Dict
from aiohttp import ClientSession, ClientWebSocketResponse

# Internal imports
from .http import HTTPHandler
from .cache import CacheHandler

class WebSocketHandler:
    """
    The base Voltage Websocket Handler.
    
    Attributes
    ----------
    client: aiohttp.ClientSession
        The aiohttp client session.
    http: voltage.HTTPHandler
        The http handler.
    ws: aiohttp.ClientWebSocketResponse
        The websocket.
    token: str
        The bot token.
    dispatch: Callable[..., Any]
        The dispatch function.
    raw_dispatch: Callable[[Dict[Any, Any]], Any]
        The raw dispatch function.
    loop: asyncio.AbstractEventLoop
        The event loop.
    """
    def __init__(self, client: ClientSession, http: HTTPHandler, token: str,
                 dispatch: Callable[..., Any],
                 raw_dispatch: Callable[[Dict[Any, Any]], Any]):
        self.loop = get_event_loop()
        self.client = client
        self.http = http
        self.ws: ClientWebSocketResponse
        self.token = token
        self.dispatch = dispatch
        self.raw_dispatch = raw_dispatch

    async def authorize(self):
        """
        Sends an authorization request to the websocket api.
        """
        await self.ws.send_json({"type": "Authenticate", "token": self.token})
    
    async def heartbeat(self):
        """
        Sends regular heartbeats to the websocket api.
        """
        while True:
            await self.ws.ping()
            await sleep(15)

    async def connect(self):
        """
        Starts the websocket.
        """
        info = await self.http.query_node()
        ws_url = info["ws"]
        self.ws = await self.client.ws_connect(ws_url)
        await self.authorize()
        self.loop.create_task(self.heartbeat())
        async for message in self.ws:
            payload = loads(message.data)
            self.loop.create_task(self.handle_event(payload))
            self.loop.create_task(self.raw_dispatch(payload))

    async def handle_event(self, payload: dict[any, any]):
        """
        Handles an event.
        """
        event = payload["type"].lower()
        if func := getattr(self, f"handle_{event}", None):
            await func(payload)

    async def handle_ready(self, payload: dict[any, any]):
        """
        Handles the ready event.
        """
        