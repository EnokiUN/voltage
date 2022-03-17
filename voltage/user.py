from __future__ import annotations
from typing import TYPE_CHECKING, NamedTuple, Optional

from .asset import Asset
from .channels import DMCChannel
from .enums import PresenseType, RelationshipType
from .internals import UserFlags
from .messageable import Messageable

if TYPE_CHECKING:
    from .internals import CacheHandler
    from .types import FilePayload, StatusPayload, UserPayload, UserProfilePayload

class Relationship(NamedTuple):
    """A tuple that represents the relationship between two users."""
    type: RelationshipType
    user: User

class Status(NamedTuple):
    """A tuple that represents the status of a user."""
    text: Optional[str]
    presense: PresenseType

class UserProfile(NamedTuple):
    """A tuple that represent's a user's profile."""
    content: Optional[str]
    background: Optional[Asset]

class User(Messageable):
    def __init__(self, data: UserPayload, cache: CacheHandler):
        self.cache = cache
        self.id = data['_id']
        
        self.name = data['username']
        self.dm_channel = cache.get_dm_channel(self.id)
        self.flags = data.get('flags', 0)
        self.badges = UserFlags.new_with_flags(self.flags)
        self.online = data.get('online', False)

        avatar = data.get('avatar')
        self.avatar = Asset(avatar, cache.http) if avatar else None

        relationships = []
        for i in data.get('relations', []):
            if user := cache.get_user(i['_id']):
                relationships.append(Relationship(RelationshipType(i['status']), cache.get_user(i['_id'])))
    
        self.relationships = relationships

        self.status = Status(data.get('status', {}).get('text'), PresenseType(data.get('status', {}).get('presence'))) if data.get('status') else None

        self.profile = UserProfile(None, None)

        self.bot, self.owner = (data.get('bot', False), cache.get_user(data.get('owner_id'), cache)) if data.get('bot') else (False, None)

    async def get_id(self):
        if self.dm_channel is None:
            self.dm_channel = await self.cache.fetch_dm_channel(self.id)
        return self.dm_channel.id

    async def default_avatar(self):
        """
        A method which return's a user's default avatar.

        Returns
        -------
        :class:`bytes`
            The default avatar of the user.
        """
        return await self.cache.http.get_default_avatar(self.id)

    async def fetch_profile(self) -> UserProfile:
        """
        A method which fetches a user's profile.

        Returns
        -------
        :class:`UserProfile`
            The user's profile.
        """
        data = await self.cache.http.fetch_user_profile(self.id)
        bg = data.get('background')
        background = Asset(bg, self.cache.http) if bg is not None else None
        self.profile = UserProfile(data.get('content'), background)
        return self.profile

    async def _update(self, data: Optional[UserPayload] = None, profile_data: Optional[UserProfilePayload] = None):
        if data:
            self.name = data['username']
            self.flags = data.get('flags', 0)
            self.badges = UserFlags.new_with_flags(self.flags)
            self.online = data.get('online', False)

            avatar = data.get('avatar')
            self.avatar = Asset(avatar, self.cache.http) if avatar else None

            relationships = []
            for i in data.get('relations', []):
                if user := self.cache.get_user(i['_id']):
                    relationships.append(Relationship(RelationshipType(i['status']), user))
        
            self.relationships = relationships

            self.status = Status(data.get('status', {}).get('text'), PresenseType(data.get('status', {}).get('presence'))) if data.get('status') else None

        if profile_data:
            bg = profile_data.get('background')
            background = Asset(bg, self.cache.http) if bg is not None else None
            self.profile = UserProfile(profile_data.get('content'), background)
