from __future__ import annotations

from typing import TYPE_CHECKING, List, TypedDict, Union

from typing_extensions import NotRequired

if TYPE_CHECKING:
    from .embed import EmbedPayload
    from .file import FilePayload


class ContentPayload(TypedDict):
    id: str
    by: NotRequired[str]
    name: NotRequired[str]


EditedPayload = TypedDict("EditedPayload", {"$date": str})


class MasqueradePayload(TypedDict):
    name: str
    avatar: str


class MessagePayload(TypedDict):
    _id: str
    channel: str
    author: str
    content: str
    attachments: NotRequired[List[FilePayload]]
    edited: NotRequired[EditedPayload]
    embeds: NotRequired[List[EmbedPayload]]
    mentions: NotRequired[List[str]]
    replies: NotRequired[List[str]]
    masquerade: NotRequired[MasqueradePayload]


class MessageReplyPayload(TypedDict):
    id: str
    mention: bool
