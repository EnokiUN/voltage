from __future__ import annotations
from typing import TYPE_CHECKING, Optional, Union, Dict

# Internal imports
from .enums import EmbedType
from .asset import Asset
from .file import File

if TYPE_CHECKING:
    from .internals import HTTPHandler
    from .types import ImageEmbedPayload, TextEmbedPayload, WebsiteEmbedPayload, SendableEmbedPayload

class WebsiteEmbed:
    """
    A class that represents a website embed.

    Attributes
    ----------
    title: Optional[str]
        The title of the embed.
    description: Optional[str]
        The description of the embed.
    url: Optional[str]
        The url of the embed.
    colour: Optional[int]
        The colour of the embed.
    special: Optional[str]
        The special data of the embed.
    image: Optional[str]
        The image of the embed.
    video: Optional[str]
        The video of the embed.
    icon_url: Optional[str]
        The icon url of the embed.
    site_name: Optional[str]
        The site name of the embed.
    """

    type = EmbedType.website

    def __init__(self, embed: WebsiteEmbedPayload):
        self.title = embed.get("title")
        self.description = embed.get("description")
        self.url = embed.get("url")
        self.colour = embed.get("colour")
        self.special = embed.get("special")
        self.image = embed.get("image")
        self.video = embed.get("video")
        self.icon_url = embed.get("icon_url")
        self.site_name = embed.get("site_name")


class ImageEmbed:
    """
    A class that represents an image embed.

    Attributes
    ----------
    url: Optional[str]
        The url of the embed.
    size: Optional[int]
        The size of the embed.
    height: Optional[int]
        The height of the embed.
    width: Optional[int]
        The width of the embed.
    """

    type = EmbedType.image

    def __init__(self, embed: ImageEmbedPayload):
        self.url = embed.get("url")
        self.size = embed.get("size")
        self.height = embed.get("height")
        self.width = embed.get("width")


class TextEmbed:
    """
    A class that represents a text embed.

    Attributes
    ----------
    title: Optional[str]
        The title of the embed.
    description: Optional[str]
        The description of the embed.
    url: Optional[str]
        The url of the embed.
    colour: Optional[int]
        The colour of the embed.
    icon_url: Optional[str]
        The icon url of the embed.
    media: Optional[Asset]
        The media of the embed.
    """
    type = EmbedType.text

    def __init__(self, embed: TextEmbedPayload, http: HTTPHandler):
        self.title = embed.get("title")
        self.description = embed.get("description")
        self.url = embed.get("url")
        self.colour = embed.get("colour")
        self.icon_url = embed.get("icon_url")
        media = embed.get("media")
        self.media = Asset(media, http) if media else None

class NoneEmbed:
    type = EmbedType.none

Embed = Union[WebsiteEmbed, ImageEmbed, TextEmbed, NoneEmbed]

class SendableEmbed: # It's Zoma's fault the name is this long.
    """
    A class that represents a sendable TextEmbed.
    This type of embed can be constructed using the new_embed function then sent.
    You should not need to construct this class yourself instead use the new_embed function.

    Attributes
    ----------
    title: Optional[str]
        The title of the embed.
    description: Optional[str]
        The description of the embed.
    url: Optional[str]
        The url of the embed.
    colour: Optional[int]
        The colour of the embed.
    icon_url: Optional[str]
        The icon url of the embed.
    media: Optional[str]
        The media of the embed.
    """
    def __init__(self, title: Optional[str] = None, description: Optional[str] = None, url: Optional[str] = None, colour: Optional[int] = None, icon_url: Optional[str] = None, media: Optional[Union[str, File]] = None):
        self.title = title
        self.description = description
        self.url = url
        self.colour = colour
        self.icon_url = icon_url
        self.media = media

    async def to_dict(self, http: HTTPHandler) -> SendableEmbedPayload:
        """
        A function that returns an embed as a dict for api purposes.
        You shouldn't run this method yourself.

        Returns
        -------
        SendableEmbedPayload
            The embed as a dict.
        """
        embed: SendableEmbedPayload = {"type": "Text"}
        if self.title is not None:
            embed["title"] = self.title
        if self.description is not None:
            embed["description"] = self.description
        if self.url is not None:
            embed["url"] = self.url
        if self.colour is not None:
            embed["colour"] = str(self.colour)
        if self.icon_url is not None:
            embed["icon_url"] = self.icon_url
        if self.media is not None:
            if isinstance(self.media, File):
                embed["media"] = await self.media.get_id(http)
            else:
                embed["media"] = (await http.upload_file((await http.get_file_binary(self.media.split("?")[0])), "Embed Attachment", "attachments"))["id"]
        return embed