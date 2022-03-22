from asyncio import get_event_loop
from typing import Any, Callable, Dict, Optional

import aiohttp

# Internal imports
from .internals import CacheHandler, HTTPHandler, WebSocketHandler


class Client:
    """
    Base voltage client.

    Attributes
    ----------
    cache_message_limit: :class:`int`
        The maximum amount of messages to cache.
    fancy_ready: :class:`bool`
        Whether or not to print a fancy ready message.

    Methods
    -------
    listen:
        Registers a function to listen for an event.
    run:
        Runs the client.
    """

    def __init__(self, *, cache_message_limit: int = 5000, fancy_ready: bool = True):
        self.cache_message_limit = cache_message_limit
        self.fancy_ready = fancy_ready
        self.client = aiohttp.ClientSession()
        self.http: HTTPHandler
        self.ws: WebSocketHandler
        self.listeners: Dict[str, Callable[..., Any]] = {}
        self.raw_listeners: Dict[str, Callable[[Dict], Any]] = {}
        self.loop = get_event_loop()
        self.cache: CacheHandler

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

        def inner(func: Callable[..., Any]):
            if raw:
                self.raw_listeners[event.lower()] = func
            else:
                self.listeners[event.lower()] = func # Why would we have more than one listener for the same event?
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
        self.http = HTTPHandler(self.client, token)
        self.cache = CacheHandler(self.http, self.loop, self.cache_message_limit)
        self.ws = WebSocketHandler(self.client, self.http, self.cache, token, self.dispatch, self.raw_dispatch)
        self.loop.run_until_complete(self.ws.connect())

    async def dispatch(self, event: str, *args, **kwargs):
        event = event.lower()
        if func := self.listeners.get(event):
            func(*args, **kwargs)

    async def raw_dispatch(self, payload: Dict[Any, Any]):
        event = payload["type"].lower()  # Subject to change
        if func := self.raw_listeners.get(event):
            func(payload)
