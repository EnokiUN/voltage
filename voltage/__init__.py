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

from .asset import Asset as Asset
from .asset import PartialAsset as PartialAsset
from .categories import Category as Category
from .channels import Channel as Channel
from .channels import DMChannel as DMChannel
from .channels import GroupDMChannel as GroupDMChannel
from .channels import SavedMessageChannel as SavedMessageChannel
from .channels import TextChannel as TextChannel
from .channels import VoiceChannel as VoiceChannel
from .channels import create_channel as create_channel
from .client import Client as Client
from .embed import Embed as Embed
from .embed import SendableEmbed as SendableEmbed
from .enums import AssetType as AssetType
from .enums import ChannelType as ChannelType
from .enums import EmbedType as EmbedType
from .enums import PresenceType as PresenceType
from .enums import RelationshipType as RelationshipType
from .enums import SortType as SortType
from .errors import BotNotEnoughPerms as BotNotEnoughPerms
from .errors import ChannelNotFound as ChannelNotFound
from .errors import CommandNotFound as CommandNotFound
from .errors import HTTPError as HTTPError
from .errors import MemberNotFound as MemberNotFound
from .errors import NotBotOwner as NotBotOwner
from .errors import NotEnoughArgs as NotEnoughArgs
from .errors import NotEnoughPerms as NotEnoughPerms
from .errors import NotFoundException as NotFoundException
from .errors import PermissionError as PermissionError
from .errors import RoleNotFound as RoleNotFound
from .errors import UserNotFound as UserNotFound
from .errors import VoltageException as VoltageException
from .file import File as File
from .invites import Invite as Invite
from .member import Member as Member
from .message import Message as Message
from .message import MessageMasquerade as MessageMasquerade
from .message import MessageReply as MessageReply
from .messageable import Messageable as Messageable
from .permissions import Permissions as Permissions
from .permissions import PermissionsFlags as PermissionsFlags
from .roles import Role as Role
from .server import Server as Server
from .server import ServerBan as ServerBan
from .server import SystemMessages as SystemMessages
from .user import User as User
from .utils import get as get
