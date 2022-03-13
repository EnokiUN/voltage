"""
The internal Voltage library that provides types.

Heavily taken from revolt.py (https://github.com/revoltchat/revolt.py) as I couldn't find what I needed in the docs.
"""

from .message import MessagePayload, MasqueradePayload, MessageReplyPayload
from .file import FilePayload, FileMetadataPayload
from .embed import EmbedPayload, TextEmbedPayload, WebsiteEmbedPayload, ImageEmbedPayload
from .channel import ChannelPayload, DMChannelPayload, GroupDMChannelPayload, TextChannelPayload, VoiceChannelPayload, CategoryPayload
from .server import MemberPayload, InvitePayload, PartialInvitePayload, ServerPayload, BannedUserPayload, BanPayload, ServerBansPayload, SystemMessagesConfigPayload, RolePayload, PermissionPayload
from .user import UserPayload, StatusPayload, UserProfilePayload, UserRelationPayload, RelationPayload, UserBotPayload
from .http import ApiInfoPayload, VosoFeaturePayload, AutumnPayload, GetServerMembersPayload, MessageWihUserDataPayload