from asyncio import get_event_loop
from collections import defaultdict
from typing import Optional, Callable

import aiohttp

from .http import HTTPClient
from .ws import WebSocketHandler


class Client:
    """
    Base pyvolt client.

    Attributes
    ----------
    client: aiohttp.ClientSession
        The aiohttp client session.
    http: pyvolt.HTTPClient
        The http handler.
    ws: pyvolt.WebSocketHandler
        The websocket handler.
    listeners: dict
        A dictionary of listeners.
    raw_listeners: dict
        A dictionary of raw listeners.
    loop: asyncio.AbstractEventLoop
        The event loop.

    Methods
    -------
    TODO
    """

    def __init__(self):
        self.client = aiohttp.ClientSession()
        self.http: HTTPClient
        self.ws: WebSocketHandler
        self.listeners = defaultdict(list)
        self.raw_listeners = {}
        self.loop = get_event_loop()

    def listen(self, event: str, *, raw: Optional[bool] = False):
        """
        Registers a function to listen for an event.

        Parameters
        ----------
        func: Callable
            The function to call when the event is triggered.
        event: str
            The event to listen for.
        raw: bool
            Whether or not to listen for raw events.
        """

        def inner(func: Callable[[dict[any, any]], any]):
            if raw:
                self.raw_listeners[
                    event.lower()] = func  # Only 1 raw listener per event because the raw listener dispatches the processed payload
            else:
                self.listeners[event.lower()].append(func)  # Multiple listeners for the non-raw
            return func

        return inner  # Returns the function so the user can use it by itself

    def run(self, token: str):
        """
        Run the client.

        Parameters
        ----------
        token: str
            The bot token.
        """
        self.http = HTTPClient(self.client, token)
        self.ws = WebSocketHandler(self.client, self.http, token, self.raw_dispatch)
        self.loop.run_until_complete(self.ws.connect())

    async def dispatch(self, event: str, *args, **kwargs):
        for func in self.listeners[event.lower()]:
            await func(*args, **kwargs)
    
    async def raw_dispatch(self, payload: dict[any, any]):
        event = payload["type"].lower()  # Subject to change
        if event.lower() in self.raw_listeners:
            await self.raw_listeners[event.lower()](payload)
