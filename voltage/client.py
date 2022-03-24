from __future__ import annotations

from asyncio import get_event_loop
from re import search
from typing import TYPE_CHECKING, Any, Callable, Dict, Optional

import aiohttp

# Internal imports
from .internals import CacheHandler, HTTPHandler, WebSocketHandler

if TYPE_CHECKING:
    from .user import User


class Client:
    """
    Base voltage client.

    Attributes
    ----------
    cache_message_limit: :class:`int`
        The maximum amount of messages to cache.
    user: :class:`User`
        The user of the client.

    Methods
    -------
    listen:
        Registers a function to listen for an event.
    run:
        Runs the client.
    """

    def __init__(self, *, cache_message_limit: int = 5000):
        self.cache_message_limit = cache_message_limit
        self.client = aiohttp.ClientSession()
        self.http: HTTPHandler
        self.ws: WebSocketHandler
        self.listeners: Dict[str, Callable[..., Any]] = {}
        self.raw_listeners: Dict[str, Callable[[Dict], Any]] = {}
        self.loop = get_event_loop()
        self.cache: CacheHandler
        self.user: User
        self.error_handlers: Dict[str, Callable[..., Any]] = {}

    def listen(self, event: str, *, raw: bool = False):
        """
        Registers a function to listen for an event.

        This function is meant to be used as a decorator.

        Parameters
        ----------
        func: Callable[..., Any]
            The function to call when the event is triggered.
        event: :class:`str`
            The event to listen for.
        raw: :class:`bool`
            Whether or not to listen for raw events.

        Examples
        --------

        .. code-block:: python3

            @client.listen("message")
            async def any_name_you_want(message):
                if message.content == "ping":
                    await message.channel.send("pong")

            # example of a raw event
            @client.listen("message", raw=True)
            async def raw(payload):
                if payload["content"] == "ping":
                    await client.http.send_message(payload["channel"], "pong")

        """

        def inner(func: Callable[..., Any]):
            if raw:
                self.raw_listeners[event.lower()] = func
            else:
                self.listeners[event.lower()] = func  # Why would we have more than one listener for the same event?
            return func

        return inner  # Returns the function so the user can use it by itself

    def error(self, event: str):
        """
        Registers a function to handle errors for a specific **non-raw** event.

        This function is meant to be used as a decorator.

        Parameters
        ----------
        event: :class:`str`
            The event to handle errors for.

        Examples
        --------

        .. code-block:: python3

            @client.error("message")
            async def message_error(error, message):
                if isinstance(error, IndexError): # You probably don't want to handle all the index errors like this but this is just an example.
                    await message.reply("Not enough arguments.")

        """

        def inner(func: Callable[..., Any]):
            self.error_handlers[event.lower()] = func
            return func

        return inner

    def run(self, token: str):
        """
        Run the client.

        Parameters
        ----------
        token: :class:`str`
            The bot token.
        """
        self.loop.run_until_complete(self.start(token))

    async def start(self, token: str):
        """
        Start the client.

        Parameters
        ----------
        token: :class:`str`
            The bot token.
        """
        self.http = HTTPHandler(self.client, token)
        self.cache = CacheHandler(self.http, self.loop, self.cache_message_limit)
        self.ws = WebSocketHandler(self.client, self.http, self.cache, token, self.dispatch, self.raw_dispatch)
        await self.http.get_api_info()
        self.user = self.cache.add_user(await self.http.fetch_self())
        await self.ws.connect()

    async def dispatch(self, event: str, *args, **kwargs):
        event = event.lower()
        if func := self.listeners.get(event):
            if self.error_handlers.get(event):
                try:
                    await func(*args, **kwargs)
                except Exception as e:
                    await self.error_handlers[event](e, *args, **kwargs)
            else:
                await func(*args, **kwargs)

    async def raw_dispatch(self, payload: Dict[Any, Any]):
        event = payload["type"].lower()  # Subject to change
        if func := self.raw_listeners.get(event):
            await func(payload)

    def get_user(self, user: str) -> Optional[User]:
        """
        Gets a user from the cache by ID, mention or name.

        Parameters
        ----------
        user: :class:`str`
            The ID, mention or name of the user.

        Returns
        -------
        Optional[:class:`User`]
            The user.
        """
        if match := search(r"[0-9A-HJ-KM-NP-TV-Z]{26}", user):
            return self.cache.get_user(match.group(0))
        try:
            return self.cache.get_user(user.replace("@", ""), "name", case=False)
        except ValueError:
            return None
