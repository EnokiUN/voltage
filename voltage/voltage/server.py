from __future__ import annotations

from re import search
from typing import TYPE_CHECKING, Dict, List, Literal, Optional

from .asset import Asset
from .categories import Category
from .invites import Invite

# Internal imports
from .permissions import ChannelPermissions, ServerPermissions
from .roles import Role

if TYPE_CHECKING:
    from .channels import Channel
    from .internals import CacheHandler
    from .member import Member
    from .types import (
        BanPayload,
        OnServerUpdatePayload,
        ServerPayload,
        SystemMessagesConfigPayload,
    )
    from .user import User


class ServerBan:  # No idea why this exists tbh
    """
    A class which represents a Voltage server ban.

    Attributes
    ----------
    user: :class:`User`
        The user who was banned.
    server: :class:`Server`
        The server the user was banned from.
    reason: Optional[:class:`str`]
        The reason for the ban.
    """

    __slots__ = ("data", "cache", "reason", "user", "server")

    def __init__(self, data: BanPayload, cache: CacheHandler):
        self.data = data
        self.cache = cache
        self.reason = data.get("reason")
        self.user = cache.get_user(data["_id"]["user"])
        self.server = cache.get_server(data["_id"]["server"])

    async def unban(self):
        """
        Unbans the user from the server.
        """
        await self.cache.http.unban_member(self.server.id, self.user.id)


class SystemMessages:
    """
    A class that represents a Voltage server's system message configuration.

    Attributes
    ----------
    user_joined: Optional[:class:`Channel`]
        The channel the user joined message is configured to.
    user_left: Optional[:class:`Channel`]
        The channel the user left message is configured to.
    user_banned: Optional[:class:`Channel`]
        The channel the user banned message is configured to.
    user_kicked: Optional[:class:`Channel`]
        The channel the user kicked message is configured to.
    """

    __slots__ = ("data", "cache", "server")

    def __init__(self, data: SystemMessagesConfigPayload, cache: CacheHandler):
        self.data = data
        self.cache = cache

    @property
    def user_joined(self) -> Optional[Channel]:
        """
        The channel the user joined message is configured to.
        """
        return self.cache.get_channel(self.data.get("user_joined"))

    @property
    def user_left(self) -> Optional[Channel]:
        """
        The channel the user left message is configured to.
        """
        return self.cache.get_channel(self.data.get("user_left"))

    @property
    def user_kicked(self) -> Optional[Channel]:
        """
        The channel the user kicked message is configured to.
        """
        return self.cache.get_channel(self.data.get("user_kicked"))

    @property
    def user_banned(self) -> Optional[Channel]:
        """
        The channel the user banned message is configured to.
        """
        return self.cache.get_channel(self.data.get("user_banned"))


class Server:  # As of writing this this is the final major thing I have to implement before the lib is usable and sadly I am traveling in less than 12 hours so it's a race with time.
    """
    A class which represents a Voltage server.

    Attributes
    ----------
    id: :class:`str`
        The server's ID.
    name: :class:`str`
        The server's name.
    description: Optional[:class:`str`]
        The server's description.
    owner_id: :class:`str`
        The server's owner's ID.
    owner: :class:`User`
        The server's owner.
    nsfw: :class:`bool`
        Whether the server is NSFW or not.
    system_messages: Optional[:class:`SystemMessages`]
        The server's system message configuration.
    icon: Optional[:class:`Asset`]
        The server's icon.
    banner: Optional[:class:`Asset`]
        The server's banner.
    members: List[:class:`Member`]
        The server's members.
    channels: List[:class:`Channel`]
        The server's channels.
    roles: List[:class:`Role`]
        The server's roles.
    categories: List[:class:`Category`]
        The server's categories.
    """

    __slots__ = (
        "data",
        "cache",
        "id",
        "name",
        "description",
        "owner_id",
        "nsfw",
        "system_messages",
        "icon",
        "banner",
        "channel_ids",
        "member_ids",
        "default_channel_permissions",
        "default_role_permissions",
        "category_ids",
        "role_ids",
    )

    def __init__(self, data: ServerPayload, cache: CacheHandler):
        self.data = data
        self.cache = cache
        self.id = data["_id"]
        self.name = data["name"]
        self.description = data.get("description")
        self.owner_id = data["owner"]
        self.nsfw = data.get("nsfw", False)

        self.system_messages: Optional[SystemMessages]
        if system_messages := data.get("system_messages"):
            self.system_messages = SystemMessages(system_messages, cache)
        else:
            self.system_messages = None

        self.default_channel_permissions = ChannelPermissions.new_with_flags(data["default_permissions"][0])
        self.default_role_permissions = ServerPermissions.new_with_flags(data["default_permissions"][1])
        self.category_ids = {i["id"]: Category(i, cache) for i in data.get("categories", [])}

        self.icon: Optional[Asset]
        if icon := data.get("icon"):
            self.icon = Asset(icon, cache.http)
        else:
            self.icon = None

        self.banner: Optional[Asset]
        if banner := data.get("banner"):
            self.banner = Asset(banner, cache.http)
        else:
            self.banner = None

        self.channel_ids = [i for i in data.get("channels", [])]
        self.role_ids = {i: Role(data, i, self, cache.http) for i, data in data.get("roles", {}).items()}
        self.member_ids: Dict[str, Member] = {}

    def _add_member(self, member: Member):
        """
        A function used by the websocket handler to add a member to the server object.

        You ***really*** shouldn't call this function manually.
        """
        self.member_ids[member.id] = member

    def _update(self, data: OnServerUpdatePayload):
        if clear := data.get("clear"):
            if clear == "Icon":
                self.icon = None
            elif clear == "Banner":
                self.banner = None
            elif clear == "Description":
                self.description = None

        if new := data.get("data"):
            if owner := new.get("owner"):
                self.owner_id = owner
            if name := new.get("name"):
                self.name = name
            if description := new.get("description"):
                self.description = description
            if nsfw := new.get("nsfw"):
                self.nsfw = nsfw
            if icon := new.get("icon"):
                self.icon = Asset(icon, self.cache.http)
            if banner := new.get("banner"):
                self.banner = Asset(banner, self.cache.http)
            if system_messages := new.get("system_messages"):
                self.system_messages = SystemMessages(system_messages, self.cache)
            if default_permissions := new.get("default_permissions"):
                self.default_channel_permissions = ChannelPermissions.new_with_flags(default_permissions[0])
                self.default_role_permissions = ServerPermissions.new_with_flags(default_permissions[1])
            if categories := new.get("categories"):
                self.category_ids = {i["id"]: Category(i, self.cache) for i in categories}

    # do the same for members, roles, and categories
    @property
    def channels(self) -> List[Channel]:
        """
        A list of all the channels this server has.
        """
        return [self.cache.get_channel(i) for i in self.channel_ids]

    @property
    def members(self) -> List[Member]:
        """
        A list of all the members this server has.
        """
        return list(self.member_ids.values())

    @property
    def roles(self) -> List[Role]:
        """
        A list of all the roles this server has.
        """
        return list(self.role_ids.values())

    @property
    def categories(self) -> List[Category]:
        """
        A list of all the categories this server has.
        """
        return list(self.category_ids.values())

    @property
    def owner(self) -> User:
        """
        The server's owner.
        """
        return self.cache.get_user(self.owner_id)

    def __str__(self):
        return self.name

    def __repr__(self):
        return f"<Server id={self.id} name={self.name}>"

    def get_channel(self, channel_id: str) -> Optional[Channel]:
        """
        Gets a channel by its ID.

        Parameters
        ----------
        channel_id: str
            The ID of the channel to get.

        Returns
        -------
        Optional[:class:`Channel`]
            The channel with the given ID, or None if it doesn't exist.
        """
        return self.cache.get_channel(channel_id)

    def get_member(self, member: str) -> Optional[Member]:
        """
        Gets a member by their ID, a mention, their name or nickname.

        Parameters
        ----------
        member: :class:`str`
            The ID, mention, name or nickname of the member to get.

        Returns
        -------
        Optional[:class:`Member`]
            The member with the given ID, or None if it doesn't exist.
        """
        if match := search(r"[0-9A-HJ-KM-NP-TV-Z]{26}", member):
            return self.cache.get_member(self.id, match.group(0))
        try:
            return self.cache.get_member(self.id, member.replace("@", ""), "name", case=False)
        except ValueError:
            try:
                return self.cache.get_member(self.id, member.replace("@", ""), "nickname", case=False)
            except ValueError:
                return None

    def get_role(self, role_id: str) -> Optional[Role]:
        """
        Gets a role by its ID.

        Parameters
        ----------
        role_id: str
            The ID of the role to get.

        Returns
        -------
        Optional[:class:`Role`]
            The role with the given ID, or None if it doesn't exist.
        """
        return self.role_ids.get(role_id)

    def get_category(self, category_id: str) -> Optional[Category]:
        """
        Gets a category by its ID.

        Parameters
        ----------
        category_id: str
            The ID of the category to get.

        Returns
        -------
        Optional[:class:`Category`]
            The category with the given ID, or None if it doesn't exist.
        """
        return self.category_ids.get(category_id)

    async def set_default_permissions(
        self, channel_permissions: ChannelPermissions, role_permissions: ServerPermissions
    ):
        """
        Sets the default permissions for the server.

        Parameters
        ----------
        channel_permissions: :class:`ChannelPermissions`
            The channel permissions to set.
        role_permissions: :class:`ServerPermissions`
            The role permissions to set.
        """
        await self.cache.http.set_default_permissions(self.id, channel_permissions.flags, role_permissions.flags)

    async def create_channel(
        self, name: str, description: Optional[str] = None, nsfw: bool = False, type: Literal["Text", "Voice"] = "Text"
    ):
        """
        Creates a channel in this server.

        Parameters
        ----------
        name: str
            The name of the channel to create.
        description: Optional[str]
            The description of the channel to create.
        nsfw: Optional[bool]
            Whether the channel is NSFW or not.
        type: Optional[:class:`Literal`]
            The type of channel to create.

        Returns
        -------
        :class:`Channel`
            The channel that was created.
        """
        data = await self.cache.http.create_channel(self.id, type=type, name=name, description=description, nsfw=nsfw)
        return self.cache.add_channel(data)

    async def create_role(self, name: str):
        """
        Creates a role in this server.

        Parameters
        ----------
        name: str
            The name of the role to create.

        Returns
        -------
        :class:`Role`
            The role that was created.
        """
        data = await self.cache.http.create_role(self.id, name=name)
        return Role(data, self.id, self, self.cache.http)

    async def leave(self):
        """
        Leaves the server.

        .. note::

            Due to revolt api being *weird*, if the bot owns the server (somehow), it will delete it instead of leaving.
        """
        await self.cache.http.delete_server(self.id)

    async def fetch_invites(self):
        """
        Fetches all the invites for this server.

        Returns
        -------
        List[:class:`Invite`]
            A list of all the invites for this server.
        """
        data = await self.cache.http.fetch_invites(self.id)
        return [Invite.from_partial(i["_id"], i, self.cache) for i in data]

    async def fetch_member(self, member_id: str) -> Member:
        """
        Fetches a member from this server.

        Parameters
        ----------
        member_id: str
            The ID of the member to fetch.

        Returns
        -------
        :class:`Member`
            The member with the given ID.
        """
        return await self.cache.fetch_member(self.id, member_id)

    async def fetch_bans(self):
        """
        Fetches all the bans for this server.

        Returns
        -------
        List[:class:`Ban`]
            A list of all the bans for this server.
        """
        data = await self.cache.http.fetch_bans(self.id)
        return [ServerBan(i, self.cache) for i in data]
