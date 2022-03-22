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
    id: str
        The id of the asset.
    tag: str
        The tag of the asset.
    size: int
        The size of the asset.
    name: str
        The name of the asset.
    width: Optional[int]
        The width of the asset.
    height: Optional[int]
        The height of the asset.
    type: Optional[voltage.AssetType]
        The type of the asset.
    content_type: str
        The content type of the asset.
    url: str
        The url of the asset.
    """

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

        self.url: Optional[str]
        if http.api_info:
            url = http.api_info["features"]["autumn"]["url"]
            self.url = f"{url}/{self.tag}/{self.id}"
        else:
            self.url = None

    async def get_binary(self) -> bytes:
        """
        Gets the binary data of the asset.

        Returns
        -------
        bytes
            The binary data of the asset.
        """
        return await self.http.get_file_binary(self.url)


class PartialAsset(Asset):
    """
    A partial asset caused by data lack.

    Attributes
    ----------
    url: str
        The url of the asset.
    http: HTTPHandler
        The http handler of the request.
    id: str
        The id of the asset.
    tag: Optional[str]
        The tag of the asset.
    size: int
        The size of the asset.
    name: str
        The name of the asset.
    width: Optional[int]
        The width of the asset.
    height: Optional[int]
        The height of the asset.
    type: Optional[voltage.AssetType]
        The type of the asset.
    """

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
