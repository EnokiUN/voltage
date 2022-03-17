from __future__ import annotations

from typing import TYPE_CHECKING, Dict, List, Literal, TypedDict, Union

from typing_extensions import NotRequired

if TYPE_CHECKING:
    from .file import FilePayload
    from .message import MessagePayload


class BaseChannelPayload(TypedDict):
    _id: str
    nonce: NotRequired[str]


class SavedMessagePayload(BaseChannelPayload):
    user: str
    channel_type: Literal["SavedMessage"]


class DMChannelPayload(BaseChannelPayload):
    active: bool
    recipients: List[str]
    channel_type: Literal["DirectMessage"]
    last_message: MessagePayload


class GroupDMChannelPayload(BaseChannelPayload):
    recipients: List[str]
    name: str
    owner: str
    channel_type: Literal["Group"]
    icon: NotRequired[FilePayload]
    permission: NotRequired[int]
    description: NotRequired[str]


class TextChannelPayload(BaseChannelPayload):
    server: str
    name: str
    description: NotRequired[str]
    icon: NotRequired[FilePayload]
    default_permissions: NotRequired[int]
    role_permissions: NotRequired[Dict[str, int]]
    last_message: NotRequired[str]
    channel_type: Literal["TextChannel"]


class VoiceChannelPayload(BaseChannelPayload):
    server: str
    name: str
    description: NotRequired[str]
    icon: NotRequired[FilePayload]
    default_permissions: NotRequired[int]
    role_permissions: NotRequired[Dict[str, int]]
    channel_type: Literal["VoiceChannel"]


ChannelPayload = Union[
    SavedMessagePayload, DMChannelPayload, GroupDMChannelPayload, TextChannelPayload, VoiceChannelPayload
]


class CategoryPayload(TypedDict):
    id: str
    title: str
    channels: List[ChannelPayload]
