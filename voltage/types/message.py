from typing import TYPE_CHECKING, TypedDict, List
from typing_extensions import NotRequired

if TYPE_CHECKING:
    from .embed import EmbedPayload
    from .file import FileMetaDataPayload

class ContentPayload(TypedDict):
    type: str
    content: str

EditedPayload = TypedDict("EditedPayload", {"$date": str})

class MasqueradePayload(TypedDict):
    name: str
    avatar: str

class MessagePayload(TypedDict):
    _id: str
    channel: str
    author: str
    content: ContentPayload
    attachments: NotRequired[List[FileMetadataPayload]]
    edited: NotRequired[EditedPayload]
    embeds: NotRequired[List[EmbedPayload]]
    mentions: NotRequired[List[str]]
    replies: NotRequired[List[str]]
    masquerade: NotRequired[MasqueradePayload]

class MessageReplyPayload(TypedDict):
    id: str
    mention: bool