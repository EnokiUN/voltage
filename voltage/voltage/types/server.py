from __future__ import annotations

from typing import TYPE_CHECKING, Dict, List, Literal, Tuple, TypedDict

from typing_extensions import NotRequired, Required

from voltage.types.channel import CategoryPayload

if TYPE_CHECKING:
    from .file import FilePayload


class _MemberBase(TypedDict):
    nickname: NotRequired[str]
    avatar: NotRequired[FilePayload]
    roles: NotRequired[List[str]]


class MemberIDPayload(_MemberBase):
    server: str
    user: str


class MemberPayload(_MemberBase):
    _id: MemberIDPayload


PermissionPayload = Tuple[int, int]


class PartialRolePayload(TypedDict):
    name: str
    permissions: PermissionPayload


class RolePayload(TypedDict):
    name: str
    permissions: PermissionPayload
    colour: NotRequired[str]
    hoist: NotRequired[bool]
    rank: int


class InvitePayload(TypedDict):
    type: Literal["Server"]
    server_id: str
    server_name: str
    server_icon: NotRequired[str]
    server_banner: NotRequired[str]
    channel_id: str
    channel_name: str
    channel_description: NotRequired[str]
    user_name: str
    user_avatar: NotRequired[str]
    member_count: int


class PartialInvitePayload(TypedDict):
    _id: str
    server: str
    channel: str
    creator: str


class SystemMessagesConfigPayload(TypedDict):
    user_joined: NotRequired[str]
    user_left: NotRequired[str]
    user_kicked: NotRequired[str]
    user_banned: NotRequired[str]


class ServerPayload(TypedDict):
    _id: str
    name: str
    owner: str
    channels: List[str]
    default_permissions: PermissionPayload
    nonce: NotRequired[str]
    description: NotRequired[str]
    categories: NotRequired[List[CategoryPayload]]
    system_messages: NotRequired[SystemMessagesConfigPayload]
    roles: NotRequired[Dict[str, RolePayload]]
    icon: NotRequired[FilePayload]
    banner: NotRequired[FilePayload]
    nsfw: NotRequired[bool]
    flags: NotRequired[int]
    analytics: NotRequired[bool]
    discoverable: NotRequired[bool]


class BannedUserPayload(TypedDict):
    _id: str
    username: str
    avatar: NotRequired[FilePayload]


class BanIdPayload(TypedDict):
    server: str
    user: str


class BanPayload(TypedDict):
    _id: BanIdPayload
    reason: NotRequired[str]


class ServerBansPayload(TypedDict):
    users: List[BannedUserPayload]
    bans: List[BanPayload]
