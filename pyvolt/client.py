from asyncio import get_event_loop
from typing import Optional, Callable, Any
import aiohttp

from .http import HttpHandler
from .ws import WebSocketHandler


class Client:
    """
    Base pyvolt client.

    Attributes:
        client: aiohttp.ClientSession
            The aiohttp client session.
        http: pyvolt.HttpHandler  
            The http handler.
        ws: pyvolt.WebSocketHandler
            The websocket handler.
        listeners: dict
            A dictionary of listeners.
        raw_listeners: dict
            A dictionary of raw listeners.
        loop: asyncio.AbstractEventLoop
            The event loop.
    """

    def __init__(self):
        self.client = aiohttp.ClientSession()
        self.http = None
        self.ws = None
        self.listeners = {}
        self.raw_listeners = {}
        self.loop = get_event_loop()

    def listen(self, event: str, raw: Optional[bool]=False):
        """
        Registers a function to listen for an event.

        Args:
            event: str
                The event to listen for.
            raw: bool
                Whether or not to listen for raw events.
        """
        def inner(func: Callable[[dict[any, any]], any]):
            if raw:
                self.raw_listeners[event.lower()] = func
            else:
                self.listeners[event.lower()] = func
            return func
        return inner

    def run(self, token: str):
        """
        Run the client.
        """
        self.http = HttpHandler(self.client, token)
        self.ws = WebSocketHandler(self.client, self.http, token, self.dispatch, self.raw_dispatch)
        self.loop.run_until_complete(self.ws.connect())

    async def dispatch(self, event: str, *args, **kwargs):
        if event.lower() in self.listeners:
            await self.listeners[event.lower()](*args, **kwargs)
    
    async def raw_dispatch(self, payload: dict[any, any]):
        event = payload["type"].lower()
        if event.lower() in self.raw_listeners:
            await self.raw_listeners[event.lower()](payload)
