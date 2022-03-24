from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, List, NamedTuple, Optional, Union

from .asset import Asset, PartialAsset
from .embed import SendableEmbed, create_embed

if TYPE_CHECKING:
    from .file import File
    from .internals import CacheHandler
    from .types import (
        MessagePayload,
        MessageReplyPayload,
        OnMessageUpdatePayload,
        SendableEmbedPayload,
    )


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
        return {"id": self.message.id, "mention": self.mention}


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
        return {"name": self.name if self.name else None, "avatar": self.avatar if self.avatar else None}


class Message:
    """
    A class that represents a Voltage message.

    Attributes
    ----------
    id: :class:`str`
        The id of the message.
    channel: :class:`Channel`
        The channel the message was sent in.
    attachments: List[:class:`Asset`]]
        The attachments of the message.
    embeds: List[:class:`Embed`]
        The embeds of the message.
    content: :class:`str`
        The content of the message.
    author: Union[:class:`User`, :class:`Member`]
        The author of the message.
    replies: List[:class:`Message`]
        The replies of the message.
    """

    __slots__ = (
        "id",
        "channel",
        "attachments",
        "server",
        "embeds",
        "content",
        "author",
        "edited_at",
        "reply_ids",
        "replies",
        "cache",
    )

    def __init__(self, data: MessagePayload, cache: CacheHandler):
        self.cache = cache
        self.id = data["_id"]
        self.content = data["content"]
        self.attachments = [Asset(a, cache.http) for a in data.get("attachments", [])]
        self.embeds = [create_embed(e, cache.http) for e in data.get("embeds", [])]

        self.channel = cache.get_channel(data["channel"])

        self.server = self.channel.server
        self.author = (
            cache.get_member(self.server.id, data["author"]) if self.server else cache.get_user(data["author"])
        )

        if masquerade := data.get("masquerade"):
            if av := masquerade.get("avatar"):
                avatar = PartialAsset(av, cache.http)
            else:
                avatar = None
            self.author.set_masquerade(masquerade.get("name"), avatar)

        self.edited_at: Optional[datetime]
        if edited := data.get("edited"):
            self.edited_at = datetime.strptime(edited["$date"], "%Y-%m-%dT%H:%M:%S.%fz")
        else:
            self.edited_at = None

        self.reply_ids = data.get("replies", [])
        self.replies = []
        for i in self.reply_ids:
            try:
                self.replies.append(cache.get_message(i))
            except KeyError:
                pass

    async def full_replies(self):
        """
        Returns the full list of replies of the message.
        """
        return [await self.cache.fetch_message(self.channel.id, i) for i in self.reply_ids]

    async def edit(
        self,
        *,
        content: Optional[str] = None,
        embed: Optional[SendableEmbed] = None,
        embeds: Optional[List[SendableEmbed]] = None,
    ):
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
            raise ValueError("You must provide at least one of the following: content, embed, embeds")

        if embed:
            embeds = [embed]

        await self.cache.http.edit_message(self.channel.id, self.id, content, embeds=embeds)  # type: ignore

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
        mention: bool = True,
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
            self.channel.id, content, embeds=embeds, attachments=attachments, replies=[replies], masquerade=masquerade
        )
        return self.cache.add_message(message)

    def _update(self, data: OnMessageUpdatePayload):
        if new := data.get("data"):
            if new.get("edited"):
                self.edited_at = datetime.strptime(new["data"]["$date"], "%Y-%m-%dT%H:%M:%S.%fz")
            if new.get("content"):
                self.content = new["content"]
