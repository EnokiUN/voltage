from typing import Literal, TypedDict

from typing_extensions import NotRequired


class FileMetaDataPayload(TypedDict):
    type: Literal["Video", "Image", "File", "Text", "Audio"]
    height: NotRequired[int]
    width: NotRequired[int]


class FilePayload(TypedDict):
    _id: str
    tag: str
    size: int
    filename: str
    metadata: FileMetaDataPayload
    content_type: str
