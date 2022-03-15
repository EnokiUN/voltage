"""
-------
Voltage
-------

A Simple Pythonic Asynchronous API wrapper for Revolt.

very wip rn
"""

__title__ = "Voltage"
__author__ = "EnokiUN"
__license__ = "MIT"
__copyright__ = "Copyright (c) 2021-present EnokiUN"
__version__ = "0.1.0a"

from .client import Client
from .embed import Embed, new_embed
from .enums import AssetType, ChannelType, EmbedType, PresenseType, SortType
from .file import File
