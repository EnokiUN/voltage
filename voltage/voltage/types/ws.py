from __future__ import annotations

from tkinter import W
from typing import TYPE_CHECKING, List, Literal, TypedDict, Union

if TYPE_CHECKING:
    from .channel import (
        ChannelPayload,
        DMChannelPayload,
        GroupDMChannelPayload,
        SavedMessagePayload,
        TextChannelPayload,
        VoiceChannelPayload,
    )
    from .message import EditedPayload, MessagePayload
    from .server import MemberIDPayload, MemberPayload, ServerPayload
    from .user import StatusPayload, UserPayload


class BasePayload(TypedDict):
    type: str


class AuthenticatePayload(BasePayload):
    token: str


class OnReadyPayload(BasePayload):
    users: List[UserPayload]
    servers: List[ServerPayload]
    channels: List[ChannelPayload]
    members: List[MemberPayload]


class OnMessagePayload(BasePayload, MessagePayload):
    pass


class MessageUpdateDataPayload(BasePayload):
    content: str
    data: EditedPayload


class OnMessageUpdatePayload(BasePayload):
    id: str
    channel: str
    data: MessageUpdateDataPayload


class OnMessageDeletePayload(BasePayload):
    id: str
    channel: str


class OnChannelCreatePayload_SavedMessage(BasePayload, SavedMessagePayload):
    pass


class OnChannelCreatePayload_Group(BasePayload, GroupDMChannelPayload):
    pass


class OnChannelCreatePayload_TextChannel(BasePayload, TextChannelPayload):
    pass


class OnChannelCreatePayload_VoiceChannel(BasePayload, VoiceChannelPayload):
    pass


class OnChannelCreatePayload_DMChannel(BasePayload, DMChannelPayload):
    pass


OnChannelCreatePayload = Union[
    OnChannelCreatePayload_SavedMessage,
    OnChannelCreatePayload_Group,
    OnChannelCreatePayload_DMChannel,
    OnChannelCreatePayload_VoiceChannel,
    OnChannelCreatePayload_TextChannel,
]


class OnChannelUpdatePayload(BasePayload):
    id: str
    data: ChannelPayload
    clear: Literal["Icon", "Description"]


class OnChannelDeletePayload(BasePayload):
    id: str


class OnChannelStartTypingPayload(BasePayload):
    id: str
    user: str


OnChannelDeleteTypingPayload = OnChannelStartTypingPayload


class OnServerUpdatePayload(BasePayload):
    id: str
    data: dict
    clear: Literal["Icon", "Banner", "Description"]


class OnServerDeletePayload(BasePayload):
    id: str


class OnServerMemberUpdatePayload(BasePayload):
    id: MemberIDPayload
    data: dict
    clear: Literal["Nickname", "Avatar"]


class OnServerMemberJoinPayload(BasePayload):
    id: str
    user: str


OnServerMemberLeavePayload = OnServerMemberJoinPayload


class OnServerRoleUpdatePayload(BasePayload):
    id: str
    role_id: str
    data: dict
    clear: Literal["Color"]


class OnServerRoleDeletePayload(BasePayload):
    id: str
    role_id: str


class OnUserUpdatePayload(BasePayload):
    id: str
    data: dict
    clear: Literal["ProfileContent", "ProfileBackground", "StatusText", "Avatar"]


class OnUserRelationshipPayload(BasePayload):
    id: str
    user: str
    status: StatusPayload
