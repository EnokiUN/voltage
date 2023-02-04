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
__version__ = "0.1.5a8"  # Updating this is such a pain.

from .asset import Asset as Asset, PartialAsset as PartialAsset
from .categories import Category as Category
from .channels import (
    Channel as Channel,
    DMChannel as DMChannel,
    GroupDMChannel as GroupDMChannel,
    SavedMessageChannel as SavedMessageChannel,
    TextChannel as TextChannel,
    VoiceChannel as VoiceChannel,
    create_channel as create_channel,
)
from .client import Client as Client
from .embed import Embed as Embed, SendableEmbed as SendableEmbed
from .enums import (
    AssetType as AssetType,
    ChannelType as ChannelType,
    EmbedType as EmbedType,
    PresenceType as PresenceType,
    RelationshipType as RelationshipType,
    SortType as SortType,
)
from .errors import (
    BotNotEnoughPerms as BotNotEnoughPerms,
    ChannelNotFound as ChannelNotFound,
    CommandNotFound as CommandNotFound,
    HTTPError as HTTPError,
    MemberNotFound as MemberNotFound,
    NotBotOwner as NotBotOwner,
    NotEnoughArgs as NotEnoughArgs,
    NotEnoughPerms as NotEnoughPerms,
    NotFoundException as NotFoundException,
    PermissionError as PermissionError,
    RoleNotFound as RoleNotFound,
    UserNotFound as UserNotFound,
    VoltageException as VoltageException,
)
from .file import File as File
from .invites import Invite as Invite
from .member import Member as Member
from .message import (
    Message as Message,
    MessageMasquerade as MessageMasquerade,
    MessageReply as MessageReply,
)
from .messageable import Messageable as Messageable
from .permissions import (
    Permissions as Permissions,
    PermissionsFlags as PermissionsFlags,
)
from .roles import Role as Role
from .server import (
    Server as Server,
    ServerBan as ServerBan,
    SystemMessages as SystemMessages,
)
from .user import User as User
from .utils import get as get
