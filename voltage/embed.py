from typing import TYPE_CHECKING

# Internal imports
from .enums import EmbedType

if TYPE_CHECKING:
    from .types import ImageEmbedPayload, TextEmbedPayload, WebsiteEmbedPayload


class WebsiteEmbed:
    type = EmbedType.website

    def __init__(self, embed: WebsiteEmbedPayload):
        pass
