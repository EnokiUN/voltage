from __future__ import annotations

from typing import TYPE_CHECKING, Union

from .asset import Asset

if TYPE_CHECKING:
    from .internals import CacheHandler
    from .types import InvitePayload, PartialInvitePayload


class Invite:
    """
    A class which represents a Voltage invite.

    Attributes
    ----------
    code: :class:`str`
        The invite code.
    type: :class:`str`
        The invite type.
    server_id: :class:`str`
        The server ID.
    server: :class:`Server`
        The server the invite is for.
    channel_id: :class:`str`
        The channel ID.
    channel: :class:`Channel`
        The channel the invite is for.
    member_count: :class:`int`
        The member count.
    author_name: :class:`str`
        The author name.
    user: :class:`User`
        The user who created the invite.
    avatar: :class:`Asset`
        The avatar of the user who created the invite.
    """

    __slots__ = (
        "code",
        "type",
        "payload",
        "server_id",
        "server",
        "channel_id",
        "channel",
        "member_count",
        "user",
        "cache",
    )

    def __init__(self, data: InvitePayload, code: str, cache: CacheHandler):
        self.code = code
        self.type = data["type"]
        self.payload: Union[InvitePayload, PartialInvitePayload] = data

        self.server_id = data["server_id"]
        self.server = cache.get_server(self.server_id)

        self.channel_id = data["channel_id"]
        self.channel = cache.get_channel(self.channel_id)
        self.member_count = data["member_count"]

        self.user = cache.get_user(data["user_name"], "name")

        self.cache = cache

    @staticmethod
    def from_partial(code: str, data: PartialInvitePayload, cache: CacheHandler) -> Invite:
        """
        A utility function that creates an Invite object from a partial payload.

        Parameters
        ----------
        code: :class:`str`
            The invite code.
        data: :class:`PartialInvitePayload`
            The partial payload.
        cache: :class:`CacheHandler`
            The cache handler.
        """
        self = Invite.__new__(Invite)

        self.code = code
        self.payload = data
        self.cache = cache
        self.type = "Server"

        self.server_id = data["server"]
        self.server = cache.get_server(self.server_id)
        self.member_count = len(self.server.members)

        self.channel_id = data["channel"]
        self.channel = cache.get_channel(self.channel_id)

        self.user = cache.get_user(data["creator"])

        return self

    async def delete(self):
        return await self.cache.http.delete_invite(self.code)
