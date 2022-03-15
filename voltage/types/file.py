from __future__ import annotations

from typing import Literal, TypedDict

from typing_extensions import NotRequired


class FileMetadataPayload(TypedDict):
    type: Literal["Video", "Image", "File", "Text", "Audio"]
    height: NotRequired[int]
    width: NotRequired[int]


class FilePayload(TypedDict):
    _id: str
    tag: str
    size: int
    filename: str
    metadata: FileMetadataPayload
    content_type: str
