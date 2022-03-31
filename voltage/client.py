from __future__ import annotations

from asyncio import Future, get_event_loop, wait_for
from re import search
from typing import TYPE_CHECKING, Any, Callable, Dict, Literal, Optional, Union

import aiohttp

# Internal imports
from .internals import CacheHandler, HTTPHandler, WebSocketHandler

if TYPE_CHECKING:
    from .channels import Channel
    from .enums import PresenceType
    from .member import Member
    from .server import Server
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
    members: List[:class:`Member`]
        The members the client has cached.
    servers: List[:class:`Server`]
        The servers the client is in.
    users: List[:class:`User`]
        The users the client has cached.
    channels: List[:class:`Channel`]
        The channels the client has cached.

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
        self.waits: Dict[str, list[tuple[Callable[..., bool], Future[Any]]]] = {}
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

    def run(self, token: str, *, bot: bool = True):
        """
        Run the client.

        Parameters
        ----------
        token: :class:`str`
            The bot token.
        bot: :class:`bool`
            Whether or not the client is a bot.
        """
        self.loop.run_until_complete(self.start(token, bot=bot))

    async def wait_for(
        self, event: str, *, timeout: Optional[float] = None, check: Optional[Callable[..., bool]] = None
    ) -> Any:
        """
        Waits for an event to be triggered.

        .. note::

            The event can be *anything*, be it a message, userupdate or whatever. :trol:

        Parameters
        ----------
        event: :class:`str`
            The event to wait for.
        timeout: Optional[:class:`float`]
            The amount of time to wait for the event to be triggered.
        check: Optional[Callable[..., bool]]
            A function to filter events to a matching predicate, ***must*** return a boolean for it to work properly.

        Raises
        ------
        :class:`asyncio.TimeoutError`
            If the event wasn't triggered within the timeout.

        Examples
        --------

        .. code-block:: python3

            import voltage

            client = voltage.Client()

            @client.listen("message")
            async def message(message):
                if message.content == "-wait":
                    await message.reply("Okay, send something")
                    await client.wait_for("message", check=lambda message: message.author == client.user)
                    await message.reply("You sent: " + message.content)

            client.run("token")

        """
        if check is None:
            check = lambda *_, **__: True

        future = self.loop.create_future()
        self.waits[event] = self.waits.get(event, []) + [(check, future)]

        return await wait_for(future, timeout)

    @property
    def servers(self) -> list[Server]:
        """The list of servers the client is in."""
        return list(self.cache.servers.values())

    @property
    def users(self) -> list[User]:
        """The list of users the client has cached."""
        return list(self.cache.users.values())

    @property
    def channels(self) -> list[Any]:
        """The list of channels the client has cached."""
        return list(self.cache.channels.values())

    @property
    def members(self) -> list[Member]:
        """The list of members the client has cached."""
        members: list[Member] = []
        for (server, servermembers) in self.cache.members.items():
            members += list(servermembers.values())
        return members

    async def start(self, token: str, *, bot: bool = True):
        """
        Start the client.

        Parameters
        ----------
        token: :class:`str`
            The bot token.
        bot: :class:`bool`
            Whether or not the client is a bot.
        """
        self.http = HTTPHandler(self.client, token, bot=bot)
        self.cache = CacheHandler(self.http, self.loop, self.cache_message_limit)
        self.ws = WebSocketHandler(self.client, self.http, self.cache, token, self.dispatch, self.raw_dispatch)
        await self.http.get_api_info()
        self.user = self.cache.add_user(await self.http.fetch_self())
        await self.ws.connect()

    async def dispatch(self, event: str, *args, **kwargs):
        event = event.lower()

        for i in self.waits.get(event, []):
            if i[0](*args, **kwargs):
                i[1].set_result(*args, **kwargs)
                self.waits[event].remove(i)

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

    def get_channel(self, channel_id: str) -> Optional[Channel]:
        """
        Gets a channel from the cache by ID.

        Parameters
        ----------
        channel_id: :class:`str`
            The ID of the channel.

        Returns
        -------
        Optional[:class:`Channel`]
            The channel.
        """
        try:
            return self.cache.get_channel(channel_id)
        except ValueError:
            return None

    def get_server(self, server_id: str) -> Optional[Server]:
        """
        Gets a server from the cache by ID.

        Parameters
        ----------
        server_id: :class:`str`
            The ID of the server.

        Returns
        -------
        Optional[:class:`Server`]
            The server.
        """
        try:
            return self.cache.get_server(server_id)
        except ValueError:
            return None

    async def set_status(self, text: Optional[str] = None, presence: Optional[PresenceType] = None):
        """
        Sets the client's status.

        Parameters
        ----------
        text: Optional[:class:`str`]
            The text to set the status to.
        presence: Optional[:class:`str`]
            The presence to set the status to.
        """
        data: dict[Literal["text", "presence"], Union[str, Literal["Online", "Busy", "Idle", "Offline"]]] = {}
        if text:
            data["text"] = text
        if presence:
            data["presence"] = presence.value
        await self.http.edit_self(status=data)
