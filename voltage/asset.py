from __future__ import annotations

from typing import TYPE_CHECKING, Optional

# Internal imports
from .enums import AssetType

if TYPE_CHECKING:
    from .internals import HTTPHandler
    from .types import FilePayload


class Asset:
    """
    A class that represents a revolt asset.

    Attributes
    ----------
    id: :class:`str`
        The id of the asset.
    tag: :class:`str`
        The tag of the asset.
    size: :class:`int`
        The size of the asset.
    name: :class:`str`
        The name of the asset.
    width: Optional[:class:`int`]
        The width of the asset.
    height: Optional[:class:`int`]
        The height of the asset.
    type: Optional[:class:`AssetType`]
        The type of the asset.
    content_type: :class:`str`
        The content type of the asset.
    url: :class:`str`
        The url of the asset.
    """

    __slots__ = ("id", "tag", "size", "name", "width", "height", "type", "content_type", "url", "http", "data")

    def __init__(self, data: FilePayload, http: HTTPHandler):
        self.data = data
        self.http = http

        self.id = data.get("_id")
        self.tag = data.get("tag")
        self.size = data.get("size")
        self.name = data.get("filename")

        metadata = data.get("metadata")
        if metadata:
            self.width = metadata.get("width")
            self.height = metadata.get("height")
            self.type = AssetType(metadata.get("type"))

        self.content_type = data.get("content_type")

        if http.api_info:
            url = http.api_info["features"]["autumn"]["url"]
            self.url = f"{url}/{self.tag}/{self.id}"
        else:
            self.url = ""  # this cannot happen lmfao

    async def get_binary(self) -> bytes:
        """
        Gets the binary data of the asset.

        Returns
        -------
        :class:`bytes`
            The binary data of the asset.
        """
        return await self.http.get_file_binary(self.url)


class PartialAsset(Asset):
    """
    A partial asset caused by data lack.

    Attributes
    ----------
    url: :class:`str`
        The url of the asset.
    id: :class:`str`
        The id of the asset.
    tag: Optional[:class:`str`]
        The tag of the asset.
    size: :class:`int`
        The size of the asset.
    name: :class:`str`
        The name of the asset.
    width: Optional[:class:`int`]
        The width of the asset.
    height: Optional[:class:`int`]
        The height of the asset.
    type: Optional[:class:`AssetType`]
        The type of the asset.
    """

    __slots__ = ("url", "http", "id", "tag", "size", "name", "width", "height", "type", "content_type")

    def __init__(self, url: str, http: HTTPHandler):
        self.url = url
        self.http = http

        self.id = "0"
        self.tag = None
        self.size = 0
        self.name = ""
        self.width = None
        self.height = None
        self.type = AssetType.file
        self.content_type = None
