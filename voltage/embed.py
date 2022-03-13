from typing import TYPE_CHECKING

# Internal imports
from .enums import EmbedType

if TYPE_CHECKING:
    from .types import WebsiteEmbedPayload, ImageEmbedPayload, TextEmbedPayload

class WebsiteEmbed:
    type = EmbedType.website

    def __init__(self, embed: WebsiteEmbedPayload):
        pass