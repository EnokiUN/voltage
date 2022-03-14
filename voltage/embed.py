from __future__ import annotations
from typing import TYPE_CHECKING, Union, Optional

# Internal imports
from .enums import EmbedType

if TYPE_CHECKING:
    from .types import WebsiteEmbedPayload, ImageEmbedPayload, TextEmbedPayload
    from .internals import CacheHandler

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
    This type of embed can be constructed using the new_embed function then sent.
    
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

    def __init__(self, embed: TextEmbedPayload):
        self.title = embed.get("title")
        self.description = embed.get("description")
        self.url = embed.get("url")
        self.colour = embed.get("colour")
        self.icon_url = embed.get("icon_url")
        media = embed.get("media")
        self.media = media

    def to_dict(self) -> TextEmbedPayload:
        """
        Returns the embed as a dict.
        """
        embed: TextEmbedPayload = {"type": "Text"}

        if title := self.title:
            embed["title"] = title
        if description := self.description:
            embed["description"] = description
        if url := self.url:
            embed["url"] = url
        if colour := self.colour:
            embed["colour"] = colour
        if icon_url := self.icon_url:
            embed["icon_url"] = icon_url
        if media := self.media:
            embed["media"] = media
        
        return embed

class NoneEmbed:
    type = EmbedType.none
    
Embed = Union[WebsiteEmbed, ImageEmbed, TextEmbed, NoneEmbed]

def new_embed(title: Optional[str] = None, description: Optional[str] = None, url: Optional[str] = None, colour: Optional[int] = None, icon_url: Optional[str] = None, media: Optional[str] = None) -> TextEmbed:
    """
    The base function to create a Voltage TextEmbed for sending purposes.
    
    Parameters
    ----------
    title: Optional[str]
        The title of the embed.
    description: Optional[str]
        The description of the embed.
    url: Optional[str]
        The url at the title of the embed.
    colour: Optional[int]
        The colour of the embed as an integer ex 0xffffff.
    icon_url: Optional[str]
        The url of the embeds icon.
    media: Optional[str]
        The media of the embed.
    """
    payload: TextEmbedPayload = {"type": "Text"}
    if title:
        payload["title"] = title
    if description:
        payload["description"] = description
    if url:
        payload["url"] = url
    if colour:
        payload["colour"] = str(colour)
    if icon_url:
        payload["icon_url"] = icon_url
    if media:
        payload["media"] = media
    return TextEmbed(payload)
