from __future__ import annotations

from typing import TYPE_CHECKING, Literal, Optional

from ulid import ULID

from .notsupplied import NotSupplied

# Internal imports
from .permissions import Permissions

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
    created_at: :class:int:
        The timestamp of when the role was created.
    name: :class:`str`
        The role's name.
    colour: :class:`str`
        The role's colour.
    color: :class:`str`
        Alias for :attr:`colour`.
    hoist: :class:`bool`
        Whether the role is hoisted.
    rank: :class:`int`
        The role's position in the role hierarchy.
    permissions: :class:`Permissions`
        The role's permissions..
    server: :class:`Server`
        The server the role belongs to.
    server_id: :class:`str`
        The ID of the server the role belongs to.
    """

    __slots__ = (
        "id",
        "created_at",
        "name",
        "colour",
        "color",
        "hoist",
        "rank",
        "permissions",
        "server",
        "server_id",
        "http",
    )

    def __init__(self, data: RolePayload, id: str, server: Server, http: HTTPHandler):
        self.id = id
        self.created_at = ULID().decode(id)
        self.name = data["name"]
        self.colour = data.get("colour")
        self.color = self.colour
        self.hoist = data.get("hoist", False)
        self.rank = data["rank"]
        Permissions(data["permissions"])
        self.server = server
        self.server_id = server.id
        self.http = http

    def __str__(self):
        return self.name

    def __repr__(self):
        return f"<Role {self.name}>"

    async def set_permissions(
        self,
        permissions: Permissions
    ):
        """
        Sets the role's permissions.

        Parameters
        ----------
        permissions: Optional[:class:`Permissions`]
            The new server permissions.
        """
        await self.http.set_role_permission(
            self.server_id, self.id, permissions.to_dict()
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
        color: Optional[str] = NotSupplied,
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
        color: Optional[:class:`str`]
            Alias for :attr:`colour`.
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

        if colour is NotSupplied and color is not NotSupplied:
            colour = color

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
