from __future__ import annotations
from asyncio import get_event_loop, sleep
from json import loads
from typing import TYPE_CHECKING, Any, Callable, Dict

if TYPE_CHECKING:
    from ..types import OnReadyPayload, OnMessagePayload
    from .http import HTTPHandler
    from .cache import CacheHandler
    from aiohttp import ClientSession, ClientWebSocketResponse

class WebSocketHandler:
    """
    The base Voltage Websocket Handler.

    Attributes
    ----------
    client: :class:`aiohttp.ClientSession`
        The aiohttp client session.
    http: :class:`voltage.internals.HTTPHandler`
        The http handler.
    cache: :class:`voltage.internals.CacheHandler`
        The cache handler.
    ws: :class:`aiohttp.ClientWebSocketResponse`
        The websocket.
    token: :class:`str`
        The bot token.
    dispatch: Callable[..., Any]
        The dispatch function.
    raw_dispatch: Callable[[Dict[Any, Any]], Any]
        The raw dispatch function.
    loop: :class:`asyncio.AbstractEventLoop`
        The event loop.
    """

    __slots__ = ("client", "http", "cache", "ws", "token", "dispatch", "raw_dispatch", "loop")

    def __init__(
        self,
        client: ClientSession,
        http: HTTPHandler,
        cache: CacheHandler,
        token: str,
        dispatch: Callable[..., Any],
        raw_dispatch: Callable[[Dict[Any, Any]], Any],
    ):
        self.loop = get_event_loop()
        self.client = client
        self.http = http
        self.cache = cache
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
        info = await self.http.get_api_info()
        ws_url = info["ws"]
        self.ws = await self.client.ws_connect(ws_url)
        await self.authorize()
        self.loop.create_task(self.heartbeat())
        async for message in self.ws:
            payload = loads(message.data)
            self.loop.create_task(self.handle_event(payload))
            self.loop.create_task(self.raw_dispatch(payload))

    async def handle_event(self, payload: Dict[Any, Any]):
        """
        Handles an event.
        """
        event = payload["type"].lower()
        if func := getattr(self, f"handle_{event}", None):
            await func(payload)

    async def handle_ready(self, payload: OnReadyPayload):
        """
        Handles the ready event.
        """
        await self.cache.handle_ready_caching(payload)
        await self.dispatch("ready")

    async def handle_message(self, payload: OnMessagePayload):
        """
        Handles the message event.
        """
        await self.dispatch("message", self.cache.add_message(payload))
