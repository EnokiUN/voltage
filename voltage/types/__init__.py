"""
The internal Voltage library that provides types.
"""

from .embed import (
    EmbedPayload,
    ImageEmbedPayload,
    TextEmbedPayload,
    WebsiteEmbedPayload,
)
from .file import FileMetaDataPayload, FilePayload
from .message import MasqueradePayload, MessagePayload, MessageReplyPayload
