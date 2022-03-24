from __future__ import annotations

from asyncio import get_event_loop, sleep
from copy import copy
from json import loads
from typing import TYPE_CHECKING, Any, Callable, Dict

from ..enums import RelationshipType

if TYPE_CHECKING:
    from aiohttp import ClientSession, ClientWebSocketResponse

    from ..channels import GroupDMChannel
    from ..types.ws import *
    from .cache import CacheHandler
    from .http import HTTPHandler


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

    __slots__ = ("client", "http", "cache", "ws", "token", "dispatch", "raw_dispatch", "loop", "ready")

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
        self.ready = False

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
        user = self.cache.add_user(await self.http.fetch_self())
        print(
            f"""\033[1;31m                                                  
\033[1;31m                  **************                  \033[1;34mLibrary: Voltage
\033[1;31m               ***  ***************               \033[1;35mVersion: 0.1.4a4
\033[1;31m               ***   **************               \033[1;36mBot: {user}
\033[1;31m               ********************               \033[1;37mBot ID: {user.id}
\033[1;31m                         **********               \033[1;30mAPI endpoint: {self.http.api_url}
\033[1;31m          *************************  *****        
\033[1;31m      *****************************  ********     \033[1;32mGitHub: https://github.com/EnokiUN/voltage
\033[1;31m     ******************************  *********    \033[1;33mSupport server: https://rvlt.gg/bwtscg1F
\033[1;31m    *******************************  *********    
\033[1;31m    *****************************   **********    
\033[1;31m    ************                  ************    
\033[1;31m    **********   *****************************    
\033[1;31m    ********** *******************************    
\033[1;31m     ********  ******************************     
\033[1;31m      *******  *****************************      
\033[1;31m               **********                         
\033[1;31m               ********************               
\033[1;31m               ***************  ***               
\033[1;31m               **************    **               
\033[1;31m                *******************               
\033[1;31m                    ***********                   
\033[1;31m                                                  \033[0m"""
        )
        info = await self.http.get_api_info()
        ws_url = info["ws"]
        print(f"\033[1;31m[Voltage]    Connecting to the websocket...\033[0m")
        self.ws = await self.client.ws_connect(ws_url)
        await self.authorize()
        self.loop.create_task(self.heartbeat())
        print(f"\033[1;31m[Voltage]    Connected to {ws_url}!\033[0m")
        async for message in self.ws:
            payload = loads(message.data)
            self.loop.create_task(self.handle_event(payload))
            self.loop.create_task(self.raw_dispatch(payload))

    async def handle_event(self, payload: Dict[Any, Any]):
        """
        Handles an event.
        """
        event = payload["type"].lower()
        if event != "ready" and not self.ready:
            return
        if func := getattr(self, f"handle_{event}", None):
            await func(payload)

    async def handle_authenticated(self, _):
        """
        Handles the authenticated event.
        """
        pass

    async def handle_ready(self, payload: OnReadyPayload):
        """
        Handles the ready event.
        """
        print("\033[1;31m[Voltage]    Started caching data...\033[0m")
        await self.cache.handle_ready_caching(payload)
        print("\033[1;31m[Voltage]    Finished caching data.\033[0m")
        print("\033[1;32m[Voltage]    Bot is running!\033[0m")
        self.ready = True
        await self.dispatch("ready")

    async def handle_message(self, payload: OnMessagePayload):
        """
        Handles the message event.
        """
        await self.dispatch("message", self.cache.add_message(payload))

    async def handle_messageupdate(self, payload: OnMessageUpdatePayload):
        """
        Handles the message update event.
        """
        await self.dispatch("raw_message_update", payload)

        try:
            message = self.cache.get_message(payload["id"])
            old = copy(message)
            message._update(payload)
            await self.dispatch("message_update", old, message)
        except KeyError:
            return

    async def handle_messagedelete(self, payload: OnMessageDeletePayload):
        """
        Handles the message delete event.
        """
        await self.dispatch("raw_message_delete", payload)

        try:
            message = self.cache.get_message(payload["id"])
            self.cache.messages.pop(message.id)
            await self.dispatch("message_delete", message)
        except KeyError:
            return

    async def handle_channelcreate(self, payload: OnChannelCreatePayload):
        """
        Handles the channel create event.
        """
        await self.dispatch("channel_create", self.cache.add_channel(payload))

    async def handle_channelupdate(self, payload: OnChannelUpdatePayload):
        """
        Handles the channel update event.
        """
        channel = self.cache.get_channel(payload["id"])
        old = copy(channel)
        channel._update(payload)
        await self.dispatch("channel_update", old, channel)

    async def handle_channeldelete(self, payload: OnChannelDeletePayload):
        """
        Handles the channel delete event.
        """
        channel = self.cache.get_channel(payload["id"])
        self.cache.channels.pop(channel.id)
        await self.dispatch("channel_delete", channel)

    async def handle_groupchanneljoin(self, payload):
        """
        Handles the group channel join event.
        """
        channel = self.cache.get_channel(payload["id"])
        user = self.cache.get_user(payload["user"])
        if isinstance(channel, GroupDMChannel):
            channel.add_recepient(user)
            await self.dispatch("group_channel_join", channel, user)

    async def handle_groupchannelleave(self, payload):
        """
        Handles the group channel leave event.
        """
        channel = self.cache.get_channel(payload["id"])
        user = self.cache.get_user(payload["user"])
        if isinstance(channel, GroupDMChannel):
            channel.remove_recepient(user)
            await self.dispatch("group_channel_leave", channel, user)

    async def handle_channelstarttyping(self, payload: OnChannelStartTypingPayload):
        """
        Handles the channel start typing event.
        """
        channel = self.cache.get_channel(payload["id"])
        user = self.cache.get_user(payload["user"])
        await self.dispatch("channel_start_typing", channel, user)

    async def handle_channelstoptyping(self, payload: OnChannelDeleteTypingPayload):
        """
        Handles the channel stop typing event.
        """
        channel = self.cache.get_channel(payload["id"])
        user = self.cache.get_user(payload["user"])
        await self.dispatch("channel_stop_typing", channel, user)

    async def handle_serverupdate(self, payload: OnServerUpdatePayload):
        """
        Handles the server update event.
        """
        server = self.cache.get_server(payload["id"])
        old = copy(server)
        server._update(payload)
        await self.dispatch("server_update", old, server)

    async def handle_serverdelete(self, payload: OnServerDeletePayload):
        """
        Handles the server delete event.
        """
        server = self.cache.get_server(payload["id"])
        self.cache.servers.pop(server.id)
        await self.dispatch("server_delete", server)

    async def handle_servermemberupdate(self, payload: OnServerMemberUpdatePayload):
        """
        Handles the server member update event.
        """
        server = self.cache.get_server(payload["id"]["server"])
        member = server.get_member(server.id)
        if member:
            old = copy(member)
            member._update(payload)
            await self.dispatch("server_member_update", old, member)

    async def handle_servermemberjoin(self, payload: OnServerMemberJoinPayload):
        """
        Handles the server member join event.
        """
        try:
            self.cache.get_user(payload["user"])
        except KeyError:
            self.cache.add_user(await self.http.fetch_user(payload["user"]))
        member = self.cache.add_member(payload["id"], {"_id": {"server": payload["id"], "user": payload["user"]}})
        await self.dispatch("server_member_join", member)

    async def handle_memberleave(self, payload: OnServerMemberLeavePayload):
        """
        Handles the member leave event.
        """
        server = self.cache.get_server(payload["id"])
        member = server.get_member(payload["user"])
        if member:
            server.members.remove(member)
            await self.dispatch("member_leave", member)

    async def handle_serverroleupdate(self, payload: OnServerRoleUpdatePayload):
        """
        Handles the server role update event.
        """
        server = self.cache.get_server(payload["id"])
        role = server.get_role(payload["role_id"])
        if role:
            old = copy(role)
            role._update(payload)
            await self.dispatch("server_role_update", old, role)

    async def handle_serverroledelete(self, payload: OnServerRoleDeletePayload):
        """
        Handles the server role delete event.
        """
        server = self.cache.get_server(payload["id"])
        role = server.get_role(payload["role_id"])
        if role:
            server.roles.remove(role)
            await self.dispatch("server_role_delete", role)

    async def handle_userupdate(self, payload: OnUserUpdatePayload):
        """
        Handles the user update event.
        """
        user = self.cache.get_user(payload["id"])
        old = copy(user)
        user._update(payload)
        await self.dispatch("user_update", old, user)
