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

from .asset import Asset, PartialAsset
from .categories import Category
from .channels import (
    Channel,
    DMChannel,
    GroupDMChannel,
    SavedMessageChannel,
    TextChannel,
    VoiceChannel,
    create_channel,
)
from .client import Client
from .embed import Embed, SendableEmbed
from .enums import AssetType, ChannelType, EmbedType, PresenceType, SortType
from .errors import HTTPError, VoltageException
from .file import File
from .invites import Invite
from .message import Message, MessageMasquerade, MessageReply
from .messageable import Messageable
from .permissions import (
    ChannelPermissions,
    ServerPermissions,
    channel_permissions,
    server_permissions,
)
from .roles import Role
from .user import User
from .member import Member
from .server import Server, ServerBan, SystemMessages
