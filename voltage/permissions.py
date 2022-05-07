# Thanks Jan <3
from __future__ import annotations

from typing import TYPE_CHECKING

# Internal Imports
from .flag import FlagBase, FlagValue

if TYPE_CHECKING:
    from .types import OverrideFieldPayload

# https://github.com/revoltchat/revolt.js/blob/master/src/permissions/definitions.ts
class PermissionsFlags(FlagBase):
    """
    A class which represents a channel permissions object.

    Methods
    -------
    none: :class:`PermissionsFlags`
        Returns a new :class:`PermissionsFlags` object with all permissions set to ``False``.
    all: :class:`ChannelPermissions`
        Returns a new :class:`PermissionsFlags` object with all permissions set to ``True``.
    """

    @classmethod
    def none(cls) -> PermissionsFlags:
        return cls.new_with_flags(0b0)

    @classmethod
    def all(cls) -> PermissionsFlags:
        return cls.new_with_flags(0xFFFFFFFFFF)

    @FlagValue
    def manage_channels(self):
        """
        Whether the manage channels permission is granted.
        """
        return 1 << 0

    @FlagValue
    def manage_server(self):
        """
        Whether the manager server permission is granted.
        """
        return 1 << 1

    @FlagValue
    def manage_permissions(self):
        """
        Whether the manage permissions permission is granted.
        """
        return 1 << 2

    @FlagValue
    def manage_role(self):
        """
        Whether the manage role permission is granted.
        """
        return 1 << 3

    @FlagValue
    def kick_members(self):
        """
        Whether the kick members permission is granted.
        """
        return 1 << 6

    @FlagValue
    def ban_members(self):
        """
        Whether the ban members permission is granted.
        """
        return 1 << 7

    @FlagValue
    def timeout_members(self):
        """
        Whether the timeout members permission is granted.
        """
        return 1 << 8

    @FlagValue
    def assign_roles(self):
        """
        Whether the assign roles permission is granted.
        """
        return 1 << 9

    @FlagValue
    def change_nickname(self):
        """
        Whether the change nickname permission is granted.
        """
        return 1 << 10

    @FlagValue
    def manage_nicknames(self):
        """
        Whether the manager nicknames permission is granted.
        """
        return 1 << 11

    @FlagValue
    def change_avatar(self):
        """
        Whether the change avatar permission is granted.
        """
        return 1 << 12

    @FlagValue
    def remove_avatars(self):
        """
        Whether the remove avatars permission is granted.
        """
        return 1 << 13

    @FlagValue
    def view_channel(self):
        """
        Whether the view channel permission is granted.
        """
        return 1 << 20

    @FlagValue
    def read_message_history(self):
        """
        Whether the read message history permission is granted.
        """
        return 1 << 21

    @FlagValue
    def send_message(self):
        """
        Whether the send message permission is granted.
        """
        return 1 << 22

    @FlagValue
    def manage_messages(self):
        """
        Whether the manage messages permission is granted.
        """
        return 1 << 23

    @FlagValue
    def manage_webhooks(self):
        """
        Whether the manage webhooks permission is granted.
        """
        return 1 << 24

    @FlagValue
    def invite_others(self):
        """
        Whether the invite others permission is granted.
        """
        return 1 << 25

    @FlagValue
    def send_embeds(self):
        """
        Whether the send embeds permission is granted.
        """
        return 1 << 26

    @FlagValue
    def upload_files(self):
        """
        Whether the upload files permission is granted.
        """
        return 1 << 27

    @FlagValue
    def masquerade(self):
        """
        Whether the masquerade permission is granted.
        """
        return 1 << 28

    @FlagValue
    def connect(self):
        """
        Whether the connect permission is granted.
        """
        return 1 << 30

    @FlagValue
    def speak(self):
        """
        Whether the speak permission is granted.
        """
        return 1 << 31

    @FlagValue
    def video(self):
        """
        Whether the video permission is granted.
        """
        return 1 << 31

    @FlagValue
    def mute_members(self):
        """
        Whether the mute members permission is granted.
        """
        return 1 << 32

    @FlagValue
    def defen_members(self):
        """
        Whether the defen members permission is granted.
        """
        return 1 << 33

    @FlagValue
    def move_members(self):
        """
        Whether the move members permission is granted.
        """
        return 1 << 34


class Permissions:
    """
    A class which represents a member's permissions.
    """

    def __init__(self, data: OverrideFieldPayload):
        self.allow = PermissionsFlag.new_with_flags(data["a"])
        self.deny = PermissionsFlag.new_with_flags(data["d"])

        self.actual = PermissionsFlag.new_with_flags(data["a"] - data["d"])

        for name, val in self.actual.__dict__:
            if isinstance(val, FlagBase):
                setattr(self, name, val)

    def to_dict(self) -> OverrideFieldPayload:
        """Turns a permission object to a dictionary for api sending purposes."""
        return {"a": self.allow.flags, "d": self.deny.flags}

    @classmethod
    def from_flags(cls, allow: PermissionsFlags, deny: PermissionsFlags) -> Permissions:
        """
        Creates a Permissions object from two PermissionsFlags.

        Also note `PermissionsFlags.none()`

        Attributes
        ----------
        allow: :class:`PermissionsFlags:
            The allowed permissions.
        deny: :class:`PermissionsFlags:
            The denied permissions.
        """
        return cls.__new__({"a": allow.flags, "d": deny.flags})
