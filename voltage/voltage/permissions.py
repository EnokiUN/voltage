# Thanks Jan <3
from __future__ import annotations

from typing import Optional

from .flag import FlagBase, FlagValue


def channel_permissions(
    view: Optional[bool] = False,
    send_messages: Optional[bool] = False,
    manage_messages: Optional[bool] = False,
    manage_channel: Optional[bool] = False,
    voice_call: Optional[bool] = False,
    invite_others: Optional[bool] = False,
    embed_links: Optional[bool] = False,
    upload_files: Optional[bool] = False,
):
    """
    A function which simplifies the process of creating a new channel permissions objects perhaps for comparison purposes.

    Parameters
    ----------
    view: Optional[:class:`bool`]
        Whether the view permission is granted.
    send_messages: Optional[:class:`bool`]
        Whether the send messages permission is granted.
    manage_messages: Optional[:class:`bool`]
        Whether the manage messages permission is granted.
    manage_channel: Optional[:class:`bool`]
        Whether the manage channels permission is granted.
    voice_call: Optional[:class:`bool`]
        Whether the voice call permission is granted.
    invite_others: Optional[:class:`bool`]
        Whether the invite others permission is granted.
    embed_links: Optional[:class:`bool`]
        Whether the embed links permission is granted.
    upload_files: Optional[:class:`bool`]
        Whether the upload files permission is granted.
    """
    permission_int = 0
    if view:
        permission_int |= 1 << 0
    if send_messages:
        permission_int |= 1 << 1
    if manage_messages:
        permission_int |= 1 << 2
    if manage_channel:
        permission_int |= 1 << 3
    if voice_call:
        permission_int |= 1 << 4
    if invite_others:
        permission_int |= 1 << 5
    if embed_links:
        permission_int |= 1 << 6
    if upload_files:
        permission_int |= 1 << 7
    return ChannelPermissions.new_with_flags(permission_int)


class ChannelPermissions(FlagBase):
    """
    A class which represents a channel permissions object.

    Methods
    -------
    none: :class:`ChannelPermissions`
        Returns a new :class:`ChannelPermissions` object with all permissions set to ``False``.
    all: :class:`ChannelPermissions`
        Returns a new :class:`ChannelPermissions` object with all permissions set to ``True``.
    """

    @classmethod
    def none(cls) -> ChannelPermissions:
        return cls.new_with_flags(0b0)

    @classmethod
    def all(cls) -> ChannelPermissions:
        return cls.new_with_flags(0b11111111)

    @FlagValue
    def view(self):
        """
        Whether the view permission is granted.
        """
        return 1 << 0

    @FlagValue
    def send_messages(self):
        """
        Whether the send messages permission is granted.
        """
        return 1 << 1

    @FlagValue
    def manage_messages(self):
        """
        Whether the manage messages permission is granted.
        """
        return 1 << 2

    @FlagValue
    def manage_channel(self):
        """
        Whether the manage channels permission is granted.
        """
        return 1 << 3

    @FlagValue
    def voice_call(self):
        """
        Whether the voice call permission is granted.
        """
        return 1 << 4

    @FlagValue
    def invite_others(self):
        """
        Whether the invite others permission is granted.
        """
        return 1 << 5

    @FlagValue
    def embed_links(self):
        """
        Whether the embed links permission is granted.
        """
        return 1 << 6

    @FlagValue
    def upload_files(self):
        """
        Whether the upload files permission is granted.
        """
        return 1 << 7


def server_permissions(
    view: Optional[bool] = False,
    manage_roles: Optional[bool] = False,
    manage_channels: Optional[bool] = False,
    manage_server: Optional[bool] = False,
    kick_members: Optional[bool] = False,
    ban_members: Optional[bool] = False,
    change_nickname: Optional[bool] = False,
    manage_nicknames: Optional[bool] = False,
    change_avatar: Optional[bool] = False,
    remove_avatars: Optional[bool] = False,
):
    """
    A function which simplifies the process of creating a new server permissions objects perhaps for comparison purposes.

    Parameters
    ----------
    view: Optional[:class:`bool`]
        Whether the view permission is granted.
    manage_roles: Optional[:class:`bool`]
        Whether the manage roles permission is granted.
    manage_channels: Optional[:class:`bool`]
        Whether the manage channels permission is granted.
    manage_server: Optional[:class:`bool`]
        Whether the manage server permission is granted.
    kick_members: Optional[:class:`bool`]
        Whether the kick members permission is granted.
    ban_members: Optional[:class:`bool`]
        Whether the ban members permission is granted.
    change_nickname: Optional[:class:`bool`]
        Whether the change nickname permission is granted.
    manage_nicknames: Optional[:class:`bool`]
        Whether the manage nicknames permission is granted.
    change_avatar: Optional[:class:`bool`]
        Whether the change avatar permission is granted.
    remove_avatars: Optional[:class:`bool`]
        Whether the remove avatars permission is granted.
    """
    permission_int = 0
    if view:
        permission_int |= 1 << 0
    if manage_roles:
        permission_int |= 1 << 1
    if manage_channels:
        permission_int |= 1 << 2
    if manage_server:
        permission_int |= 1 << 3
    if kick_members:
        permission_int |= 1 << 4
    if ban_members:
        permission_int |= 1 << 5
    if change_nickname:
        permission_int |= 1 << 12
    if manage_nicknames:
        permission_int |= 1 << 13
    if change_avatar:
        permission_int |= 1 << 14
    if remove_avatars:
        permission_int |= 1 << 15
    return ServerPermissions.new_with_flags(permission_int)


class ServerPermissions(FlagBase):
    """
    A class which represents a server permissions object.

    Methods
    -------
    none: :class:`ServerPermissions`
        Returns a new :class:`ServerPermissions` object with all permissions set to ``False``.
    all: :class:`ServerPermissions`
        Returns a new :class:`ServerPermissions` object with all permissions set to ``True``.
    """

    @classmethod
    def none(cls) -> ServerPermissions:
        return cls.new_with_flags(0b0)

    @classmethod
    def all(cls) -> ServerPermissions:
        return cls.new_with_flags(0b1111000000111111)

    @FlagValue
    def view(self):
        """
        Whether the view permission is granted.
        """
        return 1 << 0

    @FlagValue
    def manage_roles(self):
        """
        Whether the manage roles permission is granted.
        """
        return 1 << 1

    @FlagValue
    def manage_channels(self):
        """
        Whether the manage channels permission is granted.
        """
        return 1 << 2

    @FlagValue
    def manage_server(self):
        """
        Whether the manage server permission is granted.
        """
        return 1 << 3

    @FlagValue
    def kick_members(self):
        """
        Whether the kick members permission is granted.
        """
        return 1 << 4

    @FlagValue
    def ban_members(self):
        """
        Whether the ban members permission is granted.
        """
        return 1 << 5

    @FlagValue
    def change_nickname(self):
        """
        Whether the change nickname permission is granted.
        """
        return 1 << 12

    @FlagValue
    def manage_nicknames(self):
        """
        Whether the manage nicknames permission is granted.
        """
        return 1 << 13

    @FlagValue
    def change_avatar(self):
        """
        Whether the change avatar permission is granted.
        """
        return 1 << 14

    @FlagValue
    def remove_avatars(self):
        """
        Whether the remove avatars permission is granted.
        """
        return 1 << 15
