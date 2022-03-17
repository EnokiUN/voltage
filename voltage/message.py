from __future__ import annotations
from typing import TYPE_CHECKING, NamedTuple, Optional, List, Union

from .asset import Asset, PartialAsset
from .embed import SendableEmbed, create_embed
from datetime import datetime

if TYPE_CHECKING:
    from .types import MessageReplyPayload, MessagePayload, SendableEmbedPayload, OnMessageUpdatePayload
    from .internals import CacheHandler
    from .file import File

class MessageReply(NamedTuple):
    """
    A named tuple that represents a message reply.

    Attributes
    ----------
    message: :class:`Message`
        The message that was replied to,
    mention: :class:`bool`
        Wether or not the reply mentions the author of the message.
    """
    message: Message
    mention: bool

    def to_dict(self) -> MessageReplyPayload:
        """
        Returns a dictionary representation of the message reply.
        """
        return {
            'id': self.message.id,
            'mention': self.mention
        }

class MessageMasquerade(NamedTuple):
    """
    A named tuple that represents a message's masquerade.

    Attributes
    ----------
    name: Optional[:class:`str`]
        The name of the masquerade.
    avatar: Optional[:class:`str`]
        The url to the masquerade avatar.
    """
    name: Optional[str] = None
    avatar: Optional[str] = None

    def to_dict(self) -> dict:
        """
        Returns a dictionary representation of the message masquerade.
        """
        return {
            'name': self.name if self.name else None,
            'avatar': self.avatar if self.avatar else None
        }

class Message:
    def __init__(self, data: MessagePayload, cache: CacheHandler):
        self.cache = cache
        self.id = data['_id']
        self.content = data['content']
        self.attachments = [Asset(a, cache.http) for a in data.get('attachments', [])]
        self.embeds = [create_embed(e, cache.http) for e in data.get('embeds', [])]

        self.channel = cache.get_channel(data['channel'])

        self.server = self.channel and self.channel.server
        self.author = cache.get_member(self.server.id, data['author']) if self.server else cache.get_user(data['author'])

        if masquerade := data.get('masquerade'):
            if av := masquerade.get('avatar'):
                avatar = PartialAsset(av, cache.http)
            else:
                avatar = None
            self.author.set_masquerade(masquerade.get('name'), avatar)

        self.edited_at: Optional[datetime]
        if edited := data.get('edited'):
            self.edited_at = datetime.strptime(edited['$date'], '%Y-%m-%dT%H:%M:%S.%fz')
        else:
            self.edited_at = None

        self.replies = [cache.get_message(r) for r in data.get('replies', [])]

    async def edit(self, *, content: Optional[str] = None, embed: Optional[SendableEmbed] = None, embeds: Optional[List[SendableEmbed]]):
        """
        Edits the message.

        Parameters
        ----------
        content: Optional[:class:`str`]
            The new content of the message.
        embed: Optional[:class:`SendableEmbed`]
            The new embed of the message.
        embeds: Optional[:class:`List[SendableEmbed]`]
            The new embeds of the message.
        """
        if content is None and embed is None and embeds is None:
            raise ValueError('You must provide at least one of the following: content, embed, embeds')

        if embed:
            embeds = [embed]

        await self.cache.http.edit_message(self.channel.id, self.id, content, embeds=embeds) # type: ignore

    async def delete(self):
        """
        Deletes the message.
        """
        await self.cache.http.delete_message(self.channel.id, self.id)

    async def reply(
        self,
        content: str,
        *,
        embed: Optional[Union[SendableEmbed, SendableEmbedPayload]] = None,
        embeds: Optional[List[Union[SendableEmbed, SendableEmbedPayload]]] = None,
        attachment: Optional[Union[File, str]] = None,
        attachments: Optional[List[Union[File, str]]] = None,
        masquerade: Optional[MessageMasquerade] = None,
        mention: bool = True
    ) -> Message:
        """
        Replies to the message.

        Parameters
        ----------
        content: :class:`str`
            The content of the message.
        embed: Optional[:class:`Embed`]
            The embed of the message.
        embeds: Optional[List[:class:`Embed`]]
            The embeds of the message.
        attachment: Optional[:class:`File`]
            The attachment of the message.
        attachments: Optional[List[:class:`File`]]
            The attachments of the message.
        masquerade: Optional[:class:`MessageMasquerade`]
            The masquerade of the message.
        mention: Optional[:class:`bool`]
            Wether or not the reply mentions the author of the message.

        Returns
        -------
        :class:`Message`
            The message that got sent.
        """
        embeds = [embed] if embed else embeds
        attachments = [attachment] if attachment else attachments
        replies = MessageReply(self, mention)

        message = await self.cache.http.send_message(
            self.channel.id, content, embeds=embeds, attachments=attachments, replies=replies, masquerade=masquerade
        )
        return self.cache.add_messsage(message)

    def _update(self, data: OnMessageUpdatePayload):
        if new := data.get('data'):
            if content := new.get('content'):
                self.content = content
            if edited_at := new.get('edited'):
                self.edited_at = datetime.strptime(edited_at['$date'], '%Y-%m-%dT%H:%M:%S.%fz')
            if embeds := new.get('embeds'):
                self.embeds = [create_embed(e, self.cache.http) for e in embeds]
