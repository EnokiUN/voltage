from __future__ import annotations

from typing import TYPE_CHECKING, Literal, Optional

from .notsuplied import NotSupplied

# Internal imports
from .permissions import ChannelPermissions, ServerPermissions

if TYPE_CHECKING:
    from .internals import HTTPHandler
    from .server import Server
    from .types import OnServerRoleUpdatePayload, RolePayload


class Role:
    """
    A class that represents a Voltage role.

    Attributes
    ----------
    id: :class:`str`
        The role's ID.
    name: :class:`str`
        The role's name.
    colour: :class:`str`
        The role's colour.
    hoist: :class:`bool`
        Whether the role is hoisted.
    rank: :class:`int`
        The role's position in the role hierarchy.
    permissions: :class:`ServerPermissions`
        The role's permissions.
    channel_permissions: :class:`ChannelPermissions`
        The role's channel permissions.
    server: :class:`Server`
        The server the role belongs to.
    server_id: :class:`str`
        The ID of the server the role belongs to.
    """

    __slots__ = (
        "id",
        "name",
        "colour",
        "hoist",
        "rank",
        "permissions",
        "channel_permissions",
        "server",
        "server_id",
        "http",
    )

    def __init__(self, data: RolePayload, id: str, server: Server, http: HTTPHandler):
        self.id = id
        self.name = data["name"]
        self.colour = data.get("colour")
        self.hoist = data.get("hoist", False)
        self.rank = data["rank"]
        self.permissions = ServerPermissions.new_with_flags(data["permissions"][0])
        self.channel_permissions = ChannelPermissions.new_with_flags(data["permissions"][1])
        self.server = server
        self.server_id = server.id
        self.http = http

    def __str__(self):
        return self.name

    def __repr__(self):
        return f"<Role {self.name}>"

    async def set_permissions(
        self,
        *,
        server_permissions: Optional[ServerPermissions] = None,
        channel_permissions: Optional[ChannelPermissions] = None,
    ):
        """
        Sets the role's permissions.

        Parameters
        ----------
        server_permissions: Optional[:class:`ServerPermissions`]
            The new server permissions.
        channel_permissions: Optional[:class:`ChannelPermissions`]
            The new channel permissions.
        """
        if server_permissions is None and channel_permissions is None:
            raise ValueError("You must provide either server_permissions or channel_permissions")
        await self.http.set_role_permission(
            self.server_id, self.id, self.permissions.flags, self.channel_permissions.flags
        )

    async def delete(self):
        """
        Deletes the role.
        """
        await self.http.delete_role(self.server_id, self.id)

    async def edit(
        self,
        *,
        name: Optional[str] = None,
        colour: Optional[str] = NotSupplied,
        hoist: Optional[bool] = None,
        rank: Optional[int] = None,
    ):
        """
        Edits the role.

        Parameters
        ----------
        name: Optional[:class:`str`]
            The new name of the role.
        colour: Optional[:class:`str`]
            The new colour of the role.
        hoist: Optional[:class:`bool`]
            Whether the role is hoisted.
        rank: Optional[:class:`int`]
            The new rank of the role.
        """
        if name is None and colour is NotSupplied and hoist is None and rank is None:
            raise ValueError("You must provide at least one of the following: name, colour, hoist, rank")

        if name is None:
            name = self.name

        if name is None:
            raise ValueError(
                "You must provide a name"
            )  # god forgive me for I have sinned in the name of appeasing pyright.

        remove: Optional[Literal["Colour"]] = "Colour" if colour is None else None
        await self.http.edit_role(self.server_id, self.id, name, colour=colour, hoist=hoist, rank=rank, remove=remove)

    def __lt__(self, other: Role):
        return self.rank < other.rank

    def __le__(self, other: Role):
        return self.rank <= other.rank

    def __gt__(self, other: Role):
        return self.rank > other.rank

    def __ge__(self, other: Role):
        return self.rank >= other.rank

    def _update(self, data: OnServerRoleUpdatePayload):
        if clear := data.get("clear"):
            if clear == "colour":
                self.colour = None

        if new := data.get("data"):
            if name := new.get("name"):
                self.name = name

            if colour := new.get("colour"):
                self.colour = colour

            if hoist := new.get("hoist"):
                self.hoist = hoist

            if rank := new.get("rank"):
                self.rank = rank
