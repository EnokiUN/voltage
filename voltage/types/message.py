from __future__ import annotations
from __future__ import annotations
from typing import TYPE_CHECKING, TypedDict, List, Union
from typing_extensions import NotRequired

if TYPE_CHECKING:
    from .embed import EmbedPayload
    from .file import FileMetadataPayload

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
    content: Union[str, ContentPayload]
    attachments: NotRequired[List[FileMetadataPayload]]
    edited: NotRequired[EditedPayload]
    embeds: NotRequired[List[EmbedPayload]]
    mentions: NotRequired[List[str]]
    replies: NotRequired[List[str]]
    masquerade: NotRequired[MasqueradePayload]

class MessageReplyPayload(TypedDict):
    id: str
    mention: bool