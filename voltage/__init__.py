"""
-------
Voltage
-------

A Simple Pythonic Asynchronous API wrapper for Revolt.

=====
Usage
=====

.. code-block:: python3

    import voltage

    client = voltage.Client()

    @client.listen('ready')
    async def on_ready(payload):
        print(f"Logged in as {client.user}")

    @client.listen('message')
    async def on_message(message): # doesn't matter what you call the function.
        if message.content == '-ping':
            await message.channel.send('pong!')
        if message.content == '-embed':
            embed = voltage.SendableEmbed(title="Hello World", description="This is an embed")
            await message.reply(content="embed", embed=embed) # Obligatory message content.

    client.run("TOKEN")

=======
Credits
=======

    - **Contributers**, thank you :)

    - `Revolt.py <https://github.com/revoltchat/revolt.py>`_, When shit broke, that's where I went.

    - `Revolt.js <https://github.com/revoltchat/revolt.js>`_, When the docs fail you.

    - `Discord.py <https://github.com/Rapptz/discord.py>`_, Also a really great help while making this.

    - **Revolt development team**, Absolute chads.

"""

__title__ = "Voltage"
__author__ = "EnokiUN"
__license__ = "MIT"
__copyright__ = "Copyright (c) 2021-present EnokiUN"
__version__ = "0.1.4a4"

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
from .member import Member
from .message import Message, MessageMasquerade, MessageReply
from .messageable import Messageable
from .permissions import (
    ChannelPermissions,
    ServerPermissions,
    channel_permissions,
    server_permissions,
)
from .roles import Role
from .server import Server, ServerBan, SystemMessages
from .user import User

__all__ = [
    "Asset",
    "AssetType",
    "Channel",
    "ChannelType",
    "Client",
    "Category",
    "DMChannel",
    "Embed",
    "EmbedType",
    "File",
    "HTTPError",
    "Invite",
    "GroupDMChannel",
    "Member",
    "Message",
    "MessageMasquerade",
    "MessageReply",
    "Messageable",
    "PartialAsset",
    "PresenceType",
    "Role",
    "SavedMessageChannel",
    "SendableEmbed",
    "Server",
    "ServerBan",
    "ServerPermissions",
    "SavedMessageChannel",
    "SortType",
    "SystemMessages",
    "TextChannel",
    "VoiceChannel",
    "VoltageException",
    "channel_permissions",
    "server_permissions",
    "create_channel",
    "server_permissions",
]
