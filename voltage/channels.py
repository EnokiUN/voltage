from __future__ import annotations

from typing import TYPE_CHECKING, Any, Literal, Optional, Union

from .asset import Asset
from .enums import ChannelType
from .messageable import Messageable
from .notsuplied import NotSupplied
from .permissions import ChannelPermissions

if TYPE_CHECKING:
    from .file import File
    from .internals import CacheHandler
    from .message import Message
    from .roles import Role
    from .server import Server
    from .types import (
        ChannelPayload,
        DMChannelPayload,
        GroupDMChannelPayload,
        OnChannelUpdatePayload,
        SavedMessagePayload,
        TextChannelPayload,
        VoiceChannelPayload,
    )
    from .user import User


class Channel:
    """
    The base class that all channels inherit from.

    Attributes
    ----------
    id: :class:`str`
        The ID of the channel.
    type: :class:`ChannelType`
        The type of the channel.
    server: Optional[:class:`Server`]
        The server the channel belongs to.
    """

    __slots__ = ("id", "type", "server", "cache")

    def __init__(self, data: ChannelPayload, cache: CacheHandler, server_id: Optional[str] = None):
        self.id = data["_id"]
        self.type = ChannelType(data["channel_type"])
        self.server = cache.get_server(server_id) if server_id else None
        self.cache = cache

    def __repr__(self):
        return f"<{self.__class__.__name__} id={self.id}>"

    async def get_id(self):
        return self.id

    @property
    def mention(self):
        """Returns a string that allows you to mention the channel."""
        return f"<#{self.id}>"

    def _update(self, data: OnChannelUpdatePayload):
        raise NotImplementedError

    async def edit(
        self,
        *,
        name: Optional[str] = None,
        description: Optional[str] = NotSupplied,
        icon: Optional[Union[str, File]] = NotSupplied,
        nsfw: Optional[bool] = None,
    ):  # No idea where else to put this.
        """Edits the channel.

        Parameters
        ----------
        name: Optional[:class:`str`]
            The new name of the channel.
        description: Optional[:class:`str`]
            The new description of the channel.
        icon: Optional[:class:`str` or :class:`File`]
            The new icon of the channel.
        nsfw: Optional[:class:`bool`]
            Whether the channel is NSFW or not.
        """
        remove: Optional[Literal["Description", "Icon"]] = (
            "Description" if description is None else "Icon" if icon is None else None
        )
        if isinstance(icon, File):
            icon = await icon.get_id(self.cache.http)
        return self.cache.http.edit_channel(
            self.id, name=name, description=description, icon=icon, nsfw=nsfw, remove=remove
        )

    async def delete(self):
        """Deletes the channel."""
        return self.cache.http.close_channel(self.id)

    async def set_default_permissions(self, permissions: ChannelPermissions):
        """Sets the default permissions for the channel.

        Parameters
        ----------
        permissions: :class:`ChannelPermissions`
            The new default permissions for the channel.
        """
        return self.cache.http.set_default_perms(self.id, permissions.flags)

    async def set_role_permission(self, role: Role, permissions: ChannelPermissions):
        """Sets the permissions for a role in the channel.

        Parameters
        ----------
        role: :class:`Role`
            The role to set the permissions for.
        permissions: :class:`ChannelPermissions`
            The new permissions for the role.
        """
        return self.cache.http.set_role_perms(self.id, role.id, permissions.flags)


class SavedMessageChannel(Channel, Messageable):
    """
    The class representing the Voltage saved messages channel.
    """

    def __init__(self, data: SavedMessagePayload, cache: CacheHandler):
        super().__init__(data, cache)

    async def edit(self):
        raise NotImplementedError

    async def set_default_permissions(self):
        raise NotImplementedError

    async def set_role_permission(self):
        raise NotImplementedError


class DMChannel(Channel, Messageable):
    """
    The class representing the Voltage direct messages channel.
    """

    def __init__(self, data: DMChannelPayload, cache: CacheHandler):
        super().__init__(data, cache)

    async def edit(self):
        raise NotImplementedError

    async def set_default_permissions(self):
        raise NotImplementedError

    async def set_role_permission(self):
        raise NotImplementedError


class GroupDMChannel(Channel, Messageable):
    """
    The class representing the Voltage group direct messages channel.

    Attributes
    ----------
    name: :class:`str`
        The name of the group direct messages channel.
    description: Optional[:class:`str`]
        The description of the group direct messages channel.
    nsfw: :class:`bool`
        Whether the channel is NSFW or not.
    owner: :class:`User`
        The owner of the group direct messages channel.
    recipients: List[:class:`User`]
        The recipients of the group direct messages channel.
    icon: Optional[:class:`Asset`]
        The icon of the group direct messages channel.
    permissions: :class:`ChannelPermissions`
        The permissions of the group direct messages channel.
    """

    __slots__ = ("name", "description", "nsfw", "owner", "recipients", "icon", "permissions")

    def __init__(self, data: GroupDMChannelPayload, cache: CacheHandler):
        super().__init__(data, cache)
        self.name = data["name"]
        self.description = data.get("description")
        self.nsfw = data.get("nsfw", False)
        self.owner = cache.get_user(data["owner"])
        self.recipients = [cache.get_user(recipient) for recipient in data["recipients"]]

        self.icon: Optional[Asset]
        if icon := data.get("icon"):
            self.icon = Asset(icon, self.cache.http)
        else:
            self.icon = None

        self.permissions = ChannelPermissions.new_with_flags(data.get("permissions", 0))

    async def set_role_permission(self):
        raise NotImplementedError

    def add_recepient(self, user: User):
        """Adds a user to the group direct messages channel.

        Parameters
        ----------
        user: :class:`User`
            The user to add to the group direct messages channel.
        """
        self.recipients.append(user)

    def remove_recepient(self, user: User):
        """Removes a user from the group direct messages channel.

        Parameters
        ----------
        user: :class:`User`
            The user to remove from the group direct messages channel.
        """
        self.recipients.remove(user)

    def _update(self, data: Any):  # Finally, inner peace.
        if clear := data.get("clear"):
            if clear == "Icon":
                self.icon = None
            elif clear == "Description":
                self.description = None

        # mypy is complainint about this, but it's not my fault.
        # please stfu I've been tryna stop this for half an hour.
        # PLEASE, FOR THE LOVE OF GOD, STOP.
        # even github copilot is angry now :(
        # IT HAS BEEN AN HOUR, DON'T FORCE ME TO DO THIS.
        # GODDAMIT type: ignore IT IS
        # no im sorry pls forgive me we can find a solution to this together, right?
        # hahahahahahahhaahhahahahaahhahahahahahhaahhahahh fml mypy is shit
        # okay im done imma yeet mypy and get pyright
        # PYRIGHT WHY DID YOU BETRAY MEEEEEEEEEEEEEEE
        # ight fuck pyright back to mypy my beloved
        # mypy is a fucking piece of shit
        # aaaaaaaaaaa
        # I started this at 22:17 and it's 23:44 now
        # I'm not even going to bother to type this
        # AWSERDG<F18>HIJOKPL<>:SDRFGYHJMK
        # ight fuck it that does it for me
        # Okay, Okay, I just gotta be smart about it
        # no fuck you mypy
        # Seriously considering removing typing from the lib
        # after 38479823748923 iterations i give up
        # wait, I have an idea
        if new := data.get("data"):
            if name := new.get("name"):
                self.name = name
            if description := new.get("description"):
                self.description = description
            if recipients := new.get("recipients", []):
                self.recipients = [self.cache.get_user(recipient) for recipient in recipients]


class TextChannel(Channel, Messageable):
    """
    The class representing the Voltage text channels.

    Attributes
    ----------
    name: :class:`str`
        The name of the text channel.
    description: Optional[:class:`str`]
        The description of the text channel.
    last_message: Optional[:class:`Message`]
        The last message sent in the text channel.
    nsfw: :class:`bool`
        Whether the text channel is NSFW or not.
    default_permissions: :class:`ChannelPermissions`
        The default permissions for the text channel.
    role_permissions: Dict[:class:`ChannelPermissions`]
        A role-id permission pair dict representing the role-specific permissions for the text channel.
    icon: Optional[:class:`Asset`]
        The icon of the text channel.
    """

    __slots__ = ("name", "description", "last_message", "nsfw", "default_permissions", "role_permissions", "icon")

    def __init__(self, data: TextChannelPayload, cache: CacheHandler, server_id: Optional[str] = None):
        super().__init__(data, cache, server_id)
        self.name = data["name"]
        self.description = data.get("description")
        self.nsfw = data.get("nsfw", False)

        self.last_message: Optional[Message]
        if last_message := data.get("last_message"):
            self.last_message = cache.get_message(last_message)
        else:
            self.last_message = None

        self.default_permissions = ChannelPermissions.new_with_flags(data.get("default_permissions", 0))
        self.role_permissions = {
            role: ChannelPermissions.new_with_flags(permissions)
            for role, permissions in data.get("role_permissions", {}).items()
        }

        self.icon: Optional[Asset]
        if icon := data.get("icon"):
            self.icon = Asset(icon, self.cache.http)
        else:
            self.icon = None

    def _update(self, data: Any):
        if clear := data.get("clear"):
            if clear == "Icon":
                self.icon = None
            elif clear == "Description":
                self.description = None

        if new := data.get("data"):
            if name := new.get("name"):
                self.name = name
            if description := new.get("description"):
                self.description = description


class VoiceChannel(Channel):
    """
    The class representing the Voltage voice channels.

    Attributes
    ----------
    name: :class:`str`
        The name of the voice channel.
    description: Optional[:class:`str`]
        The description of the voice channel.
    default_permissions: :class:`ChannelPermissions`
        The default permissions for the voice channel.
    role_permissions: Dict[str, :class:`ChannelPermissions`]
        A role-id permission pair dict representing the role-specific permissions for the voice channel.
    icon: Optional[:class:`Asset`]
        The icon of the voice channel.
    """

    __slots__ = ("name", "description", "default_permissions", "role_permissions", "icon")

    def __init__(self, data: VoiceChannelPayload, cache: CacheHandler, server_id: Optional[str] = None):
        super().__init__(data, cache, server_id)
        self.name = data["name"]
        self.description = data.get("description")

        self.default_permissions = ChannelPermissions.new_with_flags(data.get("default_permissions", 0))
        self.role_permissions = {
            role: ChannelPermissions.new_with_flags(permissions)
            for role, permissions in data.get("role_permissions", {}).items()
        }

        self.icon: Optional[Asset]
        if icon := data.get("icon"):
            self.icon = Asset(icon, self.cache.http)
        else:
            self.icon = None

    def _update(self, data: Any):
        if clear := data.get("clear"):
            if clear == "Icon":
                self.icon = None
            elif clear == "Description":
                self.description = None

        if new := data.get("data"):
            if name := new.get("name"):
                self.name = name
            if description := new.get("description"):
                self.description = description


# no fuck you not again
def create_channel(
    data: Any,
    cache: CacheHandler,
    server_id: Optional[str] = None,
) -> Union[TextChannel, VoiceChannel, GroupDMChannel, SavedMessageChannel, DMChannel]:
    """
    Creates a channel based on the data provided.

    Parameters
    ----------
    data: :class:`ChannelPayload`
        The data to create the channel with.
    cache: :class:`CacheHandler`
        The cache to use.
    server_id: Optional[:class:`str`]
        The ID of the channel's server.

    Returns
    -------
    :class:`Channel`
        The created channel.
    """
    type = data["channel_type"]
    if type == "TextChannel":
        return TextChannel(data, cache, server_id)
    elif type == "VoiceChannel":
        return VoiceChannel(data, cache, server_id)
    elif type == "Group":
        return GroupDMChannel(data, cache)
    elif type == "SavedMessage":
        return SavedMessageChannel(data, cache)
    elif type == "DirectMessage":
        return DMChannel(data, cache)
    else:
        raise ValueError(f"Unknown channel type: {type}")
