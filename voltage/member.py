from __future__ import annotations

from typing import TYPE_CHECKING, Any, Optional, Union

from .asset import Asset
from .permissions import ServerPermissions

# Internal imports
from .user import User

if TYPE_CHECKING:
    from .internals import CacheHandler
    from .roles import Role
    from .server import Server
    from .types import MemberPayload, OnServerMemberUpdatePayload


def make_member_dot_zip(
    member: Member, user: User
):  # very excellanto functiono it take memberru object and it users objecto and give it all atrr like naem, avartar and sow on.
    for i in user.__slots__:
        setattr(member, i, getattr(user, i))


class Member(User):
    """
    A class that represents a Voltage server member.

    This class is a subclass of :class:`User` and inherits all of its attributes.

    Attributes
    ----------
    server: :class:`Server`
        The server that the member belongs to.
    nickname: Optional[:class:`str`]
        The member's nickname.
    server_avatar: Optional[:class:`Asset`]
        The member's avatar.
    roles: List[:class:`Role`]
        The member's roles.
    permissions: :class:`ServerPermissions`
        The member's permissions.
    """

    __slots__ = ("nickname", "server_avatar", "roles", "server", "permissions")

    def __init__(self, data: MemberPayload, server: Server, cache: CacheHandler):
        user = cache.get_user(data["_id"]["user"])
        make_member_dot_zip(self, user)

        self.nickname = data.get("nickname")

        if av := data.get("avatar"):
            self.server_avatar: Optional[Asset] = Asset(av, cache.http)
        else:
            self.server_avatar = None

        roles = []
        permint = 0
        for i in data.get("roles", []):
            role = server.get_role(i)
            if role:
                roles.append(role)
                permint |= role.permissions.flags

        self.roles: list[Role] = sorted(roles, key=lambda r: r.rank, reverse=True)
        self.permissions = ServerPermissions.new_with_flags(permint)

        self.server = server

    def __repr__(self):
        return f"<Member {self.name}>"

    @property
    def display_name(self):
        """
        Returns the member's display name.

        This is the member's masquerade name or nickname if they have one, otherwise their username.
        """
        return self.masquerade_name or self.nickname or self.name

    @property
    def display_avatar(self):
        """
        Returns the member's display avatar.

        This is the member's masquerade avatar or their server's avatar if they have one, otherwise their avatar.
        """
        return self.masquerade_avatar or self.server_avatar or self.avatar

    async def kick(self):
        """
        A method that kicks the member from the server.
        """
        await self.cache.http.kick_member(self.server.id, self.id)

    async def ban(self, reason: Optional[str] = None):
        """
        A method that bans the member from the server.

        Parameters
        ----------
        reason: Optional[:class:`str`]
            The reason for banning the member.
        """
        await self.cache.http.ban_member(self.server.id, self.id, reason=reason)

    async def unban(self):
        """
        A method that unbans the member from the server.
        """
        await self.cache.http.unban_member(self.server.id, self.id)

    async def add_roles(self, *roles: Role):
        """
        A method that adds roles to the member.

        Parameters
        ----------
        *roles: :class:`Role`
            The roles to add to the member.
        """
        await self.cache.http.edit_member(
            self.server.id, self.id, roles=[r.id for r in roles] + [r.id for r in self.roles]
        )

    def _update(self, data: Union[Any, OnServerMemberUpdatePayload]):  # god bless mypy
        if clear := data.get("clear"):
            if clear == "Nickname":
                self.nickname = None
            elif clear == "Avatar":
                self.server_avatar = None

        if new := data.get("data"):
            if new.get("nickname"):
                self.nickname = new["nickname"]
            if new.get("avatar"):
                self.server_avatar = Asset(new["avatar"], self.cache.http)
            if new.get("roles"):
                roles = []
                for i in new["roles"]:
                    role = self.server.get_role(i)
                    if role:
                        roles.append(role)

                self.roles = sorted(roles, key=lambda r: r.rank, reverse=True)
