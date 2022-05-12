"""
-------
Voltage
-------

A Simple Pythonic Asynchronous API wrapper for Revolt.

To whoever sees this: The impostor is sus.
"""

# 2 = 1 # How's this haru?

# Edit: apparently defying the laws of math isn't enough to make all my problems dissappear and I have to expend some actual effort and time making my stuff works or else I get stupid errors, like WTF!

__title__ = "Voltage"
__author__ = "EnokiUN"
__license__ = "MIT"
__copyright__ = "Copyright (c) 2021-present EnokiUN"
__version__ = "0.1.5a5"  # Updating this is such a pain.

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
from .enums import (
    AssetType,
    ChannelType,
    EmbedType,
    PresenceType,
    RelationshipType,
    SortType,
)
from .errors import (
    ChannelNotFound,
    CommandNotFound,
    HTTPError,
    MemberNotFound,
    NotBotOwner,
    NotEnoughArgs,
    NotEnoughPerms,
    NotFoundException,
    PermissionError,
    RoleNotFound,
    UserNotFound,
    VoltageException,
)
from .file import File
from .invites import Invite
from .member import Member
from .message import Message, MessageMasquerade, MessageReply
from .messageable import Messageable
from .permissions import Permissions, PermissionsFlags
from .roles import Role
from .server import Server, ServerBan, SystemMessages
from .user import User
from .utils import get
