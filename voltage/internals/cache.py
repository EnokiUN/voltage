from __future__ import annotations

from asyncio import AbstractEventLoop, gather
from time import time
from typing import TYPE_CHECKING, Any, Dict, Optional

from ..channels import Channel, DMChannel, create_channel
from ..errors import HTTPError
from ..member import Member
from ..message import Message
from ..server import Server
from ..user import User

# Internal imports
from .http import HTTPHandler
from .ws import WebSocketHandler

if TYPE_CHECKING:
    from ..types import (
        ChannelPayload,
        DMChannelPayload,
        MemberPayload,
        MessagePayload,
        OnReadyPayload,
        ServerPayload,
        UserPayload,
    )


class CacheHandler:
    """
    CacheHandler is a class that handles caching of messages, channels, members, servers, users and dm channels.

    It is used to reduce the amount of requests made to the revolt api.

    It stores the data in id-object pairs of dicts.

    It provides methods to get the object from the cache, or to add it to the cache.

    Atributes
    ---------
    message_limit: :class:`int`
        The maximum amount of messages to cache.
    """

    __slots__ = (
        "channels",
        "dm_channels",
        "http",
        "loop",
        "ws",
        "message_limit",
        "members",
        "messages",
        "servers",
        "users",
    )

    def __init__(self, http: HTTPHandler, loop: AbstractEventLoop, message_limit: int = 5000):
        self.http = http
        self.message_limit = message_limit
        self.loop = loop
        self.ws: WebSocketHandler

        self.messages: Dict[str, Message] = {}
        self.channels: Dict[str, Channel] = {}
        self.members: Dict[str, Dict[str, Member]] = {}
        self.servers: Dict[str, Server] = {}
        self.users: Dict[str, User] = {}
        self.dm_channels: Dict[str, DMChannel] = {}

    def get_message(self, message_id: str) -> Message:
        """
        Gets a message from the cache.

        Parameters
        ----------
        message_id: :class:`str`
            The id of the message to get.

        Returns
        -------
        :class:`Message`
            The message object from the cache.
        """
        return self.messages[message_id]

    def get_channel(self, channel_id: str) -> Channel:
        """
        Gets a channel from the cache.

        Parameters
        ----------
        channel_id: :class:`str`
            The id of the channel to get.

        Returns
        -------
        :class:`Channel`
            The channel object from the cache.
        """
        return self.channels[channel_id]

    def get_member(self, server_id: str, member_id: str) -> Member:
        """
        Gets a member from the cache.

        Parameters
        ----------
        server_id: :class:`str`
            The id of the server the member is in.
        member_id: :class:`str`
            The id of the member to get.

        Returns
        -------
        :class:`Member`
            The member object from the cache.
        """
        return self.members[server_id][member_id]

    def get_server(self, server_id: str) -> Server:
        """
        Gets a server from the cache.

        Parameters
        ----------
        server_id: :class:`str`
            The id of the server to get.

        Returns
        -------
        :class:`Server`
            The server object from the cache.
        """
        return self.servers[server_id]

    def get_user(self, user_id: str) -> User:
        """
        Gets a user from the cache.

        Parameters
        ----------
        user_id: str

        Returns
        -------
        :class:`User`
            The user object from the cache.
        """
        return self.users[user_id]

    def get_dm_channel(self, dm_channel_id: str) -> Optional[DMChannel]:
        """
        Gets a dm channel from the cache.

        Parameters
        ----------
        dm_channel_id: :class:`str`
            The id of the dm channel to get.

        Returns
        -------
        :class:`DMChannel`
            The dm channel object from the cache.
        """
        return self.dm_channels.get(dm_channel_id)

    async def fetch_message(self, server_id: str, message_id: str) -> Message:
        """
        Fetches a message from the api if it doesn't exist in the cache.

        Parameters
        ----------
        server_id: :class:`str`
            The id of the server the message is in.
        message_id: :class:`str`
            The id of the message to fetch.

        Returns
        -------
        :class:`Message`
            The message with the given id.
        """
        if message := self.messages.get(message_id):
            return message
        return self.add_message(await self.http.fetch_message(server_id, message_id))

    async def fetch_member(self, server_id: str, member_id: str) -> Member:
        """
        Fetches a member from the api if it doesn't exist in the cache.

        Parameters
        ----------
        server_id: :class:`str`
            The id of the server the member is in.
        member_id: :class:`str`
            The id of the member to fetch.

        Returns
        -------
        :class:`Member`
            The member with the given id.
        """
        if member := self.members[server_id].get(member_id):
            return member
        return self.add_member(server_id, await self.http.fetch_member(server_id, member_id))

    async def fetch_dm_channel(self, user_id: str) -> DMChannel:
        """
        Fetches a dm channel from the api if it doesn't exist in the cache.

        Parameters
        ----------
        user_id: :class:`str`
            The id of the user to fetch the dm channel of.

        Returns
        -------
        :class:`DMChannel`
            The dm channel with the given id.
        """
        if dm_channel := self.dm_channels.get(user_id):
            return dm_channel
        return self.add_dm_channel(await self.http.open_dm(user_id))

    def add_message(self, data: MessagePayload) -> Message:
        """
        Creates a message object and adds it to the cache if it doesn't exist already.

        Parameters
        ----------
        data: :class:`MessagePayload`
            The data of the message to add.

        Returns
        -------
        :class:`Message`
            The message that was added.
        """
        if message := self.messages.get(data["_id"]):
            return message
        message = Message(data, self)
        self.messages[message.id] = message
        if len(self.messages) > self.message_limit:
            self.messages.pop(next(iter(self.messages)))
        return message

    def add_channel(self, data: ChannelPayload) -> Channel:
        """
        Creates a channel object and adds it to the cache if it doesn't exist already.

        Parameters
        ----------
        data: :class:`ChannelPayload`
            The data of the channel to add.

        Returns
        -------
        :class:`Channel`
            The channel that was added.
        """
        if channel := self.channels.get(data["_id"]):
            return channel
        channel = create_channel(
            data,
            self,
            str(
                data.get(
                    "server",
                )
            ),
        )  # blame mypy
        self.channels[channel.id] = channel
        return channel

    async def add_channel_by_id(self, channel_id: str) -> Channel:
        """
        Fetches a channel object by it's id then caches it if it doesn't exist already.

        Parameters
        ----------
        channel_id: :class:`str`
            The id of the channel to add.

        Returns
        -------
        :class:`Channel`
            The channel that was added.
        """
        if channel := self.channels.get(channel_id):
            return channel
        try:
            return self.add_channel(await self.http.fetch_channel(channel_id))
        except HTTPError as e:
            if e.response.status != 404:
                raise

    def add_member(self, server_id: str, data: MemberPayload) -> Member:
        """
        Creates a member object and adds it to the cache if it doesn't exist already.

        Parameters
        ----------
        server_id: :class:`str`
            The id of the server the member is in.
        data: :class:`MemberPayload`
            The data of the member to add.

        Returns
        -------
        :class:`Member`
            The member that was added.
        """
        if server_id not in self.members:
            self.members[server_id] = {}
        if member := self.members[server_id].get(data["_id"]["user"]):
            return member
        server = self.get_server(server_id)
        member = Member(data, server, self)
        self.members[server_id][member.id] = member
        server._add_member(member)
        return member

    def add_server(self, data: ServerPayload) -> Server:
        """
        Creates a server object and adds it to the cache if it doesn't exist already.

        Parameters
        ----------
        data: :class:`ServerPayload`
            The data of the server to add.

        Returns
        -------
        :class:`Server`
            The server that was added.
        """
        if server := self.servers.get(data["_id"]):
            return server
        server = Server(data, self)
        self.servers[server.id] = server
        for channel in server.channel_ids:
            self.loop.create_task(self.add_channel_by_id(channel))
        return server

    def add_user(self, data: UserPayload) -> User:
        """
        Creates a user object and adds it to the cache if it doesn't exist already.

        Parameters
        ----------
        data: :class:`UserPayload`
            The data of the user to add.

        Returns
        -------
        :class:`User`
            The user that was added.
        """
        if user := self.users.get(data["_id"]):
            return user
        user = User(data, self)
        # Hello there future Enoki, I'm here to tell you that 1. yes that worked 2. yes you did that you fucking idiot 3. whatever your fix is it will probably break after a while.
        # What that line does? figure it out for yourself loser.

        # self.loop.create_task(user.fetch_profile())
        # Sham btw ^^^^^
        self.users[user.id] = user
        return user

    def add_dm_channel(self, data: DMChannelPayload) -> DMChannel:
        """
        Creates a dm channel object and adds it to the cache if it doesn't exist already.

        Parameters
        ----------
        data: :class:`DMChannelPayload`
            The data of the dm channel to add.

        Returns
        -------
        :class:`DMChannel`
            The dm channel that was added.
        """
        if dm_channel := self.get_dm_channel(data["_id"]):
            return dm_channel
        dm_channel = DMChannel(data, self)
        self.dm_channels[dm_channel.id] = dm_channel
        return dm_channel

    async def populate_server(self, server_id: str) -> Server:
        """
        Adds all the members of a server to the server object present in the cache.

        Parameters
        ----------
        server_id: :class:`str`
            The id of the server to populate.

        Returns
        -------
        :class:`Server`
            The server with the given id.
        """
        server = self.get_server(server_id)
        data = await self.http.fetch_members(server_id)
        for user in data["users"]:
            self.add_user(user)
        for member in data["members"]:
            if member["_id"]["user"] not in self.users:
                continue  # Ignore deleted accounts.
            self.add_member(server_id, member)
        return server

    async def populate_all_servers(self):
        """
        Adds all the members of all the servers to the server objects present in the cache.
        """
        await gather(*[self.populate_server(server_id) for server_id in self.servers])

    async def handle_ready_user(self, data: UserPayload):
        """
        Adds a user to the cache asynchroneously.

        Parameters
        ----------
        data: :class:`UserPayload`
            The data of the users to add.
        """
        self.add_user(data)

    async def handle_ready_channel(self, data: ChannelPayload):
        """
        Adds a channel to the cache asynchroneously.

        Parameters
        ----------
        data: :class:`ChannelPayload`
            The data of the channels to add.
        """
        self.add_channel(data)

    async def handle_ready_server(self, data: ServerPayload):
        """
        Adds a server to the cache asynchroneously.

        Parameters
        ----------
        data: :class:`ServerPayload`
            The data of the servers to add.
        """
        self.add_server(data)

    async def handle_ready_member(self, data: MemberPayload):
        """
        Adds a member to the cache asynchroneously.

        Parameters
        ----------
        data: :class:`MemberPayload`
            The data of the members to add.
        """
        self.add_member(data["_id"]["server"], data)

    async def handle_ready_caching(self, data: OnReadyPayload, ws: WebSocketHandler):
        self.ws = ws
        """
        Handles the caching of the ready event.
        """
        start = time()
        print("\033[1;34m[CACHE]      Started caching users.\033[0m")
        await gather(*[self.handle_ready_user(user) for user in data["users"]])
        print("\033[1;34m[CACHE]      Started caching servers.\033[0m")
        await gather(*[self.handle_ready_server(server) for server in data["servers"]])
        print("\033[1;34m[CACHE]      Started caching channels.\033[0m")
        await gather(*[self.handle_ready_channel(channel) for channel in data["channels"]])
        print("\033[1;34m[CACHE]      Started caching members.\033[0m")
        await gather(*[self.handle_ready_member(member) for member in data["members"]])
        print("\033[1;34m[CACHE]      Populating servers.\033[0m")
        await self.populate_all_servers()
        print(
            f"\033[1;32m[CACHE]      Finished caching {len(self.servers)} servers, {len(self.channels)} channels, {len(self.users)} users and {(sum([len(i) for i in self.members.values()]))} members in {time() - start:.2f} seconds.\033[0m"
        )
