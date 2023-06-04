from __future__ import annotations

from typing import TYPE_CHECKING, NamedTuple, Optional

from ulid import ULID

from .asset import Asset, PartialAsset
from .enums import PresenceType, RelationshipType
from .flag import UserFlags
from .messageable import Messageable

if TYPE_CHECKING:
    from .internals import CacheHandler
    from .types import OnUserUpdatePayload, UserPayload


class Relationship(NamedTuple):
    """
    A tuple that represents the relationship between two users.

    Attributes
    ----------
    type: :class:`RelationshipType`
        The type of relationship between the two users.
    user: :class:`User`
        The user that is the target of the relationship.
    """

    type: RelationshipType
    user: User


class Status(NamedTuple):
    """
    A tuple that represents the status of a user.

    Attributes
    ----------
    text: Optional[:class:`str`]
        The status message of the user.
    presence: :class:`PresenceType`
        The presence of the user.
    """

    text: Optional[str]
    presence: PresenceType


class UserProfile(NamedTuple):
    """
    A tuple that represent's a user's profile.

    Attributes
    ----------
    content: Optional[:class:`str`]
        The content of the user's profile.
    background: Optional[:class:`PartialAsset`]
        The background of the user's profile.
    """

    content: Optional[str]
    background: Optional[Asset]


class User(Messageable):
    """
    A class that represents a Voltage user.

    Attributes
    ----------
    id: :class:`str`
        The user's ID.
    created_at: :class:`int`
        The epoch time when the user was created.
    name: :class:`str`
        The user's name.
    avatar: :class:`Asset`
        The user's avatar.
    badges: :class:`UserFlags`
        The user's badges.
    online: :class:`bool`
        Whether the user is online or not.
    status: :class:`Status`
        The user's status.
    relationships: :class:`list` of :class:`Relationship`
        The user's relationships.
    profile: :class:`UserProfile`
        The user's profile.
    bot: :class:`bool`
        Whether the user is a bot or not.
    owner: :class:`User`
        The bot's owner.
    """

    __slots__ = (
        "id",
        "created_at",
        "name",
        "avatar",
        "dm_channel",
        "default_avatar",
        "flags",
        "badges",
        "online",
        "status",
        "relationships",
        "avatar",
        "_profile",
        "_profile_fetched",
        "bot",
        "owner_id",
        "cache",
        "masquerade_name",
        "masquerade_avatar",
    )

    def __init__(self, data: UserPayload, cache: CacheHandler):
        self.cache = cache
        self.id = data["_id"]
        self.created_at = ULID(buffer=self.id.encode()).timestamp()

        self.name = data["username"]
        self.dm_channel = cache.get_dm_channel(self.id)
        self.flags = data.get("flags", 0)
        self.badges = UserFlags.new_with_flags(self.flags)
        self.online = data.get("online", False)

        avatar = data.get("avatar")
        self.avatar = Asset(avatar, cache.http) if avatar else None
        self.default_avatar = PartialAsset(f"{cache.http.api_url}/users/{self.id}/default_avatar", cache.http)

        relationships = []
        for i in data.get("relations", []):
            try:
                if user := cache.get_user(i["_id"]):
                    relationships.append(Relationship(RelationshipType(i["status"]), user))
            except KeyError:
                continue

        self.relationships = relationships

        if status := data.get("status"):
            if presence := status.get("presence"):
                self.status = Status(status.get("text"), PresenceType(presence))
            else:
                self.status = Status(status.get("text"), PresenceType.invisible)
        else:
            self.status = Status(None, PresenceType.invisible)

        self._profile = UserProfile(None, None)
        self._profile_fetched = False

        bot = data.get("bot", {})
        self.bot = True if bot else False
        self.owner_id = bot.get("owner")

        self.masquerade_name: Optional[str] = None
        self.masquerade_avatar: Optional[PartialAsset] = None

    def set_masquerade(self, name: Optional[str], avatar: Optional[PartialAsset]):
        """
        A method which sets a user's masquerade.

        Parameters
        ----------
        name: :class:`str`
            The masquerade name.
        avatar: :class:`PartialAsset`
            The masquerade avatar.
        """
        self.masquerade_name = name
        self.masquerade_avatar = avatar

    async def get_id(self):
        if self.dm_channel is None:
            self.dm_channel = await self.cache.fetch_dm_channel(self.id)
        return self.dm_channel.id

    def __str__(self):
        return f"@{self.name}"

    def __repr__(self):
        return f"<User {self.name}>"

    @property
    def profile(self) -> UserProfile:
        if not self._profile_fetched:
            self.cache.loop.create_task(self.fetch_profile())
            self._profile_fetched = True
        return self._profile

    @property
    def mention(self):
        return f"<@{self.id}>"

    @property
    def display_name(self):
        return self.masquerade_name or self.name

    @property
    def display_avatar(self):
        return self.masquerade_avatar or self.avatar or self.default_avatar

    @property
    def owner(self):
        return self.cache.get_user(self.owner_id) if self.bot and self.owner_id else None

    async def fetch_profile(self) -> UserProfile:
        """
        A method which fetches a user's profile.

        Returns
        -------
        :class:`UserProfile`
            The user's profile.
        """
        data = await self.cache.http.fetch_user_profile(self.id)
        bg = data.get("background")
        background = Asset(bg, self.cache.http) if bg is not None else None
        self._profile = UserProfile(data.get("content"), background)
        return self.profile

    def _update(self, data: OnUserUpdatePayload):
        if clear := data.get("clear"):
            if clear == "ProfileContent":
                self._profile = UserProfile(None, self._profile.background)
            elif clear == "ProfileBackground":
                self._profile = UserProfile(self._profile.content, None)
            elif clear == "StatusText":
                self.status = Status(None, self.status.presence)
            elif clear == "Avatar":
                self.avatar = None

        if new := data.get("data"):
            if status := new.get("status"):
                presence = status.get("presence") or self.status.presence
                self.status = Status(status.get("text"), PresenceType(presence))
            if bg := new.get("profile.background"):
                self._profile = UserProfile(self._profile.content, Asset(bg, self.cache.http))
            if content := new.get("profile.content"):
                self._profile = UserProfile(content, self._profile.background)
            if avatar := new.get("avatar"):
                self.avatar = Asset(avatar, self.cache.http)
            if online := new.get("online"):
                self.online = online
